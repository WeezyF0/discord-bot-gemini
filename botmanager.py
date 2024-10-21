import configs.DefaultConfig as defaultConfig
import os
import utils.DiscordUtil as discordUtil
import asyncio
import discord
from cogs.GeminiCog import GeminiAgent
import requests
from discord.ext import commands
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import aiohttp
import logging
import yt_dlp
import os
import subprocess

# Locate ffmpeg
ffmpeg_path = subprocess.getoutput("which ffmpeg")
print(f"FFmpeg path: {ffmpeg_path}")


DISCORD_MAX_MESSAGE_LENGTH = 2000
logging.basicConfig(level=logging.INFO)

owner_id = defaultConfig.DISCORD_OWNER_ID
intents = discord.Intents.all()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


# For deployment on Render
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/healthz':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')


def run_health_check_server():
    port = int(os.getenv('PORT', '10000'))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()


def start_health_check_server():
    health_server_thread = threading.Thread(target=run_health_check_server)
    health_server_thread.daemon = True
    health_server_thread.start()


async def send_message_in_chunks(ctx, response):
    message = ""
    for chunk in response:
        message += chunk
        while len(message) > DISCORD_MAX_MESSAGE_LENGTH:
            extra_message = message[DISCORD_MAX_MESSAGE_LENGTH:]
            await ctx.send(message[:DISCORD_MAX_MESSAGE_LENGTH])
            message = extra_message
    if len(message) > 0:
        await ctx.send(message)


@bot.event
async def on_ready():
    logging.info("Bot is online...")


@bot.event
async def on_member_join(member):
    print("Hello Ji")
    guild = member.guild
    guildname = guild.name
    dmchannel = await member.create_dm()
    await dmchannel.send(f"Hello bbg, welcome to {guildname}, cg dilwade")


@bot.command(aliases=["about"])
async def help(ctx):
    MyEmbed = discord.Embed(
        title="Commands",
        description="These are the Commands that you can use for this bot. Once you are in a private message with the bot you can interact with it normally without issuing commands",
        color=discord.Color.dark_gold(),
    )
    MyEmbed.set_thumbnail(url="https://i.imgur.com/O250HqL.jpg")
    MyEmbed.add_field(
        name="!q",
        value="This command allows you to communicate with Gemini AI Bot on the Server. Please wrap your questions with quotation marks.",
        inline=False,
    )
    MyEmbed.add_field(
        name="!dm", value="This command allows you to private message the Gemini AI Bot.", inline=False
    )
    MyEmbed.add_field(
        name="!pfp", value="This command allows you to view the profile picture of the mentioned user.", inline=False
    )
    await ctx.send(embed=MyEmbed)


@bot.command()
@commands.check(discordUtil.is_me)
async def unloadGemini(ctx):
    await bot.remove_cog("GeminiAgent")


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
    if ctx.author.id == int(defaultConfig.DISCORD_OWNER_ID):  # basically the is_me function of DiscordUtil.py
        await ctx.send("Shutting down bot!")
        await bot.close()
    else:
        await ctx.send("He thinks he's him xD")


last_known_notices = None


async def check_and_send_notices(ctx):
    url = "https://dtu.ac.in/"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:  # Use `.get()` for the GET request

            if response.status == 200:  # Status code in aiohttp is `response.status`, not `response.status_code`
                response_text = await response.text()  # Use `.text()` to get the content
                soup = BeautifulSoup(response_text, "html.parser")
                latest_news_section = soup.find("div", class_="latest_tab")

                if latest_news_section:
                    notices = latest_news_section.find_all("li")[:5]

                    if notices:
                        global last_known_notices
                        current_notices_text = []

                        def clean_text(text):
                            return re.sub(r"\s+", " ", text).strip()  # Whitespace, newlines, and trailing spaces.

                        def extract_links(li_element):
                            links = []
                            for a_tag in li_element.find_all("a", href=True):
                                link_text = a_tag.get_text(strip=True)
                                link_url = a_tag["href"]
                                # Handle relative URLs
                                if not link_url.startswith("http"):
                                    link_url = urljoin(url, link_url)
                                links.append(f"[{link_text}]({link_url})")
                            return "\n".join(links)  # Use new lines to separate links

                        # Extract and clean notice texts and links
                        for index, notice in enumerate(notices):
                            notice_text = notice.get_text(separator=" ").replace("\xa0", " ")
                            links_text = extract_links(notice)
                            cleaned_text = clean_text(notice_text)
                            notice_entry = f"**{index + 1}.** {cleaned_text}"
                            if links_text:
                                notice_entry += f"\n{links_text}"  # Append links below the notice
                            current_notices_text.append(notice_entry)

                        # Join all notice texts
                        current_notices_text = "\n\n".join(current_notices_text)

                        # Check if the notices have changed
                        if current_notices_text != last_known_notices:
                            last_known_notices = current_notices_text
                            await send_message_in_chunks(ctx, current_notices_text)
                        else:
                            await ctx.send("No changes detected in the notices.")
                    else:
                        await ctx.send("No notices found.")
                else:
                    await ctx.send("Latest news section not found.")
            else:
                await ctx.send("Failed to fetch information from the website.")


@bot.command()
async def dtu(ctx):
    
    try:
        await check_and_send_notices(ctx)
    except Exception as e:
        logging.error(f"Error in website check: {e}")
        await ctx.send("An error occurred while checking the website.")


@bot.command()
async def convert(ctx, link: str, format: str = 'a'):
    dir = "tmp/downloads"
    
    # Ensure the directory exists
    if not os.path.exists(dir):
        os.makedirs(dir)
    
    # Change the directory to save the file
    os.chdir(dir)
    
    # Set options based on the chosen format
    if format == 'a':
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'ffmpeg_location': '/usr/bin/ffmpeg',  # Ensure ffmpeg is available
            'outtmpl': '%(title)s.%(ext)s'
        }
    else:
        ydl_opts = {
            'format': 'bv*+ba/b',
            'ffmpeg_location': 'ffmpeg.exe',
            'outtmpl': '%(title)s.%(ext)s'
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            file_name = ydl.prepare_filename(info)
            
            # Send the file if it's an audio download
            if format == 'a' and os.path.isfile(file_name):
                if os.path.getsize()< 8*1024*1024:
                    await ctx.send(file=discord.File(file_name))
                else:
                    await ctx.send("Imma figure this out later bro")
            else:
                await ctx.send("Download complete! Check your specified folder.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")




async def startcogs():
    await bot.add_cog(GeminiAgent(bot))


async def main():
    await startcogs()
    await bot.start(defaultConfig.DISCORD_SDK)

if __name__ == "__main__":
    start_health_check_server()
    asyncio.run(main())

