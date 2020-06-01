# bot.py
__author__ = 'Ron Roth Jr'
__contact__ = 'u/ensosati'
__version__ = 'v1.0.57'

import os
from mongoengine import connect

from discord.ext import commands
from discord import Embed, Game, Status
from discord.ext.commands.context import Context
from dotenv import load_dotenv

from config.setup import Setup
from handlers.dreamcraft import DreamcraftHandler

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('DISCORD_PREFIX')
COMMAND = os.getenv('DISCORD_COMMAND')
DATABASE = os.getenv('DISCORD_DATABASE')
SETUP = Setup()
START = SETUP.start
HELP = SETUP.help

connect(DATABASE)


bot = commands.Bot(command_prefix=PREFIX)


@bot.event
async def on_ready() -> None:
    await bot.change_presence(status=Status.online, activity=Game(name=f'{PREFIX}{COMMAND} to start', type=3))

@bot.command(name=COMMAND)
async def command_handler(ctx: Context, *args) -> None:
    """
    Command handler for .d, the Dreamcraft Bot command

    Parameters
    ----------
    ctx : object(Context)
        The Discord.Context object used to retrieve and send information to Discord users
    args : array(str)
        The arguments sent to the bot to parse and evaluate
    """

    if len(args) == 0:
        await ctx.send(embed=Embed(title='𝕯𝖗𝖊𝖆𝖒𝖈𝖗𝖆𝖋𝖙 𝕭𝖔𝖙', colour=13400320, description=START))
        return

    if len(args) == 1 and args[0].lower() in ['h','help']:
        await ctx.send(embed=Embed(title='𝕯𝖗𝖊𝖆𝖒𝖈𝖗𝖆𝖋𝖙 𝕭𝖔𝖙', colour=13400320, description=HELP))
        return
    
    handler = DreamcraftHandler(ctx, args)
    title, messages = handler.get_messages()
    # Concatenate messages and send; handles str and list of str
    if isinstance(messages, list):
        [await send(ctx, title, f'{m}\n') for m in messages]
    else:
        await send(ctx, title, messages)

async def send(ctx: Context, title: str, message: str) -> None:
    """
    Parses the message content to determine how to send it

    Parameters
    ----------
    ctx : object(Context)
        The Discord.Context object used to retrieve and send information to Discord users
    title : str
        The title of the messsage
    message : str
        The body of the message (max 2048 characters)
    """

    if message:
        # Check of message that exceeds the 2048 embed description limit.
        # Chunk them just before the \n (newline) character just before exceeding the 2048 mark
        if len(message) > 2048:
            chunks = message.split('\n')
            chunked = []
            for cursor in range(0, len(chunks)):
                chunk = chunks[cursor]
                if len('\n'.join(chunked) + '\n' + chunk) > 2048:
                    await send_message(ctx, title, '\n'.join(chunked))
                    chunked = []
                else:
                    chunked.append(chunk)
            if chunked:
                if len('\n'.join(chunked)) > 2048:
                    await send_message(ctx, title, 'Message exceeds maximum length of 2048')
                else:
                    await send_message(ctx, title, '\n'.join(chunked))
        else:
            await send_message(ctx, title, message)
    else:
        # Some errors may result in no message content being sent. Let the user know to notify the Admin
        await send_message(ctx, title, 'Well, I\'ve got nothing to say to you. Ask the Admin.')

async def send_message(ctx: Context, title: str, message: str) -> None:
    """
    Sends a rich embed message with a title and a message

    Parameters
    ----------
    ctx : object(Context)
        The Discord.Context object used to retrieve and send information to Discord users
    title : str
        The title of the messsage
    message : str
        The body of the message (max 2048 characters)
    """

    title = f'{title} Module - {PREFIX}{COMMAND} {title.lower()} help'
    description = ''
    # Look for the '!image' token which marks the beginning and end of an image url to be embedded
    # Example message with image url: "Blah blah blah image!http://imgur.com/938712634918image!"
    image_url = ''
    if '!image' in message:
        # Split the image url from the message text
        image_split = message.split('!image')
        description = image_split[0]
        if len(image_split) > 1:
            image_url = image_split[1]
        if len(image_split) > 2:
            description += ''.join(image_split[2:])
    else:
        description = message
    embed = Embed(type='rich', title=title, colour=13400320, description=description)
    # Set the url image for the embed if one was found
    if image_url:
        embed.set_image(url=image_url)
    await ctx.send(embed=embed)

bot.run(TOKEN)