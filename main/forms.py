import re
from django import forms
from django.contrib.auth.models import User
from .models import Review
from datetime import date
from django.core.exceptions import ValidationError

# =======================================================
# 1. ФОРМА ОТЗЫВОВ (БЕЗ ОГРАНИЧЕНИЯ 18+)
# =======================================================
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['user_name', 'birth_date', 'rating', 'text']
        widgets = {
            'user_name': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean_text(self):
        text = self.cleaned_data.get("text")
        if text and len(text) < 5:
            raise forms.ValidationError("Отзыв слишком короткий!")
        return text


# =======================================================
# 2. ФОРМА РЕГИСТРАЦИИ ПОЛЬЗОВАТЕЛЯ (СТРОГО 18+ И ТЕЛЕФОН ПО РЕГУЛЯРКЕ)
# =======================================================
class ExtendedRegistrationForm(forms.ModelForm):
    # Новое кастомное поле вместо почты
    phone_number = forms.CharField(
        label="Номер телефона",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '+375 (29) XXX-XX-XX'
        })
    )
    birth_date = forms.DateField(
        label="Дата рождения", 
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    password = forms.CharField(
        label="Пароль", 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        # Убрали 'email', добавили 'phone_number'
        fields = ['username', 'phone_number', 'birth_date', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    # ВАЛИДАЦИЯ НОМЕРА ТЕЛЕФОНА ЧЕРЕЗ РЕГУЛЯРНОЕ ВЫРАЖЕНИЕ
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        
        # Регулярка проверяет строго формат: +375 (XX) XXX-XX-XX
        phone_regex = r'^\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}$'
        
        if not phone or not re.match(phone_regex, phone):
            raise ValidationError("Номер телефона должен быть строго в формате +375 (29) XXX-XX-XX")
            
        return phone

    # ТВОЯ ВАЛИДАЦИЯ НА 18 ЛЕТ (ОСТАЛАСЬ БЕЗ ИЗМЕНЕНИЙ)
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 18:
                raise forms.ValidationError("Регистрация разрешена только лицам старше 18 лет.")
        return birth_date

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            # Дополнительно: если у тебя в базе есть отдельный профиль пользователя, 
            # где хранится телефон, его можно сохранить здесь. Например:
            # Profile.objects.create(user=user, phone=self.cleaned_data['phone_number'], birth_date=self.cleaned_data['birth_date'])
        return user