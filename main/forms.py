from django import forms
from .models import Review
from datetime import date

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

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if age < 18:
            raise forms.ValidationError("Вам должно быть не менее 18 лет.")
        return birth_date

    def clean_text(self):
        text = self.cleaned_data.get("text")
        if text and len(text) < 5:
            raise forms.ValidationError("Отзыв слишком короткий!")
        return text