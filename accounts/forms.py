from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import re

class MemberRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, required=True,
        help_text='Your legal first name.',
        widget=forms.TextInput(attrs={'placeholder': 'e.g. John', 'autocomplete': 'given-name'})
    )
    last_name = forms.CharField(
        max_length=30, required=True,
        help_text='Your legal last name.',
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Smith', 'autocomplete': 'family-name'})
    )
    email = forms.EmailField(
        required=True,
        help_text='A valid email address for library notifications.',
        widget=forms.EmailInput(attrs={'placeholder': 'e.g. john.smith@email.com', 'autocomplete': 'email'})
    )
    phone_number = forms.CharField(
        max_length=20, required=False,
        help_text='Optional. We may contact you about reservations.',
        widget=forms.TextInput(attrs={'placeholder': 'e.g. +1-555-0123', 'autocomplete': 'tel'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email address already exists.')
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        if phone and not re.match(r'^[\d\s\+\-\(\)]{7,20}$', phone):
            raise forms.ValidationError('Please enter a valid phone number (digits, spaces, +, -, parentheses).')
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # The signal handles profile creation, but let's update phone_number
            if hasattr(user, 'profile'):
                user.profile.phone_number = self.cleaned_data.get('phone_number', '')
                user.profile.save()
        return user
