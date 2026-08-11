from django import forms
from catalog.models import Book, EBookMetadata

class EBookUploadForm(forms.Form):
    book = forms.ModelChoiceField(
        queryset=Book.objects.filter(book_type__in=['EBOOK', 'BOTH'], is_active=True).order_by('title'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Select Book Title",
        help_text="Only books marked as 'E-Book Only' or 'Both Physical and E-Book' are shown."
    )
    file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        label="PDF Document",
        help_text="Must be a valid PDF file under 20 MB."
    )
    access_mode = forms.ChoiceField(
        choices=EBookMetadata.ACCESS_MODE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Access Mode"
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
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        label="Replace PDF Document (Optional)",
        help_text="Leave blank to keep the current PDF file.",
        required=False
    )
    access_mode = forms.ChoiceField(
        choices=EBookMetadata.ACCESS_MODE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Access Mode"
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
