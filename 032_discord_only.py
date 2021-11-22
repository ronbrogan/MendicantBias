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
#import datetime
from datetime import datetime
import time
import math
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

print(f"{discord.__version__}\nVersion 2021.8.31")
mb = Bot(command_prefix='!') # Creates the main bot object - asynchronous
TOKEN = open("TOKEN.txt", "r").readline() # reads the token used by the bot from the local directory
ENDPOINT = "https://api.haloruns.com/" # API ENDPOINT for HaloRuns.com
STREAMS_ENDPOINT = "https://haloruns.com/content/feeds/streamList.json"
RECORDS_ENDPOINT = "https://haloruns.com/content/feeds/latestRecords.json"
OLDEST_ENDPOINT = "https://haloruns.com/content/boards/oldest.json"
NOTIFS_CHANNEL_ID = 491719347929219072 # Hard-coded #live-streams channel - need to change this if the channel gets replaced
RECORDS_CHANNEL_ID = 600075722232692746 # Hard-coded #wr-runs channel - need to change this if the channel gets replaced
TEST_CHANNEL = 818617029011177492 # Wackee's test channel
#NOTIFS_CHANNEL_ID = TEST_CHANNEL##
NO_STREAMS_TEXT = "Nobody is currently streaming" + "<:NotLikeThis:257718094049443850>" # Default text used when there are no current streamers
DEFAULT_SOME_STREAMS = "To appear on the HaloRuns stream tracker, link your Twitch account at https://haloruns.com/\nFor a list of terms that will automatically hide your stream from being shown here (if you are not speedrunning or would prefer to have your stream hidden) you can use the .nohr command anywhere in the server, or DM me directly!\n- - - - - - - - - - - - -\nCURRENTLY LIVE:\n- - - - - - - - - - - - -" # Default text used when there are some current streamers
SOME_STREAMS_TEXT=DEFAULT_SOME_STREAMS
TUT_ENDPOINT = "haloruns.info/tutorial?id=" # Once we get tutorials off the ground, this can be used to add commands for any number of tutorials present on the .info site
NOHR = open("nohr.txt").readline().strip().split(",")

## Flags - Used to turn conditional behaviors on or off - crude, and should upgrade functionality
RELAY = False
RACE = False

modIds = json.load(open("modIds.json", "r"))["modIds"]
print(modIds)

temps = {}

