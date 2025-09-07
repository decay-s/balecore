```markdown
# balecore

A Python library for building bots on the **Bale** and **Telegram** messaging platforms.

## Installation

To install the library, clone the repository directly into your project:

```bash
mkdir balecore && git clone https://github.com/decay-s/balecore.git balecore
```

## Quick Start

Here's a simple example to get you started with a basic echo bot that responds to the `/start` command in private chats.

```python
from balecore import Bot
from balecore.updates import Message
from balecore.filters import Filters

# Initialize your bot with the token provided by BotFather (Telegram) or BotBot (Bale)
bot: Bot = Bot(token="YOUR_BOT_TOKEN_HERE")

# Create a Filters instance
filters: Filters = Filters(bot=bot)

# Register a handler for the /start command
@bot.Message(filters.command("start") & filters.text & filters.private)
async def start_command(bot: Bot, message: Message):
    """Echos the received message back to the user."""
    await message.reply_text(message.text)

# Start the bot
bot.start()
```

## Core Concepts

### The Bot Class
The `Bot` class is the main entry point for your application. It manages the connection to the messaging platform and dispatches updates to your handlers.

### Updates
Updates represent incoming data from the messaging platform, such as messages, callbacks, or edits. The `Message` class is used for handling text and media messages.

### Filters
Filters are used to narrow down which updates your handlers will process. You can combine them using logical operators (`&` for AND, `|` for OR, `~` for NOT).

**Commonly Used Filters:**
*   `filters.command`: Matches a bot command (e.g., `/start`, `/help`).
*   `filters.text`: Matches text messages.
*   `filters.private`: Matches messages from private chats.
*   `filters.group`: Matches messages from group chats.

## Key Features

*   **Cross-Platform:** Write code that works for both Telegram and Bale bots.
*   **Modern Async/Await:** Built on Python's `asyncio` for high performance.
*   **Intuitive API:** Easy-to-understand syntax for defining message handlers.
*   **Powerful Filtering:** Precisely target the messages your bot responds to.

## Basic Usage Pattern

1.  **Import:** Import the necessary classes (`Bot`, `Message`, `Filters`).
2.  **Initialize:** Create a `Bot` instance with your API token.
3.  **Define Handlers:** Use the `@bot.Message()` decorator to define functions that will handle incoming messages. Apply filters to specify the exact criteria a message must meet.
4.  **Start:** Call `bot.start` to begin polling for updates.

## Learn More

For more detailed documentation, advanced usage examples, and information about contributing, please visit the project's [GitHub repository](https://github.com/decay-s/balecore).
```
