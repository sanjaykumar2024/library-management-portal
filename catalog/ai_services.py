import re
import math
from collections import Counter
from catalog.models import Book
from ebooks.models import EBookMetadata

STOPWORDS = {
    'the', 'a', 'an', 'is', 'in', 'at', 'of', 'on', 'and', 'to', 'for', 'with', 'by',
    'about', 'as', 'into', 'like', 'through', 'after', 'over', 'between', 'out',
    'against', 'during', 'without', 'before', 'under', 'around', 'among', 'this',
    'that', 'these', 'those', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
    'has', 'had', 'do', 'does', 'did', 'but', 'if', 'or', 'because', 'what', 'which',
    'who', 'whom', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each',
    'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
    'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just', 'should',
    'now', 'i', 'me', 'my', 'we', 'our', 'you', 'your', 'he', 'him', 'his', 'she',
    'her', 'it', 'its', 'they', 'them', 'their', 'book', 'books', 'want', 'please',
    'show', 'find', 'get', 'tell'
}

class AIAssistantEngine:
    """
    Production-grade Semantic Search & RAG (Retrieval-Augmented Generation) Engine.
    Combines sublinear TF-IDF vectors, n-gram shingle expansion, IDF weighting,
    cosine similarity distance, extractive passage retrieval, and context-grounded
    answer generation.
    """

    @staticmethod
    def _tokenize(text, include_bigrams=True):
        if not text:
            return []
        words = [w.lower() for w in re.findall(r'\b[a-zA-Z0-9]{2,}\b', text)]
        meaningful_words = [w for w in words if w not in STOPWORDS]
        tokens = list(meaningful_words)
        
        if include_bigrams and len(words) >= 2:
            for i in range(len(words) - 1):
                w1, w2 = words[i], words[i+1]
                if w1 not in STOPWORDS or w2 not in STOPWORDS:
                    tokens.append(f"{w1}_{w2}")
        return tokens or words

    @staticmethod
    def _compute_tf(tokens):
        if not tokens:
            return {}
        counts = Counter(tokens)
        total = len(tokens)
        # Sublinear TF scaling
        return {term: (1.0 + math.log(count)) / math.log(total + 2.0) for term, count in counts.items()}

    @staticmethod
    def _extract_relevant_passage(text, query_tokens):
        if not text:
            return ""
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        if not sentences:
            return text[:140] + "..." if len(text) > 140 else text
            
        best_sentence = sentences[0]
        best_overlap = -1
        query_set = {t.replace('_', ' ') for t in query_tokens}

        for sent in sentences:
            sent_lower = sent.lower()
            overlap = sum(1 for q in query_set if q in sent_lower)
            if overlap > best_overlap:
                best_overlap = overlap
                best_sentence = sent

        clean_passage = best_sentence.strip()
        if len(clean_passage) > 160:
            clean_passage = clean_passage[:157].rsplit(' ', 1)[0] + "..."
        return clean_passage

    @classmethod
    def rank_catalog_books(cls, query, category_id=None, book_type=None, avail_only=False):
        """
        Ranks all matching books using semantic vector cosine similarity.
        Returns list of tuples: (book, score_percentage, top_passage)
        """
        query_clean = query.strip()
        if not query_clean:
            return []

        query_tokens = cls._tokenize(query_clean, include_bigrams=True)
        if not query_tokens:
            return []

        query_tf = cls._compute_tf(query_tokens)

        # Base QuerySet
        qs = Book.objects.filter(is_active=True).select_related('category', 'ebook_metadata').prefetch_related('authors', 'copies')
        if category_id:
            if isinstance(category_id, int) or (isinstance(category_id, str) and str(category_id).isdigit()):
                qs = qs.filter(category_id=int(category_id))
            else:
                from .models import Category
                cat = Category.resolve(category_id)
                if cat:
                    qs = qs.filter(category=cat)
                else:
                    from django.db.models import Q
                    qs = qs.filter(Q(category__name__iexact=str(category_id)) | Q(category__name__icontains=str(category_id)))
        if book_type:
            qs = qs.filter(book_type=book_type)
        if avail_only:
            from django.db.models import Q
            qs = qs.filter(Q(copies__status='AVAILABLE') | Q(ebook_metadata__is_active=True)).distinct()

        all_books = list(qs)
        if not all_books:
            return []

        # Build corpus document tokens & compute IDF
        doc_tokens_list = []
        doc_frequency = Counter()
        for book in all_books:
            authors_str = " ".join(a.full_name for a in book.authors.all())
            cat_str = book.category.name if book.category else ""
            desc_str = book.description or ""
            doc_text = f"{book.title} {book.title} {authors_str} {cat_str} {desc_str}"
            tokens = cls._tokenize(doc_text, include_bigrams=True)
            doc_tokens_list.append(tokens)
            unique_terms = set(tokens)
            doc_frequency.update(unique_terms)

        n_docs = len(all_books)
        idf = {term: math.log((n_docs + 1.0) / (doc_frequency[term] + 1.0)) + 1.0 for term in doc_frequency}

        # Weight query vector by IDF
        query_vec = {}
        for t, tf_val in query_tf.items():
            query_vec[t] = tf_val * idf.get(t, 1.0)

        query_norm = math.sqrt(sum(v * v for v in query_vec.values())) or 1.0

        scored = []
        query_lower = query_clean.lower()

        for idx, book in enumerate(all_books):
            doc_tokens = doc_tokens_list[idx]
            if not doc_tokens:
                continue

            doc_tf = cls._compute_tf(doc_tokens)
            dot_product = 0.0
            for t, q_weight in query_vec.items():
                if t in doc_tf:
                    doc_weight = doc_tf[t] * idf.get(t, 1.0)
                    dot_product += q_weight * doc_weight

            doc_norm = math.sqrt(sum((doc_tf[t] * idf.get(t, 1.0)) ** 2 for t in doc_tf)) or 1.0
            cosine_sim = dot_product / (query_norm * doc_norm)

            # Contextual Lexical Boosts
            title_lower = book.title.lower()
            authors_lower = " ".join(a.full_name.lower() for a in book.authors.all())
            cat_lower = (book.category.name if book.category else "").lower()

            boost = 0.0
            if query_lower in title_lower:
                boost += 0.40
            if query_lower in authors_lower:
                boost += 0.35
            if query_lower in cat_lower:
                boost += 0.25

            # Partial token matches
            for token in query_tokens:
                t_clean = token.replace('_', ' ')
                if len(t_clean) >= 3:
                    if t_clean in title_lower:
                        boost += 0.15
                    if t_clean in authors_lower:
                        boost += 0.10

            final_score = cosine_sim + boost

            if final_score > 0.02:
                # Calibrate to percentage 60% - 99%
                percentage = min(99, int(60 + (final_score / 1.5) * 39))
                passage = cls._extract_relevant_passage(book.description, query_tokens)
                scored.append((book, percentage, passage, final_score))

        scored.sort(key=lambda item: item[3], reverse=True)
        return [(item[0], item[1], item[2]) for item in scored]

    @classmethod
    def search_and_generate_response(cls, query):
        """
        RAG Assistant: Retrieves relevant catalog items and synthesizes
        a context-grounded conversational response with citation cards and copy radar.
        """
        query_clean = query.strip()
        if not query_clean:
            return {
                "answer": "Hello! Ask me any question about books, authors, topics, or e-books available in LibrarySphere.",
                "citations": [],
                "suggested_questions": [
                    "What books are available on Technology or AI?",
                    "Which e-books can I read online immediately?",
                    "Recommend books about artificial intelligence or machine learning."
                ]
            }

        ranked_results = cls.rank_catalog_books(query_clean)
        top_matches = ranked_results[:5]

        citations = []
        for book, match_score, passage in top_matches:
            available_copies = book.copies.filter(status='AVAILABLE').count()
            total_copies = book.copies.count()
            has_ebook = hasattr(book, 'ebook_metadata') and book.ebook_metadata is not None and book.ebook_metadata.is_active

            citations.append({
                'id': book.id,
                'title': book.title,
                'isbn': book.isbn,
                'category': book.category.name if book.category else 'General Literature',
                'authors': book.author,
                'book_type': book.get_book_type_display(),
                'available_copies': available_copies,
                'total_copies': total_copies,
                'has_ebook': has_ebook,
                'ebook_id': book.ebook_metadata.id if has_ebook else None,
                'ebook_access_mode': book.ebook_metadata.get_access_mode_display() if has_ebook else None,
                'cover_image_url': book.cover_image.url if book.cover_image else None,
                'match_score': match_score,
                'passage': passage,
            })

        # Grounded RAG Answer Synthesis
        query_lower = query_clean.lower()
        if citations:
            best_match = citations[0]
            titles_list = ", ".join(f"**{c['title']}**" for c in citations[:3])

            if any(term in query_lower for term in ['ebook', 'e-book', 'digital', 'pdf', 'read online', 'stream']):
                ebook_citations = [c for c in citations if c['has_ebook']]
                if ebook_citations:
                    answer = (
                        f"I found **{len(ebook_citations)} digital e-book(s)** directly matching your inquiry! "
                        f"You can stream and read **{ebook_citations[0]['title']}** online immediately ({ebook_citations[0]['ebook_access_mode']}). "
                        f"Click **Read E-Book Online** below to launch the protected viewer."
                    )
                else:
                    answer = (
                        f"I analyzed our collection for *\"{query_clean}\"*. While physical editions of {titles_list} are catalogued, "
                        f"they currently do not have digital streaming e-book passes attached."
                    )
            elif any(term in query_lower for term in ['available', 'borrow', 'issue', 'copies', 'copy', 'shelf']):
                avail_citations = [c for c in citations if c['available_copies'] > 0 or c['has_ebook']]
                if avail_citations:
                    top_avail = avail_citations[0]
                    answer = (
                        f"Great news! We have **{len(avail_citations)} matching title(s)** available right now. "
                        f"Specifically, **{top_avail['title']}** has **{top_avail['available_copies']} physical copy(ies) on shelf** at the circulation desk, ready for checkout or pickup hold."
                    )
                else:
                    answer = (
                        f"All physical copies for the top matching books ({titles_list}) are currently checked out by other readers. "
                        f"However, you can join the hold waitlist with 1 click, and our system will automatically reserve the next returned copy for you!"
                    )
            else:
                answer = (
                    f"Based on semantic indexing of our library collection, I found strong relevance for {titles_list}. "
                    f"The top match is **{best_match['title']}** ({best_match['match_score']}% Semantic Match) by {best_match['authors']}. "
                    f"*{best_match['passage']}* "
                    f"You can explore copies, place holds, or read digital editions from the citation cards below."
                )
        else:
            answer = (
                f"I performed a semantic analysis of our library database for *\"{query_clean}\"*, but found no matching books or passages. "
                f"Try searching by broad topics (e.g. *Technology*, *Science Fiction*, *History*), author names, or general keywords."
            )

        suggested_questions = [
            "Which e-books can I read online immediately?",
            "What books are available right now on the shelf?",
            "Show me top recommended books in Technology and Computer Science."
        ]

        return {
            "answer": answer,
            "citations": citations,
            "suggested_questions": suggested_questions,
            "total_matches": len(citations)
        }

