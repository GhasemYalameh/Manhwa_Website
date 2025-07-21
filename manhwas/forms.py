from django import forms
from django.core.exceptions import ValidationError

from re import search

from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        text = self.cleaned_data['text']
        is_html = search(r'<[^>]+>', text)
        if is_html:
            raise ValidationError('text cant be included html tags.')

        return text
