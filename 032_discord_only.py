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
import time
import math
import math

print(discord.__version__)
mb = Bot(command_prefix='!') # Creates the main bot object - asynchronous
TOKEN = open("TOKEN.txt", "r").readline() # reads the token used by the bot from the local directory
ENDPOINT = "https://haloruns.com/api/" # API ENDPOINT for HaloRuns.com
NOTIFS_CHANNEL_ID = 491719347929219072 # Hard-coded #live-streams channel - need to change this if the channel gets replaced
RECORDS_CHANNEL_ID = 600075722232692746 # Hard-coded #wr-runs channel - need to change this if the channel gets replaced
TEST_CHANNEL = 718209912341135374 # Wackee's test channel
RECORDS_CHANNEL_ID = TEST_CHANNEL
NO_STREAMS_TEXT = "Nobody is currently streaming" + "<:NotLikeThis:257718094049443850>" # Default text used when there are no current streamers
SOME_STREAMS_TEXT = "CURRENTLY LIVE:\n- - - - - - - - - - - - -" # Default text used when there are some current streamers
TUT_ENDPOINT = "haloruns.info/tutorial?id=" # Once we get tutorials off the ground, this can be used to add commands for any number of tutorials present on the .info site

## Flags - Used to turn conditional behaviors on or off - crude, and should upgrade functionality
RELAY = False
RACE = False

@mb.event
async def on_message(message):
	### This needs to STOP - gotta find a way to make this cleaner
	### Numerous behaviors based on conditions present in any message the bot has access to - some memes, some links, some tools

	if message.content.lower() == ".sc_fling":
		await message.channel.send(
			" It is known. It skips the plasmas from Goldie so its not really worth. It would save time in coop or if you picked up plasmas before the fling."
			)
	if message.content.lower() == ".race":
		if RACE == True:
			delta = await raceCountdown(ret=True)
			await message.channel.send(embed=discord.Embed(description=delta))
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

async def apiRecentWRs():
	### Returns the most recent records list, and replaces the locally stored records list with a new one.
	###NOTE: this means there is no aggregation over time - leaving that to HaloRuns.com

	records = requests.get(str(ENDPOINT + "records/recent" + "/12")).json()
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
		oldRecords = apiRecentWRs()
		print("reset recent world records")
	return oldRecords

async def announce(record):
	### Announces a new record, according to the announcement string; Hoping to add time the previous record stood, as well as what rank in Oldest Records it was

	#record["vid"] = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" test vid link, dont think we need it anymore

	recordsChannel = mb.get_channel(RECORDS_CHANNEL_ID)
	try:
	# new method, trying to be cleaner about what data is being used; hopefully to be cleaned up more, maybe learn to create better objects for less json
		prev_record = record["prev_record"]#better to split the previous record before messing with the json,^ again might wanna learn objects
		icon = parseIcon(record)
		game = record["game_name"]
		diff = record["difficulty_name"]
		level = record["level_name"]
		coop = isCoop(record)
		levelUrl = record["il_board_url"]
		runTime = record["time"]
		vidUrl = record["vid"]
		players = parsePlayers(record)
		if prev_record != None:
			prevRunTime = prev_record["time"]
			prevVidUrl = prev_record["vid"]
			prevPlayers = parsePlayers(prev_record)
			timeDiff = str(convertTimes(record["prev_record"]["run_time"]-record["run_time"]))
			prevTimeStanding = getTimeStood(record, prev_record)
			oldestRank = ordinalize(findOldestRank(prev_record))
		#split announcement for ease of printing, logging
		if prev_record != None:
			announcement = f":trophy: **New Record!**    {icon}\n{game} {diff} - [{level} {coop}]({levelUrl}) | [{runTime}]({vidUrl})\nSet by: {players}\n\nPrevious Record:\n[{prevRunTime}]({prevVidUrl}) by {prevPlayers}\nBeaten by {timeDiff}\nStanding for {prevTimeStanding},\n it was the {oldestRank} oldest record"
		else:
		#if doesn't have previous:
			announcement = f":trophy: **NEW RECORD!**    {icon}\n{game} {diff} - [{level} {coop}]({levelUrl}) | [{runTime}]({vidUrl})\nSet by: {players}"
		print(announcement)
		embedLink = discord.Embed(description=announcement, color=0xff0000)
		# old working method but ugly # embedlink = discord.Embed(description=":trophy: **new record!**\n%s %s - [%s %s](%s) | [%s](%s)\nset by: %s\n\nprevious record:\n[%s](%s) by %s\nbeaten by %s" % (record["game_name"], record["difficulty_name"], record["level_name"], iscoop(record), record["il_board_url"], record["time"], str(record["vid"]), parseplayers(record), record["prev_record"]["time"], str(record["prev_record"]["vid"]), parseplayers(record["prev_record"]), str(converttimes(record["prev_record"]["run_time"]-record["run_time"]))), color=0xff0000)
	except:
		embedLink = discord.Embed(description=":trophy: **New Record!**\n%s %s - [%s %s](%s) | [%s](%s)\nSet by: %s" % (record["game_name"], record["difficulty_name"], record["level_name"], isCoop(record), record["il_board_url"], record["time"], str(record["vid"]), parsePlayers(record)), color=0xFF0000)
	try:
		await recordsChannel.send(embed=embedLink)
	except:
		print("record announcement failed")
