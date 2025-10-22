from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import Profile


username_validator = RegexValidator(
    regex=r'^[a-z0-9._]{5,16}$',
    message='5–16 characters. lowercase letters, digits, dot and underscore allowed.'
)

class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=16,
        min_length=5,
        validators=[username_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'id': 'id_username',
            'placeholder': 'username',
            'autocomplete': 'username'
        })
    )
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control form-control-lg',
        'id': 'id_email',
        'placeholder': 'you@example.com',
        'autocomplete': 'email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-lg',
        'id': 'id_password',
        'placeholder': 'Create a password',
        'autocomplete': 'new-password'
    }), min_length=8)
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-lg',
        'id': 'id_password_confirm',
        'placeholder': 'Confirm password',
        'autocomplete': 'new-password'
    }), min_length=8)

    def clean_username(self):
        uname = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError("This username is already taken.")
        return uname

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get('password')
        pwc = cleaned.get('password_confirm')
        if pw and pwc and pw != pwc:
            self.add_error('password_confirm', 'Passwords do not match.')
        return cleaned

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'bio', 'picture']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Display name'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Short bio',
                'rows': 3
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name') or ''
        return name.strip()
