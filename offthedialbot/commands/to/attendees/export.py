"""$to attendees export"""
import csv
from io import StringIO

import discord

from offthedialbot import utils
from . import attendee_and_profile


@utils.deco.require_role("Organiser")
@utils.deco.tourney()
async def main(ctx):
    """Export attendee profiles to a csv."""
    await ctx.trigger_typing()
    await export_attendees(ctx)


async def export_attendees(ctx):
    file = create_file(ctx)
    await send_file(ctx, file)


def create_file(ctx):
    """Create StringIO file."""
    file = StringIO()
    writer: csv.writer = csv.writer(file)
    csv_profiles = []

    for attendee, profile in attendee_and_profile(ctx):

        csv_profiles.append([
            f'@{attendee.name}#{attendee.discriminator}' if attendee else "ATTENDEE-NOT-FOUND",
            profile.get_status()["IGN"],
            f"'{profile.get_status()['SW']}'",
            *[profile.convert_rank_power(rank) for rank in profile.get_ranks().values()],
            profile.calculate_elo(),
            profile.get_stylepoints(),
            profile.get_cxp(),
            profile.get_ss(),
            profile.get_banned(),
            f"'{attendee.id}'" if attendee else "ATTENDEE-NOT-FOUND"
        ])
    writer.writerows([["Discord Mention", "IGN", "SW", "SZ", "RM", "TC", "CB", "Cumulative ELO", "Stylepoints", "CXP",
                       "Signal Strength", "Droppout Ban", "Discord ID"], []] + csv_profiles)
    file.seek(0)
    return discord.File(file, filename="profiles.csv")


async def send_file(ctx, file):
    await utils.Alert(ctx, utils.Alert.Style.SUCCESS,
        title=":incoming_envelope: *Exporting attendees complete!*",
        description="Download the spreadsheet below. \U0001f4e5"
    )
    await ctx.send(file=file)