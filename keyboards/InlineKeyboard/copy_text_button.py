class CopyTextButton:
    def __init__(self, copy_text):
        self.copy_text = copy_text

    def to_dict(self):
        return {"copy_text": self.copy_text}