@mb.event
async def on_message(message):
        ### This needs to STOP - gotta find a way to make this cleaner
        ### Numerous behaviors based on conditions present in any message the bot has access to - some memes, some links, some tools

        if message.content.lower() == ".sc_fling":
                await message.channel.send(
                        " It is known. It skips the plasmas from Goldie so its not really worth. It would save time in coop or if you picked up plasmas before the fling."
                        )
        if message.content.lower() == ".race":
                if RACE == True:#1==1:#RACE == True:
                        delta = await raceCountdown(ret=True)#turned it off because of chaz
                        #await message.channel.send(embed=discord.Embed(description=delta))#turned it off because of chaz
        if ".scarab_deload" == message.content.lower():
                await message.channel.send(
                                "If you reach the top of the stairs between 1:14 and 1:20 from the Scarab's initial spawn, it will deload. Full explanation at https://www.youtube.com/watch?v=j9fgKI74dwo"
                                )
        if ".storm" == message.content.lower():
                await message.channel.send(
                                "The Storm (Halo 3) on the Easy difficulty is the greatest level (IL) to speedrun. The combat is perfect, (no rng) the movement is clean, you get help from your allies, (marines) and you get to do a cool skip! (Scarab skip) Then you WALK for 40 seconds to the end and do a cross map shot to end the level. (The Storm) How could anyone think that this level, (The Storm) is bad? It's my favorite level, (IL) in the entire game! (Halo 3)"
                                )
        if ".craig" == message.content.lower():
                await message.channel.send(
                                "What.  The.  FUCK?!?!  34HeadFuckin3 has yet again come out with ANOTHER goddamn update, and what did it do you ask?  ODST is now on pc.  Fucking brilliant, of all thing, that's what gets added??  NO.  ONE.  CARES!!!  BUT WAIT!! That's not all...not only did they add something that no one give a rat's ass about, but whadaya know?  THEY FUCKED UP SHIT IN MY HALO 3 SPEEDRUN™!!!  The AI is busted to all hell.  I have put over 50,000 goddamn hours into this shit, AND THEY GO AHEAD AND PUT FUCKING CRAIG IN THE GODDAMN JETPACK CLEAR?!?!?  Do they not realize how important EVERY SECOND is on the easy difficulty??  Every mother fucking AI now has 2Head levels on mechanics, my fucking hermit crab could program a better code.  Fucks sake 343, every fucking record on HaloRuns™ is now impossible to beat because of your incompetent team of high school dropouts.  Fuck you."
                                )
        if ".points" in message.content.lower():
                print(message.content.lower().split(), message.content.lower().split()[0])
                if len(message.content.lower().split()) == 3 and ".points" == message.content.lower().split()[0]:
                        cmd = message.content.lower().split()
                        points = await getPoints(cmd[1], cmd[2])
                        emb = discord.Embed(title="Points Calculator", description=points)
                        await message.channel.send(embed=emb)
        if ".scoped" in message.content.lower():
                await message.channel.send("Scoped flies are different than unscoped; read: https://discordapp.com/channels/83061848139632640/293842240529235968/727967537114906657")
        if ".calc" in message.content.lower():
                if message.content.lower() == ".calc":
                    await message.channel.send("\nSpecify the game that you'd like to see the calculator for\nExample: `.calc odst`\n(reach)\n(h1, hce, ce)\n(h2)\n(h3)\n(odst)\n(h4)\n(h5)")
                if len(message.content.lower().split()) == 2:
                        game = message.content.lower().split()[1]
                        if game == "reach":
                                await message.channel.send("https://haloruns.com/calc/reach")                
                        if game in ["h1", "hce", "ce"]:
                                await message.channel.send("https://haloruns.com/calc/hce") 
                        if game == "h2":
                                await message.channel.send("https://haloruns.com/calc/h2") 
                        if game == "h2a":
                                await message.channel.send("https://haloruns.com/calc/h2a") 
                        if game == "h3":
                                await message.channel.send("https://haloruns.com/calc/h3") 
                        if game == "odst":
                                await message.channel.send("https://haloruns.com/calc/odst")
                        if game == "h4":
                                await message.channel.send("https://haloruns.com/calc/h4") 
                        if game == "h5":
                                await message.channel.send("https://haloruns.com/calc/h5")
        if ".nohr" in message.content.lower():
                            await message.channel.send(f"Add one of these tags to your stream title to be hidden from the stream list, when you don't want to be listed, or are doing something non-speedrun related\n{NOHR}")
        if ".keyes" in message.content.lower():
            await message.channel.send("Keyes midroll cutscene is not timed by MCC, and takes 43-44 seconds  - please add that to your PGCR (Post-Game Carnage Report) for an approximation, and manually re-time your RTA before submitting a fake world record :)")
        if ".rules" in message.content.lower():
            #if message.content.lower == ".rules":
            rules_desc = "[Rules Page](https://haloruns.com/rules)\n[H2 Timing Video Guide](https://youtu.be/1DT7XwIDrwE)\n[Coop Forum Posts](https://haloruns.com/forums?t=595)\nPlease read the posts carefully, and ask question if you need some clarification" 
            #[Rules Forum Posts](https://haloruns.com/forums?t=3)\n
            rules_embed = discord.Embed(description=rules_desc)
            await message.channel.send(embed=rules_embed)
        if ".ban" in message.content.lower():
                print(f"ban message detected from {message.author.id}")
                print(f"mods: {modIds}")
                if message.author.id in modIds:
                        print("modCheck")
                        link = message.content.lower().split(" ")[1]
                        retStr = f"banning {link} from the stream list for the default timeout period"
                        print(f"banning {link} from the stream list for the default timeout period")
                        await message.channel.send(retStr)
                        temps[link] = time.time()

async def manageTemps():
        while True:
                await asyncio.sleep(10)
                defTimeout = 60*60*8
                timeout = defTimeout
                for key in temps.keys():
                        if time.time() > temps[key] + timeout:
                                print(f"{temps.pop(temps[key])} removed from temp list")


async def apiRecentWRs():
        ### Returns the most recent records list, and replaces the locally stored records list with a new one.
        ###NOTE: this means there is no aggregation over time - leaving that to HaloRuns.com

        #records = requests.get(str(ENDPOINT + "records/recent" + "/12")).json()# - old
        # Note to wackee: new endpoint is haloruns.com/content/feeds/latestRecords.json
        #records = getJSON(str(ENDPOINT + "records/recent" + "/12"))
        records = getJSON(str(RECORDS_ENDPOINT))["Entries"]
        file = open("records.json", "w+")
        json.dump(records, file)
        file.truncate()
        file.close()
        return records

