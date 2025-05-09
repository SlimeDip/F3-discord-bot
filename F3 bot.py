import discord
import random
import time
import os
import asyncio
import asyncpraw
import requests
import io
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv


# Config
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USER_AGENT = os.getenv("USER_AGENT")
REDDIT = None
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.messages = True
intents.guild_messages = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

# f3ml
tracker = {
    "core": "",
    "exp": "",
    "gold": "",
    "mid": "",
    "roam": ""
}

blame_message = None
blame_thread = None

def format_board():
    return "\n".join(
        f"{role}: {tracker[role] if tracker[role] else ''}"
        for role in tracker
    )

async def shuffle_roles():
    assigned_players = [tracker[role] for role in tracker if tracker[role]]
    
    random.shuffle(assigned_players)
    
    i = 0
    for role in tracker:
        if tracker[role]:
            tracker[role] = assigned_players[i]
            i += 1

async def handle_fml(message):
    global blame_message, blame_thread
    
    if "f3ml" in message.content.lower():
        tracker.update({role: "" for role in tracker})
    
    if blame_message:
        await blame_message.edit(content=f"@everyone EMLEM!!!!!:\n\n{format_board()}")
    else:
        blame_message = await message.channel.send(f"@everyone EMLEM!!!!!:\n\n{format_board()}")
        blame_thread = await blame_message.create_thread(
            name="Emlem X-UP",
            auto_archive_duration=60
        )
        await blame_thread.send("Assign roles here by typing `x core`, `x exp`, etc. `x (role) out` to out. `shuffle` to randomize roles.")

async def xup(message):
    global blame_message
    
    if blame_thread and message.channel.id != blame_thread.id:
        return
        
    msg = message.content.lower()
    updated = False
    
    current_role = None
    for role in tracker:
        if tracker[role] == message.author.mention:
            current_role = role
            break
    
    for role in tracker:
        if f"x {role}" in msg:
            if tracker[role] == "":
                if current_role:
                    tracker[current_role] = ""
                tracker[role] = message.author.mention
                updated = True
    
    for role in tracker:
        if f"x {role} out" in msg:
            if message.author.mention == tracker[role]:
                tracker[role] = ""
                updated = True
                break
    
    if msg == "shuffle":
        await shuffle_roles()
        updated = True
    
    if updated and blame_message:
        await blame_message.edit(content=f"@everyone EMLEM!!!!!:\n\n{format_board()}")

# f3cf
async def coinflip(message):
    result = random.choice(["Heads", "Tails"])
    await message.channel.send(f":coin: Coin flip result: **{result}**!")

# f3abunis
async def abunis(message):
    if message.author.voice is None:
        await message.channel.send("You need to be in a voice channel to use this command.")
        return
    
    voice_channel = message.author.voice.channel
    voice_client = get(bot.voice_clients, guild=message.guild)

    if voice_client is None:
        voice_client = await voice_channel.connect()

    file_path = os.path.join(BASE_DIR, "audio", "abunis.mp3")

    if not voice_client.is_playing():
        audio_source = discord.FFmpegPCMAudio(file_path)
        voice_client.play(audio_source, after=lambda e: print(f"Finished playing: {e}"))
        await message.channel.send("Playing 'Isaw ni pinsan' by Abunis")
    else:
        await message.channel.send("Oi kalma, nagplaplay pa eh")

    while voice_client.is_playing():
        await asyncio.sleep(1)
    await voice_client.disconnect()

# f3wonhee
async def wonhee(message):
    num = str(random.randrange(0, 7))
    image_path = os.path.join(BASE_DIR, "images", f"Kurto{num}.jpg")
    file = discord.File(image_path)
    await message.channel.send(file=file)

# f3rate
async def rate(message):
    if len(message.mentions) == 0:
        await message.channel.send("Pls mention someone to rate")
        return
    
    user = message.mentions[0]
    ratings = random.randrange(0,11)

    bad_comments = [
        "Medyo burat.",
        "Mukhang bisaya.",
        "Bisakol masyado.",
        "Eto na yon?",
        "Di ko trip eh.",
        "No comment nalang.",
        "Haup na badtrip ako bigla."]
    
    good_comments = [
        "Pwede na.",
        "Masarap kahit walang ulam.",
        "Napaka angas.",
        "Krazy masyado."]

    if ratings < 7:
        comment = random.choice(bad_comments)
    else:
        comment = random.choice(good_comments)

    await message.channel.send(f"{user.mention} is {ratings}/10. {comment}")

# f3scatter
async def scatter(message):
    scatter = ""
    for i in range(4):
        for j in range(5):
            scatter += random.choices([":diamonds:", ":coin:"], weights=[90, 10])[0] + " "
        scatter += "\n"
    await message.channel.send(scatter)

    if scatter.count(":coin:") >= 3:
        await message.channel.send("Paldogs")
    else:
        await message.channel.send("Eguls")

# f3slots
async def slot(message):
    slots = []
    for i in range(3):
        slots.append(random.choices([":gem:", ":cherries:", ":bell:", ":seven:"])[0])
    await message.channel.send(" ".join(slots))

    if len(set(slots)) == 1:
        await message.channel.send("Paldogs")
    else:
        await message.channel.send("Eguls")

