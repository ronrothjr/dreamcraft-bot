# bot.py
import os
from mongoengine import *

from discord.ext import commands
from discord import Embed, Game, Status
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
async def on_ready():
    await bot.change_presence(status=Status.online, activity=Game(name=f'{PREFIX}{COMMAND} to start', type=3))

@bot.command(name=COMMAND)
async def command_handler(ctx, *args):
    """
    Command handler for .d, the Dreamcraft Bot command
    """

    if len(args) == 0:
        await ctx.send(embed=Embed(title='𝕯𝖗𝖊𝖆𝖒𝖈𝖗𝖆𝖋𝖙 𝕭𝖔𝖙', colour=13400320, description=START))
        return

    if len(args) == 1 and args[0].lower() in ['h','help']:
        await ctx.send(embed=Embed(title='𝕯𝖗𝖊𝖆𝖒𝖈𝖗𝖆𝖋𝖙 𝕭𝖔𝖙', colour=13400320, description=HELP))
        return
    
    handler = DreamcraftHandler(ctx, args)
    title, messages = handler.get_messages()
    # Concatenate messages and send
    if isinstance(messages, list):
        [await send(ctx, title, f'{m}\n') for m in messages]
    else:
        await send(ctx, title, messages)

async def send(ctx, title, message):
    if message:
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
                    await send_message(ctx, title, 'Mesage exceeds maximum length of 2048')
                else:
                    await send_message(ctx, title, '\n'.join(chunked))
        else:
            await send_message(ctx, title, message)

async def send_message(ctx, title, message):
    image_split = message.split('!image')
    message = image_split[0]
    if len(image_split) > 2:
        message += ''.join(image_split[2:])
    embed = Embed(type='rich', title=f'{title} Module - {PREFIX}{COMMAND} {title.lower()} help', colour=13400320, description=message)
    # embed.set_author(name='Dreamcraft Bot', icon_url='http://drive.google.com/uc?export=view&id=1jSmg-SJx5YwjgIepYA6SYjtPZ_aNQnNr')
    if len(image_split) > 1:
        embed.set_image(url=image_split[1])
    await ctx.send(embed=embed)

bot.run(TOKEN)