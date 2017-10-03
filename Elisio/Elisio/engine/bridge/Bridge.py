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
