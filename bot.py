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
    await handler.handle()


bot.run(TOKEN)