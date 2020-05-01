from time import gmtime, strftime
import os
import requests
import json
from time import sleep
from dateutil import parser
import sched, time
import asyncio
import discord
from discord.ext.commands import Bot
import csv
import sys
print(discord.__version__)
mb = Bot(command_prefix='!')
TOKEN = open("TOKEN.txt", "r").readline()
Streampoint = 0
Endpoint = "https://haloruns.com/api/"
NOTIFS_CHANNEL_ID = 491719347929219072
RECORDS_CHANNEL_ID =  600075722232692746
NO_STREAMS_TEXT = "Nobody is currently streaming" + "<:NotLikeThis:257718094049443850>"
SOME_STREAMS_TEXT = "CURRENTLY LIVE:\n- - - - - - - - - - - - -"


async def getProfile(user):
    return requests.get(str(Endpoint + "users/" + user)).json()

async def apiRecentWRs():
    records = requests.get(str(Endpoint + "records/recent" + "/12")).json()
    file = open("records.json", "w+")
    json.dump(records, file)
    file.truncate()
    file.close()
    return records

async def apiStreams():
    response = requests.get(str(BETA_ENDPOINT + "streams")).json().content.decode("utf-8")
    streams = []
    for item in response:
        streams.append(item)
    return streams

async def savedRecentWRs():
    try:
        oldRecords = json.load(open("records.json", "r"))
    except :
        oldRecords = json.load(requests.get(str(Endpoint + "recentRecords" + ResponseFormat + "&showTimestamps=1")).json())
        file = open("records.json", "w+")
        json.dump(oldRecords, file)
        file.truncate()
        file.close()
        print("reset recent world records")
    return oldRecords

async def announce(record):
    #record["vid"] = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    recordsChannel = mb.get_channel(RECORDS_CHANNEL_ID)
##    try:
    print(":trophy: **New Record!**\n%s %s - %s %s: [%s](%s)\nSet by: %s" % (record["game_name"], record["difficulty_name"], record["level_name"], isCoop(record), record["time"], str(record["vid"]), parsePlayers(record)))
    embedLink = discord.Embed(description=":trophy: **New Record!**\n%s %s - %s %s: [%s](%s)\nSet by: %s" % (record["game_name"], record["difficulty_name"], record["level_name"], isCoop(record), record["time"], str(record["vid"]), parsePlayers(record)), color=0xFF0000)
    try:
        
        await recordsChannel.send(embed=embedLink)
    except:
        print("record announcement failed")
                                  
async def maintainTwitchNotifs():
    while True:
        await asyncio.sleep(1220)
        print("looking for streams to post")
        responses = []
        postedStreamList = []
##        try:
        try:
            streams = requests.get(str(Endpoint + "streams")).json()
        except:
            print("failed to pull from main API, proceeding to backup...")
        try:
            if streams:
                pass
        except:
            streams = requests.get(str(BETA_ENDPOINT + "streams")).json()# = requests.get(str(Endpoint + "streams" + ResponseFormat)).json()
##        except:
##            print("stream pull failed")
        postedStreams = await mb.get_channel(NOTIFS_CHANNEL_ID).history(oldest_first = True).flatten()
        postedStreams = postedStreams[1:]
        for stream in postedStreams:
            postedStreamList.append(stream.content)
##        try:
        if streams != []:
##            config = loadConfig()
            for stream in streams:
                if stream["stream"] not in postedStreamList:
##                        if config[stream["#" + "stream".lower()]]["muted"] == False:
                    responses.append(stream["stream"])
            streamsChannel = mb.get_channel(NOTIFS_CHANNEL_ID)
            if responses != "":
                for response in responses:
                        await streamsChannel.send(response)
##        except:
##            print("Failed posting new streams")
        parsedStreams = []
        for stream in streams:
            parsedStreams.append(stream["stream"])
        await purgeNotStreams(parsedStreams)

async def purgeNotStreams(streams):
    flat = await mb.get_channel(NOTIFS_CHANNEL_ID).history(oldest_first=True).flatten()
    oldestMessage = flat[0]
##    streams = {}
    if streams != []:
        for stream in streams:
            stream = stream.rstrip()
        for messageObject in flat:
            if messageObject == oldestMessage:
                if messageObject.content != SOME_STREAMS_TEXT:   
                    print("Streams found, editing top message")
                    await messageObject.edit(content = SOME_STREAMS_TEXT)
                else:
                    print("Found streams, continuing...")
##            config = loadConfig()
##            else:
##                config["#" + messageObject.content.split("/")[-1].lower()]["muted"] == True
##                await messageObject.delete()
            if messageObject.content not in streams:
                if messageObject == oldestMessage:
                    pass
                else:
                    await messageObject.delete()
                    
    else:
        print("No Streams found, editing top message")
        messagesLen = len(flat)
        for messageObject in flat:
            if messageObject == oldestMessage:
                await messageObject.edit(content=NO_STREAMS_TEXT)
            else:
                await messageObject.delete()

async def lookForRecord():
    while True:
        await asyncio.sleep(120)
        try:
            oldRecords = await savedRecentWRs()
            print("checking records")
            newRecords = await apiRecentWRs()
            for record in newRecords:
                if record not in oldRecords:
                    print("announcing!")
                    await announce(record)
        except:
            pass

def isCoop(record):
    return 'Co-op' if record["is_coop"] else 'Solo'

def fixUrl(word):
    newWord = "<" + word + ">"
    return newWord

def fixEscape(string):
    decoded = bytes(string, "utf-8").decode("unicode_escape")
    return decoded

def un2(game):
    if game == "Halo 2 MCC":
        return "Halo: Master Chief Collection"
    else:
        return game

def infoStream(stream):
    splitStream = stream.split("\n")
    print(splitStream)
    streamEr = (" ").join(splitStream[0].split("is live!")[0])
    streamGame = (" ").join(splitStream[1].split(" ")[1:])
    streamTitle = splitStream[2]
    print(streamEr, streamGame, streamTitle)
    return (streamEr, streamGame, streamTitle)

def streams(streams):
    streamList = []
    for stream in streams:
        streamList.append(stream["stream"])
    return streams

##def loadConfig():
##    file = json.load(open("config.json", "r+"))
##    return file
##    
def parseStream(stream):
    val = URLValidator()
    newTitleList = []
    title = fixEscape(stream["title"])
    print(title)
    for word in stream["title"].split(" "):
        try:
            val(word)
            newTitleList.append(fixUrl(word))
        except:
            newTitleList.append(word)
    newTitle = " ".join(newTitleList)
    streamParse = "%s is live!\nPlaying %s\n%s\n%s" % (stream["name"], un2(stream["game"]), newTitle, stream["stream"])
    return streamParse

def buildPlayerMD(player):
    print(str("[%s](https://haloruns.com/profiles/%s)" % (player, player)))
    return str("[%s](https://haloruns.com/profiles/%s)" % (player, player))
    
def parsePlayers(record):
    players = []
    for player in record["runners"]:
        if player != None:
            players.append(buildPlayerMD(player))
    return " | ".join(players)

mb.loop.create_task(lookForRecord())
mb.loop.create_task(maintainTwitchNotifs())
mb.run(TOKEN)
