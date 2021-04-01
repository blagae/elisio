""" module for creating an xml file from given input """
from elisio.models.metadata import DatabaseVerse, Author, Book, Opus, Poem
from elisio.numerals import roman_to_int, int_to_roman


def find_author(abbr):
    return Author.objects.get(abbreviation=abbr)


def find_opus(author, abbr):
    return Opus.objects.get(abbreviation=abbr, author=author)


def find_book(opus, number):
    try:
        return Book.objects.get(opus=opus, number=roman_to_int(number))
    except TypeError:
        return Book.objects.get(opus=opus, number=number)


def find_poem(book, number=None, create=False):
    poem = Poem.objects.filter(book=book)
    if len(poem) == 1:
        return poem[0]
    try:
        return poem.get(number=number)
    except Poem.DoesNotExist as e:
        if create:
            return Poem(book=book, number=number)
        raise e


def create_verses(poem, verses):
    db_lines = DatabaseVerse.objects.filter(poem=poem)
    if len(verses) <= db_lines.count():
        return
    db_lines.delete()
    count = 1
    entries = []
    for verse in verses:
        item = DatabaseVerse()
        item.poem = poem
        parsed = verse.split('$')
        if len(parsed) > 1:
            try:
                count = int(parsed[0])
            except (TypeError, ValueError):
                count = int(parsed[0][:-1])
                item.alternative = parsed[0][-1]
        item.number = count
        count += 1
        item.contents = parsed[-1].rstrip()
        vf = poem.verseForm.get_verse_types()
        item.verseType = vf[count % len(vf)]
        entries.append(item)
    DatabaseVerse.objects.bulk_create(entries)


def get_location_string(dbverse):
    if not isinstance(dbverse, DatabaseVerse):
        # dbverse is an id
        dbverse = DatabaseVerse.objects.get(dbverse)
    poem = dbverse.poem
    book = poem.book
    opus = book.opus
    author = opus.author

    result = "%s\t%s %s %s, %s, %s" % (dbverse.id, author.abbreviation, opus.abbreviation,
                                       int_to_roman(book.number), poem.number, dbverse.number)
    if dbverse.alternative:
        result += " " + dbverse.alternative + "---"
    return result
