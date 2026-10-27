import re

from django import forms
from django.contrib.auth.models import User
from datetime import date
from django.core.exceptions import ValidationError

from .models import Review


# ========================== ФОРМА ОТЗЫВОВ =============================
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 1,
                    'max': 5
                }
            ),
            'text': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4
                }
            ),
        }

    def clean_text(self):
        text = self.cleaned_data.get("text")
        if text and len(text) < 5:
            raise forms.ValidationError("Отзыв слишком короткий!")
        return text


# ======================== ФОРМА РЕГИСТРАЦИИ ===========================
class ExtendedRegistrationForm(forms.ModelForm):
    phone_number = forms.CharField(
        label="Номер телефона",
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '+375 (29) XXX-XX-XX'
            }
        )
    )

    birth_date = forms.DateField(
        label="Дата рождения",
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date'
            }
        )
    )

    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    class Meta:
        model = User
        fields = ['username', 'phone_number', 'birth_date', 'password']
        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        phone_regex = r'^\+375\(\d{2}\)\d{3}\d{2}\d{2}$'

        if not phone or not re.match(phone_regex, phone):
            raise ValidationError(
                "Номер телефона должен быть строго в формате +375(29)XXXXXXX"
            )

        return phone

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')

        if birth_date:
            today = date.today()
            age = (
                today.year
                - birth_date.year
                - ((today.month, today.day) < (birth_date.month, birth_date.day))
            )

            if age < 18:
                raise forms.ValidationError(
                    "Регистрация разрешена только лицам старше 18 лет."
                )

        return birth_date

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

        return user


# =========================== ФОРМА ЗАКАЗА =============================
class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        label="Имя получателя",
        max_length=100
    )

    phone = forms.CharField(
        label="Телефон",
        max_length=30
    )

    email = forms.EmailField(
        label="Email"
    )

    fulfillment_method = forms.ChoiceField(
        label="Способ получения",
        choices=[
            ('delivery', 'Доставка'),
            ('pickup', 'Самовывоз из PizzaTime')
        ]
    )

    address = forms.CharField(
        label="Адрес доставки",
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': 3
            }
        )
    )

    payment_method = forms.ChoiceField(
        label="Способ оплаты",
        choices=[
            ('card', 'Банковская карта'),
            ('cash', 'Наличными курьеру')
        ]
    )

    promo_code = forms.CharField(
        label="Промокод",
        required=False,
        max_length=50
    )

    comment = forms.CharField(
        label="Комментарий к заказу",
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': 2
            }
        )
    )

    agree = forms.BooleanField(
        label="Согласен с условиями заказа",
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()

        if (
            cleaned_data.get('fulfillment_method') == 'delivery'
            and not cleaned_data.get('address')
        ):
            self.add_error(
                'address',
                'Укажите адрес для доставки.'
            )

        return cleaned_data