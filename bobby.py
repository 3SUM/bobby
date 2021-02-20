import os
import discord
from discord.ext import commands

TOKEN = os.environ.get("TOKEN")
DATABASE = os.environ.get("DATABASE")
USER = os.environ.get("USER")
PASSWORD = os.environ.get("PASSWORD")
HOST = os.environ.get("HOST")
PORT = os.environ.get("PORT")

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="b!", intents=intents)


class Bobby:
    thank_you_list = ["THANK YOU", "THANKS", "TY"]

    @bot.event
    async def on_guild_join(guild):
        print(f"{bot.user.name} joined {guild.name}")

    @bot.event
    async def on_member_join(member):
        print(f"{member.name} has joined!")

    @bot.event
    async def on_member_remove(member):
        print(f"{member.name} has left!")

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        content = message.content.upper()
        for check in thank_you_list:
            if content.find(check) > -1:
                for i in message.mentions:
                    if i != message.author and i != bot.user:
                        await message.channel.send(f"Gave +1 Rep to {i.mention}")
                break
        await bot.process_commands(message)

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user.name}")
              
    def main():
        bot.run(TOKEN)


if __name__ == "__main__":
    Bobby.main()