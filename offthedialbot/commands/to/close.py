"""$to close"""
import discord

from offthedialbot import utils
from . import attendees


@utils.deco.require_role("Organiser")
@utils.deco.tourney(2)
async def main(ctx):
    """Close registration and end checkin for the tournament."""
    ui: utils.CommandUI = await utils.CommandUI(ctx,
        discord.Embed(title="Commencing tournament...", color=utils.colors.COMPETING))

    await close_signup(ui)
    await end_checkin(ui)
    await attendees.remove.disqualified(ctx, checkin=True)
    await attendees.export.export_attendees(ctx, attendees.attendee_and_profile(ctx))
    await ui.ui.delete()
    await ui.end(True)


async def close_signup(ui):
    """Set tournament reg to false."""
    ui.embed.description = "Closing registration..."
    await ui.update()
    utils.tourney.update(reg=False)


async def end_checkin(ui):
    """Disable the checkin command."""
    ui.embed.description = "Disabling `$checkin`..."
    await ui.update()
    utils.tourney.update(checkin=False)


