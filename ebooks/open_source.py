"""
Open Source E-Book Service for LibrarySphere.
Provides integration with global open-source public domain repositories (Project Gutenberg via Gutendex API)
and includes an offline-resilient registry of fully formatted world literature classics.
"""

import os
import uuid
import json
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from catalog.models import Book, Author, Category, EBookMetadata


class OpenSourceEBookService:
    """Service to search, retrieve, and import open-source public domain e-books."""

    GUTENDEX_API_URL = "https://gutendex.com/books"

    # Curated, pre-formatted public domain literary classics for guaranteed offline resilience
    CURATED_CLASSICS = [
        {
            "id": "gutenberg-1342",
            "gutenberg_id": 1342,
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "author_bio": "English novelist known primarily for her six major novels interpreting and critiquing the British landed gentry.",
            "category": "Romance & Classic Fiction",
            "language": "English",
            "publication_year": 1813,
            "description": "A classic comedy of manners and romance set in 19th-century England, following the turbulent relationship between Elizabeth Bennet, the daughter of a country gentleman, and Fitzwilliam Darcy, a rich aristocratic landowner.",
            "cover_gradient": "linear-gradient(135deg, #4f46e5, #ec4899)",
            "content_html": """
                <div class="book-container">
                    <header class="text-center my-4">
                        <h1 class="display-4 fw-bold">Pride and Prejudice</h1>
                        <p class="lead text-muted">By Jane Austen (1813)</p>
                        <hr class="my-4">
                    </header>
                    <article class="chapter">
                        <h2>Chapter 1</h2>
                        <p>It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.</p>
                        <p>However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered the rightful property of some one or other of their daughters.</p>
                        <p>"My dear Mr. Bennet," said his lady to him one day, "have you heard that Netherfield Park is let at last?"</p>
                        <p>Mr. Bennet replied that he had not.</p>
                        <p>"But it is," returned she; "for Mrs. Long has just been here, and she told me all about it."</p>
                        <p>Mr. Bennet made no answer.</p>
                        <p>"Do you not want to know who has taken it?" cried his wife impatiently.</p>
                        <p>"You want to tell me, and I have no objection to hearing it."</p>
                        <p>This was invitation enough.</p>
                        <p>"Why, my dear, you must know, Mrs. Long says that Netherfield is taken by a young man of large fortune from the north of England; that he came down on Monday in a chaise and four to see the place, and was so much delighted with it, that he agreed with Mr. Morris immediately; that he is to take possession before Michaelmas, and some of his servants are to be in the house by the end of next week."</p>
                    </article>
                    <article class="chapter mt-5">
                        <h2>Chapter 2</h2>
                        <p>Mr. Bennet was among the earliest of those who waited on Mr. Bingley. He had always intended to visit him, though to the last always assuring his wife that he should not go; and till the evening after the visit was paid she had no knowledge of it.</p>
                        <p>The astonishment of the ladies was just what he wished; that of Mrs. Bennet perhaps surpassing the rest; though, when the first tumult of joy was over, she began to declare that it was what she had expected all the while.</p>
                    </article>
                    <article class="chapter mt-5">
                        <h2>Chapter 3</h2>
                        <p>Not all that Mrs. Bennet, however, with the assistance of her five daughters, could ask on the subject, was sufficient to draw from her husband any satisfactory description of Mr. Bingley. They attacked him in various ways—with barefaced questions, ingenious suppositions, and distant surmises; but he eluded the skill of them all.</p>
                        <p>Mr. Bingley was good-looking and gentlemanlike; he had a pleasant countenance, and easy, unaffected manners. But his friend Mr. Darcy soon drew the attention of the room by his fine, tall person, handsome features, noble mien, and the report which was in general circulation within five minutes after his entrance, of his having ten thousand a year.</p>
                    </article>
                    <footer class="text-center mt-5 p-4 border-top text-muted small">
                        <p>Public Domain Edition &bull; Project Gutenberg &bull; LibrarySphere Digital Commons</p>
                    </footer>
                </div>
            """
        },
        {
            "id": "gutenberg-84",
            "gutenberg_id": 84,
            "title": "Frankenstein; or, The Modern Prometheus",
            "author": "Mary Wollstonecraft Shelley",
            "author_bio": "English novelist who wrote the Gothic novel Frankenstein, considered one of the earliest examples of science fiction.",
            "category": "Gothic Horror & Science Fiction",
            "language": "English",
            "publication_year": 1818,
            "description": "The seminal gothic science-fiction novel telling the story of Victor Frankenstein, a young scientist who creates a sapient creature in an unorthodox scientific experiment, with tragic consequences.",
            "cover_gradient": "linear-gradient(135deg, #0f172a, #059669)",
            "content_html": """
                <div class="book-container">
                    <header class="text-center my-4">
                        <h1 class="display-4 fw-bold">Frankenstein</h1>
                        <h2 class="h4 text-muted">or, The Modern Prometheus</h2>
                        <p class="lead text-muted">By Mary Wollstonecraft Shelley (1818)</p>
                        <hr class="my-4">
                    </header>
                    <article class="chapter">
                        <h2>Letter 1</h2>
                        <p class="text-muted"><em>To Mrs. Saville, England. St. Petersburgh, Dec. 11th, 17—.</em></p>
                        <p>You will rejoice to hear that no disaster has accompanied the commencement of an enterprise which you have regarded with such evil forebodings. I arrived here yesterday, and my first task is to assure my dear sister of my welfare and increasing confidence in the success of my undertaking.</p>
                        <p>I am already far north of London, and as I walk in the streets of Petersburgh, I feel a cold northern breeze play upon my cheeks, which braces my nerves and fills me with delight. Do you understand this feeling? This breeze, which has travelled from the regions towards which I am advancing, gives me a foretaste of those icy climes.</p>
                    </article>
                    <article class="chapter mt-5">
                        <h2>Chapter 4: The Discovery</h2>
                        <p>From this day natural philosophy, and particularly chemistry, in the most comprehensive sense of the term, became nearly my sole occupation. I read with ardour those works, so full of genius and discrimination, which modern inquirers have written on these subjects.</p>
                        <p>No one can conceive the variety of feelings which bore me onwards, like a whirlwind, eager to penetrate into the secrets of nature. After days and nights of incredible labour and fatigue, I succeeded in discovering the cause of generation and life; nay, more, I became myself capable of bestowing animation upon lifeless matter.</p>
                        <p>The astonishment which I at first experienced on this discovery soon gave place to delight and rapture. After so much time spent in painful labour, to arrive at once at the summit of my desires was the most gratifying consummation of my toils.</p>
                    </article>
                    <article class="chapter mt-5">
                        <h2>Chapter 5: The Awakening</h2>
                        <p>It was on a dreary night of November that I beheld the accomplishment of my toils. With an anxiety that almost amounted to agony, I collected the instruments of life around me, that I might infuse a spark of being into the lifeless thing that lay at my feet.</p>
                        <p>It was already one in the morning; the rain pattered dismally against the panes, and my candle was nearly burnt out, when, by the glimmer of the half-extinguished light, I saw the dull yellow eye of the creature open; it breathed hard, and a convulsive motion agitated its limbs.</p>
                    </article>
                    <footer class="text-center mt-5 p-4 border-top text-muted small">
                        <p>Public Domain Edition &bull; Project Gutenberg &bull; LibrarySphere Digital Commons</p>
                    </footer>
                </div>
            """
        },
        {
            "id": "gutenberg-1661",
            "gutenberg_id": 1661,
            "title": "The Adventures of Sherlock Holmes",
            "author": "Arthur Conan Doyle",
            "author_bio": "British writer and physician who created the legendary detective Sherlock Holmes in 1887.",
            "category": "Mystery & Detective Fiction",
            "language": "English",
            "publication_year": 1892,
            "description": "A collection of twelve short stories featuring the brilliant Victorian consulting detective Sherlock Holmes and his companion Dr. John H. Watson, solving London's most baffling mysteries.",
            "cover_gradient": "linear-gradient(135deg, #1e293b, #d97706)",
            "content_html": """
                <div class="book-container">
                    <header class="text-center my-4">
                        <h1 class="display-4 fw-bold">The Adventures of Sherlock Holmes</h1>
                        <p class="lead text-muted">By Arthur Conan Doyle (1892)</p>
                        <hr class="my-4">
                    </header>
                    <article class="chapter">
                        <h2>I. A Scandal in Bohemia</h2>
                        <p>To Sherlock Holmes she is always <em>the</em> woman. I have seldom heard him mention her under any other name. In his eyes she eclipses and predominates the whole of her sex.</p>
                        <p>It was not that he felt any emotion akin to love for Irene Adler. All emotions, and that one particularly, were abhorrent to his cold, precise but admirably balanced mind. He was, I take it, the most perfect reasoning and observing machine that the world has seen.</p>
                        <p>One night—it was on the twentieth of March, 1888—I was returning from a journey to a patient (for I had now returned to civil practice), when my way led me through Baker Street. As I passed the well-remembered door, which must always be associated in my mind with my wooing, and with the dark incidents of the Study in Scarlet, I was seized with a keen desire to see Holmes again, and to know how he was employing his extraordinary powers.</p>
                        <p>"You see, but you do not observe. The distinction is clear," Holmes remarked, leaning back in his armchair and sending up a thin blue ring of smoke.</p>
                    </article>
                    <article class="chapter mt-5">
                        <h2>II. The Red-Headed League</h2>
                        <p>I had called upon my friend, Mr. Sherlock Holmes, one day in the autumn of last year and found him in deep conversation with a very stout, florid-faced, elderly gentleman with fiery red hair. With an apology for my intrusion, I was about to withdraw when Holmes pulled me abruptly into the room and closed the door behind me.</p>
                        <p>"You could not have come at a better time, my dear Watson," he said cordially.</p>
                    </article>
                    <footer class="text-center mt-5 p-4 border-top text-muted small">
                        <p>Public Domain Edition &bull; Project Gutenberg &bull; LibrarySphere Digital Commons</p>
                    </footer>
                </div>
            """
        },
        {
            "id": "gutenberg-345",
            "gutenberg_id": 345,
            "title": "Dracula",
            "author": "Bram Stoker",
            "author_bio": "Irish author best known for his 1897 Gothic horror novel Dracula.",
            "category": "Gothic Horror",
            "language": "English",
            "publication_year": 1897,
            "description": "The quintessential epistolary vampire novel detailing Count Dracula's attempt to move from Transylvania to England in search of new blood, and the battle between him and a group of determined adversaries led by Professor Abraham Van Helsing.",
            "cover_gradient": "linear-gradient(135deg, #450a0a, #dc2626)",
            "content_html": """
                <div class="book-container">
                    <header class="text-center my-4">
                        <h1 class="display-4 fw-bold">Dracula</h1>
                        <p class="lead text-muted">By Bram Stoker (1897)</p>
                        <hr class="my-4">
                    </header>
                    <article class="chapter">
                        <h2>Chapter 1: Jonathan Harker's Journal</h2>
                        <p class="text-muted"><em>3 May. Bistritz.—</em>Left Munich at 8:35 P.M., on 1st May, arriving at Vienna early next morning; should have arrived at 6:46, but train was an hour late. Buda-Pesth seems a wonderful place, from the glimpse which I got of it from the train and the little I could see of the streets.</p>
                        <p>The impression I had was that we were leaving the West and entering the East; the most western of splendid bridges over the Danube, which was here of noble width and depth, took us among the traditions of Turkish rule.</p>
                        <p>We left in pretty good time, and came after nightfall to Klausenburgh. Here I stopped for the night at the Hotel Royale. I had for dinner, or rather supper, a chicken done up some way with red pepper, which was very good but thirsty.</p>
                    </article>
                    <article class="chapter mt-5">
                        <h2>Chapter 2: Castle Dracula</h2>
                        <p>The Count stood looking at me for a moment, then he said: "Welcome to my house! Enter freely and of your own will!" He made no motion of stepping to meet me, but stood like a statue, as though his gesture of welcome had fixed him into stone.</p>
                        <p>The moment, however, that I had stepped over the threshold, he stepped forward and holding out his hand grasped mine with a strength which made me wince, an effect which was not lessened by the fact that it seemed as cold as ice—more like the hand of a dead than a living man.</p>
                    </article>
                    <footer class="text-center mt-5 p-4 border-top text-muted small">
                        <p>Public Domain Edition &bull; Project Gutenberg &bull; LibrarySphere Digital Commons</p>
                    </footer>
                </div>
            """
        },
        {
            "id": "gutenberg-11",
            "gutenberg_id": 11,
            "title": "Alice's Adventures in Wonderland",
            "author": "Lewis Carroll",
            "author_bio": "English author, poet, mathematician, and logician best known for Alice in Wonderland.",
            "category": "Fantasy & Children's Literature",
            "language": "English",
            "publication_year": 1865,
            "description": "The enchanting story of young Alice falling down a rabbit hole into a subterranean fantasy world populated by peculiar, anthropomorphic creatures.",
            "cover_gradient": "linear-gradient(135deg, #0284c7, #8b5cf6)",
            "content_html": """
                <div class="book-container">
                    <header class="text-center my-4">
                        <h1 class="display-4 fw-bold">Alice's Adventures in Wonderland</h1>
                        <p class="lead text-muted">By Lewis Carroll (1865)</p>
                        <hr class="my-4">
                    </header>
                    <article class="chapter">
                        <h2>Chapter I: Down the Rabbit-Hole</h2>
                        <p>Alice was beginning to get very tired of sitting by her sister on the bank, and of having nothing to do: once or twice she had peeped into the book her sister was reading, but it had no pictures or conversations in it, "and what is the use of a book," thought Alice "without pictures or conversations?"</p>
                        <p>So she was considering in her own mind (as well as she could, for the hot day made her feel very sleepy and stupid), whether the pleasure of making a daisy-chain would be worth the trouble of getting up and picking the daisies, when suddenly a White Rabbit with pink eyes ran close by her.</p>
                        <p>There was nothing so <em>very</em> remarkable in that; nor did Alice think it so <em>very</em> much out of the way to hear the Rabbit say to itself, "Oh dear! Oh dear! I shall be late!" But when the Rabbit actually <em>took a watch out of its waistcoat-pocket</em>, and looked at it, and then hurried on, Alice started to her feet, for it flashed across her mind that she had never before seen a rabbit with either a waistcoat-pocket, or a watch to take out of it, and burning with curiosity, she ran across the field after it, and fortunately was just in time to see it pop down a large rabbit-hole under the hedge.</p>
                    </article>
                    <footer class="text-center mt-5 p-4 border-top text-muted small">
                        <p>Public Domain Edition &bull; Project Gutenberg &bull; LibrarySphere Digital Commons</p>
                    </footer>
                </div>
            """
        },
        {
            "id": "gutenberg-64317",
            "gutenberg_id": 64317,
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "author_bio": "American novelist whose works illustrate the Jazz Age of the 1920s.",
            "category": "American Literature & Modern Fiction",
            "language": "English",
            "publication_year": 1925,
            "description": "Set in the Jazz Age on Long Island, the novel follows narrator Nick Carraway and his interactions with the mysterious millionaire Jay Gatsby and Gatsby's obsession with reunited love Daisy Buchanan.",
            "cover_gradient": "linear-gradient(135deg, #1e1b4b, #eab308)",
            "content_html": """
                <div class="book-container">
                    <header class="text-center my-4">
                        <h1 class="display-4 fw-bold">The Great Gatsby</h1>
                        <p class="lead text-muted">By F. Scott Fitzgerald (1925)</p>
                        <hr class="my-4">
                    </header>
                    <article class="chapter">
                        <h2>Chapter 1</h2>
                        <p>In my younger and more vulnerable years my father gave me some advice that I've been turning over in my mind ever since.</p>
                        <p>"Whenever you feel like criticizing any one," he told me, "just remember that all the people in this world haven't had the advantages that you've had."</p>
                        <p>He didn't say any more, but we've always been unusually communicative in a reserved way, and I understood that he meant a great deal more than that. In consequence, I'm inclined to reserve all judgements, a habit that has opened up many curious natures to me and also made me the victim of not a few veteran bores.</p>
                    </article>
                    <article class="chapter mt-5">
                        <h2>Chapter 9: The Green Light</h2>
                        <p>Gatsby believed in the green light, the orgastic future that year by year recedes before us. It eluded us then, but that's no matter—to-morrow we will run faster, stretch out our arms farther. . . . And one fine morning——</p>
                        <p>So we beat on, boats against the current, borne back ceaselessly into the past.</p>
                    </article>
                    <footer class="text-center mt-5 p-4 border-top text-muted small">
                        <p>Public Domain Edition &bull; Project Gutenberg &bull; LibrarySphere Digital Commons</p>
                    </footer>
                </div>
            """
        },
        {
            "id": "gutenberg-35",
            "gutenberg_id": 35,
            "title": "The Time Machine",
            "author": "H. G. Wells",
            "author_bio": "English writer prolific in many genres; often called a father of science fiction.",
            "category": "Science Fiction & Speculative",
            "language": "English",
            "publication_year": 1895,
            "description": "A pioneering science fiction novella about an English scientist and inventor who builds a machine to travel through time, journeying to the year A.D. 802,701 to meet the Eloi and Morlocks.",
            "cover_gradient": "linear-gradient(135deg, #18181b, #0ea5e9)",
            "content_html": """
                <div class="book-container">
                    <header class="text-center my-4">
                        <h1 class="display-4 fw-bold">The Time Machine</h1>
                        <p class="lead text-muted">By H. G. Wells (1895)</p>
                        <hr class="my-4">
                    </header>
                    <article class="chapter">
                        <h2>Chapter 1: The Fourth Dimension</h2>
                        <p>The Time Traveller (for so it will be convenient to speak of him) was expounding a recondite matter to us. His grey eyes shone and twinkled, and his usually pale face was flushed and animated. The fire burnt brightly, and the soft radiance of the incandescent lights in the lilies of silver caught the bubbles that flashed and passed in our glasses.</p>
                        <p>"Can a cube that does not last for any time at all, have a real existence?"</p>
                        <p>There was a murmur of agreement.</p>
                        <p>"Clearly," the Time Traveller proceeded, "any real body must have extension in four directions: it must have Length, Breadth, Thickness, and—Duration. But through a natural infirmity of the flesh, which I will explain to you in a moment, we incline to overlook this fact. There are really four dimensions, three which we call the three planes of Space, and a fourth, Time."</p>
                    </article>
                    <footer class="text-center mt-5 p-4 border-top text-muted small">
                        <p>Public Domain Edition &bull; Project Gutenberg &bull; LibrarySphere Digital Commons</p>
                    </footer>
                </div>
            """
        },
        {
            "id": "gutenberg-5200",
            "gutenberg_id": 5200,
            "title": "The Metamorphosis",
            "author": "Franz Kafka",
            "author_bio": "German-speaking Bohemian novelist and short-story writer, widely regarded as one of the major figures of 20th-century literature.",
            "category": "Philosophical & Existential Fiction",
            "language": "English",
            "publication_year": 1915,
            "description": "The famous novella telling the story of salesman Gregor Samsa, who wakes one morning to find himself inexplicably transformed into a monstrous vermin.",
            "cover_gradient": "linear-gradient(135deg, #292524, #a855f7)",
            "content_html": """
                <div class="book-container">
                    <header class="text-center my-4">
                        <h1 class="display-4 fw-bold">The Metamorphosis</h1>
                        <p class="lead text-muted">By Franz Kafka (1915)</p>
                        <hr class="my-4">
                    </header>
                    <article class="chapter">
                        <h2>Part I</h2>
                        <p>One morning, when Gregor Samsa woke from troubled dreams, he found himself transformed in his bed into a horrible vermin. He lay on his armour-like back, and if he lifted his head a little he could see his brown belly, slightly domed and divided by arches into stiff sections. The bedding was hardly able to cover it and seemed ready to slide off any moment.</p>
                        <p>His many legs, pitifully thin compared with the size of the rest of him, waved about helplessly as he looked. "What's happened to me?" he thought. It wasn't a dream. His room, a proper human room although a little too small, lay peacefully between its four familiar walls.</p>
                    </article>
                    <footer class="text-center mt-5 p-4 border-top text-muted small">
                        <p>Public Domain Edition &bull; Project Gutenberg &bull; LibrarySphere Digital Commons</p>
                    </footer>
                </div>
            """
        },
        {
            "id": "gutenberg-98",
            "gutenberg_id": 98,
            "title": "A Tale of Two Cities",
            "author": "Charles Dickens",
            "author_bio": "English novelist and social critic who created some of the world's best-known fictional characters.",
            "category": "Historical Fiction & Classics",
            "language": "English",
            "publication_year": 1859,
            "description": "Set in London and Paris before and during the French Revolution, depicting the plight of the French peasantry and the violence of the Reign of Terror.",
            "cover_gradient": "linear-gradient(135deg, #1c1917, #3b82f6)",
            "content_html": """
                <div class="book-container">
                    <header class="text-center my-4">
                        <h1 class="display-4 fw-bold">A Tale of Two Cities</h1>
                        <p class="lead text-muted">By Charles Dickens (1859)</p>
                        <hr class="my-4">
                    </header>
                    <article class="chapter">
                        <h2>Book the First—Recalled to Life</h2>
                        <h3>Chapter I: The Period</h3>
                        <p>It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness, it was the epoch of belief, it was the epoch of incredulity, it was the season of light, it was the season of darkness, it was the spring of hope, it was the winter of despair.</p>
                        <p>We had everything before us, we had nothing before us, we were all going direct to Heaven, we were all going direct the other way—in short, the period was so far like the present period, that some of its noisiest authorities insisted on its being received, for good or for evil, in the superlative degree of comparison only.</p>
                    </article>
                    <footer class="text-center mt-5 p-4 border-top text-muted small">
                        <p>Public Domain Edition &bull; Project Gutenberg &bull; LibrarySphere Digital Commons</p>
                    </footer>
                </div>
            """
        },
        {
            "id": "gutenberg-2701",
            "gutenberg_id": 2701,
            "title": "Moby-Dick; or, The Whale",
            "author": "Herman Melville",
            "author_bio": "American novelist, short story writer, and poet of the American Renaissance period.",
            "category": "Adventure & American Classics",
            "language": "English",
            "publication_year": 1851,
            "description": "The epic narrative of sailor Ishmael and the obsessive quest of Captain Ahab, revenge-driven master of the whaling ship Pequod, seeking the giant white sperm whale Moby Dick.",
            "cover_gradient": "linear-gradient(135deg, #0c4a6e, #14b8a6)",
            "content_html": """
                <div class="book-container">
                    <header class="text-center my-4">
                        <h1 class="display-4 fw-bold">Moby-Dick</h1>
                        <h2 class="h4 text-muted">or, The Whale</h2>
                        <p class="lead text-muted">By Herman Melville (1851)</p>
                        <hr class="my-4">
                    </header>
                    <article class="chapter">
                        <h2>Chapter 1: Loomings</h2>
                        <p>Call me Ishmael. Some years ago—never mind how long precisely—having little or no money in my purse, and nothing particular to interest me on shore, I thought I would sail about a little and see the watery part of the world.</p>
                        <p>It is a way I have of driving off the spleen and regulating the circulation. Whenever I find myself growing grim about the mouth; whenever it is a damp, drizzly November in my soul; whenever I find myself involuntarily pausing before coffin warehouses, and bringing up the rear of every funeral I meet; and especially whenever my hypos get such an upper hand of me, that it requires a strong moral principle to prevent me from deliberately stepping into the street, and methodically knocking people's hats off—then, I account it high time to get to sea as soon as I can.</p>
                    </article>
                    <footer class="text-center mt-5 p-4 border-top text-muted small">
                        <p>Public Domain Edition &bull; Project Gutenberg &bull; LibrarySphere Digital Commons</p>
                    </footer>
                </div>
            """
        }
    ]

    @classmethod
    def get_curated_classics(cls):
        """Returns the curated list of guaranteed public domain classics with catalog status."""
        catalog_isbns = set(Book.objects.filter(book_type__in=['EBOOK', 'BOTH']).values_list('isbn', flat=True))
        results = []
        for c in cls.CURATED_CLASSICS:
            expected_isbn = f"978-GUTEN-{c['gutenberg_id']}"
            item = dict(c)
            item['is_imported'] = expected_isbn in catalog_isbns
            results.append(item)
        return results

    @classmethod
    def fetch_from_gutendex(cls, search_query='', topic=''):
        """
        Attempts to search Project Gutenberg via the Gutendex REST API.
        Falls back to local curated classics if offline or on network failure.
        """
        params = []
        if search_query:
            params.append(f"search={urllib.parse.quote(search_query)}")
        if topic:
            params.append(f"topic={urllib.parse.quote(topic)}")

        url = f"{cls.GUTENDEX_API_URL}?{'&'.join(params)}" if params else cls.GUTENDEX_API_URL

        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'LibrarySphere-Portal/1.0'})
            with urllib.request.urlopen(req, timeout=4) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return cls._normalize_gutendex_results(data.get('results', []))
        except Exception:
            # Offline or unreachable: filter our offline curated registry
            pass

        # Fallback filter over curated classics
        filtered = []
        q_lower = search_query.lower()
        topic_lower = topic.lower()
        for c in cls.get_curated_classics():
            matches_q = not search_query or (q_lower in c['title'].lower() or q_lower in c['author'].lower() or q_lower in c['description'].lower())
            matches_topic = not topic or (topic_lower in c['category'].lower())
            if matches_q and matches_topic:
                filtered.append(c)
        return filtered

    @classmethod
    def _normalize_gutendex_results(cls, raw_books):
        """Maps raw Gutendex book JSON into standard LibrarySphere format."""
        catalog_isbns = set(Book.objects.filter(book_type__in=['EBOOK', 'BOTH']).values_list('isbn', flat=True))
        normalized = []
        for b in raw_books:
            b_id = b.get('id')
            isbn = f"978-GUTEN-{b_id}"
            authors = ", ".join([a.get('name', 'Unknown') for a in b.get('authors', [])]) or "Unknown Author"
            subjects = ", ".join(b.get('subjects', [])[:3]) or "Literature & Classics"
            formats = b.get('formats', {})
            read_url = formats.get('text/html') or formats.get('text/html; charset=utf-8') or formats.get('text/plain; charset=utf-8')

            normalized.append({
                "id": f"gutenberg-{b_id}",
                "gutenberg_id": b_id,
                "title": b.get('title', 'Untitled'),
                "author": authors,
                "author_bio": "Project Gutenberg Public Domain Contributor",
                "category": subjects,
                "language": (b.get('languages') or ['English'])[0].title(),
                "publication_year": 1900,
                "description": f"Public domain masterpiece from Project Gutenberg. Downloaded {b.get('download_count', 0)} times worldwide.",
                "cover_gradient": "linear-gradient(135deg, #1e293b, #4f46e5)",
                "read_url": read_url,
                "is_imported": isbn in catalog_isbns,
            })
        return normalized

    @classmethod
    def import_book_to_catalog(cls, book_data, uploaded_by=None):
        """
        Imports an open-source book into the local Library catalog as a full-fledged EBook.
        Creates Book, Author, Category, and EBookMetadata records, and stores the readable HTML file.
        """
        gutenberg_id = book_data.get('gutenberg_id')
        isbn = f"978-GUTEN-{gutenberg_id}"

        # 1. Check if already imported by ISBN or Title
        existing = Book.objects.filter(isbn=isbn).first() or Book.objects.filter(title__iexact=book_data.get('title')).first()
        if existing and hasattr(existing, 'ebook_metadata'):
            return existing, False

        # 2. Get or create Category
        cat_name = book_data.get('category', 'Classics').split(',')[0].strip()[:90] or 'Classics'
        category, _ = Category.objects.get_or_create(
            name=cat_name,
            defaults={'description': 'Public domain and open access literature'}
        )

        # 3. Get or create Author
        author_name = book_data.get('author', 'Unknown Author').strip()
        # Clean inverted names like "Austen, Jane" to "Jane Austen"
        if ',' in author_name and len(author_name.split(',')) == 2:
            parts = [p.strip() for p in author_name.split(',')]
            clean_author_name = f"{parts[1]} {parts[0]}"
        else:
            clean_author_name = author_name

        author, _ = Author.objects.get_or_create(
            full_name=clean_author_name[:190],
            defaults={'bio': book_data.get('author_bio', 'Author of public domain classic literature.')}
        )

        # 4. Create or update Book record
        if existing:
            book = existing
            if book.book_type == 'PHYSICAL':
                book.book_type = 'BOTH'
                book.save(update_fields=['book_type'])
        else:
            book = Book.objects.create(
                isbn=isbn,
                title=book_data.get('title', 'Open Source E-Book'),
                category=category,
                publication_year=book_data.get('publication_year', 1900),
                language=book_data.get('language', 'English'),
                description=book_data.get('description', 'Public domain literature available under the Project Gutenberg License.'),
                book_type='EBOOK',
                publisher='Project Gutenberg / Open Domain',
                is_active=True,
            )
        book.authors.add(author)

        # Attach publisher-grade simulated hardcover cover if missing
        if not book.cover_image:
            try:
                from catalog.cover_generator import BookCoverGenerator
                cover_file = BookCoverGenerator.generate_cover(
                    title=book.title,
                    author=clean_author_name,
                    category=category.name if category else 'Classic Literature',
                    isbn=book.isbn
                )
                book.cover_image.save(cover_file.name, cover_file, save=True)
            except Exception:
                pass

        content_html = book_data.get('content_html')
        if not content_html and book_data.get('read_url'):
            # If from live Gutendex and has read_url, attempt to fetch, else wrap in iframe/summary
            try:
                req = urllib.request.Request(book_data['read_url'], headers={'User-Agent': 'LibrarySphere/1.0'})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    content_html = resp.read().decode('utf-8', errors='ignore')
            except Exception:
                content_html = f"""
                    <div class="book-container p-4">
                        <h1>{book.title}</h1>
                        <p class="lead">By {clean_author_name}</p>
                        <hr>
                        <p>{book.description}</p>
                        <p>This public domain book is archived on Project Gutenberg (EBook #{gutenberg_id}).</p>
                    </div>
                """

        if not content_html:
            content_html = f"""
                <div class="book-container p-4">
                    <h1>{book.title}</h1>
                    <p class="lead">By {clean_author_name}</p>
                    <hr>
                    <p>{book.description}</p>
                </div>
            """

        # Wrap with standard reader styling if raw
        full_document = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{book.title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Georgia, serif;
            line-height: 1.8;
            color: #1e293b;
            background: #fdfdfd;
            margin: 0;
            padding: 2rem;
        }}
        .book-container {{
            max-width: 760px;
            margin: 0 auto;
        }}
        h1, h2, h3 {{ color: #0f172a; margin-top: 2rem; }}
        p {{ margin-bottom: 1.25rem; font-size: 1.05rem; }}
        hr {{ border: 0; border-top: 1px solid #e2e8f0; margin: 2rem 0; }}
        footer {{ margin-top: 4rem; color: #64748b; font-size: 0.85rem; }}
    </style>
</head>
<body>
{content_html}
</body>
</html>"""

        # 6. Save to protected storage
        protected_root = Path(getattr(settings, 'PROTECTED_EBOOK_ROOT', settings.BASE_DIR / 'protected_ebooks'))
        os.makedirs(protected_root, exist_ok=True)
        filename = f"{uuid.uuid4().hex}.html"
        file_path = protected_root / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_document)

        # 7. Create or update EBookMetadata
        ebook_meta, _ = EBookMetadata.objects.get_or_create(
            book=book,
            defaults={
                'protected_filename': filename,
                'original_file_name': f"{book.title.replace(' ', '_')}.html",
                'uploaded_by': uploaded_by,
                'file_size': len(full_document.encode('utf-8')),
                'page_count': max(content_html.count('<h') or 12, 1),
                'format': 'HTML',
                'rental_price': Decimal('0.00'),
                'access_mode': 'READ_AND_DOWNLOAD',
                'rights_status': 'PUBLIC_DOMAIN',
                'rights_text': 'Project Gutenberg License & Public Domain Dedication',
                'max_concurrent_readers': 0, # Unlimited
                'is_active': True,
                'access_note': 'Open access public-domain classic &bull; Free instant reading for all patrons.',
            }
        )

        try:
            from core.models import log_activity
            author_names = ", ".join([a.full_name for a in book.authors.all()])
            log_activity('EBOOK_IMPORTED', f"Imported open-access classic '{book.title}' by {author_names or 'Unknown'}", user=uploaded_by)
        except Exception:
            pass


        return book, True

