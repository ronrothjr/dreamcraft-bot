https://www.mongodb.com/download-center/community?tck=docs_server

your settings.json file setup:
https://github.com/microsoft/vscode-python/issues/9346

Mongoengine info:
http://mongoengine.org/

Mongoengine Tutorial:
http://docs.mongoengine.org/tutorial.html

Mongoengine API Reference:
http://docs.mongoengine.org/apireference.html

Discord.py Docs:
https://discordpy.readthedocs.io/en/latest/index.html

Use “virtualenv”
“virtualenv” is a 3rd-party python package that effectively “clones” a python installation, thereby creating an isolated location to install packages. The evolution of “virtualenv” started before the existence of the User installation scheme. “virtualenv” provides a version of easy_install that is scoped to the cloned python install and is used in the normal way. “virtualenv” does offer various features that the User installation scheme alone does not provide, e.g. the ability to hide the main python site-packages.

Please refer to the virtualenv documentation for more details.
Setting up your virtual environment:
c:\>python -m venv c:\path\to\myenv
c:\path\to\myenv\scripts\acitvate

{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Dreamcraft Bot",
            "type": "python",
            "request": "launch",
            "pythonPath": "${config:python.pythonPath}",
            "program": "${workspaceFolder}/bot.py",
            "console": "externalTerminal"
        }
    ]
}

Making a test Discord bot:
https://realpython.com/how-to-make-a-discord-bot-python/