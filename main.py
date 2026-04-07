import discord
import pandas as pd
import re
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

TOKEN = os.getenv("DISCORD_TOKEN")  # Get the token from environment variable
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # Replace with your channel ID

client = discord.Client(intents=discord.Intents.default())

def parse_multi_report_message(content, message_date):
    # 1. Split the message by the start of each event report
    # This assumes each report starts with something like "Thattu Kadda"
    reports = re.split(r'(?=Thattu [Kk]adda)', content)
    
    extracted_data = []

    for report in reports:
        if not report.strip():
            continue
            
        # 2. Extract specific numbers
        # Revenue: Grabs the number after the LAST equals sign in that section
        rev_match = re.search(r"Total Revenue.*?=\s*\$?\s*([\d,.]+)(?=\s|$)", report, re.DOTALL)
        exp_match = re.search(r"Total Expenses\s*=\s*\$?\s*([\d,.]+)", report)
        prof_match = re.search(r"Total Profit\s*=\s*\$?\s*([\d,.]+)", report)

        if rev_match or exp_match or prof_match:
            extracted_data.append({
                "Date": message_date,
                "Revenue": float(rev_match.group(1).replace(',', '')) if rev_match else 0.0,
                "Expenses": float(exp_match.group(1).replace(',', '')) if exp_match else 0.0,
                "Profit": float(prof_match.group(1).replace(',', '')) if prof_match else 0.0
            })
            
    return extracted_data

@client.event
async def on_ready():
    channel = client.get_channel(CHANNEL_ID)
    data = []

    # Iterating through history
    async for message in channel.history(limit=None):
        if "Total Revenue" in message.content:
            
            """
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
            """
            report_data = parse_multi_report_message(message.content, message.created_at.strftime("%Y-%m-%d"))
            for report in report_data:
                data.append(report)

    # Save to CSV (which can be imported to Google Sheets)
    df = pd.DataFrame(data)
    df.to_csv("thattu_kadda_reports.csv", index=False)
    print("Report compiled!")
    await client.close()

client.run(TOKEN)