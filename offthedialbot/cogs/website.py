"""cogs.Website"""
from discord.ext import commands

from offthedialbot import utils


class Website(commands.Cog):

    @commands.group(invoke_without_command=True)
    async def website(self, ctx):
        pass

    @commands.command()
    async def moved(self, ctx, page: str):
        """This channel has been moved!"""
        await utils.Alert(ctx, utils.Alert.Style.WARNING,
            title="This page has been moved! :construction_site:",
            description=f"Soon this channel will be gone, you can find the new and updated version here:\n**https://otd.ink/{page}**")
