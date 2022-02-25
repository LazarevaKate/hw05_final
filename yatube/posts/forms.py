from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': _('Текст поста'),
            'group': _('Группа, к которой относится пост'),
            'image': _('Тут может быть картиночка')
        }
        help_texts = {
            'text': _('Введите текст'),
            'image': _('Вставьте картинку')
        },
        error_messages = {
            'text': {
                'empty_labels': _('Не забудь заполнить поле'),
            },
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': _('Текст')
        }
        help_texts = {
            'text': _('Текст нового комментария'),
        }

    def clean_text(self):
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError
        return data
