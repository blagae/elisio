""" module for creating an xml file from given input """
import re
import xml.dom.minidom as mini
import xml.etree.ElementTree as Et
from os import listdir, getcwd
from os.path import isfile, join

from Elisio.dbhandler import create_verses, find_author, find_opus, find_book, find_poem
from Elisio.engine.verse.VerseType import VerseForm
from Elisio.models.metadata import Poem
from Elisio.numerals import int_to_roman


form_extensions = {
    'hen': VerseForm.HENDECASYLLABUS,
    'dis': VerseForm.ELEGIAC_DISTICHON,
    'hex': VerseForm.HEXAMETRIC  # default
}

extension_forms = {v: k for k, v in form_extensions.items()}


def create_output_file(tree):
    """ create the file from the given xml tree """
    if isinstance(tree, Et.Element):
        xml = mini.parseString(Et.tostring(tree)).toprettyxml()
        with open('Elisio/fixtures/verses/initial_data.xml', "w", encoding='utf-8') as file:
            file.writelines(xml)
    else:
        raise IOError("Invalid XML Tree object")


def clean_name(file):
    # Verg. Aen. I
    split = file.split('/')
    split = re.split('[^a-zA-Z0-9]+', split[-1])
    if 'txt' in split:
        split = split[:-1]
    return split


def get_extension(file):
    split = file.split('.')
    return form_extensions[split[-1]]


def find_poem_for_file(file):
    split = clean_name(file)
    frm = get_extension(file)
    author = find_author(split[0])
    opus = find_opus(author, split[1])
    book = find_book(opus, split[2])
    if len(split) > 3:
        poem = find_poem(book, split[3], True)
    else:
        poem = find_poem(book, True)
    if poem and not poem.pk:
        poem.verseForm = frm
        poem.save()
    return poem


def name_poem(poem):
    book = poem.book
    opus = book.opus
    author = opus.author
    res = "{0}. {1}. {2}".format(author.abbreviation, opus.abbreviation, int_to_roman(book.number))
    poems = book.poem_set.count()
    if poems > 1:
        res += " " + str(poem.number)
    return res


def fill_xml_object():
    """ externally facing method """
    root = Et.Element("django-objects", {'version': '1.0'})
    path = 'Elisio/fixtures/sources/'
    # https://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python
    all_filenames = [f for f in listdir(path) if isfile(join(path, f))]
    # FYI if you get encoding exceptions with new files, manually set them to UTF-8
    for filename in all_filenames:
        with open(join(path, filename), "r", encoding='utf-8') as file:
            verses = [line.replace('\n', '').strip() for line in file.readlines()]
        poem = find_poem_for_file(file.name)
        count = 1
        for verse in verses:
            obj = Et.SubElement(root, "object",
                                {'model': 'Elisio.DatabaseVerse'})
            poem_field = Et.SubElement(obj, "field",
                                       {'type': 'ForeignKey',
                                        'name': 'poem'})
            poem_field.text = str(poem.id)
            number_field = Et.SubElement(obj, "field",
                                         {'type': 'IntegerField',
                                          'name': 'number'})
            parsed = verse.split('$')
            if len(parsed) > 1:
                try:
                    count = int(parsed[0])
                except TypeError:
                    count = int(parsed[0][:-1])
                    alt_field = Et.SubElement(obj, "field",
                                              {'type': 'CharField',
                                               'name': 'alternative'})
                    alt_field.text = parsed[0][-1]
            number_field.text = str(count)
            count += 1
            verse_type_field = Et.SubElement(obj, "field",
                                             {'type': 'enum.EnumField',
                                              'name': 'verseType'})
            vf = poem.verseForm.get_verse_types()
            current_form = vf[count % len(vf)]
            verse_type_field.text = str(current_form.value)
            verse_field = Et.SubElement(obj, "field",
                                        {'type': 'CharField',
                                         'name': 'contents',
                                         })
            verse_field.text = parsed[-1]
    create_output_file(root)


def sync_files():
    path = join(getcwd(), 'Elisio', 'fixtures', 'sources')
    for poem in Poem.objects.all():
        name = join(path, name_poem(poem) + "." + extension_forms[poem.verseForm])
        if isfile(name):
            continue
        f = open(name, 'w', encoding='utf-8')
        previous_verse = 0
        # force order in which they were inserted
        for verse in poem.databaseverse_set.order_by('id').all():
            item = verse.contents
            if verse.number != previous_verse + 1 or verse.alternative:
                prefix = str(verse.number) + verse.alternative + '$'
                item = prefix + item
            f.write(item + "\n")
            previous_verse = verse.number
        f.close()


def sync_db():
    path = join(getcwd(), 'Elisio', 'fixtures', 'sources')
    all_filenames = [f for f in listdir(path) if isfile(join(path, f))]
    for filename in all_filenames:
        verses = [line for line in open(join(path, filename), encoding='utf-8') if line.rstrip()]
        poem = find_poem_for_file(filename)
        create_verses(poem, verses)