async def savedRecentWRs():
        ### Returns the locally stored records list, or creates one from the haloruns API if not present before returning

        try:
                oldRecords = json.load(open("records.json", "r"))
        except :
                oldRecords = await apiRecentWRs()
                print("reset recent world records")
        return oldRecords

async def announce(record):
        ### Announces a new record, according to the announcement string; Hoping to add time the previous record stood, as well as what rank in Oldest Records it was

        #record["vid"] = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" test vid link, dont think we need it anymore
        recordsChannel = mb.get_channel(RECORDS_CHANNEL_ID)
        try:
        # new method, trying to be cleaner about what data is being used; hopefully to be cleaned up more, maybe learn to create better objects for less json
                #prev_record = record["prev_record"]#better to split the previous record before messing with the json,^ again might wanna learn objects
                icon = parseIcon(record)
                game = record["GameName"]
                diff = record["Difficulty"]
                level = record["LevelName"]
                coop = isCoop(record)
                levelUrl = record["LeaderboardUrl"]
                runTime = record["Duration"]
                vidUrl = record["Participants"][0]["EvidenceLink"]
                parsedPlayers = parsePlayers(record)
                players = parsedPlayers[0]
                if record["PreviousRecordId"] != "00000000-0000-0000-0000-000000000000":
                        prevRunTime = record["PreviousRecordDuration"]
                        prevVidUrl = record["PreviousRecordParticipants"][0]["EvidenceLink"]
                        prevPlayers = parsedPlayers[1]
                        timeDiff = str(convertTimes(getSecondsDiff(record["PreviousRecordDuration"], record["Duration"])))
                        prevTimeStanding = getTimeStood(int((H2I(record["OccuredAt"]) - H2I(record["PreviousRecordOccuredAt"])).total_seconds()))
                        oldestRank = ordinalize(findOldestRank(record))
                #split announcement for ease of printing, logging
                if record["PreviousRecordId"] != "00000000-0000-0000-0000-000000000000":
                        announcement = f":trophy: **New Record!**    {icon}\n{game} {diff} - [{level} {coop}]({levelUrl}) | [{runTime}]({vidUrl})\nSet by: {players}\n\nPrevious Record:\n[{prevRunTime}]({prevVidUrl}) by {prevPlayers}\nBeaten by {timeDiff}\nStanding for {prevTimeStanding},\nit was the {oldestRank} oldest record"#{coop} record"
                else:
                #if doesn't have previous:
                        announcement = f":trophy: **NEW RECORD!**    {icon}\n{game} {diff} - [{level} {coop}]({levelUrl}) | [{runTime}]({vidUrl})\nSet by: {players}"
                print(announcement)
                embedLink = discord.Embed(description=announcement, color=0xff0000)
                await recordsChannel.send(embed=embedLink)
                # old working method but ugly # embedlink = discord.Embed(description=":trophy: **new record!**\n%s %s - [%s %s](%s) | [%s](%s)\nset by: %s\n\nprevious record:\n[%s](%s) by %s\nbeaten by %s" % (record["game_name"], record["difficulty_name"], record["level_name"], iscoop(record), record["il_board_url"], record["time"], str(record["vid"]), parseplayers(record), record["prev_record"]["time"], str(record["prev_record"]["vid"]), parseplayers(record["prev_record"]), str(converttimes(record["prev_record"]["run_time"]-record["run_time"]))), color=0xff0000)
        except:
                print("record announcement failed")

async def getPostedStreams():
        postedStreamList = []
        postedStreams = await mb.get_channel(NOTIFS_CHANNEL_ID).history(oldest_first = True).flatten() # Ordered return of messages in the channel
        postedStreams = postedStreams[1:] # Retain first message in the list for a header post
        for streamMessage in postedStreams:
                streamMessageContent = list(filter(lambda x: "[Watch Here]" in x.value, streamMessage.embeds[0].fields))
                streamMessageContentString = streamMessageContent[0].value
                streamMessageUrl = streamMessageContentString.split("]")[1].strip("()")
                postedStreamList.append(streamMessageUrl)
        return postedStreamList

def saveStreamsToFile(postedStreamList, filename):
        with open(filename, "a+") as file:
                for stream in postedStreamList:
                        file.append(stream + "\n")
                file.truncate()