async def maintainTwitchNotifs():
	### Adds any streams in the current stream list that are not present in the #live-streams channel
	### Then it calls the function to remove what doesn't belong any longer
	### This ought to be changed almost entirely, i hate looking at this abomination

	while True:
		await asyncio.sleep(10) # Update interval, seconds
		streams = []
		print("looking for streams to post")
		responses = []
		postedStreamList = []
#        try:
		streamsData = requests.get(str(ENDPOINT + "streams"))
		try:
			streams = streamsData.json()
		except:
			print("LOGGING", "[" + str(time.ctime())[:-5] + "]" + " | STREAM UPDATE FAILURE\n")
			log = open("log.txt", "a")
			log_string = "[" + str(time.ctime())[:-5] + "]" + " | STREAM UPDATE FAILURE\n"
			log.write(log_string, str(streamsData))
			log.close()
		log = open("log.txt", "a")
		print("LOGGING", "[" + str(time.ctime())[:-5] + "]" + " | STREAM UPDATE\n")
		log_string = "[" + str(time.ctime())[:-5] + "]" + " | STREAM UPDATE\n"
		log.write(log_string)
#        print(streams)
		for stream in streams:
			log.write(str(stream["stream"] + "\n"))
		log.close()
#        except:
#            print("stream pull failed")
		postedStreams = await mb.get_channel(NOTIFS_CHANNEL_ID).history(oldest_first = True).flatten()
		postedStreams = postedStreams[1:]
		for stream in postedStreams:
			postedStreamList.append(stream.content)
#        try:
		if streams != []:
#            config = loadConfig()
			for stream in streams:
				if stream["stream"] not in postedStreamList:
#                        if config[stream["#" + "stream".lower()]]["muted"] == False:
					responses.append(stream["stream"])
			streamsChannel = mb.get_channel(NOTIFS_CHANNEL_ID)
			if responses != "":
				for response in responses:
						await streamsChannel.send(response)
#        except:
#            print("Failed posting new streams")
		parsedStreams = []
		for stream in streams:
			parsedStreams.append(stream["stream"])
		await purgeNotStreams(parsedStreams)

async def purgeNotStreams(streams):
	### Removes any streams present in the #live-streams channel that are not in the current stream list

	flat = await mb.get_channel(NOTIFS_CHANNEL_ID).history(oldest_first=True).flatten() # returns a flattened ordered list of all present messages in the channel
#    await relayCountdown() # idek lol, think this is here because the channel could flicker if not checked before removal of streams
	oldestMessage = flat[0] # this identifies the top message, because it's used for ^ periodic messages
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

async def getPoints(pb, wr):
	### Returns the description field for the ".points" command
	### FIX: make this work either way, and with hours

	print("checking points", pb, wr)
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
	help_string = "Use like this: .points [pb]mm:ss [wr]mm:ss .\nIf you are comparing a full game, fit hours to minutes please.\n"
	print(str("Your PB of " + pb + " against "  + wr + " is worth " + str(points) + " points"))
	return(str(help_string + "Your PB of " + pb + " against "  + wr + " is worth " + str(points) + " points"))

async def lookForRecord():
	### Upon a new record being added to the HR database, this catches it by checking the API against the locally stored records
	### It then calls the announce() function to push it to the Discord channel

	while True:
		await asyncio.sleep(120) # Sleeps first, to avoid trying to perform an action before the bot is ready - there's certainly a better way to do this async stuff
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

#wackee's method
#def convertTimes(seconds): 
#	seconds = seconds % (24 * 3600) 
#	hour = seconds // 3600
#	seconds %= 3600
#	minutes = seconds // 60
#	seconds %= 60
#	if hour == 0:
#		if minutes == 00:
#			return ":%02d" % (seconds)
#		else:
#			return "%02d:%02d" % (minutes, seconds)
#	else:
#		return "%d:%02d:%02d" % (hour, minutes, seconds)

