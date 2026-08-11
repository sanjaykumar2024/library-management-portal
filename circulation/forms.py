from django import forms
from .models import Loan
from accounts.models import UserProfile
from catalog.models import BookCopy

class IssueBookForm(forms.Form):
    membership_number = forms.CharField(
        max_length=50,
        label='Member ID',
        help_text='Enter the member\'s library card number (e.g. LIB-2026-12345).',
        widget=forms.TextInput(attrs={'placeholder': 'e.g. LIB-2026-12345', 'autocomplete': 'off'})
    )
    accession_number = forms.CharField(
        max_length=50,
        label='Book Copy Accession Number',
        help_text='Enter the unique copy identifier found on the book\'s barcode label.',
        widget=forms.TextInput(attrs={'placeholder': 'e.g. BOK-1001', 'autocomplete': 'off'})
    )

    def clean_membership_number(self):
        mem_num = self.cleaned_data.get('membership_number')
        try:
            member = UserProfile.objects.get(membership_number=mem_num)
        except UserProfile.DoesNotExist:
            raise forms.ValidationError('Member with this ID does not exist.')

        if member.membership_status != 'ACTIVE':
            raise forms.ValidationError(f'Cannot issue to member. Status is {member.get_membership_status_display()}.')

        # Check active loan limit (max 5 books at a time)
        active_loans = Loan.objects.filter(member=member, status='ISSUED').count()
        if active_loans >= 5:
            raise forms.ValidationError(
                f'This member already has {active_loans} active loans. '
                f'Maximum 5 books can be issued at a time.'
            )

        return member

    def clean_accession_number(self):
        acc_num = self.cleaned_data.get('accession_number')
        try:
            copy = BookCopy.objects.select_related('book').get(accession_number=acc_num)
        except BookCopy.DoesNotExist:
            raise forms.ValidationError('Book copy with this accession number does not exist.')

        if copy.status != 'AVAILABLE':
            raise forms.ValidationError(f'Book copy is not available. Current status: {copy.get_status_display()}')

        return copy
