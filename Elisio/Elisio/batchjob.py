""" module for creating an xml file from given input """
import xml.etree.ElementTree as ET

def create_file(tree):
    """ create the file from the given xml tree """
    if isinstance(tree, ET.ElementTree):
        tree.write("Elisio/fixtures/omg.xml")
    else:
        raise IOError("Invalid XML Tree object")

def read_object():
    """ read the entries from a file """
    # TODO: read-out from flatfile
    result = ['omgomgomg', 'yeyeyey']
    return result

def fill_tree():
    """ externally facing method """
    verses = read_object()

    root = ET.Element("django-objects", {'version': '1.0'})

    poem_number = 2
    count = 1
    for verse in verses:
        obj = ET.SubElement(root, "object",
                            {'pk': str(count),
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
                                     'name': 'contents'})
        verse_field.text = verse

        count += 1

    tree = ET.ElementTree(root)

    create_file(tree)

def find_all_verses_containing(regex, must_be_parsed = False):
    from Elisio.engine.Verse import set_django, Hexameter
    from Elisio.models import DatabaseVerse
    from Elisio.exceptions import ScansionException
    import re
    set_django()
    dbverses = DatabaseVerse.objects.all()
    total = []
    for dbverse in dbverses:
        verse = Hexameter(dbverse.contents)
        verse.split()
        boo = False
        for word in verse.words:
            boo = boo or re.compile(regex).match(word.text)
        if must_be_parsed:
            try:
                verse.scan()
            except ScansionException:
                continue
        if boo:
            total.append(verse)
    for v in total:
        print(v.text)