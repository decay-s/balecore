from .inline_keyboard_button import InlineKeyboardButton

class InlineKeyboardMarkup:
    def __init__(self, keyboard=None):
        self.keyboard = keyboard if keyboard else []

    def add_row(self, *buttons):
        processed_buttons = []
        for button in buttons:
            if isinstance(button, InlineKeyboardButton):
                processed_buttons.append(button)
            elif isinstance(button, (tuple, list)):
                if all(isinstance(item, str) for item in button) and len(button) == 2:
                    processed_buttons.append(InlineKeyboardButton(text=button[0], callback_data=button[1]))
                elif hasattr(button, '_fields'):
                    button_kwargs = dict(button._asdict())
                    processed_buttons.append(InlineKeyboardButton(**button_kwargs))
                else:
                    try:
                        button_kwargs = dict(button)
                        processed_buttons.append(InlineKeyboardButton(**button_kwargs))
                    except (TypeError, ValueError):
                        raise ValueError("Invalid button format. Use either InlineKeyboardButton, (text, callback_data), or (text='...', callback_data='...')")
            elif isinstance(button, dict):
                processed_buttons.append(InlineKeyboardButton(**button))
            else:
                raise ValueError("Button must be either InlineKeyboardButton, tuple, or dict")
        
        self.keyboard.append(processed_buttons)
        return self

    def add_button(self, button):
        if not self.keyboard:
            self.keyboard.append([])
            
        if isinstance(button, InlineKeyboardButton):
            self.keyboard[-1].append(button)
        elif isinstance(button, (tuple, list)):
            if all(isinstance(item, str) for item in button) and len(button) == 2:
                self.keyboard[-1].append(InlineKeyboardButton(text=button[0], callback_data=button[1]))
            elif hasattr(button, '_fields'):
                button_kwargs = dict(button._asdict())
                self.keyboard[-1].append(InlineKeyboardButton(**button_kwargs))
            else:
                try:
                    button_kwargs = dict(button)
                    self.keyboard[-1].append(InlineKeyboardButton(**button_kwargs))
                except (TypeError, ValueError):
                    raise ValueError("Invalid button format")
        elif isinstance(button, dict):
            self.keyboard[-1].append(InlineKeyboardButton(**button))
        else:
            raise ValueError("Button must be either InlineKeyboardButton, tuple, or dict")
        
        return self

    def to_dict(self):
        return {
            "inline_keyboard": [
                [button.to_dict() for button in row] 
                for row in self.keyboard
            ]
        }