import discord
import pandas as pd
import re
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

TOKEN = os.getenv("DISCORD_TOKEN")  # Get the token from environment variable
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # Replace with your channel ID

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    channel = client.get_channel(CHANNEL_ID)
    data = []

    # Iterating through history
    async for message in channel.history(limit=500):
        if "cash received" in message.content:
            print(message.content)
            # Regex to find numbers after keywords
            rev = re.search(r"(?<=Total Revenue = ).*= \s*\$?\s*([\d,.]+)", message.content)
            exp = re.search(r"Total Expenses\s*=\s*\$?\s*([\d,.]+)", message.content)
            prof = re.search(r"Total Profit\s*=\s*\$?\s*([\d,.]+)", message.content)
            
            if rev and exp and prof:
                data.append({
                    "Date": message.created_at.strftime("%Y-%m-%d"),
                    "Revenue": rev.group(1),
                    "Expenses": exp.group(1),
                    "Profit": prof.group(1)
                })

    # Save to CSV (which can be imported to Google Sheets)
    df = pd.DataFrame(data)
    df.to_csv("thattu_kadda_reports.csv", index=False)
    print("Report compiled!")
    await client.close()

client.run(TOKEN)