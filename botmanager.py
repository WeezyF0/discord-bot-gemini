import configs.DefaultConfig as defaultConfig

import utils.DiscordUtil as discordUtil
import asyncio
import discord
from cogs.GeminiCog import GeminiAgent

from discord.ext import commands
owner_id= defaultConfig.DISCORD_OWNER_ID
intents= discord.Intents.all()
intents.message_content= True
intents.members= True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)



@bot.event
async def on_ready():
    print("Bot is online...")

@bot.event
async def on_member_join(member):
    print("Hello Ji")
    guild= member.guild
    guildname = guild.name
    dmchannel = await member.create_dm()
    await dmchannel.send(f"Hello bbg, welcome to {guildname}, cg dilwade")

@bot.command(aliases = ["about"])
async def help(ctx):
    MyEmbed = discord.Embed(title = "Commands",
                            description = "These are the Commands that you can use for this bot. Once you are in a private message with the bot you can interact with it normally without issuing commands",
                            color = discord.Color.dark_gold())
    MyEmbed.set_thumbnail(url = "https://i.imgur.com/O250HqL.jpg")
    MyEmbed.add_field(name = "!q", value = "This command allows you to communicate with Gemini AI Bot on the Server. Please wrap your questions with quotation marks.", inline = False)
    MyEmbed.add_field(name = "!dm", value = "This command allows you to private message the Gemini AI Bot.", inline = False)
    MyEmbed.add_field(name = "!pfp", value = "This command allows you to view the profile picture of the mentioned user.", inline = False)
    await ctx.send(embed = MyEmbed)

@bot.command()
@commands.check(discordUtil.is_me)
async def unloadGemini(ctx):
    await bot.remove_cog('GeminiAgent')

@bot.command()
@commands.check(discordUtil.is_me)
async def reloadGemini(ctx):
    await bot.add_cog(GeminiAgent(bot))

@bot.command()
async def pfp(ctx, user: discord.User):
    avatar_url = user.avatar.url

    Myembed = discord.Embed(title=f"Profile picture of {user}")
    Myembed.set_image(url=avatar_url)
    await ctx.send(embed=Myembed)

@bot.command()
async def shutdown(ctx):
    if ctx.author.id == int(defaultConfig.DISCORD_OWNER_ID):
        await ctx.send("Shutting down bot!")
        await bot.close()
    else:
        await ctx.send("He thinks he's him xD")




    


async def startcogs():
    await bot.add_cog(GeminiAgent(bot))

asyncio.run(startcogs())
bot.run(defaultConfig.DISCORD_SDK)


