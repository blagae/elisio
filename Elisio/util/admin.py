from django.contrib import admin
from elisio.models.metadata import Author, Genre, Opus, Book, Poem, Period

# currently no need for admin classes
admin.site.register(Period)
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Opus)
admin.site.register(Book)
admin.site.register(Poem)
