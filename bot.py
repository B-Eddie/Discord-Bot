import random
import discord
import os
from dotenv import load_dotenv
import re

# Load the environment variables from the .env file
load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

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

# Event to handle incoming messages
@client.event
async def on_message(message):
    if message.author.id == 972637072991068220:  # Replace YOUR_USER_ID with the bot's user ID
        if message.embeds:
            for embed in message.embeds:
                if embed.title == "Community Composter":
                    text_content = get_embed_text(embed)
                    # print(text_content)
                    splitted = text_content.split("**")


                    efficiency_level = extract_numbers(splitted[0]).strip()
                    efficiency = splitted[1][5:].strip()
                    fertalizer_applied = splitted[3].split("%")[0].strip()

                    quality_level = extract_numbers(splitted[4]).strip()
                    quality = splitted[5][5:].strip()
                    quality_reduction = splitted[7].split("%")[0].strip()


                    #print(efficiency, "\n\n", fertalizer_applied, "\n\n", quality, "\n\n", quality_reduction)

                    # Parse the embed content (this is just an example, parsing needs to be accurate as per actual embed structure)
                    eff_level = float(efficiency_level)  # Replace with actual parsing logic
                    eff_cost = float(efficiency.split(" ")[0].split("/")[1]) # Replace with actual parsing logic
                    eff_increase = float(efficiency.split("+")[1].split("%")[0])  # Replace with actual parsing logic
                    eff_chance = float(fertalizer_applied)  # Replace with actual parsing logic

                    qual_level = float(quality_level)  # Replace with actual parsing logic
                    qual_cost = float(quality.split(" ")[0].split("/")[1])  # Replace with actual parsing logic
                    qual_increase = float(quality.split("+")[1].split("%")[0])  # Replace with actual parsing logic
                    qual_reduction = float(quality_reduction)  # Replace with actual parsing logic

                    efficiency_total = (eff_increase * qual_reduction) / eff_cost
                    quality_total = (qual_increase * eff_chance) / qual_cost


                    print(f"({eff_increase}x{qual_reduction})/{eff_cost}")
                    print(f"({qual_increase}x{eff_chance}) / {qual_cost}")
                    # print(eff_level, "\n", eff_cost, "\n", eff_increase, "\n", qual_level, "\n", qual_cost, "\n", qual_increase)
                    # print(eff_chance, "\n", qual_reduction)
                    # recommendation = get_upgrade_recommendation(eff_level, eff_cost, eff_increase, eff_chance, qual_level, qual_cost, qual_increase, qual_reduction)

                    #print(f"Recommendation: {recommendation}")
                    if efficiency_total > quality_total:
                        await message.channel.send("**Upgrade Efficiency**")
                        await message.channel.send(f"||Efficiency: ({eff_increase}x{qual_reduction})/{eff_cost} = {round(efficiency_total, 5)}||")
                        await message.channel.send(f"||Quality: ({qual_increase}x{eff_chance}) / {qual_cost} = {round(quality_total, 5)}||")
                    elif  efficiency_total < quality_total:
                        await message.channel.send("**Upgrade Quality**")
                        await message.channel.send(f"||Efficiency: ({eff_increase}x{qual_reduction})/{eff_cost} = {round(efficiency_total, 5)}||")
                        await message.channel.send(f"||Quality: ({qual_increase}x{eff_chance}) / {qual_cost} = {round(quality_total, 5)}||")
                    else:
                        await message.channel.send("Error :( rip")
                        await message.channel.send(eff_level, "\n", eff_cost, "\n", eff_increase, "\n", qual_level, "\n", qual_cost, "\n", qual_increase)
                    # await message.channel.send("```css\n [im a real bot now]```") blue text
                    
                    # GUILD_ID = 1242531256949014689  # replace with your guild ID
                    # USER_ID = 882679657881812993   # replace with the user ID to kick
                    # guild = await client.fetch_guild(GUILD_ID)
                    # role = discord.utils.get(guild.roles, name="perms")
                    # await guild.get_member(USER_ID).add_roles(role)
                    # await (await client.fetch_guild(GUILD_ID)).kick(await client.fetch_user(USER_ID));
                    
                    # invite = await (await client.fetch_channel(1225912244953415745)).create_invite(max_uses=5)
                    # print(invite)
                

                    # GUILD_ID = 1225912243477024778  # Replace with your guild ID
                    # # USER_ID = 1237906707125112875   # Replace with the user ID to unban
                    # guild = client.get_guild(GUILD_ID)
                    # # Fetch the guild object
                    # banned_users = []
                    # async for ban_entry in guild.bans():
                    #     banned_users.append(ban_entry.user)
                    
                    # # Iterate through the banned users and unban the specified user
                    # for user in banned_users:
                    #     if user.id == USER_ID:
                    #         await guild.unban(user)
                    #         print(f"User with ID {USER_ID} has been unbanned.")
                    #         break

                    # guild = client.get_guild(GUILD_ID)

                    # Fetch and print the moderation logs
                    # async for entry in guild.audit_logs(limit=50):
                    #     print(f"User: {entry.user}, Action: {entry.action}, Target: {entry.target}, Time: {entry.created_at}")







def get_embed_text(embed):
    text_content = ""
    # if embed.title:
    #     text_content += f"Title: {embed.title}\n"
    #     print(embed.title)
    #if embed.description:
        # text_content += f"Description: {embed.description}\n"
    if embed.fields:
        for field in embed.fields:
            text_content += f"{field.name}: {field.value}\n"
    return text_content.strip()

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}\n\n')

client.run(TOKEN)
