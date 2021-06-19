from time import gmtime, strftime, sleep
#import os
import requests
import json
#from dateutil import parser
import time#, sched
import asyncio
import discord
from discord.ext.commands import Bot
#import csv, sys
from datetime import datetime
import math
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#COMMANDS_FILE = 'commands.json'
#CONFIG_FILE = 'config.json'
ENDPOINT = NOTIFS_CHANNEL_ID = RECORDS_CHANNEL_ID = TEST_CHANNEL = RECORDS_CHANNEL_ID = STREAM_INFO_MESSAGE = NO_STREAMS_TEXT = SOME_STREAMS_TEXT = BROADCAST_OVERRIDE = EVENT_DT = None
for key, value in json.loads(open(CONFIG_FILE, 'r').read()).items():
    globals()[key] = value

#NOTIFS_CHANNEL_ID = TEST_CHANNEL

print(discord.__version__)

mb = Bot

@mb.event
async def on_message(message):
    if(scheduled):
        return
    response_content = await commands.find(message.content.lower()[1:])
    if(response_content is not None):
        if(isinstance(response_content, discord.Embed)):
            await message.channel.send(embed=response_content)
        else:
            await message.channel.send(response_content)


@mb.event
async def on_ready():
    # if a CLI arg is passed, run that scheduled task and quit
    if(scheduled):
        await getattr(commands, sys.argv[1])(mb)
        os._exit(0)

scheduled = len(sys.argv) == 2 and \
                sys.argv[1] in \
                list(map(lambda func: func.__name__, commands.scheduled))

mb.run(open("TOKEN.txt", "r").readline())