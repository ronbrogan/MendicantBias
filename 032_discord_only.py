from time import gmtime, strftime
import requests
import json
from time import sleep
from dateutil import parser
import time
import asyncio
import discord
from discord.ext.commands import Bot
from datetime import datetime, timedelta, tzinfo, timezone
import math
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import re
from azure.storage.queue import QueueServiceClient
import base64
import humanize
import traceback

print(f"Version 2022.02.01\nDiscord Version: {discord.__version__}\nCredit Wackee\nBackflip\nScales\nXero\nNervy")
mb = Bot(command_prefix='!') # Creates the main bot object - asynchronous
secrets = open("TOKEN.txt", "r")
TOKEN = secrets.readline() # reads the token used by the bot from the local directory
QUEUE_AUTH = secrets.readline()

record_queue = None
try:
    queue_service = QueueServiceClient.from_connection_string(conn_str=QUEUE_AUTH)
    record_queue = queue_service.get_queue_client("records-discord")
except:
    print("unable to connect to record queue, polling queue will be skipped")

STREAMS_ENDPOINT = "https://haloruns.com/content/feeds/streamList.json"
RECORDS_ENDPOINT = "https://haloruns.com/content/feeds/latestRecords.json"
OLDEST_ENDPOINT = "https://haloruns.com/content/boards/oldest.json"

NOTIFS_CHANNEL_ID = 491719347929219072 # Hard-coded #live-streams channel - need to change this if the channel gets replaced
RECORDS_CHANNEL_ID = 600075722232692746 # Hard-coded #wr-runs channel - need to change this if the channel gets replaced
TEST_CHANNEL = 818617029011177492 # Wackee's test channel
#NOTIFS_CHANNEL_ID = TEST_CHANNEL##

INFO_TEXT = "To appear on the HaloRuns stream tracker, link your Twitch account at https://haloruns.com/\nFor a list of terms that will automatically hide your stream from being shown here (if you are not speedrunning or would prefer to have your stream hidden) you can use the .nohr command anywhere in the server, or DM me directly!\n You can now also toggle your stream visibility from your HaloRuns Profile!"
NO_STREAMS_TEXT = f"Nobody is currently streaming<:NotLikeThis:257718094049443850>\n{INFO_TEXT}" # Default text used when there are no current streamers
DEFAULT_SOME_STREAMS = f"{INFO_TEXT}\nCURRENTLY LIVE:\n- - - - - - - - - - - - -" # Default text used when there are some current streamers
SOME_STREAMS_TEXT=DEFAULT_SOME_STREAMS

NOTICE_TEXT = ""

NOHR = open("nohr.txt").readline().strip().split(",")

THROTTLE = 300 # not yet used
STREAMS_THROTTLE = 120 # seconds between allowing an update
RECORDS_THROTTLE = 120 # seconds between allowing an update


@mb.event
async def on_message(message):
    ### This needs to STOP - gotta find a way to make this cleaner
    ### Numerous behaviors based on conditions present in any message the bot has access to - some memes, some links, some tools

    if message.content.lower() == ".sc_fling":
        await message.channel.send(
                " It is known. It skips the plasmas from Goldie so its not really worth. It would save time in coop or if you picked up plasmas before the fling."
                )
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
        if len(message.content.lower().split()) == 4 and ".points" == message.content.lower().split()[0]:
            cmd = message.content.lower().split()
            points = await getPoints(cmd[1], cmd[2], cmd[3])
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
        rules_desc = "[Rules Page](https://haloruns.com/rules)\n[H2 Timing Video Guide](https://youtu.be/1DT7XwIDrwE)\n[Coop Forum Posts](https://haloruns.com/forums?t=595)\nPlease read the posts carefully, and ask question if you need some clarification"
        rules_embed = discord.Embed(description=rules_desc)
        await message.channel.send(embed=rules_embed)

def getJSON(url):
    ### Tries to return a valid JSON Response from a url
    ### Sometimes the bot crashes when bad data is returned, this aims to fix that

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

def updatedAt(data):
    try:
        if data == "streams":
            return H2I(json.load(open("streams.json", "r"))["UpdatedAt"])
        if data == "records":
            return H2I(json.load(open("records.json", "r"))["UpdatedAt"])
    except:
        return datetime(2000, 1, 1).astimezone(timezone.utc)

async def apiRecentWRs():
    ### Returns the most recent records list, and replaces the locally stored records list with a new one.

    records = getJSON(str(RECORDS_ENDPOINT))
    file = open("records.json", "w+")
    json.dump(records, file)
    file.truncate()
    file.close()
    # print(f"Records log updated {records['UpdatedAt']}")
    entryNames = []
    for entry in records["Entries"]:
        entryNames.append(entry["Participants"][0]["Username"])
    # print(f"API DATA:\n{entryNames}")
    return records["Entries"]

