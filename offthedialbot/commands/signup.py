"""$signup"""
from contextlib import contextmanager, asynccontextmanager

import discord

from offthedialbot import utils
from offthedialbot.commands.profile import create, update, create_status_embed


@utils.deco.otd_only
async def main(ctx):
    """Sign up for the upcoming tournament!"""
    tourney, profile = await check_prerequisites(ctx)

    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(color=utils.colors.COMPETING))
    checklist = Checklist(ui, {
        "prerequisites": True,
        "accepted rules": False,
        "profile is up-to-date": False,
        "smash.gg integration": False,
        "final confirmation": False
    })

    # Check requirements
    with checklist.checking("accepted rules"):
        await accepted_rules(ui, tourney["rules"])
    with checklist.checking("profile is up-to-date"):
        profile = await profile_uptodate(ui, profile)
    with checklist.checking("smash.gg integration"):
        await smashgg(ui, profile, tourney["link"])
    with checklist.checking("final confirmation"):
        await confirm_signup(ui)

    await finalize_signup(ui, profile)
    await ui.end(True)


async def check_prerequisites(ctx):
    """Check to make sure the user fits all the prerequisites."""
    tourney = utils.dbh.get_tourney()
    try:
        profile = utils.Profile(ctx.author.id)
    except utils.Profile.NotFound:
        profile = utils.ProfileMeta(ctx.author.id)

    check = {
        (lambda: not tourney or tourney["reg"] is False): "Registration is not open.",
        (lambda: profile and profile.get_banned()):
            "You are currently banned from competing in Off the Dial tournaments.",
        (lambda: profile and profile.get_reg()): "You are already signed up!"
    }
    if any(values := [value for key, value in check.items() if key()]):
        await utils.Alert(ctx, utils.Alert.Style.DANGER, title="Registration Failed.", description=values[0])
        raise utils.exc.CommandCancel

    return tourney, profile


async def accepted_rules(ui, rules):
    """Make sure the user has accepted the tournament rules."""
    ui.embed.title = f"Read over the rules at **<{rules}>**."
    ui.embed.description = "Once finished, select \u2705. By proceeding, you accept and agree to the rules."
    await ui.get_valid_reaction(["\u2705"])


async def profile_uptodate(ui, profile):
    """Make sure the user's has a profile, and it is updated."""
    if isinstance(profile, utils.ProfileMeta):
        ui.embed.title = "A profile is required to compete. To create one and proceed, select \u2705."
        ui.embed.description = "Your profile will be saved for future use."
        await ui.get_valid_reaction(["\u2705"])
        await ui.run_command(create.main)
    else:
        await profile_updated(ui, profile)

    return utils.Profile(ui.ctx.author.id)


async def profile_updated(ui, profile):
    """Make sure the user's profile is updated."""
    emojis = {
        "check": "\u2705",
        "pencil": "\u270f\ufe0f"
    }
    ui.embed.title = "Is your profile up-to-date?"
    ui.embed.description = f"Select {emojis['check']} if it is, or select {emojis['pencil']} to update it."
    async with show_preview(ui.ctx, profile):
        reply = await ui.get_valid_reaction(list(emojis.values()))
    if reply.emoji == emojis["pencil"]:
        await ui.run_command(update.main)


@asynccontextmanager
async def show_preview(ctx, profile):
    """Show a preview for profile update."""
    preview = None
    try:
        embed = create_status_embed(ctx.author.display_name, profile, True)
        embed.title, embed.description = "Preview:", f"**{embed.title}**"
        preview = await ctx.send(embed=embed)
        yield
    finally:
        if preview:
            await preview.delete()


async def smashgg(ui, profile, link):
    """Make sure the user has signed up on smash.gg."""
    # Uses OAuth2 to link user's smash.gg account
    # Give signup code to sign up on smash.gg
    ui.embed.title = f"Sign up on smash.gg at **<{link}/register>**."
    ui.embed.description = "Once finished, enter the confirmation code you recieved in the email (`#F1PN28`)."
    code = await ui.get_valid_message(r"^#?([A-Za-z0-9]){6}$",
        {"title": "Invalid Confirmation Code", "description": "The code you entered was not valid, please try again."},
        timeout=600)
    profile.set_reg('code', code.content)


async def confirm_signup(ui):
    """Confirm user signup."""
    confirm = utils.Alert.create_embed(utils.Alert.Style.WARNING, "Confirm Signup",
        "Are you ready to sign up? You will not be able to undo without first contacting the organisers.")
    ui.embed.title, ui.embed.description, ui.embed.color = confirm.title, confirm.description, confirm.color
    await ui.get_valid_reaction(["\u2705"])


async def finalize_signup(ui, profile: utils.Profile):
    """Finalize user signup, hand out roles, update profile, etc."""
    # Hand out competing role
    await ui.ctx.author.add_roles(utils.roles.get(ui.ctx, "Competing"))

    # Set profile to competing
    profile.set_reg()
    profile.write()


class Checklist:
    """Set checklist field on the signup form."""

    emojis = {
        True: '\u2705',
        None: '\U0001f7e6',
        False: '\u2b1b'
    }

    def __init__(self, ui, checklist):
        self.ui = ui
        self.checklist = checklist

        self.ui.embed.add_field(name="Requirements:", value=self.create(self.checklist))

    @contextmanager
    def checking(self, field):
        """Check a requirement as a context manager."""
        try:
            self.update({field: None})
            yield
        finally:
            self.update({field: True})

    def update(self, updates):
        """Update the checklist inside of the UI."""
        self.checklist.update(**updates)
        self.ui.embed.set_field_at(0, name=self.ui.embed.fields[0].name, value=self.create(self.checklist))

    @classmethod
    def create(cls, checklist):
        """Create the checklist string."""
        return "\n".join(f"{cls.emojis[value]} Checking {name}..." for name, value in checklist.items())
