from .reply_keyboard_button import ReplyKeyboardButton

class ReplyKeyboardMarkup:
    def __init__(self, keyboard=None, selective=None):
        self.keyboard = keyboard if keyboard else []
        self.selective = selective

    def add_row(self, *buttons):
        processed_buttons = []
        for button in buttons:
            if isinstance(button, ReplyKeyboardButton):
                processed_buttons.append(button)
            elif isinstance(button, (tuple, list)):
                if len(button) == 2 and isinstance(button[0], str):
                    processed_buttons.append(ReplyKeyboardButton(
                        text=button[0],
                        request_contact=button[1] if len(button) > 1 else False
                    ))
                else:
                    try:
                        button_kwargs = dict(button)
                        processed_buttons.append(ReplyKeyboardButton(**button_kwargs))
                    except (TypeError, ValueError):
                        raise ValueError("Invalid button format")
            elif isinstance(button, dict):
                processed_buttons.append(ReplyKeyboardButton(**button))
            else:
                raise ValueError("Button must be ReplyKeyboardButton, tuple, or dict")
        
        self.keyboard.append(processed_buttons)
        return self

    def add_button(self, button):
        if not self.keyboard:
            self.keyboard.append([])
            
        if isinstance(button, ReplyKeyboardButton):
            self.keyboard[-1].append(button)
        elif isinstance(button, (tuple, list)):
            if len(button) == 2 and isinstance(button[0], str):
                self.keyboard[-1].append(ReplyKeyboardButton(
                    text=button[0],
                    request_contact=button[1] if len(button) > 1 else False
                ))
            else:
                try:
                    button_kwargs = dict(button)
                    self.keyboard[-1].append(ReplyKeyboardButton(**button_kwargs))
                except (TypeError, ValueError):
                    raise ValueError("Invalid button format")
        elif isinstance(button, dict):
            self.keyboard[-1].append(ReplyKeyboardButton(**button))
        else:
            raise ValueError("Button must be ReplyKeyboardButton, tuple, or dict")
        
        return self

    def to_dict(self):
        result = {
            "keyboard": [
                [button.to_dict() for button in row] 
                for row in self.keyboard
            ]
        }
        if self.selective is not None:
            result["selective"] = self.selective
        return result