async def savedRecentWRs():
    ### Returns the locally stored records list, or creates one from the haloruns API if not present before returning

    try:
        oldRecords = json.load(open("records.json", "r"))
    except :
        oldRecords = await apiRecentWRs()
        print("reset recent world records")
    entryNames = []
    for entry in oldRecords["Entries"]:
        entryNames.append(entry["Participants"][0]["Username"])
    # print(f"SAVED DATA:\n{entryNames}")
    return oldRecords["Entries"]

async def getPostedStreams():
    ### Returns a list of strings, for the streams currently posted in the live-streams channel

    postedStreamList = []
    postedStreams = await mb.get_channel(NOTIFS_CHANNEL_ID).history(oldest_first = True).flatten() # Ordered return of messages in the channel
    topMessage = postedStreams[0]
    postedStreams = postedStreams[1:] # Retain first message in the list for a header post
    for streamMessage in postedStreams:
        streamMessageUrl = messageToUrl(streamMessage)
        postedStreamList.append(streamMessageUrl)
    if NOTICE_TEXT != "":
        await topMessage.edit(content=NOTICE_TEXT)
    return postedStreamList

async def pollQueueForRecords():
    while record_queue != None:
        await asyncio.sleep(10)
        msg = record_queue.receive_message(timeout = 1)
        if msg != None:
            try:
                msgtext = base64.b64decode(msg.content)
                record = json.loads(msgtext.decode('utf-8'))
                print(f'announcing {record["RunId"]} !')
                await announce(record)
                record_queue.delete_message(msg)
            except Exception  as e: 
                print("failure during record poll")
                print(e)
                traceback.print_exc()

async def lookForRecord():
    ### Upon a new record being added to the HR database, this catches it by checking the API against the locally stored records
    ### It then calls the announce() function to push it to the Discord channel

    while True:
        await asyncio.sleep(20) # Sleeps first, to avoid trying to perform an action before the bot is ready - there's certainly a better way to do this async stuff
        diff = int( (datetime.now(timezone.utc) - updatedAt("records") ).total_seconds())
        if diff > STREAMS_THROTTLE:
            print("diff too high, calling records")
            try:
                oldRecords = await savedRecentWRs()
                print("checking records")
                newRecords = await apiRecentWRs()
                RunIds = list(map(lambda x: x["RunId"], oldRecords))
                #for element in oldRecords:
                    #print(f'\nLine 203 | for record in oldRecords: \n{element["RunId"]}\n')
                    #RunIds.append(element["RunId"])
                for record in newRecords:
                    if record['RunId'] not in RunIds:
                        # if record["Tie"] == False:
                        #         print("announcing!")
                        #         await announce(record)
                        print(f'announcing {record["RunId"]} !')
                        await announce(record)
            except:
                logEvent("Problem in lookForRecord")


async def announce(record):
    ### Announces a new record, according to the announcement string:
    ### time the previous record stood
    ### what rank in Oldest Records it was

    recordsChannel = mb.get_channel(RECORDS_CHANNEL_ID)
    announcement = formatWRAnn(record)
    if record["Tie"] == False:
        embeddedAnnouncement = discord.Embed(description=announcement[0], color=announcement[1]["embedColor"])
        await recordsChannel.send(embed=embeddedAnnouncement)

def formatWRAnn(record):
    notNew = False
    embedConfig = {
        "embedColor":0xff0000
    }
    icon = parseIcon(record)
    game = record["GameName"]
    diff = record["Difficulty"]
    level = record["LevelName"]
    genre = parseGenre(record) # includes coop/solo, bit of a hack to get extras going
    extra = record["IsExtension"] # awaiting
    levelUrl = removeSpaces(record["LeaderboardUrl"])
    runTimeDelta = duration_delta(record["Duration"])
    runTime = format_duration(runTimeDelta)
    vidUrl = record["Participants"][0]["EvidenceLink"]
    parsedPlayers = parsePlayers(record)
    players = parsedPlayers[0]
    setBy = f"Set by: {players}"
    title = f":trophy: **New Record!**    {icon}"

    # if previous record exists:
    if record["PreviousRecordId"] != "00000000-0000-0000-0000-000000000000":
        notNew = True
        prevRunTimeDelta = duration_delta(record["PreviousRecordDuration"])
        prevRunTime = format_duration(prevRunTimeDelta)
        prevVidUrl = record["PreviousRecordParticipants"][0]["EvidenceLink"]
        prevPlayers = parsedPlayers[1]
        timeDiff = format_duration(prevRunTimeDelta - runTimeDelta)
        prevTimeStanding = humanize.precisedelta(H2I(record["OccuredAt"]) - H2I(record["PreviousRecordOccuredAt"]), format="%.0f")
        oldestRank = ordinalize(findOldestRank(record))
        # Formatting string segments - doing it here so i can pick and choose later
        previousString = f"Previous Record:\n[{prevRunTime}]({prevVidUrl}) by {prevPlayers}"
        beatenBy = f"Beaten by {timeDiff}"
        standingFor = f"Standing for {prevTimeStanding},\nIt was the {oldestRank} oldest record"
        prevComp = f"\n\n{previousString}\n{beatenBy}\n{standingFor}"

    # if no previous record:
    run = f"[{game} {diff} - {level} {genre}]({levelUrl}) | [{runTime}]({vidUrl})"
    if extra == True:
        embedColor = 0x0000ff
        embedConfig["embedColor"] = embedColor
        title = f":trophy: **New Record! (Extra)**    {icon}"
        run = f"[{game} {diff} - {level} {genre}]({levelUrl}) | [{runTime}]({vidUrl})"
        if game == "Multi Game":
            game = ""
            run = f"[{diff} {genre}]({levelUrl}) | [{runTime}]({vidUrl})"

    # Final compositions
    announcement = f"{title}\n{run}\n{setBy}"
    if notNew:
        announcement += prevComp
    return (announcement, embedConfig)

