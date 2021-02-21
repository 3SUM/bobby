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
    conn = None
    cur = None

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
                        await message.channel.send(f"Gave +1 Karma to {i.mention}")
                break
        await bot.process_commands(message)

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user.name}")
        sql = """
            CREATE TABLE IF NOT EXISTS %s (name VARCHAR(255) NOT NULL, rep INTEGER NOT NULL, UNIQUE(name))
            """
        Bobby.cur.execute(sql, (bot.user.name,))

    @bot.command()
    async def rep(ctx, member: discord.Member = None):
        roles = ""
        member = member or ctx.author

        for role in member.roles[:-1]:
            if role.name != "@everyone":
                roles += role.name + ", "
        roles += member.roles[-1].name

        profile_embed = discord.Embed(
            title=f"Profile of {member.name}",
            description="Karma Profile",
            color=0x50E3C2,
        )
        profile_embed.set_thumbnail(url=member.avatar_url)
        profile_embed.add_field(name="Karma", value=0, inline=False)
        profile_embed.add_field(name="Message Count", value=0, inline=True)
        profile_embed.add_field(name="Roles", value=roles, inline=True)
        await ctx.send(embed=profile_embed)

    @bot.command()
    async def message_count(ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        count = 0
        async for _ in channel.history(limit=None):
            count += 1
        await ctx.send(f"There were {count} message(s) in {channel.mention}")

    def main():
        Bobby.conn = psycopg2.connect(
            database=DATABASE,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
        )
        Bobby.conn.autocommit = True
        Bobby.cur = Bobby.conn.cursor()
        bot.run(TOKEN)


if __name__ == "__main__":
    Bobby.main()