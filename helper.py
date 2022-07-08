import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import DiscordUtils
from discord.ext import commands


class HelperCog(commands.Cog):
    def __init__(self):
        return

    @commands.command()
    async def is_connected(self, ctx, bot):
        voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        return voice and voice.is_connected()

    @commands.command()
    async def connected_and_verified(self, ctx, bot):
        user = ctx.message.author
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        # case where bot isn't connected to voice channel
        if not await self.is_connected(ctx, bot):
            await ctx.author.voice.channel.connect()
            await ctx.send(f"Joined **{user.voice.channel}**")
            return True
        # case where bot is in a different voice channel
        elif await self.is_connected(ctx, bot) and user.voice.channel != ctx.guild.voice_client.channel:
            await ctx.send(f"I'm in {ctx.guild.voice_client.channel} right now.")
            return False
        # case where bot is already in the same voice channel as user
        else:
            return True

    @commands.command()
    async def song_playing(self, player):
        return player is not None and player.now_playing() is not None
