from django import forms
from .models import Book, BookCopy, Category, Author


class BookForm(forms.ModelForm):
    """Librarian form for creating/editing catalogue books."""
    author_names = forms.CharField(
        max_length=500,
        help_text='Comma-separated author names (e.g., "Jane Austen, Mark Twain")',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Author Name 1, Author Name 2'})
    )

    class Meta:
        model = Book
        fields = ['title', 'isbn', 'category', 'publisher', 'publication_year',
                  'language', 'description', 'book_type', 'cover_image', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'publisher': forms.TextInput(attrs={'class': 'form-control'}),
            'publication_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'language': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'book_type': forms.Select(attrs={'class': 'form-select'}),
            'cover_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['author_names'].initial = ', '.join(
                a.full_name for a in self.instance.authors.all()
            )

    def save(self, commit=True):
        book = super().save(commit=commit)
        if commit:
            author_names_str = self.cleaned_data.get('author_names', '')
            author_names = [name.strip() for name in author_names_str.split(',') if name.strip()]
            authors = []
            for name in author_names:
                author, _ = Author.objects.get_or_create(full_name=name)
                authors.append(author)
            book.authors.set(authors)
        return book


class BookCopyForm(forms.ModelForm):
    """Librarian form for registering physical copies of a book."""
    class Meta:
        model = BookCopy
        fields = ['accession_number', 'shelf_location', 'condition', 'status']
        widgets = {
            'accession_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'LIB-PHY-00001'}),
            'shelf_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Aisle 3, Shelf B-12'}),
            'condition': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Good / New / Fair'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
