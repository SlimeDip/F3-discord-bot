import discord
import random
import os
import asyncio
import asyncpraw
import requests
import io
import json
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
intents.reactions = True
bot = commands.Bot(command_prefix="!", intents=intents)

# SAVES
scatter_highscores = {}
owned_characters = {}

def save_scatter_highscores():
    with open(os.path.join(BASE_DIR, "data", "scatter_highscores.json"), "w") as f:
        json.dump(scatter_highscores, f)

def save_owned_characters():
    with open(os.path.join(BASE_DIR, "data", "owned_characters.json"), "w") as f:
        json.dump(owned_characters, f)

def load_scatter_highscores():
    global scatter_highscores
    try:
        with open(os.path.join(BASE_DIR, "data", "scatter_highscores.json"), "r") as f:
            scatter_highscores = json.load(f)
    except FileNotFoundError:
        scatter_highscores = {}

def load_owned_characters():
    global owned_characters
    try:
        with open(os.path.join(BASE_DIR, "data", "owned_characters.json"), "r") as f:
            owned_characters = json.load(f)
    except FileNotFoundError:
        owned_characters = {}

load_scatter_highscores()
load_owned_characters()

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
    play = 9
    total = 0

    scatter = ":regional_indicator_l: :regional_indicator_o: :regional_indicator_a: :regional_indicator_d: :regional_indicator_i: :regional_indicator_n: :regional_indicator_g: "
    scattervar = await message.channel.send(scatter)
    
    while play > -1:
        earned = 0
        scatter = ""
        for i in range(5):
            for _ in range(5):
                scatter += random.choices([":diamonds:",":heart:", ":spades:", ":clubs:", ":coin:"], weights=[24, 24, 24, 24, 2])[0] + " "
            scatter += "\n"
            if (i == 4):
                scatter += f"\nRounds: {play}\n"

        if scatter.count(":diamonds:") >= 5:
            earned += scatter.count(":diamonds:")

        if scatter.count(":heart:") >= 5:
            earned += scatter.count(":heart:")

        if scatter.count(":spades:") >= 5:
            earned += scatter.count(":spades:")

        if scatter.count(":clubs:") >= 5:
            earned += scatter.count(":clubs:")

        if scatter.count(":coin:") >= 3:
            play += 10
            scatter += "+ 10 for getting 3 or more coins\n"

        total += earned
        scatter += f"+ {earned} points"
        play -= 1
        await asyncio.sleep(1)
        await scattervar.edit(content=scatter)

    scatter += f"\n\nRound over... Total points earned: {total}"

    user_id = str(message.author.id)
    prev_score = scatter_highscores.get(user_id, 0)

    if total > prev_score:
        scatter_highscores[user_id] = total
        save_scatter_highscores()
        scatter += f"\nNew highscore!"

    scatter += f"\nYour highscore: {scatter_highscores.get(user_id, total)}"

    await scattervar.edit(content=scatter)               

# f3slots
async def slot(message):
    slots = []
    user_id = str(message.author.id)
    for _ in range(3):
        slots.append(random.choices([":gem:", ":cherries:", ":bell:", ":seven:"])[0])
    await message.channel.send(" ".join(slots))

    if len(set(slots)) == 1:
        await message.channel.send("Paldogs")
    else:
        await message.channel.send("Eguls")

# f3gacha
async def gacha(message):
    user_id = str(message.author.id)

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

    for i in range(1,3):
        await asyncio.sleep(0.5)
        await msggg.edit(content=":sparkles:" * (i + 1))

    await asyncio.sleep(0.5)

    if rarity[character] == 5:
        await msggg.edit(content=":sparkles: :sparkles: :sparkles: :star2:")
        await asyncio.sleep(0.5)

    if user_id not in owned_characters:
        owned_characters[user_id] = {}

    if character in owned_characters[user_id]:
        owned_characters[user_id][character] += 1
    else:
        owned_characters[user_id][character] = 1

    save_owned_characters()

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

# f3characters
async def view_characters(message):
    user_id = str(message.author.id)
    characters = owned_characters.get(user_id, {})

    if not characters:
        await message.channel.send("You don't own any characters yet.")
        return

    character_list = "\n".join([f"{char}: {count}" for char, count in characters.items()])
    await message.channel.send(f"Your owned characters:\n{character_list}")

# f3leaderboard
async def leaderboard(message):
    global scatter_highscores

    if not scatter_highscores:
        await message.channel.send("No data available.")
        return

    sorted_scatter = sorted(scatter_highscores.items(), key=lambda x: x[1], reverse=True)
    leaderboard_msg = "\n**Scatter Highscores:**\n"
    for i, (user_id, score) in enumerate(sorted_scatter[:5], start=1):
        user = await bot.fetch_user(int(user_id))
        leaderboard_msg += f"{i}. {user.name}: {score}\n"

    await message.channel.send(leaderboard_msg)