async def maintainTwitchNotifs():
        ### Loops on sleep
        ### Pulls streams from API
        ### Adds streams that are not present in the channel, as long as they aren't temp banned by discord mods
        ### Saves the stream list to file, then calls the purge function NOTE: maybe purging earlier

        while True:
                await asyncio.sleep(10) # Timer to loop, better way but haven't gotten around to changing it
                print("Looking for streams to post") # CONSOLE OUT
                apiData = getJSON(STREAMS_ENDPOINT)
                responses = []
                messageData = await mb.get_channel(NOTIFS_CHANNEL_ID).history(oldest_first=True).flatten()
                messageData = messageData[1:]
                urlList = []
                for message in messageData:
                        messageContent = list(filter(lambda x: "[Watch Here]" in x.value, message.embeds[0].fields))
                        messageContentString = messageContent[0].value
                        messageUrl = messageContentString.split("]")[1].strip("()")
                        urlList.append(messageUrl)

                if len(apiData["Entries"]) == 0:
                      for messageObject in messageData:
                              await messageObject.delete()
                else:
                        apiList = []
                        for entry in apiData["Entries"]:
                                apiList.append(entry["StreamUrl"].lower().rstrip())
                        for url in urlList:
                                if url not in apiList:
                                        for messageObject in messageData:
                                                if list(filter(lambda x: "[Watch Here]" in x.value, messageObject.embeds[0].fields))[0].value.split("]")[1].strip("()") == url:
                                                        await messageObject.delete()
                        postedStreamList = await getPostedStreams() # Get newest channel feed
                        for stream in apiData["Entries"]:
                                if stream["StreamUrl"].lower() not in postedStreamList:
                                        if stream["StreamUrl"].lower() not in temps.keys():
                                                print(f"{stream['StreamUrl'].lower()} not in: {postedStreamList}")
                                                ### TODO: get twitch user color and set in embed
                                                title = stream["Title"]
                                                game = stream["GameName"]
                                                embed = discord.Embed(title=f"Streaming {game}", description=f"\"{title}\"", color=0x080808)
                                                embed.set_author(name=f"{stream['Username']}", url=f"https://haloruns.com/profiles/{stream['Username'].lower()}")
                                                ### TODO: Get Game Name from site when we get functionality to detect game.
                                                embed.add_field(name="\u200b", value=f"[Watch Here]({stream['StreamUrl'].lower()})", inline=True)
                                                embed.set_footer(text=f"{stream['Viewers']} Viewers | {stream['StreamUrl'].lower()}")
                                                ### Not sure if we want viewer count, but its here if we do.
                                                embed.set_thumbnail(url=f"{stream['ProfileImageUrl']}")
                                                responses.append(embed)
                        streamsChannel = mb.get_channel(NOTIFS_CHANNEL_ID)

                        if responses != []:
                                for response in responses:
                                                await streamsChannel.send(embed=response)

                postedStreamList = await getPostedStreams() # Get updated channel feed


def H2I(timestamp):
        #zulu replacement
        zs = f'{timestamp.split(".")[1]}Z'
        return parser.parse(timestamp)


        # ds = timestamp.split("T")][0]
        # ts = timestamp.split("T")[1].split(".")[0]
        # return f"{ds} {ts}"

def getTimeFormat(s):
        count = s.count(':')
        if count == 0:
                return "%S"
        if count == 1:
                return "%M:%S"
        if count == 2:
                return "%H:%M:%S"

# Pads time strings to fit the format 00:00:00
def padTime(s):
        out = ""
        x = s.split(':')
        for t in x[:-1]:
                out += t.zfill(2) + ':'
        out += x[-1].zfill(2)
        return out

async def getPoints(pb, wr):
        pointsStr = ""
        help_string = "Use like this: .points [hh:]mm:ss [hh:]mm:ss.\n"
        try:
                print("checking points", pb, wr)
                pb = pb.replace('.', ':')
                wr = wr.replace('.', ':')

                pb = padTime(pb)
                wr = padTime(wr)

                pbFormat = getTimeFormat(pb)
                wrFormat = getTimeFormat(wr)

                print(f"{pb} {pbFormat}")
                print(f"{wr} {wrFormat}")

                pbTime = datetime.strptime(pb, pbFormat) - datetime.strptime("0", "%S")
                wrTime = datetime.strptime(wr, wrFormat) - datetime.strptime("0", "%S")

                if(wrTime > pbTime):
                        pbTime, wrTime = wrTime, pbTime # swap so PB is always larger

                pointsExact = 0.008 * math.exp(4.8284*(wrTime.seconds/pbTime.seconds)) * 100

                # If more than 30 minutes, this is probably a fullgame time
                if (wrTime.seconds > 30 * 60):
                        pointsExact *= 10

                print(pointsExact)
                pointsStr = f"Your PB of {pbTime} against {wrTime} is worth {int(pointsExact)} points"
                print(pointsStr)
        except Exception as e:
                print(e)
                pointsStr = "One of your times is probably not formatted correctly."
        finally:
                return(help_string + pointsStr)

