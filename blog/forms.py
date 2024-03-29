from django import forms

from blog.models import Comment


class EmailPostForm(forms.Form):
    """
    Форма рекомендация постов по электронной почте.
    """

    name = forms.CharField(max_length=25, label="Имя")
    email = forms.EmailField(label="Email от кого")
    to = forms.EmailField(label="Email кому")
    comments = forms.CharField(
        required=False, widget=forms.Textarea, label="Комментарий"
    )


class CommentForm(forms.ModelForm):
    """
    Форма комментариев.
    """

    class Meta:
        model = Comment
        fields = ["name", "email", "body"]


class SearchForm(forms.Form):
    """Форма поиска."""

    query = forms.CharField(label="Запрос")
