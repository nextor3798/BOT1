import os
from keep_alive import keep_alive
from index import bot

if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv("DISCORD_TOKEN"))