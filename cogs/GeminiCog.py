import configs.DefaultConfig as defaultConfig
import utils.DiscordUtil as discordUtil
from discord.ext import commands
import google.generativeai as genai
import discord
import asyncio


genai.configure(api_key=defaultConfig.GEMINI_SDK)
DISCORD_MAX_MESSAGE_LENGTH=2000
PLEASE_TRY_AGAIN_ERROR_MESSAGE='Message chota kar lodu. Max length 2000 characters'

class GeminiAgent(commands.Cog):
    def __init__(self, bot):
        self.bot= bot
        self.model= genai.GenerativeModel('gemini-2.0-flash')

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.content == 'ping gemini-agent':
                await message.channel.send("Agent is connected...")
            elif 'Direct Message' in str(message.channel) and not message.author.bot:
                response = self.gemini_generate_content(message.content)
                dmchannel = await message.author.create_dm()
                await self.send_message_in_chunks(dmchannel,response) 
        except Exception as e:
            return PLEASE_TRY_AGAIN_ERROR_MESSAGE + str(e)


    @commands.command()
    async def q(self, ctx, question):
        try:
            async with ctx.typing():
                response = self.gemini_generate_content(question)
                await asyncio.sleep(2)
            await self.send_message_in_chunks(ctx, response)
        except Exception as e:
            return PLEASE_TRY_AGAIN_ERROR_MESSAGE + str(e)

    @commands.command()
    async def dm(self, ctx):
        dmchannel = await ctx.author.create_dm()
        async with dmchannel.typing():
                await asyncio.sleep(2) 
        await dmchannel.send("Wsg, How may I assist you today?")

    def gemini_generate_content(self, content):
        try:
            return self.model.generate_content(content, stream=True)
        except Exception as e:
            return PLEASE_TRY_AGAIN_ERROR_MESSAGE + str(e)

    async def send_message_in_chunks(self, ctx, response):
        message = ""
        for chunk in response:
            message += chunk.text
            if len(message) > DISCORD_MAX_MESSAGE_LENGTH:
                extraMessage = message[DISCORD_MAX_MESSAGE_LENGTH:]
                message = message[:DISCORD_MAX_MESSAGE_LENGTH]
                await ctx.send(message)
                message = extraMessage
        if len(message) > 0:
            while len(message) > DISCORD_MAX_MESSAGE_LENGTH:
                extraMessage = message[DISCORD_MAX_MESSAGE_LENGTH:]
                message = message[:DISCORD_MAX_MESSAGE_LENGTH]
                await ctx.send(message)
                message = extraMessage
            await ctx.send(message)


