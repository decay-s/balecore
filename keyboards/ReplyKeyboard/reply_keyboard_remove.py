class ReplyKeyboardRemove:
    def __init__(self, selective=False):
        self.remove_keyboard = True
        self.selective = selective

    def to_dict(self):
        return {
            "remove_keyboard": self.remove_keyboard,
            "selective": self.selective
        }