# Backflip's method
#Wackee - NOTE: unlikely, but wouldn't this break if there's over an hour timesave?
def convertTimes(seconds):
        return '%d:%02d' % (seconds // 60 if seconds > 60 else 0, seconds % 60)

def isCoop(record):
	return 'Co-op' if record["is_coop"] else 'Solo'

def findOldestRank(record):
	### Returns the rank describing how old the record is
	#Backflip's suggestion:
	#return len(list(filter(lambda pastRecord: pastRecord["timestamp"] <= record["timestamp"], requests.get(str(ENDPOINT + "records/oldest")).json()))) + 1
	try:
		recordsByOldest = requests.get(str(ENDPOINT + "records/oldest")).json()
		for index, item in enumerate(recordsByOldest, 1): # clever optional argument to help with ordinalizing
			if record["timestamp"] <= item["timestamp"]:
				return index
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

def getTimeStood(record, prev_record):
	secs = record["timestamp"] - prev_record["timestamp"]
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

	dt = datetime.datetime
	raceStartTime = dt(year=2020, month=8, day=25, hour=15)
	if ret == True:
		flat = await mb.get_channel(NOTIFS_CHANNEL_ID).history(oldest_first=True).flatten()
		now = dt.now()
		delta = raceStartTime - now
		return str(':'.join(str(delta).split(':')[:2])) + " until the HSL A1 Race begins!\nWatch [Here](https://www.twitch.tv/HaloRaces)"
	while True:
		await asyncio.sleep(10)
		if RACE==True:
			flat = await mb.get_channel(NOTIFS_CHANNEL_ID).history(oldest_first=True).flatten()
			now = dt.now()
			delta = raceStartTime - now
			oldestMessage = flat[0]            
			await oldestMessage.edit(content = str(':'.join(str(delta).split(':')[:2])) + " until the HSL A1 Race!")

# unnecessary? or old or bad idk

#def fixUrl(word):
#	newWord = "<" + word + ">"
#	return newWord

#def fixEscape(string):
#	decoded = bytes(string, "utf-8").decode("unicode_escape")
#	return decoded

#def un2(game):
#	if game == "Halo 2 MCC":
#		return "Halo: Master Chief Collection"
#	else:
#		return game

#async def getProfile(user):
#	return requests.get(str(ENDPOINT + "users/" + user)).json()
	
#def infoStream(stream):
#	splitStream = stream.split("\n")
#	print(splitStream)
#	streamEr = (" ").join(splitStream[0].split("is live!")[0])
#	streamGame = (" ").join(splitStream[1].split(" ")[1:])
#	streamTitle = splitStream[2]
#	print(streamEr, streamGame, streamTitle)
#	return (streamEr, streamGame, streamTitle)

#def streams(streams):
#	streamList = []
#	for stream in streams:
#		streamList.append(stream["stream"])
#	return streams

#def loadConfig():
#	file = json.load(open("config.json", "r+"))
#	return file

#def parseStream(stream):
#	val = URLValidator()
#	newTitleList = []
#	title = fixEscape(stream["title"])
#	print(title)
#	for word in stream["title"].split(" "):
#		try:
#			val(word)
#			newTitleList.append(fixUrl(word))
#		except:
#			newTitleList.append(word)
#	newTitle = " ".join(newTitleList)
#	streamParse = "%s is live!\nPlaying %s\n%s\n%s" % (stream["name"], un2(stream["game"]), newTitle, stream["stream"])
#	return streamParse

def buildPlayerMD(player):
	print(str("[%s](https://haloruns.com/profiles/%s)" % (player, player)))
	return str("[%s](https://haloruns.com/profiles/%s)" % (player, player))
	
def parsePlayers(record):
	players = []
	for player in record["runners"]:
		if player != None:
			players.append(buildPlayerMD(player))
	return " | ".join(players)

def parseIcon(record):
	iconDict = {
		"Halo CE":"<:CE:758288302738112543>",
		"Halo 2":"<:H2:758288302423277620>",
		"Halo 2 MCC":"<:H2:758288302423277620>",
		"Halo 3":"<:H3:758288302863941652>",
		"Halo 3: ODST":"<:ODST:758288303106555944>",
		"Halo: Reach":"<:Reach:758288303191228477>",
		"Halo 4":"<:H4:758288302985707531>",
		"Halo 5":"<:H5:758288303064612905>"
		}
	return iconDict[record['game_name']]



mb.loop.create_task(raceCountdown())
mb.loop.create_task(lookForRecord())
mb.loop.create_task(maintainTwitchNotifs())
mb.run(TOKEN)
