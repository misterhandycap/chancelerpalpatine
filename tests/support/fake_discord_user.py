class FakeDiscordUser():

    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

    def __eq__(self, value):
        try:
            return self.id == value.id
        except:
            return False
