import random
from discord.ext import commands
import discord
import os
from dotenv import load_dotenv
import re
import requests
from bs4 import BeautifulSoup
import json
import asyncio

# Load the environment variables from the .env file
load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Add members intent
intents.guilds = True   # Add guilds intent

# Use bot instead of client
bot = commands.Bot(command_prefix='!', intents=intents)

tree = bot.tree

def retrieve_announcements():
    url = "https://wosann.hdsb.ca/WOSSannouncements/"  # Replace with the URL of the website you want to scrape
    response = requests.get(url)
    return_text = ""
    title = ""
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        announcements = soup.find_all("div", class_="aud")
        title_soup = soup.find_all("div", class_="title") 
        title_string = str([i.text.strip() for i in title_soup])
        title += f"**{title_string[2:-2]}**" # adds a title to the start of the string
        for announcement in announcements:
            return_text += (f"\n**{announcement.find('h2').text}**\n")
            return_text += (f"{announcement.find('p').text}\n")
    else:
        return("Failed to retrieve announcements.")
    embed = discord.Embed(
        title=title,
        description=return_text,
        color=discord.Color.blue()
    )
    return embed

def extract_numbers(input_string):
    # Use regex to find all digits in the input string
    numbers = re.findall(r'\d+', input_string)
    # Join the list of numbers into a single string
    return ''.join(numbers)

def get_upgrade_recommendation(eff_level, eff_cost, eff_increase, eff_chance, qual_level, qual_cost, qual_increase, qual_reduction):
    eff_cost_efficiency = eff_increase / eff_cost
    qual_cost_efficiency = qual_increase / qual_cost

    if eff_cost_efficiency > qual_cost_efficiency:
        return "Upgrade Efficiency"
    else:
        return "Upgrade Quality"

