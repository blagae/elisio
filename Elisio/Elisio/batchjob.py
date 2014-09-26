import xml.etree.ElementTree as ET

def createFile(tree):
    if isinstance(tree, ET.ElementTree):
        tree.write("Elisio/fixtures/omg.xml")
    else:
        raise IOError("Invalid XML Tree object")

def readObject():
    # TODO: read-out from flatfile
    result = ['omgomgomg', 'yeyeyey']
    return result

def fillTree():
    verses = readObject()

    root = ET.Element("django-objects", {'version': '1.0'})

    poemNum = 2
    count = 1
    for verse in verses:
        object = ET.SubElement(root, "object", {'pk': str(count), 'model': 'Elisio.Db_Verse'})
        poemField = ET.SubElement(object, "field", {'type': 'ForeignKey', 'name': 'poem'})
        poemField.text = str(poemNum)
        numberField = ET.SubElement(object, "field", {'type': 'IntegerField', 'name': 'number'})
        numberField.text = str(count)
        verseField = ET.SubElement(object, "field", {'type': 'CharField', 'name': 'contents'})
        verseField.text = verse

        count += 1

    tree = ET.ElementTree(root)

    createFile(tree)
