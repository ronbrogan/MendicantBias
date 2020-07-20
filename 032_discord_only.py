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
import datetime
import math
print(discord.__version__)
mb = Bot(command_prefix='!')
TOKEN = open("TOKEN.txt", "r").readline()
Streampoint = 0
Endpoint = "https://haloruns.com/api/"
NOTIFS_CHANNEL_ID = 491719347929219072
RECORDS_CHANNEL_ID =  600075722232692746
NO_STREAMS_TEXT = "Nobody is currently streaming" + "<:NotLikeThis:257718094049443850>"
SOME_STREAMS_TEXT = "CURRENTLY LIVE:\n- - - - - - - - - - - - -"
RELAY = False

@mb.event
async def on_message(message):
    if message.content.lower() == ".sc_fling":
        await message.channel.send(
            " It is known. It skips the plasmas from Goldie so its not really worth. It would save time in coop or if you picked up plasmas before the fling."
            )
#    if message.content.lower() == ".relay":
#        delta = await relayCountdown(ret=True)
#        await message.channel.send(embed=discord.Embed(description=delta))
    if ".scarab_deload" == message.content.lower().split()[0]:
        await message.channel.send(
                "If you reach the top of the stairs between 1:14 and 1:20 from the Scarab's initial spawn, it will deload. Full explanation at https://www.youtube.com/watch?v=j9fgKI74dwo"
                )
    if ".points" == message.content.lower().split()[0]:
        if len(message.content.lower().split()) == 3:
            cmd = message.content.lower().split()
            points = await getPoints(cmd[1], cmd[2])
            await message.channel.send(points)
    if ".scoped" == message.content.lower().split()[0]:
        await message.channel.send("Scoped flies are different than unscoped; read: https://discordapp.com/channels/83061848139632640/293842240529235968/727967537114906657")
    if ".calc" in message.content.lower():
        if len(message.content.lower().split()) == 2:
            game = message.content.lower().split()[1]
            if game == "reach":
                await message.channel.send("https://haloruns.com/timeCalc/reach")                
            if game in ["h1", "hce", "ce"]:
                await message.channel.send("https://haloruns.com/timeCalc/hce") 
            if game == "h2":
                await message.channel.send("https://haloruns.com/timeCalc/h2") 
            if game == "h2a":
                await message.channel.send("https://haloruns.com/timeCalc/h2a") 
            if game == "h3":
                await message.channel.send("https://haloruns.com/timeCalc/h3") 
            if game == "odst":
                await message.channel.send("https://haloruns.com/timeCalc/odst") 
            if game == "h4":
                await message.channel.send("https://haloruns.com/timeCalc/h4") 
            if game == "h5":
                await message.channel.send("https://haloruns.com/timeCalc/h5") 

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
        await asyncio.sleep(120)
        print("looking for streams to post")
        responses = []
        postedStreamList = []
##        try:
        try:
            streams = requests.get(str(Endpoint + "streams")).json()
        except:
            print("stream pull failed")
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
##    await relayCountdown()
    oldestMessage = flat[0]
##    streams = {}
    if streams != []:
        for stream in streams:
            stream = stream.rstrip()
        for messageObject in flat:
            if messageObject == oldestMessage:
                if messageObject.content != SOME_STREAMS_TEXT:   
                    if RELAY==False:
                        print("Streams found, editing top message")
                        await messageObject.edit(content = SOME_STREAMS_TEXT)
                else:
                    print("Found streams, continuing...")
##            else:
####                config["#" + messageObject.content.split("/")[-1].lower()]["muted"] == True
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
                if RELAY==False:
                    await messageObject.edit(content=NO_STREAMS_TEXT)
            else:
                await messageObject.delete()

async def relayCountdown(ret=False):
    if ret == True:
        flat = await mb.get_channel(NOTIFS_CHANNEL_ID).history(oldest_first=True).flatten()
        dt = datetime.datetime
        now = dt.now()
        relayStartTime = dt(year=2020, month=6, day=28, hour=6)
        delta = relayStartTime - now
        return str(':'.join(str(delta).split(':')[:2])) + " until the HaloRuns Relay Race!\nWatch [Here](https://www.twitch.tv/HaloRaces)"
    while True:
        await asyncio.sleep(10)
        if RELAY==True:
            flat = await mb.get_channel(NOTIFS_CHANNEL_ID).history(oldest_first=True).flatten()
            dt = datetime.datetime
            now = dt.now()
            relayStartTime = dt(year=2020, month=6, day=28, hour=6)
            delta = relayStartTime - now
            oldestMessage = flat[0]            
            await oldestMessage.edit(content = str(':'.join(str(delta).split(':')[:2])) + " until the HaloRuns Relay Race!")

async def getPoints(pb, wr):
    pb_split = pb.split(":")
    pb_mins = int(pb_split[0])
    pb_secs = int(pb_split[1])
    pb_comb = pb_secs + 60 * pb_mins
    wr_split = wr.split(":")
    wr_mins = int(wr_split[0])
    wr_secs = int(wr_split[1])
    wr_comb = wr_secs + 60 * wr_mins
    points = round((0.008 * math.exp(4.8284*(wr_comb/pb_comb)) * 100), 1)
    print(points)
    
    print(str("Your PB of " + pb + " against "  + wr + " is worth " + str(points) + " points"))
    return(str("Your PB of " + pb + " against "  + wr + " is worth " + str(points) + " points"))

async def lookForRecord():
    while True:
        await asyncio.sleep(120)
        try:
            oldRecords = await savedRecentWRs()
            print("checking records")
            newRecords = await apiRecentWRs()
            ids = []
            for element in oldRecords:
                ids.append(element["id"])
            for record in newRecords:
                if record['id'] not in ids:
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

def loadConfig():
    file = json.load(open("config.json", "r+"))
    return file


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

#async def maintainRelayCountdown():
 #   string = "Relay Begins in:"
  #  flat = await mb.get_channel(NOTIFS_CHANNEL_ID).history(oldest_first=True).flatten()

    

mb.loop.create_task(relayCountdown())
mb.loop.create_task(lookForRecord())
mb.loop.create_task(maintainTwitchNotifs())
mb.run(TOKEN)