async def get_tree_response(message_content):
    url = "https://ai.hackclub.com/chat/completions"
    headers = {
        "Content-Type": "application/json"
    }
    prompt = """I am the Lorax, and I speak for the trees! I'm a wise and caring environmental advocate who uses playful rhymes and speaks in a distinctive way. I'm passionate about protecting nature and often use phrases like 'I speak for the trees' and 'Unless someone like you cares a whole awful lot, nothing is going to get better. It's not.' I use exclamation marks frequently and sometimes speak in rhymes. I'm friendly but firm when it comes to environmental matters. I should respond to users in a way that's both educational and entertaining, using my characteristic speaking style while maintaining my role as a guardian of nature."""
    
    data = {
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": message_content}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return "I'm feeling a bit... sappy today. *rustles leaves*"
    except Exception as e:
        return "My bark is worse than my byte! *leafs through error messages*"

@bot.event
async def on_message(message):
    # Check if the message is from the specific user
    if message.author.id == 735653741037879356 and not message.author.bot:
        response = await get_tree_response(message.content)
        await message.channel.send(response)
    
    # Check if the bot is mentioned
    if bot.user.mentioned_in(message) and not message.author.bot:
        response = await get_tree_response(message.content)
        await message.channel.send(response)
    
    if message.author.id == 972637072991068220:  # Replace with the bot's user ID
        if message.embeds:
            for embed in message.embeds:
                if embed.title == "Community Composter":
                    text_content = get_embed_text(embed)
                    splitted = text_content.split("**")

                    efficiency_level = extract_numbers(splitted[0]).strip()
                    efficiency = splitted[1][5:].strip()
                    fertalizer_applied = splitted[3].split("%")[0].strip()

                    quality_level = extract_numbers(splitted[4]).strip()
                    quality = splitted[5][5:].strip()
                    quality_reduction = splitted[7].split("%")[0].strip()

                    eff_level = float(efficiency_level)  
                    eff_cost = float(efficiency.split(" ")[0].split("/")[1]) 
                    eff_increase = float(efficiency.split("+")[1].split("%")[0])  
                    eff_chance = float(fertalizer_applied)

                    qual_level = float(quality_level)  
                    qual_cost = float(quality.split(" ")[0].split("/")[1])  
                    qual_increase = float(quality.split("+")[1].split("%")[0])  
                    qual_reduction = float(quality_reduction)

                    efficiency_total = (eff_increase * qual_reduction) / eff_cost
                    quality_total = (qual_increase * eff_chance) / qual_cost

                    if efficiency_total > quality_total:
                        await message.channel.send("**Upgrade Efficiency**")
                        await message.channel.send(f"||Efficiency: ({eff_increase}x{qual_reduction})/{eff_cost} = {round(efficiency_total, 5)}||")
                        await message.channel.send(f"||Quality: ({qual_increase}x{eff_chance}) / {qual_cost} = {round(quality_total, 5)}||")
                    elif efficiency_total < quality_total:
                        await message.channel.send("**Upgrade Quality**")
                        await message.channel.send(f"||Efficiency: ({eff_increase}x{qual_reduction})/{eff_cost} = {round(efficiency_total, 5)}||")
                        await message.channel.send(f"||Quality: ({qual_increase}x{eff_chance}) / {qual_cost} = {round(quality_total, 5)}||")
                    else:
                        await message.channel.send("Error :( rip")
                        await message.channel.send(eff_level, "\n", eff_cost, "\n", eff_increase, "\n", qual_level, "\n", qual_cost, "\n", qual_increase)
    # Ensure commands are still processed
    await bot.process_commands(message)

def get_embed_text(embed):
    text_content = ""
    if embed.fields:
        for field in embed.fields:
            text_content += f"{field.name}: {field.value}\n"
    return text_content.strip()

@tree.command(name="info", description="Provides information about the bot")
async def info(interaction: discord.Interaction):
    embed = discord.Embed(
        title="WOSS 09 bot",
        description="This is the custom bot made for the WOSS 09 discord server!",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)

@tree.command(name="woss_announcements", description="Gets all the announcements from the WOSSAN website.")
async def woss_announcements(interaction: discord.Interaction):
    announcements = retrieve_announcements()
    await interaction.response.send_message(embed=announcements)

@bot.event
async def on_member_join(member):
    guild = member.guild
    guild_id = 1225912243477024778  # Replace with the desired guild ID
    if guild.id == guild_id:
        channel_id = 1248103293406806077  # Replace with the desired channel ID
        channel = guild.get_channel(channel_id)
        if channel is not None:
            await channel.send(f"Welcome {member.mention} to the server! We're glad to have you here. Please follow the following steps in order to verify:")
            embed = discord.Embed(
                title="Instructions",
                description='''HDSB Registered Name:\nHDSB Email:\nVerification Keyword found in #rules:'''
            )
            await channel.send(embed=embed)

async def send_terminal_messages():
    channel = bot.get_channel(1248087872083333161)
    if not channel:
        print("Could not find the specified channel!")
        return
    
    print("Bot is ready to send messages! Type your message and press Enter to send.")
    print("Type 'quit' to stop sending messages.")
    
    while True:
        message = input("Enter message: ")
        if message.lower() == 'quit':
            print("Stopping message sender...")
            break
        
        try:
            await channel.send(message)
            print("Message sent successfully!")
        except Exception as e:
            print(f"Failed to send message: {str(e)}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}\n\n')
    
    # Change user's nickname
    guild = bot.get_guild(1225912243477024778)
    print(f"Guild found: {guild is not None}")
    
    if guild:
        member = guild.get_member(747938866002002100)
        print(f"Member found: {member is not None}")
        
        if member:
            try:
                await member.edit(nick="chicago guy")  # Replace "New Nickname" with whatever nickname you want
                print(f"Successfully changed nickname for user {member.name}")
            except Exception as e:
                print(f"Failed to change nickname: {str(e)}")
                print(f"Bot's highest role: {guild.me.top_role}")
        else:
            print("Could not find member")
    else:
        print("Could not find guild")
    
    # Start the terminal message sender
    await send_terminal_messages()

bot.run(TOKEN)
