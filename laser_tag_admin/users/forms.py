from django import forms
from .models import User

class UserForm(forms.ModelForm):
    subscription_end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Дата окончания подписки"
    )

    is_admin = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Администратор"
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'subscription_end_date', 'is_admin']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
