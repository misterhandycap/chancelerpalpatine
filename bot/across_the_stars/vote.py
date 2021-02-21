class Vote():
    def __init__(self, vote):
        self.vote = vote

    def voto_comum(self, options: list):
        if len(options) < 3:
            return
        if len(options) > 11: 
            return
        