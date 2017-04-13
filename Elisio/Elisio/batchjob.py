""" module for creating an xml file from given input """
import xml.etree.ElementTree as ET
import xml.dom.minidom as mini
from Elisio.numerals import roman_to_int

def create_output_file(tree):
    """ create the file from the given xml tree """
    if isinstance(tree, ET.Element):
        xml = mini.parseString(ET.tostring(tree)).toprettyxml()
        with open('Elisio/fixtures/verses/initial_data.xml', "w") as file:
            file.writelines(xml)
    else:
        raise IOError("Invalid XML Tree object")

def find_poem(file):
    from Elisio.models import Author, Book, Opus, Poem
    # Verg. Aen. I
    split = file.split('/')
    split = split[-1].split()
    split[-1] = split[-1].replace('.txt', '')
    author = Author.objects.get(abbreviation=split[0])
    opus = Opus.objects.get(abbreviation=split[1], author=author)
    book = Book.objects.get(opus=opus, number=roman_to_int(split[2]))
    poem = Poem.objects.filter(book=book)
    if len(poem) == 1:
        return poem[0].id
    return poem.get(number=split[3]).id

def fill_xml_object():
    """ externally facing method """
    root = ET.Element("django-objects", {'version': '1.0'})
    path = 'Elisio/fixtures/sources/'
    # https://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python
    from os import listdir
    from os.path import isfile, join
    all_filenames = [f for f in listdir(path) if isfile(join(path, f))]

    for filename in all_filenames:
        with open(join(path, filename), "r") as file:
            verses = [line.replace('\n', '') for line in file.readlines()]
        poem_number = find_poem(file.name)
        count = 1
        for verse in verses:
            obj = ET.SubElement(root, "object",
                                {#'pk': str(count),
                                    'model': 'Elisio.DatabaseVerse'})
            poem_field = ET.SubElement(obj, "field",
                                       {'type': 'ForeignKey',
                                        'name': 'poem'})
            poem_field.text = str(poem_number)
            number_field = ET.SubElement(obj, "field",
                                         {'type': 'IntegerField',
                                          'name': 'number'})
            number_field.text = str(count)
            verse_field = ET.SubElement(obj, "field",
                                        {'type': 'CharField',
                                         'name': 'contents',
                                         'saved': 'False'
                                        })
            verse_field.text = verse

            count += 1

    #tree = ET.ElementTree(root)

    create_output_file(root)

def find_all_verses_containing(regex, must_be_parsed=False):
    from Elisio.utils import set_django
    from Elisio.engine.VerseFactory import VerseFactory
    from Elisio.models import DatabaseVerse
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
    from Elisio.engine.Hexameter import HexameterCreator
    from Elisio.models import ScanVerseResult, ScanSession
    worked = 0
    worked_without_dict = 0
    failed = 0
    session = ScanSession()
    session.initiator = initiator
    session.save()
    for dbverse in dbverses:
        verse_saved = dbverse.saved
        scanResult = ScanVerseResult()
        scanResult.session = session
        scanResult.verse = dbverse
        try:
            verse = VerseFactory.create(dbverse.contents, not dbverse.saved, False, dbverse, classes=HexameterCreator)
            dbverse.saved = True
            scanResult.structure = verse.structure
            worked_without_dict += 1
        except VerseException:
            try:
                verse = VerseFactory.create(dbverse.contents, not dbverse.saved, True, dbverse, classes=HexameterCreator)
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