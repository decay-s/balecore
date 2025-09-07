class ReplyKeyboardButton:
    def __init__(self, text, request_contact=False, request_location=False, web_app=None):
        self.text = text
        self.request_contact = request_contact
        self.request_location = request_location
        self.web_app = web_app

    def to_dict(self):
        button_dict = {"text": self.text}
        if self.request_contact:
            button_dict["request_contact"] = True
        if self.request_location:
            button_dict["request_location"] = True
        if self.web_app:
            button_dict["web_app"] = self.web_app.to_dict()
        return button_dict