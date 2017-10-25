""" module for creating an xml file from given input """
import re
import xml.dom.minidom as mini
import xml.etree.ElementTree as Et
from os import listdir, getcwd
from os.path import isfile, join

from Elisio.engine.Verse import Foot
from Elisio.engine.VerseFactory import VerseFactory
from Elisio.engine.bridge.DatabaseBridge import DatabaseBridge
from Elisio.engine.exceptions import VerseException, ScansionException
from Elisio.engine.verse.VerseType import VerseType, VerseForm
from Elisio.models.metadata import DatabaseVerse, Author, Book, Opus, Poem
from Elisio.models.scan import ScanVerseResult, ScanSession, Batch, DatabaseBatchItem, ObjectType
from Elisio.numerals import roman_to_int, int_to_roman


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
        with open('Elisio/fixtures/verses/initial_data.xml', "w") as file:
            file.writelines(xml)
    else:
        raise IOError("Invalid XML Tree object")


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
        with open(join(path, filename), "r") as file:
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
        f = open(name, 'w')
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
        verses = [line for line in open(join(path, filename)) if line.rstrip()]
        poem = find_poem_for_file(filename)
        create_verses(poem, verses)


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


def find_all_verses_containing(regex, must_be_parsed=False):
    import re
    dbverses = DatabaseVerse.objects.all()
    total = []
    for dbverse in dbverses:
        words = VerseFactory.split(dbverse.contents)
        boolean = False
        for word in words:
            boolean = boolean or re.compile(regex).match(word.text)
        if must_be_parsed:
            try:
                VerseFactory.create(dbverse.contents).parse()
            except ScansionException:
                continue
        if boolean:
            total.append(dbverse.contents)
    return total


def get_location_string(dbverse):
    result = ''
    if not isinstance(dbverse, DatabaseVerse):
        # dbverse is an id
        dbverse = DatabaseVerse.objects.get(dbverse)
    poem = dbverse.poem
    book = poem.book
    opus = book.opus
    author = opus.author

    result += str(dbverse.id) + "\t" + author.abbreviation + " " + opus.abbreviation + " " + str(int_to_roman(book.number)) + ", " + str(poem.number) + ", " + str(dbverse.number)
    if dbverse.alternative:
        result += " " + dbverse.alternative + "---"
    return result


def scan_verses(dbverses, initiator):
    worked = 0
    worked_without_dict = 0
    failed = 0
    batch = Batch()
    batch.save()
    batch_item = DatabaseBatchItem()
    batch_item.batch = batch
    batch_item.object_type = ObjectType.ALL
    batch_item.object_id = 0
    batch_item.save()
    session = ScanSession()
    session.batch = batch
    session.initiator = initiator
    session.save()
    for dbverse in dbverses:
        verse_saved = dbverse.saved
        scan_result = ScanVerseResult()
        scan_result.session = session
        scan_result.verse = dbverse
        scan_result.scanned_as = dbverse.verseType
        scan_result.batchItem = batch_item
        try:
            verse = VerseFactory.create(dbverse, DatabaseBridge(False), classes=dbverse.verseType)
            dbverse.saved = True
            scan_result.structure = verse.structure
            worked_without_dict += 1
        except VerseException:
            try:
                verse = VerseFactory.create(dbverse, DatabaseBridge(), classes=dbverse.verseType)
                dbverse.saved = True
                scan_result.structure = verse.structure
            except VerseException as exc:
                failed += 1
                VerseFactory.get_split_syllables(dbverse.contents)
                dbverse.saved = False
                try:
                    scan_result.failure = exc.exceptions[0][0].message[:69]
                except IndexError:
                    scan_result.failure = exc.message[:69]
                scan_result.structure = ""
            else:
                worked += 1
        except ScansionException as exc:
            scan_result.failure = exc.message[:69]
            dbverse.saved = False
            scan_result.structure = ""
        else:
            worked += 1
        if verse_saved != dbverse.saved or scan_result.failure:
            dbverse.save()
        scan_result.save()
        """
        if scan_result.structure:
            print(get_location_string(dbverse) + ": " + scan_result.structure)
        else:
            print(get_location_string(dbverse) + ": failed")
        """
    return worked, failed, worked_without_dict


def scan_batch_from_flat_file(file):
    with open(file, "r") as file:
        j = 0
        for dbverse in file.readlines():
            try:
                verse = VerseFactory.create(dbverse, DatabaseBridge(), classes=VerseType.HEXAMETER)
                d = "\t"
                for i in range(4):
                    if verse.feet[i] == Foot.DACTYLUS:
                        d += "D"
                    else:
                        d += "S"
                print(str(j) + d)
            except:
                print(str(j) + "\tfailed")
            j += 1
