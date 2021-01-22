class Player():
    def __init__(self, user):
        self.id = user.id
        self.name = user.name

    def __eq__(self, value):
        try:
            return self.id == value.id
        except:
            return False
