import discord

client = discord.Client()

@client.event
async def on_message(message):
    message.content.lower()
    if message.author == client.user:
        return
    if message.content.startswith("hello"):
        await message.channel.send("eyy wahts up its me flethcer from whiplash")

@client.command()
async def play(ctx, url : str, channel):
    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name=channel)
client.run('OTk0NDgwODEyMjQ0MzU3MTMw.G_K0P4.AtTogBBDfvW5t0Q4h-zTH06v26rSKLpqjVD-as')
