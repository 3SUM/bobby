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
    thank_you_list = ["THANK YOU", "THANKS"]
    conn = None
    cur = None

    @bot.event
    async def on_guild_join(guild):
        print(f"{bot.user.name} joined {guild.name}")
        try:
            Bobby.cur.execute(
                sql.SQL(
                    "CREATE TABLE IF NOT EXISTS {} (name VARCHAR(255) NOT NULL, karma INTEGER, UNIQUE(name))"
                ).format(sql.Identifier(guild.name))
            )
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            try:
                Bobby.conn = psycopg2.connect(DATABASE_URL, sslmode="require")
                Bobby.conn.autocommit = True
                Bobby.cur = Bobby.conn.cursor()
            except (Exception, psycopg2.DatabaseError) as conErr:
                print(conErr)
        finally:
            print(f"Database Table for {guild.name} setup!")

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
                        try:
                            name = i.name + i.discriminator
                            guild = message.author.guild
                            Bobby.cur.execute(
                                sql.SQL(
                                    "INSERT INTO {table} (name, karma) VALUES (%s, %s) ON CONFLICT (name) DO UPDATE SET karma = {table}.karma + 1;"
                                ).format(table=sql.Identifier(guild.name)),
                                [name, 1],
                            )
                        except (Exception, psycopg2.DatabaseError) as error:
                            print(error)
                            try:
                                Bobby.conn = psycopg2.connect(
                                    DATABASE_URL, sslmode="require"
                                )
                                Bobby.conn.autocommit = True
                                Bobby.cur = Bobby.conn.cursor()
                            except (Exception, psycopg2.DatabaseError) as conErr:
                                print(conErr)
                        finally:
                            await message.channel.send(f"Gave +1 Karma to {i.mention}")
                break
        await bot.process_commands(message)

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user.name}")

    @bot.command()
    async def profile(ctx, member: discord.Member = None):
        roles = ""
        member = member or ctx.author
        name = member.name + member.discriminator
        karma = 0
        try:
            Bobby.cur.execute(
                sql.SQL("SELECT karma FROM {} WHERE name = %s").format(
                    sql.Identifier(member.guild.name)
                ),
                [name],
            )
            karma = Bobby.cur.fetchone()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            try:
                Bobby.conn = psycopg2.connect(DATABASE_URL, sslmode="require")
                Bobby.conn.autocommit = True
                Bobby.cur = Bobby.conn.cursor()
            except (Exception, psycopg2.DatabaseError) as conErr:
                print(conErr)
        finally:
            if karma:
                karma = karma[0]
            else:
                karma = 0

        join_date = member.joined_at
        join_date = f"{join_date.month}/{join_date.day}/{join_date.year}"
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
        profile_embed.add_field(name="Karma", value=karma, inline=False)
        profile_embed.add_field(name="Date Joined", value=join_date, inline=True)
        profile_embed.add_field(name="Roles", value=roles, inline=True)
        await ctx.send(embed=profile_embed)

    def main():
        Bobby.conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        Bobby.conn.autocommit = True
        Bobby.cur = Bobby.conn.cursor()
        bot.run(TOKEN)


if __name__ == "__main__":
    Bobby.main()