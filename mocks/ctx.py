# ctx.py

class Guild(object):
    def __init__(self, guild_name):
        self.name = guild_name

class Author(object):
    def __init__(self, author_name):
        self.name = author_name

class Type(object):
    def __init__(self, name):
        self.name = name

class CTXChannel(object):
    def __init__(self, channel_name):
        self.name = channel_name
        self.type = Type('public')

class CTX(object):
    def __init__(self, guild_name, author_name, channel_name):
        self.guild = Guild(guild_name)
        self.author = Author(author_name)
        self.channel = CTXChannel(channel_name)
        self.sent = []

    async def send(self, embed):
        self.sent.append([embed.title, embed.description])
        await print(f'Title: {embed.title}\nMessage: {embed.description}')