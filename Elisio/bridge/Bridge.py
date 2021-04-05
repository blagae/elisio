from elisio.Syllable import Weight


def assign_weights_from_dict(word, structs):
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


class Bridge(object):
    def split_from_deviant_word(self, word):
        raise Exception("must be overridden")

    def use_dictionary(self, word):
        raise Exception("must be overridden")

    def save(self, verse, db_id):
        raise Exception("must be overridden")


class DummyBridge(Bridge):
    def split_from_deviant_word(self, word):
        pass

    def use_dictionary(self, word):
        pass

    def save(self, verse, db_id):
        pass


class LocalDictionaryBridge(DummyBridge):
    """ Mock Bridge to mock database access """

    def __init__(self, cache=None):
        if not cache:
            cache = dict()
        self.cache = cache

    def use_dictionary(self, word):
        val = self.cache[word.text]
        assign_weights_from_dict(word, val)
