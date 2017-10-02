from Elisio.engine.Syllable import Weight
from Elisio.engine.Word import Word
from Elisio.models.deviant import DeviantWord
from Elisio.models.scan import WordOccurrence


def split_from_deviant_word(word):
    """
    if the word can be found in the repository of Deviant Words,
    we should use that instead
    """
    deviant = DeviantWord.find(word.without_enclitic())
    if deviant:
        word.syllables = deviant.get_syllables()
        for syll in word.syllables:
            if len(syll.text) >= 1:
                word.text = word.text[len(syll.text):]
        if len(word.text) > 0:
            wrd = Word(word.text)
            wrd.split()
            for syllab in wrd.syllables:
                word.syllables.append(syllab)
        word.recalculate_text()
    return deviant


def use_dictionary(word):
    structs = []
    for hit in WordOccurrence.objects.filter(word=word.text):
        strc = hit.struct
        if len(strc) == 1 and strc[-1] == "0":
            continue
        if len(strc) > 1 and (strc[-1] == "3" or strc[-1] == "0"):
            strc = strc[:-1]
        if strc not in structs:
            structs.append(strc)
    if len(structs) == 1:
        for count, wght in enumerate(structs[0]):
            word.syllables[count].weight = Weight(int(wght))
    if len(structs) > 1:
        structs.sort(key=len, reverse=True)
        for count in range(len(structs[0])):
            val = None
            for strc in structs:
                try:
                    if not val and (strc[count] != "3" and strc[count] != "0"):
                        val = strc[count]
                    elif val != strc[count]:
                        if strc[count] != "3" and strc[count] != "0":
                            val = "3"
                            break
                except IndexError:
                    pass
            if val:
                word.syllables[count].weight = Weight(int(val))
