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
        for check in Bobby.thank_you_list:
            if content.find(check) > -1:
                for i in message.mentions:
                    if i != message.author and i != bot.user:
                        await message.channel.send(f"Gave +1 Rep to {i.mention}")
                break
        await bot.process_commands(message)

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user.name}")

    @bot.command()
    async def rep(ctx):
        member = ctx.author
        profile_embed = discord.Embed(
            title=f"Profile of {member.name}",
            description="Karma Profile and message count",
            color=0x50E3C2,
        )
        profile_embed.set_thumbnail(url=member.avatar_url)
        profile_embed.add_field(name="total", value=0, inline=False)
        await ctx.send(embed=profile_embed)

    @bot.command()
    async def message_count(ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        count = 0
        async for _ in channel.history(limit=None):
            count += 1
        await ctx.send(f"There were {count} message(s) in {channel.mention}")

    def main():
        bot.run(TOKEN)


if __name__ == "__main__":
    Bobby.main()