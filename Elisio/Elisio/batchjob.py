""" module for creating an xml file from given input """
import xml.etree.ElementTree as ET
import xml.dom.minidom as mini

def create_file(tree):
    """ create the file from the given xml tree """
    if isinstance(tree, ET.Element):
        xml = mini.parseString(ET.tostring(tree)).toprettyxml()
        # TODO: use something less of a dirty hack to enforce UTF-8
        xml = xml.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="utf-8" ?>')

        with open('Elisio/fixtures/verses/initial_data.xml', "w") as file:
            file.writelines(xml)
    else:
        raise IOError("Invalid XML Tree object")

def read_object(name):
    """ read the entries from a file """
    with open('Elisio/fixtures/sources/'+name+'.txt', "r") as file:
        result = [x.replace('\n', '') for x in file.readlines()]
    return result

def fill_tree():
    """ externally facing method """
    verses = read_object("book1")
    #verses.extend(read_object("book2"))

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
                                     'name': 'contents',
                                     'saved': 'False'
                                     })
        verse_field.text = verse

        count += 1

    #tree = ET.ElementTree(root)

    create_file(root)

def find_all_verses_containing(regex, must_be_parsed = False):
    from Elisio.engine.Verse import set_django
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
    for v in total:
        print(v)
    print(len(total))