# f3colorgame
async def colorgame(message):
    colors = {
        "🔴": "Red",
        "🔵": "Blue",
        "🟡": "Yellow",
        "🟢": "Green",
        "🟣": "Purple",
        "🟠": "Orange"
    }
    msg = await message.channel.send("Pick 1 color to join the game! You have 5 seconds...")

    for emoji in colors.keys():
        await msg.add_reaction(emoji)

    await asyncio.sleep(5)

    msg = await message.channel.fetch_message(msg.id)

    color_users = {emoji: [] for emoji in colors.keys()}
    user_choices = {}

    for reaction in msg.reactions:
        if str(reaction.emoji) in colors:
            async for user in reaction.users():
                if not user.bot:
                    color_users[str(reaction.emoji)].append(user)
                    user_id = str(user.id)
                    if user_id in user_choices:
                        user_choices[user_id] += 1
                    else:
                        user_choices[user_id] = 1

    for emoji in color_users:
        filtered_users = []
        for user in color_users[emoji]:
            if user_choices[str(user.id)] == 1:
                filtered_users.append(user)
        color_users[emoji] = filtered_users

    winning_emojis = []
    for _ in range(3):
        winning_emojis.append(random.choice(list(colors.keys())))
    winners = []

    for emoji in winning_emojis:
        for user in color_users[emoji]:
            winners.append(user)

    win_names = ""
    for emoji in winning_emojis:
        win_names += f"{emoji} **{colors[emoji]}**, "
    win_names = win_names.rstrip(", ")

    await message.channel.send(
        f"🏁 The winning colors are {win_names}!\n"
        f"🏆 Winners: {', '.join([user.mention for user in winners]) if winners else 'No winners'}"
    )

# f3race
async def f3race(message):
    cars = {
        "🚙": "Car1",
        "🚓": "Car2",
        "🏎️": "Car3",
        "🚗": "Car4"
    }

    msg = await message.channel.send("Pick 1 car to join the race! You have 5 seconds...")

    for car in cars.keys():
        await msg.add_reaction(car)

    await asyncio.sleep(5)

    msg = await message.channel.fetch_message(msg.id)

    car_users = {car: [] for car in cars.keys()}
    user_choices = {}

    for reaction in msg.reactions:
        if str(reaction.emoji) in cars:
            async for user in reaction.users():
                if not user.bot:
                    car_users[str(reaction.emoji)].append(user)
                    user_id = str(user.id)
                    if user_id in user_choices:
                        user_choices[user_id] += 1
                    else:
                        user_choices[user_id] = 1

    for car in car_users:
        filtered_users = []
        for user in car_users[car]:
            if user_choices[str(user.id)] == 1:
                filtered_users.append(user)
        car_users[car] = filtered_users

    racetrack = ["🚙", "🚓", "🏎️", "🚗"]
    positions = [0, 0, 0, 0] 
    finish = 10

    board_msg = await message.channel.send("Starting race...")

    winner_index = None
    while winner_index is None:
        await asyncio.sleep(1)
        move = random.randint(0, 3)
        positions[move] += 1

        board = ""
        for i, car in enumerate(racetrack):
            row = ""
            for j in range(finish+1):
                if positions[i] == j:
                    row += car
                elif j == finish:
                    row += "🟩"
                else:
                    row += "⬛"
            board += row + "\n"
        await board_msg.edit(content=board)

        for i, pos in enumerate(positions):
            if pos >= finish:
                winner_index = i
                break

    winning_car = racetrack[winner_index]
    winners = car_users[winning_car]
    if winners:
        winner_mentions = ""
        for user in winners:
            winner_mentions += user.mention + ", "
        winner_mentions = winner_mentions.rstrip(", ")
        await message.channel.send(f"🏁 Winner: {winning_car} !\n🏆 Users who picked this car: {winner_mentions}")
    else:
        await message.channel.send(f"🏁 Winner: {winning_car} !\nNo one picked this car!")

# Features
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    global blame_message

    if message.author == bot.user:
        return

    msg = message.content.lower()

    if msg.strip() == "f3help":
        blame_message = await message.channel.send(
            "**List of available commands:**\n\n"
            "**F3 RANDOM**\n"
            "***f3abunis*** - isaw ni pinsan\n"
            "***f3wonhee*** - made for kurto\n"
            "***f3rate <mention>*** - rate someone\n"
            "***f3r/<subreddit>*** - reddit post\n"
            "***f3askme*** - random questions\n"

            "\n**F3 GAMES**\n"
            "***f3characters*** - show owned characters\n"
            "***f3leaderboard*** - show leaderboard\n"
            "***f3cf*** - coin flip\n"
            "***f3scatter*** - sugal na scatter\n"
            "***f3slots*** - casino slots\n"
            "***f3gacha*** - character gacha\n"
            "***f3colorgame*** - color game\n"
            "***f3race*** - car race\n"
            )

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
    
    # f3characters
    if msg.strip() == "f3characters":
        await view_characters(message)
        return
    
    # f3leaderboard
    if msg.strip() == "f3leaderboard":
        await leaderboard(message)
        return

    # f3colorgame
    if msg.strip() == "f3colorgame":
        await colorgame(message)
        return
    
    # f3race
    if msg.strip() == "f3race":
        await f3race(message)
        return
    
    await bot.process_commands(message)

# run
bot.run(TOKEN)
