from django.forms import ModelForm

from Elisio.models.metadata import Author, Opus, Book


class AuthorForm(ModelForm):
    class Meta:
        model = Author
        exclude = ()


class OpusForm(ModelForm):
    class Meta:
        model = Opus
        exclude = ()
