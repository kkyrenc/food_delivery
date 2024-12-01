from django import forms
from .models import Customers
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.contrib.auth.hashers import make_password, check_password


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Password",
        min_length=6,
        error_messages={"min_length": "Password must be at least 6 characters long."}
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password"
    )

    class Meta:
        model = Customers
        fields = ['username', 'email', 'password']

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if len(username) < 2 or len(username) > 20:
            raise ValidationError("Username must be between 2 and 20 characters.")


        if Customers.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken. Please choose another one.")

        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        print(f"DEBUG: verfing email: {email}")
        if not email or "@" not in email or "." not in email:
            raise ValidationError("Please enter a valid email address.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise ValidationError("Passwords do not match!")

        print(f"DEBUG: form errors: {self.errors}")
        return cleaned_data

    def save(self, commit=True):
        customer = super().save(commit=False)
        customer.password = self.cleaned_data["password"]
        if commit:
            customer.save()
        return customer


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        label="Username or Email",
        error_messages={'required': ''}
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Password",
        error_messages={'required': ''}
    )