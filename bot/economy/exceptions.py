class EconomyException(Exception):
    def __init__(self, message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message


class ItemNotFound(EconomyException):
    def __init__(self, *args, **kwargs):
        super().__init__("Item not found", *args, **kwargs)


class NotEnoughCredits(EconomyException):
    def __init__(self, *args, **kwargs):
        super().__init__("Not enough credits", *args, **kwargs)


class AlreadyOwnsItem(EconomyException):
    def __init__(self, *args, **kwargs):
        super().__init__("You already own this item", *args, **kwargs)