async def lookForRecord():
        ### Upon a new record being added to the HR database, this catches it by checking the API against the locally stored records
        ### It then calls the announce() function to push it to the Discord channel

        while True:
                await asyncio.sleep(20) # Sleeps first, to avoid trying to perform an action before the bot is ready - there's certainly a better way to do this async stuff
                try:
                        oldRecords = await savedRecentWRs()
                        print("checking records")
                        newRecords = await apiRecentWRs()
                        RunIds = []
                        for element in oldRecords:
                                RunIds.append(element["RunId"])
                        for record in newRecords:
                                if record['RunId'] not in RunIds:
                                        print("announcing!")
                                        await announce(record)
                except:
                        pass

def convertTimes(seconds):
                return '%d:%02d' % (seconds // 60 if seconds > 60 else 0, seconds % 60)

def getSecondsDiff(time1, time2):
        oldRecord = datetime.strptime(time1, "%H:%M:%S")
        newRecord = datetime.strptime(time2, "%H:%M:%S")
        diff = int((oldRecord - newRecord).total_seconds())
        return diff

def isCoop(record):
        return 'Co-op' if record["IsCoop"] == True else 'Solo'

#OLD# def findOldestRank(record):
#         ### Returns the rank describing how old the record is
#         #Backflip's suggestion:
#         #return len(list(filter(lambda pastRecord: pastRecord["timestamp"] <= record["timestamp"], requests.get(str(ENDPOINT + "records/oldest")).json()))) + 1
#         try:
#                 recordsByOldest = requests.get(OLDEST_ENDPOINT).json()["Entries"]
#                 soloRBO = [x for x in recordsByOldest if x['is_coop'] == False]
#                 coopRBO = [x for x in recordsByOldest if x['is_coop'] == True]
#                 if record['is_coop'] == False:
#                         recordsToCheckAgainst = soloRBO
#                 else:
#                         recordsToCheckAgainst = coopRBO
#                 for index, item in enumerate(recordsToCheckAgainst, 1): # clever optional argument to help with ordinalizing
#                         if record["timestamp"] <= item["timestamp"]:
#                                 return index
#         except:
#                 print("W E L L - oldest rank check failed")

def findOldestRank(record):
        ### Returns the rank describing how old the record is
        #Backflip's suggestion:
        #return len(list(filter(lambda pastRecord: pastRecord["timestamp"] <= record["timestamp"], requests.get(str(ENDPOINT + "records/oldest")).json()))) + 1
        try:
                # recordsByOldest = requests.get(OLDEST_ENDPOINT).json()["Entries"]
                # for index, item in enumerate(recordsByOldest, 1): # clever optional argument to help with ordinalizing
                #         if record["RunId"] <= item["RunId"]:
                #                 return index
                return record["PreviousRecordRank"]
        except:
                print("W E L L - oldest rank check failed")

def ordinalize(rank):
        ### yoinked
        SUFFIXES = {1: 'st', 2: 'nd', 3: 'rd'}
        # I'm checking for 10-20 because those are the digits that
        # don't follow the normal counting scheme. 
        if 10 <= rank % 100 <= 20:
                suffix = 'th'
        else:
                # the second parameter is a default.
                suffix = SUFFIXES.get(rank % 10, 'th')
        return str(rank) + suffix

def getTimeStood(seconds):
        if seconds == 0:
                return "1 second"
        else:
                secs = seconds #record["timestamp"] - prev_record["timestamp"]
                days = secs//86400
                hours = (secs - days*86400)//3600
                minutes = (secs - days*86400 - hours*3600)//60
                seconds = secs - days*86400 - hours*3600 - minutes*60
                result = ("{0} day{1}, ".format(days, "s" if days!=1 else "") if days else "") + \
                ("{0} hour{1}, ".format(hours, "s" if hours!=1 else "") if hours else "") + \
                ("{0} minute{1}, ".format(minutes, "s" if minutes!=1 else "") if minutes else "") + \
                ("{0} second{1}, ".format(seconds, "s" if seconds!=1 else "") if seconds else "")
                return result.rstrip(", ")

async def raceCountdown(ret=False):
        ### Replaces the top message in #live-streams with a countdown to an event, if RACE is set
        dt = datetime
        raceStartTime = dt(year=2021, month=3, day=13, hour=19)
        if ret == True:
                flat = await mb.get_channel(NOTIFS_CHANNEL_ID).history(oldest_first=True).flatten()
                now = dt.now()
                delta = raceStartTime - now
                return str(':'.join(str(delta).split(':')[:2])) + " until the #off-topic Marathon begins!\nWatch [Here](https://www.twitch.tv/HaloSpeedrunNetwork)"
        while True:
                await asyncio.sleep(20)
                if RACE==True:
                        flat = await mb.get_channel(NOTIFS_CHANNEL_ID).history(oldest_first=True).flatten()
                        now = dt.now()
                        delta = raceStartTime - now
                        oldestMessage = flat[0]
#                        await oldestMessage.edit(content = str(':'.join(str(delta).split(':')[:2])) + " until the #off-topic Marathon!")
                        await oldestMessage.edit(content = str("HaloRuns #off-topic Marathon is LIVE\nWatch at https://www.twitch.tv/HaloSpeedrunNetwork"))

                return "Halo: Master Chief Collection"

def buildPlayerMD(player):
        #print(str("[%s](https://haloruns.com/profiles/%s)" % (player, player)))
        return str("[%s](https://haloruns.com/profiles/%s)" % (player, player))
        
def parsePlayers(record):
        if record["PreviousRecordId"] != "00000000-0000-0000-0000-000000000000":
                players = []
                for player in record["Participants"]:
                        players.append(buildPlayerMD(player["Username"]))
                playersReturn = " | ".join(players)
                oldPlayers = []
                for player in record["PreviousRecordParticipants"]:
                        oldPlayers.append(buildPlayerMD(player["Username"]))
                oldPlayersReturn = " | ".join(oldPlayers)
                return [playersReturn, oldPlayersReturn]
        else:
                players = []
                for player in record["Participants"]:
                        players.append(buildPlayerMD(player["Username"]))
                playersReturn = " | ".join(players)
                return [playersReturn]


def parseIcon(record):
        return {
                "Halo CE":"<:CE:758288302738112543>",
                "Halo 2":"<:H2:758288302423277620>",
                "Halo 2 MCC":"<:H2:758288302423277620>",
                "Halo 3":"<:H3:758288302863941652>",
                "Halo 3: ODST":"<:ODST:758288303106555944>",
                "Halo: Reach":"<:Reach:758288303191228477>",
                "Halo 4":"<:H4:758288302985707531>",
                "Halo 5":"<:H5:758288303064612905>",
                "Halo Infinite":"<:HInf:911881741038411787>"
                }[record['GameName']]

def getJSON(url): # New method of guaranteeing a valid JSON response - sometimes the bot crashes when bad data is returned, this aims to fix that
        print(f"Requesting JSON from: {url}")
        attempts = 0
        errorMessage = ""
        while attempts < 10:
                try:
                        response = requests.get(url, verify=False)
                except Exception as e:#ConnectionError
                        if type(e) == type(ConnectionError):
                                print("Connection ERROR")
                                response = e                        
                        else:
                                response = e
                try:
                        responseDict = response.json()
                        print(f"Successfully returned valid JSON object")
                        return responseDict
                except:
                        print("NOT VALID JSON")

                        if str(errorMessage) != str(response):
                                print(f"NEW ERROR: {response}")
                                attempts = 0
                        else:
                                print(f"ERROR: {response}")

                        errorMessage = response
                        #print(f"-------------\nRESPONSE\n-------------\n{response}\n-------------\nEND RESPONSE\n-------------\n")
                        attempts += 1
                        print(f"Retrying api request... {attempts} attempts ({5 * attempts} seconds before next request)\n")
                        time.sleep(5 * attempts)
        print("Timed out server request")
        exit()
mb.loop.create_task(manageTemps())
mb.loop.create_task(raceCountdown())
mb.loop.create_task(lookForRecord())
mb.loop.create_task(maintainTwitchNotifs())
mb.run(TOKEN)
