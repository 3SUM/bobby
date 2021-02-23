import os
import datetime
import psycopg2
import discord
from discord.ext import commands
from psycopg2 import sql

TOKEN = os.environ["TOKEN"]
DATABASE_URL = os.environ["DATABASE_URL"]

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="?", intents=intents)


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

    @bot.command()
    async def message_count(ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        count = 0
        async for _ in channel.history(limit=None):
            count += 1
        await ctx.send(f"There were {count} message(s) in {channel.mention}")

    @bot.command()
    async def rep(ctx, member: discord.Member = None):
        roles = ""
        member = member or ctx.author
        join_date = member.joined_at
        join_date = join_date.strftime("%m/%d/%Y, %H:%M:%S")
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
        profile_embed.add_field(name="Date Joined", value=join_date, inline=True)
        profile_embed.add_field(name="Roles", value=roles, inline=True)
        await ctx.send(embed=profile_embed)

    @bot.command()
    async def setup(ctx):
        member = ctx.author
        for role in member.roles:
            if role.name == "MONKIES":
                try:
                    Bobby.cur.execute(
                        sql.SQL(
                            "CREATE TABLE IF NOT EXISTS {} (name VARCHAR(255) NOT NULL, rep INTEGER NOT NULL, UNIQUE(name))"
                        ).format(sql.Identifier(member.guild.name))
                    )
                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)
                finally:
                    await ctx.send("Database successfully setup!")
                break

    def main():
        Bobby.conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        Bobby.conn.autocommit = True
        Bobby.cur = Bobby.conn.cursor()
        bot.run(TOKEN)


if __name__ == "__main__":
    Bobby.main()