#import configparser

#config = configparser.ConfigParser()

#config.read('config.ini')


#DISCORD_OWNER_ID = config['DEFAULT']['discord_owner_id']
#DISCORD_SDK = config['DEFAULT']['discord_sdk']
#GEMINI_SDK = config['DEFAULT']['gemini_sdk']
# Import the necessary module
from dotenv import load_dotenv
import os

# Load environment variables from the .env file (if present)
load_dotenv()

# Access environment variables as if they came from the actual environment
DISCORD_OWNER_ID = os.getenv('discord_owner_id')
DISCORD_SDK = os.getenv('discord_sdk')
GEMINI_SDK= os.getenv('gemini_sdk')
