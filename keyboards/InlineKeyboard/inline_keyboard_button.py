class InlineKeyboardButton:
    def __init__(self, text, callback_data=None, url=None, web_app=None, copy_text=None):
        self.text = text
        self.callback_data = callback_data
        self.url = url
        self.web_app = web_app
        self.copy_text = copy_text

    def to_dict(self):
        button_dict = {"text": self.text}
        
        if self.callback_data:
            button_dict["callback_data"] = self.callback_data
        if self.url:
            button_dict["url"] = self.url
        if self.web_app:
            button_dict["web_app"] = self.web_app.to_dict()
        if self.copy_text is not None:
            button_dict["copy_text"] = self.copy_text.to_dict()
            
        return button_dict