import asyncio

import discord
from discord.ext import commands
import DiscordUtils
import helper
import json

# get token and prefix from config.json file (not on git)
with open('config.json') as f:
    data = json.load(f)
    token = data["token"]
    prefix = data["prefix"]

# create the bot and music
bot = commands.AutoShardedBot(command_prefix=prefix)
music = DiscordUtils.Music()

# add the helper cog to the bot to use helper functions
bot.add_cog((helper.HelperCog()))
helperCog = bot.get_cog('HelperCog')



# joins the user's voice channel
@bot.command()
async def join(ctx):
    await helperCog.connected_and_verified(ctx, bot)


# leave the bots current voice channel, if user is also in voice channel
@bot.command()
async def leave(ctx):
    user = ctx.message.author
    # check if the user is in the same voice channel as the bot
    if await helperCog.is_connected(ctx, bot) and user.voice.channel != ctx.guild.voice_client.channel:
        await ctx.send("You're not in my channel!")
    # user and bot are in the same channel, so disconnect
    elif await helperCog.is_connected(ctx, bot):
        await ctx.voice_client.disconnect()
        player = music.get_player(guild_id=ctx.guild.id)
        if player:
            player.delete()
    # bot is not in any voice channel
    else:
        await ctx.send("I'm not in a voice channel!")


# join the users voice channel if needed and play requested music
# takes in either a YouTube url or title to search in YouTube
@bot.command()
async def play(ctx, *, url):
    # join users voice channel if possible
    connected = await helperCog.connected_and_verified(ctx, bot)
    if not connected:
        return

    # create a player if needed and play/queue song
    player = music.get_player(guild_id=ctx.guild.id)
    if not player:
        player = music.create_player(ctx, ffmpeg_error_betterfix=True)

    # if nothing is currently playing then play the song
    if not ctx.voice_client.is_playing():
        await player.queue(url, search=True)
        song = await player.play()
        await ctx.send(f"Playing {song.name}")

    # if something is currently playing then add the song to the queue
    else:
        song = await player.queue(url, search=True)
        await ctx.send(f"Queued {song.name}")


# pause the current song
@bot.command()
async def pause(ctx):
    player = music.get_player(guild_id=ctx.guild.id)

    # if no song is currently playing then we don't need to pause
    if not ctx.voice_client.is_playing() or not await helperCog.song_playing(player):
        await ctx.send("Nothing is playing!")

    # pause the currently playing song
    else:
        song = await player.pause()
        await ctx.send(f"Paused {song.name}")


# resume a paused song
@bot.command()
async def resume(ctx):
    player = music.get_player(guild_id=ctx.guild.id)

    # if a song is currently playing then we can't resume
    if ctx.voice_client.is_playing():
        await ctx.send("Already playing!")

    # if a song is paused then resume
    elif await helperCog.song_playing(player):
        song = await player.resume()
        await ctx.send(f"Resumed {song.name}")

    # if there is no song playing or paused then we can't resume
    else:
        await ctx.send("Nothing is playing!")


#
@bot.command()
async def stop(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    if not ctx.voice_client.is_playing() or not await helperCog.song_playing(player):
        await ctx.send("Nothing is playing!")
    else:
        await player.stop()
        await ctx.send("Stopped")


@bot.command()
async def loop(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    if not await helperCog.song_playing(player) or not ctx.voice_client.is_playing():
        await ctx.send("Nothing is playing!")
        return
    song = await player.toggle_song_loop()
    if song.is_looping:
        await ctx.send(f"Looping {song.name}")
    else:
        await ctx.send(f"Stopped looping {song.name}")


@bot.command()
async def queue(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    if player is not None and len(player.current_queue()) > 0:
        await ctx.send(f"{', '.join([song.name for song in player.current_queue()])}")
    else:
        await ctx.send("Nothing in queue!")


@bot.command()
async def current(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    if await helperCog.song_playing(player):
        song = player.now_playing()
        await ctx.send(song.name)
    else:
        await ctx.send("Nothing is playing!")


# skips the current song
@bot.command()
async def skip(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    if await helperCog.song_playing(player):
        await player.skip(force=True)
        await ctx.send(f"Skipping {player.now_playing().name}")
    else:
        await ctx.send("Nothing is playing!")



@bot.command()
async def remove(ctx, index):
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.remove_from_queue(int(index))
    await ctx.send(f"Removed {song.name} from queue")


@bot.command()
async def command_list(ctx):
    await ctx.send(prefix + "join will make me join your voice channel. \n" +
                   prefix + "leave will make me leave my current voice channel. \n" +
                   prefix + "play (title or URL) will play the requested song. \n" +
                   prefix + "stop will stop all music \n" +
                   prefix + "pause will pause the current song. \n" +
                   prefix + "resume will resume the current song \n" +
                   prefix + "skip will skip the current song. \n" +
                   prefix + "loop will loop or un-loop the current song \n" +
                   prefix + "current will display the song currently playing \n" +
                   prefix + "queue will display the current song queue.\n" +
                   prefix + "remove (index) will remove the song at that index from the queue")


@bot.event
async def on_voice_state_update(member, before, after):
    if not member.id == bot.user.id:
        return

    elif before.channel is None:
        voice = after.channel.guild.voice_client
        time = 0
        while True:
            await asyncio.sleep(1)
            time = time + 1
            if voice.is_playing() and not voice.is_paused():
                time = 0
            if time == 120:
                await voice.disconnect()
                player = music.get_player(guild_id=after.channel.guild.id)
                if player:
                    player.delete()
            if not voice.is_connected():
                break
bot.run(token)