def saveStreamList(apiData):
    file = open("streams.json", "w+")
    json.dump(apiData, file)
    file.truncate()
    file.close()

async def maintainTwitchNotifs():
    ### Loops on sleep
    ### Pulls streams from API
    ### Removes streams not present in the most-recent api data
    ### Adds streams that are not present in the channel

    while True:
        await asyncio.sleep(10) # Timer to loop, better way but haven't gotten around to changing it
        #todo: slow down traffic using lastUpdated - 1 minute intervals at least
        #                                      datetime.datetime
        diff = int( (datetime.now(timezone.utc) - updatedAt("streams") ).total_seconds())
        if diff > STREAMS_THROTTLE:
            print("diff too high, calling streams")
            print("Looking for streams to post")
            apiData = getJSON(STREAMS_ENDPOINT)

            saveStreamList(apiData)

            notif_channel = mb.get_channel(NOTIFS_CHANNEL_ID)
            allMessages = await notif_channel.history(oldest_first=True).flatten()
            topMessage = allMessages[0]
            streamMessages = allMessages[1:]
            urlList = []
            for message in streamMessages:
                urlList.append(messageToUrl(message))

            currentStreams = len(streamMessages)

            # Purge posted streams
            apiList = []
            for entry in apiData["Entries"]:
                apiList.append(entry["StreamUrl"].lower().rstrip())

            for url in urlList:
                if url not in apiList:
                    for messageObject in streamMessages:
                        if messageToUrl(messageObject) == url:
                            print(f"Attempting to remove {url}")
                            await messageObject.delete()
                            currentStreams -= 1

            # For editing the Notice Text
            if len(apiData["Entries"]) == 0 and NOTICE_TEXT == "":
                await topMessage.edit(content=NO_STREAMS_TEXT)
            else:
                for stream in apiData["Entries"]:
                    stream_url = stream["StreamUrl"].lower()
                    existing_msg = next((x for x in streamMessages if messageToUrl(x) == stream_url), None)

                    ### TODO: get twitch user color and set in embed
                    title = re.sub(r"[\r\n\t]", "", stream["Title"])
                    game = stream["GameName"]
                    embed = discord.Embed(title=f"Streaming {game}", description=f'\"{title}\"', color=0x009e00)
                    embed.set_author(name=f"{stream['Username']}", url=f"https://haloruns.com/profiles/{stream['Username']}")
                    ### TODO: Get Game Name from site when we get functionality to detect game.
                    embed.add_field(name="\u200b", value=f"[Watch Here]({stream['StreamUrl'].lower()})", inline=True)
                    stream_duration_raw = timedelta(seconds=math.ceil((datetime.now(timezone.utc) - parser.parse(stream['StartedAt'])).total_seconds() / 60) * 60)
                    stream_duration = humanize.precisedelta(stream_duration_raw, minimum_unit="minutes", format="%.0f")
                    embed.set_footer(text=f"{stream['Viewers']} Viewers | Streaming for {stream_duration}")
                    ### Not sure if we want viewer count, but its here if we do.
                    embed.set_thumbnail(url=stream['ProfileImageUrl'])
                    embed.set_image(url=f"https://static-cdn.jtvnw.net/previews-ttv/live_user_{stream['TwitchUsername'].lower()}-640x360.jpg?ts={int(time.time())}")

                    if existing_msg == None:
                        print(f"{stream_url} not in: {streamMessages}")
                        await notif_channel.send(embed=embed)
                        currentStreams += 1
                    else:
                        # update the embed
                        await existing_msg.edit(embed=embed)

            if currentStreams > 0 and NOTICE_TEXT == "":
                await topMessage.edit(content=SOME_STREAMS_TEXT)
        else:
            #logEvent("Throttled streams poll")
            print(f"Throttled streams poll")

