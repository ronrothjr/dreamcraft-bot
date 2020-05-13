# bot.py
import os
from mongoengine import *

from discord.ext import commands
from discord import Embed
from dotenv import load_dotenv

from config.setup import Setup
from handlers.dreamcraft import DreamcraftHandler

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
SETUP = Setup()
START = SETUP.start
HELP = SETUP.help

connect('dreamcraft')


bot = commands.Bot(command_prefix='.')

@bot.command(name='d')
async def command_handler(ctx, *args):
    """
    Command handler for .d, the Dreamcraft Bot command
    """

    if len(args) == 0:
        await ctx.send(embed=Embed(title='Dreamcraft Bot', colour=13400320, description=START))
        return

    if len(args) == 1 and args[0].lower() in ['h','help']:
        await ctx.send(embed=Embed(title='Dreamcraft Bot', colour=13400320, description=HELP))
        return
    
    handler = DreamcraftHandler(ctx, args)
    await handler.handle()


bot.run(TOKEN)