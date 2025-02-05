from discord.ext import commands
import discord
import re


class MessageStore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def msg(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Ungültiger command!")

    @msg.command()
    @commands.has_permissions(manage_channels=True)
    async def set(self, ctx, name, *, content):
        with self.bot.db.get(ctx.guild.id) as db:
            if len(db.execute("SELECT name, content FROM msg WHERE name = ?", (name.lower(),)).fetchall()) > 0:
                db.execute("UPDATE msg SET content = ? WHERE name = ?", (content, name.lower()))
            else:
                db.execute("INSERT INTO msg (name, content) VALUES (?, ?)", (name.lower(), content))

        await ctx.message.add_reaction('\U00002705')

    @commands.Cog.listener()
    async def on_message(self, message):
        search = re.search(r'#(\w+)', message.content)
        if search is None:
            return

        key = search.group(1)

        with self.bot.db.get(message.guild.id) as db:
            result = db.execute("SELECT name, content FROM msg WHERE name = ?", (key.lower(),)).fetchall()

        if len(result) == 0:
            return

        await message.channel.send(result[0][1])


def setup(bot):
    bot.add_cog(MessageStore(bot))
