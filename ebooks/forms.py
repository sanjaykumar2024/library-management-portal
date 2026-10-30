from django import forms
from catalog.models import Book, EBookMetadata

class EBookUploadForm(forms.Form):
    book = forms.ModelChoiceField(
        queryset=Book.objects.filter(book_type__in=['EBOOK', 'BOTH'], is_active=True).order_by('title'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Select Existing Book Title (Optional)",
        required=False,
        help_text="Select an existing book from the catalog, OR type a new title below."
    )
    manual_title = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Artificial Intelligence & Machine Learning Guide'}),
        label="Or Type Book Title Manually",
        help_text="Type a new book title manually if it is not in the dropdown list above."
    )
    file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.html,.htm'}),
        label="PDF or HTML Document",
        help_text="Must be a valid PDF (.pdf) or HTML (.html, .htm) file under 20 MB."
    )

    def clean(self):
        cleaned_data = super().clean()
        book = cleaned_data.get('book')
        manual_title = cleaned_data.get('manual_title')

        if not book and not (manual_title and manual_title.strip()):
            raise forms.ValidationError("Please either select an existing book title or type a new book title manually.")
        return cleaned_data

    access_level = forms.ChoiceField(
        choices=EBookMetadata.ACCESS_LEVEL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Book Access Level",
        initial='MEMBERS_ONLY',
        help_text="FREE = Anyone can read (Guests & Members); MEMBERS_ONLY = Active library card required; STAFF_ONLY = Librarians & Admins only."
    )
    access_mode = forms.ChoiceField(
        choices=EBookMetadata.ACCESS_MODE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Access Mode"
    )
    rental_price = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        initial=0.00,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        label="Digital Rental Price (₹)",
        help_text="Set to 0.00 for free access, or specify a low fee (e.g. 5.00) for a reading pass."
    )

    rights_status = forms.ChoiceField(
        choices=EBookMetadata.RIGHTS_STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Rights / Licence Status"
    )
    rights_text = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'e.g. Published under CC BY 4.0 license by Public Library Press.'}),
        label="Rights & Attribution Text",
        required=True
    )
    access_note = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional instructions or notice for members...'}),
        label="Member Access Note",
        required=False
    )


class EBookEditForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.html,.htm'}),
        label="Replace PDF / HTML Document (Optional)",
        help_text="Leave blank to keep the current file.",
        required=False
    )

    access_level = forms.ChoiceField(
        choices=EBookMetadata.ACCESS_LEVEL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Book Access Level",
        initial='MEMBERS_ONLY',
        help_text="FREE = Anyone can read (Guests & Members); MEMBERS_ONLY = Active library card required; STAFF_ONLY = Librarians & Admins only."
    )
    access_mode = forms.ChoiceField(
        choices=EBookMetadata.ACCESS_MODE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Access Mode"
    )
    rental_price = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        label="Digital Rental Price (₹)",
        help_text="Set to 0.00 for free reading, or specify fee (e.g. 5.00) for reading pass."
    )
    rights_status = forms.ChoiceField(

        choices=EBookMetadata.RIGHTS_STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Rights / Licence Status"
    )
    rights_text = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label="Rights & Attribution Text",
        required=True
    )
    access_note = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label="Member Access Note",
        required=False
    )
    is_active = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Active (Available in Portal)",
        required=False
    )