### Utility Functions ###

def removeSpaces(url):
    return url.replace(" ", "")

def messageToUrl(message):
    ### Return Url contained in a live-stream embed message

    streamMessageContent = list(filter(lambda x: "[Watch Here]" in x.value, message.embeds[0].fields))
    streamMessageContentString = streamMessageContent[0].value
    streamMessageUrl = streamMessageContentString.split("]")[1].strip("()")
    return streamMessageUrl

def H2I(timestamp):
    ### Haloruns Timestamp to datetime

    #zs = f'{timestamp.split(".")[1]}Z' #zulu replacement
    return parser.parse(timestamp)

def getTimeFormat(s):
    ### Formats a time string for strptime

    count = s.count(':')
    if count == 0:
        return "%S"
    if count == 1:
        return "%M:%S"
    if count == 2:
        return "%H:%M:%S"

def padTime(s):
    ### Pads time strings to fit the format 00:00:00

    out = ""
    x = s.split(':')
    for t in x[:-1]:
        out += t.zfill(2) + ':'
    out += x[-1].zfill(2)
    return out

async def getPoints(pb, wr, points):
    ### Returns a formatted string for the embed used by the .points command

    pointsStr = ""
    help_string = "Use like this: .points [hh:]mm:ss [hh:]mm:ss MaxPoints\n"
    try:
        print("checking points", pb, wr)
        #replace periods for catching weird input?
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

        pointsExact = 0.008 * math.exp(4.8284*(wrTime.seconds/pbTime.seconds)) * points

        print(pointsExact)
        pointsStr = f"Your PB of {pbTime} against {wrTime} is worth {int(pointsExact)} points"
        print(pointsStr)
    except Exception as e:
        print(e)
        pointsStr = "One of your times is probably not formatted correctly."
    finally:
        return(help_string + pointsStr)

def duration_delta(duration):
    if(type(duration) is str): 
        t = datetime.strptime(duration,"%H:%M:%S")
        return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)

    return timedelta(seconds=duration)

def format_duration(timedelta):
    hours, remainder = divmod(timedelta.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    if(hours == 0):
        return '{:01}:{:02}'.format(int(minutes), int(seconds))

    return '{:01}:{:01}:{:02}'.format(int(hours), int(minutes), int(seconds))

def parseGenre(record):
    ### Returns string for whether coop or not
    if record["IsExtension"] == True:
        if record["IsCoop"] == True:
            return f"{record['CategoryName']} Co-op"
        else:
            return record['CategoryName']
    else:
        return 'Co-op' if record["IsCoop"] == True else 'Solo'

def findOldestRank(record):
    ### Returns the rank describing how old the record is

    try:
        return record["PreviousRecordRank"]
    except:
        print("W E L L - oldest rank check failed")

def ordinalize(rank):
    ### Convert a rank to ordinalized string, ex: 22-> 22nd
    ### yoinked

    SUFFIXES = {1: 'st', 2: 'nd', 3: 'rd'}
    # I'm checking for 10-20 because those are the digits that
    # don't follow the normal counting scheme.
    if 10 <= rank % 100 <= 20:
        suffix = 'th'
    else:
        # the second parameter is a default.
        suffix = SUFFIXES.get(rank % 10, 'th')
    # 1th meme
    if rank == 1:
        return "1th"
    else:
        return str(rank) + suffix

def buildPlayerMD(player):
    ### Returns the link to a haloruns user, from their username
    return str("[%s](https://haloruns.com/profiles/%s)" % (player, player))

def parsePlayers(record):
    ### Returns a formatted string for users present in a record entry

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
    ### Returns the string for a relevant discord icon, from a record entry
    icons = {
            "Halo CE":"<:CE:758288302738112543>",
            "Halo 2":"<:H2:758288302423277620>",
            "Halo 2 MCC":"<:H2:758288302423277620>",
            "Halo 3":"<:H3:758288302863941652>",
            "Halo 3: ODST":"<:ODST:758288303106555944>",
            "Halo: Reach":"<:Reach:758288303191228477>",
            "Halo 4":"<:H4:758288302985707531>",
            "Halo 5":"<:H5:758288303064612905>",
            "Halo Infinite":"<:HInf:911881741038411787>"
            }
    if record["GameName"] not in icons.keys():
        return "<:haloruns:230158630593232897>"
    else:
        return icons[record["GameName"]]

def logEvent(event):
    file = open("log.txt", "a")
    file.write(f"{strftime('%a, %d %b %Y %H:%M:%S', gmtime())} || {event}\n")
    file.close()

mb.loop.create_task(pollQueueForRecords())
mb.loop.create_task(lookForRecord())
mb.loop.create_task(maintainTwitchNotifs())
mb.run(TOKEN)
