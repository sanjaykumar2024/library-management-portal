from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, Author, Book, BookCopy, EBookMetadata


class CatalogSearchTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('testuser', password='Test!Pass99')
        cls.cat = Category.objects.create(name='Fiction')
        cls.author = Author.objects.create(full_name='Jane Doe')
        cls.book = Book.objects.create(
            title='Test Book Alpha',
            isbn='1111111111111',
            category=cls.cat,
            description='A test book.',
            book_type='PHYSICAL',
        )
        cls.book.authors.add(cls.author)
        BookCopy.objects.create(
            book=cls.book,
            accession_number='LIB-TEST-001',
            shelf_location='Row A, Shelf 1',
            status='AVAILABLE',
        )

    def test_catalog_page_loads(self):
        self.client.login(username='testuser', password='Test!Pass99')
        response = self.client.get(reverse('catalog:list'))
        self.assertEqual(response.status_code, 200)

    def test_search_by_title(self):
        self.client.login(username='testuser', password='Test!Pass99')
        response = self.client.get(reverse('catalog:list'), {'q': 'Alpha'})
        self.assertContains(response, 'Test Book Alpha')

    def test_search_by_author(self):
        self.client.login(username='testuser', password='Test!Pass99')
        response = self.client.get(reverse('catalog:list'), {'q': 'Jane Doe'})
        self.assertContains(response, 'Test Book Alpha')

    def test_search_no_results(self):
        self.client.login(username='testuser', password='Test!Pass99')
        response = self.client.get(reverse('catalog:list'), {'q': 'nonexistent'})
        self.assertContains(response, 'No books found')


class CatalogFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('filteruser', password='Test!Pass99')
        cls.cat1 = Category.objects.create(name='Sci-Fi')
        cls.cat2 = Category.objects.create(name='History')
        cls.author = Author.objects.create(full_name='Author One')

        cls.physical_book = Book.objects.create(
            title='Physical Only Book',
            isbn='2222222222222',
            category=cls.cat1,
            description='Physical.',
            book_type='PHYSICAL',
        )
        cls.physical_book.authors.add(cls.author)

        cls.ebook = Book.objects.create(
            title='Digital Only Book',
            isbn='3333333333333',
            category=cls.cat2,
            description='Digital.',
            book_type='EBOOK',
        )
        cls.ebook.authors.add(cls.author)
        EBookMetadata.objects.create(book=cls.ebook, format='PDF')

    def test_filter_by_category(self):
        self.client.login(username='filteruser', password='Test!Pass99')
        response = self.client.get(reverse('catalog:list'), {'category': self.cat1.id})
        self.assertContains(response, 'Physical Only Book')
        self.assertNotContains(response, 'Digital Only Book')

    def test_filter_by_category_name_string(self):
        self.client.login(username='filteruser', password='Test!Pass99')
        # Test filtering by category name as string (from home page pill/directory)
        response = self.client.get(reverse('catalog:list'), {'category': 'Sci-Fi'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Physical Only Book')
        self.assertNotContains(response, 'Digital Only Book')

    def test_filter_by_category_name_case_insensitive(self):
        self.client.login(username='filteruser', password='Test!Pass99')
        response = self.client.get(reverse('catalog:list'), {'category': 'history'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Digital Only Book')
        self.assertNotContains(response, 'Physical Only Book')

    def test_filter_by_book_type(self):
        self.client.login(username='filteruser', password='Test!Pass99')
        response = self.client.get(reverse('catalog:list'), {'type': 'EBOOK'})
        self.assertContains(response, 'Digital Only Book')
        self.assertNotContains(response, 'Physical Only Book')

    def test_book_detail_page(self):
        self.client.login(username='filteruser', password='Test!Pass99')
        response = self.client.get(reverse('catalog:detail', args=[self.physical_book.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Physical Only Book')


class AIAssistantTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('aiuser', password='Test!Pass99')
        cls.cat = Category.objects.create(name='Artificial Intelligence')
        cls.author = Author.objects.create(full_name='Alan Turing')
        cls.book = Book.objects.create(
            title='Neural Networks and RAG Search',
            isbn='9999999999999',
            category=cls.cat,
            description='Deep learning and vector semantic search.',
            book_type='EBOOK',
        )
        cls.book.authors.add(cls.author)
        EBookMetadata.objects.create(book=cls.book, format='PDF', access_mode='READ_AND_DOWNLOAD')

    def test_ai_assistant_page_loads(self):
        self.client.login(username='aiuser', password='Test!Pass99')
        response = self.client.get(reverse('catalog:ai_assistant'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Knowledge Assistant')

    def test_ai_assistant_api_search(self):
        self.client.login(username='aiuser', password='Test!Pass99')
        response = self.client.post(
            reverse('catalog:ai_assistant_api'),
            data='{"query": "Neural Networks"}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn('answer', json_data)
        self.assertIn('citations', json_data)
        self.assertTrue(len(json_data['citations']) > 0)
        self.assertEqual(json_data['citations'][0]['title'], 'Neural Networks and RAG Search')

    def test_global_semantic_search_api(self):
        self.client.login(username='aiuser', password='Test!Pass99')
        response = self.client.get(
            reverse('catalog:semantic_search_api') + '?q=Neural Networks'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn('answer', json_data)
        self.assertIn('citations', json_data)
        self.assertTrue(len(json_data['citations']) > 0)
        self.assertEqual(json_data['citations'][0]['title'], 'Neural Networks and RAG Search')
        self.assertIn('match_score', json_data['citations'][0])

    def test_catalog_semantic_mode(self):
        response = self.client.get(
            reverse('catalog:list') + '?q=Neural&mode=semantic'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_semantic'])
        self.assertEqual(response.context['selected_mode'], 'semantic')
        self.assertContains(response, 'Semantic AI Results')

