from enum import Enum

class ParseMode(str, Enum):
    MARKDOWN = "Markdown"
    MARKDOWN_V2 = "MarkdownV2"
    HTML = "HTML"
    NONE = None

    def __str__(self):
        return self.value if self.value else ""