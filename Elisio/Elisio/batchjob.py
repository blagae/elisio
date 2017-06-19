""" module for creating an xml file from given input """
import xml.etree.ElementTree as ET
import xml.dom.minidom as mini
from Elisio.numerals import roman_to_int, int_to_roman
from Elisio.models import DatabaseVerse, Author, Book, Opus, Poem
from os import listdir, getcwd
from os.path import isfile, join


def create_output_file(tree):
    """ create the file from the given xml tree """
    if isinstance(tree, ET.Element):
        xml = mini.parseString(ET.tostring(tree)).toprettyxml()
        with open('Elisio/fixtures/verses/initial_data.xml', "w") as file:
            file.writelines(xml)
    else:
        raise IOError("Invalid XML Tree object")

def find_poem(file):
    # Verg. Aen. I
    split = file.split('/')
    split = split[-1].split()
    split[-1] = split[-1].replace('.txt', '')
    author = Author.objects.get(abbreviation=split[0])
    opus = Opus.objects.get(abbreviation=split[1], author=author)
    book = Book.objects.get(opus=opus, number=roman_to_int(split[2]))
    poem = Poem.objects.filter(book=book)
    if len(poem) == 1:
        return poem[0]
    return poem.get(number=split[3])

def name_poem(poem):
    book = poem.book
    opus = book.opus
    author = opus.author
    res = "{0} {1} {2}".format(author.abbreviation, opus.abbreviation, int_to_roman(book.number))
    poems = book.poem_set.count()
    if poems > 1:
        res += " " + str(poem.number)
    return res

def fill_xml_object():
    """ externally facing method """
    root = ET.Element("django-objects", {'version': '1.0'})
    path = 'Elisio/fixtures/sources/'
    # https://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python
    all_filenames = [f for f in listdir(path) if isfile(join(path, f))]
    # FYI if you get encoding exceptions with new files, manually set them to UTF-8
    for filename in all_filenames:
        with open(join(path, filename), "r") as file:
            verses = [line.replace('\n', '').strip() for line in file.readlines()]
        poem = find_poem(file.name)
        count = 1
        for verse in verses:
            obj = ET.SubElement(root, "object",
                                {'model': 'Elisio.DatabaseVerse'})
            poem_field = ET.SubElement(obj, "field",
                                       {'type': 'ForeignKey',
                                        'name': 'poem'})
            poem_field.text = str(poem.id)
            number_field = ET.SubElement(obj, "field",
                                         {'type': 'IntegerField',
                                          'name': 'number'})
            parsed = verse.split('$')
            if (len(parsed) > 1):
                try:
                    count = int(parsed[0])
                except:
                    count = int(parsed[0][:-1])
                    alt_field = ET.SubElement(obj, "field",
                                         {'type': 'CharField',
                                          'name': 'alternative'})
                    alt_field.text = parsed[0][-1]
            number_field.text = str(count)
            count += 1
            verseType_field = ET.SubElement(obj, "field",
                                       {'type': 'enum.EnumField',
                                        'name': 'verseType'})
            vf = poem.verseForm.get_verse_types()
            current_form = vf[count % len(vf)]
            verseType_field.text = str(current_form.value)
            verse_field = ET.SubElement(obj, "field",
                                        {'type': 'CharField',
                                         'name': 'contents',
                                        })
            verse_field.text = parsed[-1]
    create_output_file(root)

def syncFiles():
    path = join(getcwd(), 'Elisio', 'fixtures', 'sources')
    for poem in Poem.objects.all():
        name = join(path, name_poem(poem) + ".txt")
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
            f.write(item)
            previous_verse = verse.number
        f.close()

def syncDb():
    path = join(getcwd(), 'Elisio', 'fixtures', 'sources')
    all_filenames = [f for f in listdir(path) if isfile(join(path, f))]
    for filename in all_filenames:
        verses = [line for line in open(join(path, filename)) if line.rstrip()]
        poem = find_poem(filename)
        db_lines = DatabaseVerse.objects.filter(poem=poem)
        if len(verses) == db_lines.count():
            continue
        db_lines.delete()
        count = 1
        entries = []
        for verse in verses:
            item = DatabaseVerse()
            item.poem = poem
            parsed = verse.split('$')
            if (len(parsed) > 1):
                try:
                    count = int(parsed[0])
                except:
                    count = int(parsed[0][:-1])
                    item.alternative = parsed[0][-1]
            item.number = count
            count += 1
            item.contents = parsed[-1]
            vf = poem.verseForm.get_verse_types()
            item.verseType = vf[count % len(vf)]
            entries.append(item)
        DatabaseVerse.objects.bulk_create(entries)

def find_all_verses_containing(regex, must_be_parsed=False):
    from Elisio.utils import set_django
    from Elisio.engine.VerseFactory import VerseFactory
    from Elisio.exceptions import ScansionException
    import re
    set_django()
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

def scan_verses(dbverses, initiator, commit=""):
    from Elisio.engine.VerseFactory import VerseFactory
    from Elisio.exceptions import HexameterException, VerseException, ScansionException
    from Elisio.models import ScanVerseResult, ScanSession, Batch, DatabaseBatchItem
    worked = 0
    worked_without_dict = 0
    failed = 0
    batch = Batch()
    batch.save()
    batchItem = DatabaseBatchItem()
    batchItem.batch = batch
    batchItem.object_type = 'author'
    batchItem.object_id = '0'
    batchItem.relation = 'dominant'
    batchItem.save()
    session = ScanSession()
    session.batch = batch
    session.initiator = initiator
    session.save()
    for dbverse in dbverses:
        verse_saved = dbverse.saved
        scanResult = ScanVerseResult()
        scanResult.session = session
        scanResult.verse = dbverse
        scanResult.scanned_as = dbverse.verseType
        scanResult.batchItem = batchItem
        try:
            verse = VerseFactory.create(dbverse, False, classes=dbverse.verseType)
            dbverse.saved = True
            scanResult.structure = verse.structure
            worked_without_dict += 1
        except VerseException:
            try:
                verse = VerseFactory.create(dbverse, True, classes=dbverse.verseType)
                dbverse.saved = True
                scanResult.structure = verse.structure
            except VerseException as exc:
                failed += 1
                verse = VerseFactory.get_split_syllables(dbverse.contents)
                dbverse.saved = False
                try:
                    scanResult.failure = exc.exceptions[0][0].message[:69]
                except IndexError:
                    scanResult.failure = exc.message[:69]
                scanResult.structure = ""
            else:
                worked += 1
        except ScansionException as exc:
            scanResult.failure = exc.message[:69]
            dbverse.saved = False
            scanResult.structure = ""
        else:
            worked += 1
        if verse_saved != dbverse.saved or scanResult.failure:
            dbverse.save()
        scanResult.save()
    return worked, failed, worked_without_dict