# f3gacha
async def gacha(message):
    character = random.choices(
        [":detective:", 
        ":health_worker:", 
        ":man_police_officer:", 
        ":judge:", 
        ":man_supervillain:", 
        ":man_mage:", 
        ":factory_worker:", 
        ":person_in_tuxedo:"], 
        weights=[5, 20, 20, 20, 5, 5, 5, 20])[0]

    rarity = {":detective:":5, 
            ":health_worker:":4, 
            ":man_police_officer:":4,
            ":judge:":4, 
            ":man_supervillain:":5, 
            ":man_mage:":5, 
            ":factory_worker:":5,
            ":person_in_tuxedo:":4}

    msggg = await message.channel.send(":sparkles:")
    await asyncio.sleep(0.5)
    await msggg.edit(content=":sparkles: :sparkles:")
    await asyncio.sleep(0.5)
    await msggg.edit(content=":sparkles: :sparkles: :sparkles:")
    await asyncio.sleep(0.5)
    if rarity[character] == 5:
        await msggg.edit(content=":sparkles: :sparkles: :sparkles: :star2:")
        await asyncio.sleep(0.5)
    await msggg.edit(content=character)
    await message.channel.send(f"{rarity[character]} star character")

# f3r/
async def reddit(message):
    global REDDIT
    
    if REDDIT is None:
        REDDIT = asyncpraw.Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            user_agent=USER_AGENT,
        )

    subreddit_name = message.content.split("/")[1].strip()

    if not subreddit_name:
        await message.channel.send("Please enter a subreddit name")
        return

    msggg = await message.channel.send("Loading...")

    try:
        subreddit = await REDDIT.subreddit(subreddit_name)
        posts = [post async for post in subreddit.top(time_filter="week", limit=10)]

        if not posts:
            await message.channel.send(f"No memes found in r/{subreddit_name}")
            return

        random.shuffle(posts)

        for post in posts:
            if post.url.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                try:
                    response = requests.get(post.url, stream=True)
                    if response.status_code == 200:
                        image_data = io.BytesIO(response.content)
                        image_data.seek(0)

                        file = discord.File(image_data, filename=f"{post.id}{os.path.splitext(post.url)[1]}")

                        await msggg.edit(content = post.title)
                        await message.channel.send(file=file)
                        return

                except Exception as e:
                    await message.channel.send(f"Error getting the post {post.url}: {str(e)}")
    except Exception as e:
        await message.channel.send(f"Failed to access subreddit: {str(e)}")

# f3askme
async def askme(message):
    global REDDIT
    
    if REDDIT is None:
        REDDIT = asyncpraw.Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            user_agent=USER_AGENT,
        )

    try:
        subreddit = await REDDIT.subreddit("AskReddit")
        posts = [post async for post in subreddit.top(time_filter="week", limit=10)]

        if not posts:
            await message.channel.send(f"Cant find questions")
            return

        post = random.choices(posts)[0]
        await message.channel.send(post.title)

    except Exception as e:
        await message.channel.send(f"Failed to gather questions: {str(e)}")
        return

# Features
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    global blame_message, blame_thread

    if message.author == bot.user:
        return

    msg = message.content.lower()

    if msg.strip() == "f3help":
        blame_message = await message.channel.send(
            "**List of available commands:**\n\n"
            "***f3ml*** - launch ml x up thread\n"
            "***f3cf*** - coin flip\n"
            "***f3abunis*** - isaw ni pinsan\n"
            "***f3wonhee*** - made for kurto\n"
            "***f3rate <mention>*** - rate someone\n"
            "***f3scatter*** - sugal na scatter\n"
            "***f3slots*** - casino slots\n"
            "***f3gacha*** - character gacha\n"
            "***f3r/<subreddit>*** - reddit post\n"
            "***f3askme*** - random questions"
            )

    # f3ml
    if msg.strip() == "f3ml":
        await handle_fml(message)
        return
    if blame_thread and message.channel.id == blame_thread.id:
        await xup(message)

    # f3cf
    if msg.strip() == "f3cf":
        await coinflip(message)
        return
    
    # f3abunis
    if msg.strip() == "f3abunis":
        await abunis(message)
        return
    
    # f3wonhee
    if msg.strip() == "f3wonhee":
        await wonhee(message)
        return
    
    # f3rate
    if msg.startswith("f3rate"):
        await rate(message)
        return
    
    # f3scatter
    if msg.strip() == "f3scatter":
        await scatter(message)
        return

    # f3slots
    if msg.strip() == "f3slots":
        await slot(message)
        return
    
    # f3gacha
    if msg.strip() == "f3gacha":
        await gacha(message)
        return
    
    # f3r/
    if msg.startswith("f3r/"):
        await reddit(message)
        return
    
    # f3askme
    if msg.strip() == "f3askme":
        await askme(message)
        return

    await bot.process_commands(message)

# run
bot.run(TOKEN)
