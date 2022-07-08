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

bot = commands.AutoShardedBot(command_prefix=prefix)
music = DiscordUtils.Music()

bot.add_cog((helper.HelperCog()))
helperCog = bot.get_cog('HelperCog')


@bot.command()
async def join(ctx):
    await helperCog.connected_and_verified(ctx, bot)


@bot.command()
async def leave(ctx):
    user = ctx.message.author
    if await helperCog.is_connected(ctx, bot) and user.voice.channel != ctx.guild.voice_client.channel:
        await ctx.send("You're not in my channel!")
    elif await helperCog.is_connected(ctx, bot):
        await ctx.voice_client.disconnect()
        player = music.get_player(guild_id=ctx.guild.id)
        if player:
            player.delete()
    else:
        await ctx.send("I'm not in a voice channel!")


@bot.command()
async def play(ctx, *, url):
    connected = await helperCog.connected_and_verified(ctx, bot)
    if not connected:
        return

    # create a player if needed and play/queue song
    player = music.get_player(guild_id=ctx.guild.id)
    if not player:
        player = music.create_player(ctx, ffmpeg_error_betterfix=True)
    if not ctx.voice_client.is_playing():
        await player.queue(url, search=True)
        song = await player.play()
        await ctx.send(f"Playing {song.name}")
    else:
        song = await player.queue(url, search=True)
        await ctx.send(f"Queued {song.name}")


@bot.command()
async def pause(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    if not ctx.voice_client.is_playing() or not await helperCog.song_playing(player):
        await ctx.send("Nothing is playing!")
    else:
        song = await player.pause()
        await ctx.send(f"Paused {song.name}")


@bot.command()
async def resume(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    if ctx.voice_client.is_playing():
        await ctx.send("Already playing!")
    elif await helperCog.song_playing(player):
        song = await player.resume()
        await ctx.send(f"Resumed {song.name}")
    else:
        await ctx.send("Nothing is playing!")


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

bot.run(token)
