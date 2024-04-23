import enum
import string
from enum import Enum

import discord
from discord import ForumTag
from discord.message import Attachment, Message

from dozer.cogs._utils import Cog


class DetectedFile:
    # which kind of file it is; used to decide what to try to detect
    # TODO: process opmodes? gradle files?
    class FileType(Enum):
        MECDRIVE = 0
        THREEWHEELODO = 1
        TWOWHEELODO = 2

    class Version(Enum):
        v0x = 0
        v1x = 1

    fileType: FileType
    version: Version


"""Automatically respond to support threads with suggestions"""


class Autohelp(Cog):
    @Cog.listener('on_thread_create')
    async def on_thread_create(self, thread: discord.Thread):

        #if thread.parent.id != 1229216062877208637:  # roadrunner-help thread in FTC discord, TODO: make configurable?
        #   return
        msg = None
        async for m in thread.history(limit=1, oldest_first=True):
            msg = m
        if msg is None or len(thread.applied_tags) < 1:
            return

        rrver = None
        for tag in thread.applied_tags:
            if tag.name == "0.5":
                rrver = "0.5"
            if tag.name == "1.0":
                rrver = "1.0"
        if rrver is None:
            if "1.0" in msg.content:
                rrver = 1.0
            elif "0.5" in msg.content:
                rrver = 0.5
            else:
                for attachment in msg.attachments:  # try to detect based on filenames
                    if "SampleMecanumDrive" in attachment.filename:
                        rrver = 0.5
                    elif "MecanumDrive" in attachment.filename:
                        rrver = 1.0

        suggests = ""
        if rrver == "0.5":
            suggests += self.findsuggest05(thread.applied_tags, msg)
        elif rrver == "1.0":
            suggests += self.findsuggest10(thread.applied_tags, msg)
        else:
            suggests += "\n No version specified! Please tell us what version of roadrunner you are using."
            suggests += "\n"
            suggests += "\n Suggestions for 1.0:"
            suggests += self.findsuggest10(thread.applied_tags, msg)
            suggests += "\n Suggestions for 0.5:"
            suggests += self.findsuggest05(thread.applied_tags, msg)

        await msg.reply(suggests, suppress_embeds=True)

    @staticmethod
    def findsuggest10(tags: list[ForumTag], message: Message) -> string:
        suggests = ""
        for tag in tags:
            if tag.name == "installation":
                suggests += ("\n Make sure to review the [installation guide.]("
                             "https://rr.brott.dev/docs/v1-0/installation/) closely.")
                suggests += "\n"
                suggests += "\n If you're encountering import errors after opening the project, try clicking"
                suggests += " File in the top left and selecting Invalidate Caches."
            elif tag.name == "tuning":
                suggests += "\n Make sure to review the [tuning guide](https://rr.brott.dev/docs/v1-0/tuning/) closely."
                if not any("MecanumDrive" in a.filename for a in message.attachments):
                    suggests += "\n"
                    suggests += "\n **No MecanumDrive file detected.**"
                    suggests += "\n **Please send a copy of your MecanumDrive and localizer files.**"
                suggests += "\n"
                suggests += "\n Common Problems"
                suggests += "\n If you are at the feedforward tuning stage and the robot is slightly overshooting"
                suggests += " the target velocity on deceleration, this is normal and will be corrected by feedback."
                suggests += "\n If you are trying to find out how to tune your odometry wheel positions, you need to"
                suggests += " scroll down on the angular ramp logger page."
            elif tag.name == "trajectories":
                suggests += "\n "

        return suggests

    @staticmethod
    def findsuggest05(tag: list[ForumTag], message: Message) -> string:
        return ""

    @Cog.listener('on_message')
    async def on_message(self, msg: discord.Message):
        if len(msg.attachments) == 0:
            return

    @staticmethod
    def process_attachment(atch: discord.Attachment) -> DetectedFile | None: # todo: finish
        if "text" not in atch.content_type:
            return None


async def setup(bot):
    """Adds the maintenance cog to the bot process."""
    await bot.add_cog(Autohelp(bot))
