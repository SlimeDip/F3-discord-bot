import discord
from discord.ext import commands
import random
import os
import asyncio
import asyncpraw
import aiohttp
import io
import json
from pathlib import Path
from dotenv import load_dotenv

# Config
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USER_AGENT = os.getenv("USER_AGENT")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = BASE_DIR / "images"
AUDIO_DIR = BASE_DIR / "audio"

DATA_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.messages = True
intents.guild_messages = True
intents.voice_states = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix="f3", intents=intents)

bot.scatter_highscores = {}
bot.owned_characters = {}
bot._data_lock = asyncio.Lock()
bot.reddit_client = None 

SCATTER_FILE = DATA_DIR / "scatter_highscores.json"
CHAR_FILE = DATA_DIR / "owned_characters.json"

async def async_json_load(path: Path):
    if not path.exists():
        return {}
    return await asyncio.to_thread(lambda: json.loads(path.read_text(encoding="utf-8")))

async def async_json_save(path: Path, data):
    await asyncio.to_thread(lambda: path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8"))

async def init_storage():
    bot.scatter_highscores = await async_json_load(SCATTER_FILE)
    bot.owned_characters = await async_json_load(CHAR_FILE)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await init_storage()
    print("Storage loaded.")

# --------------------------
# small helper functions
# --------------------------

def mention_or_name(member: discord.Member):
    return member.mention if member else "Unknown"

async def ensure_reddit():
    if bot.reddit_client is None:
        if not (CLIENT_ID and CLIENT_SECRET and USER_AGENT):
            raise RuntimeError("Reddit credentials are missing in env.")
        bot.reddit_client = asyncpraw.Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            user_agent=USER_AGENT,
        )
    return bot.reddit_client

async def _gather_reactions(ctx, message: discord.Message, valid_emojis, wait_seconds=5):
    for e in valid_emojis:
        try:
            await message.add_reaction(e)
        except Exception:
            pass
    await asyncio.sleep(wait_seconds)
    message = await ctx.channel.fetch_message(message.id)

    emoji_users = {e: [] for e in valid_emojis}
    user_choice_count = {}
    for reaction in message.reactions:
        if str(reaction.emoji) in valid_emojis:
            async for user in reaction.users():
                if user.bot:
                    continue
                emoji_users[str(reaction.emoji)].append(user)
                uid = str(user.id)
                user_choice_count[uid] = user_choice_count.get(uid, 0) + 1

    for e in list(emoji_users.keys()):
        filtered = [u for u in emoji_users[e] if user_choice_count.get(str(u.id), 0) == 1]
        emoji_users[e] = filtered
    return emoji_users

# --------------------------
# Commands
# --------------------------

# f3help
bot.remove_command("help")
@bot.command(name="help")
async def help(ctx):
    board = (
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
    "***f3case*** - open a case\n"
    )
    
    await ctx.send(board)

# f3cf
@bot.command(name="cf")
async def coinflip(ctx):
    result = random.choice(["Heads", "Tails"])
    await ctx.send(f":coin: Coin flip result: **{result}**!")

# f3abunis
@bot.command(name="abunis")
async def abunis(ctx):
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        await ctx.send("You need to be in a voice channel to use this command.")
        return

    voice_channel = ctx.author.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if voice_client is None or not voice_client.is_connected():
        try:
            voice_client = await voice_channel.connect()
        except Exception as e:
            await ctx.send(f"Failed to join voice channel: {e}")
            return

    file_path = AUDIO_DIR / "abunis.mp3"
    if not file_path.exists():
        await ctx.send("Audio file not found.")
        return

    if not voice_client.is_playing():
        source = discord.FFmpegPCMAudio(str(file_path))
        try:
            voice_client.play(source)
            while voice_client.is_playing():
                await asyncio.sleep(1)
        except Exception as e:
            await ctx.send(f"Error while playing audio: {e}")
        finally:
            try:
                await voice_client.disconnect()
            except Exception:
                pass
    else:
        await ctx.send("Already playing audio — wait until it finishes.")

# f3wonhee
@bot.command(name="wonhee")
async def wonhee(ctx):
    num = str(random.randrange(0, 7))
    image_path = IMAGES_DIR / f"Kurto{num}.jpg"
    if not image_path.exists():
        await ctx.send("Image not found.")
        return
    await ctx.send(file=discord.File(image_path))

# f3rate
@bot.command(name="rate")
async def rate(ctx, user: discord.Member = None):
    if user is None:
        await ctx.send("Please mention someone to rate.")
        return
    ratings = random.randrange(0, 11)
    bad_comments = [
        "Medyo burat.",
        "Mukhang bisaya.",
        "Bisakol masyado.",
        "Eto na yon?",
        "Di ko trip eh.",
        "No comment nalang.",
        "Haup na badtrip ako bigla."
    ]
    good_comments = [
        "Pwede na.",
        "Masarap kahit walang ulam.",
        "Napaka angas.",
        "Krazy masyado."
    ]
    comment = random.choice(bad_comments if ratings < 7 else good_comments)
    await ctx.send(f"{user.mention} is {ratings}/10. {comment}")

# f3scatter
@bot.command(name="scatter")
async def scatter(ctx):
    play = 9
    total = 0

    scatter_msg = ":regional_indicator_l: :regional_indicator_o: :regional_indicator_a: :regional_indicator_d: :regional_indicator_i: :regional_indicator_n: :regional_indicator_g:"
    scatter_var = await ctx.send(scatter_msg)

    while play > -1:
        earned = 0
        symbols = [":diamonds:", ":heart:", ":spades:", ":clubs:", ":coin:"]
        weights = [24, 24, 24, 24, 2]

        grid = []
        for _ in range(5):
            row = " ".join(random.choices(symbols, weights=weights, k=5))
            grid.append(row)
        display = "\n".join(grid)
        display += f"\n\nRounds: {play}\n"

        counts = {i: display.count(i) for i in symbols}
        for i in [":diamonds:", ":heart:", ":spades:", ":clubs:"]:
            if counts[i] >= 5:
                earned += counts[i]
        if counts[":coin:"] >= 3:
            play += 10
            display += "+ 10 for getting 3 or more coins\n"

        total += earned
        display += f"+ {earned} points"
        play -= 1

        await asyncio.sleep(1)
        await scatter_var.edit(content=display)

    display += f"\n\nRound over... Total points earned: {total}"

    user_id = str(ctx.author.id)
    prev_score = int(bot.scatter_highscores.get(user_id, 0))

    if total > prev_score:
        bot.scatter_highscores[user_id] = total
        async with bot._data_lock:
            await async_json_save(SCATTER_FILE, bot.scatter_highscores)
        display += f"\nNew highscore!"

    display += f"\nYour highscore: {bot.scatter_highscores.get(user_id, total)}"

    await scatter_var.edit(content=display)

# f3slots
@bot.command(name="slots")
async def slot(ctx):
    slots = [random.choice([":gem:", ":cherries:", ":bell:", ":seven:"]) for _ in range(3)]
    await ctx.send(" ".join(slots))
    if len(set(slots)) == 1:
        await ctx.send("Paldogs")
    else:
        await ctx.send("Eguls")

# f3gacha
@bot.command(name="gacha")
async def gacha(ctx):
    user_id = str(ctx.author.id)
    pool = [
        (":detective:", 5),
        (":health_worker:", 20),
        (":man_police_officer:", 20),
        (":judge:", 20),
        (":man_supervillain:", 5),
        (":man_mage:", 5),
        (":factory_worker:", 5),
        (":person_in_tuxedo:", 20),
    ]
    characters, weights = zip(*pool)
    character = random.choices(characters, weights=weights, k=1)[0]
    rarity = {":detective:": 5, ":health_worker:": 4, ":man_police_officer:": 4,
              ":judge:": 4, ":man_supervillain:": 5, ":man_mage:": 5,
              ":factory_worker:": 5, ":person_in_tuxedo:": 4}

    msg = await ctx.send(":sparkles:")
    for i in range(1, 3):
        await asyncio.sleep(0.5)
        await msg.edit(content=":sparkles:" * (i + 1))
    await asyncio.sleep(0.5)
    if rarity[character] == 5:
        await msg.edit(content=":sparkles: :sparkles: :sparkles: :star2:")
        await asyncio.sleep(0.5)

    if user_id not in bot.owned_characters:
        bot.owned_characters[user_id] = {}
    bot.owned_characters[user_id][character] = bot.owned_characters[user_id].get(character, 0) + 1

    async with bot._data_lock:
        await async_json_save(CHAR_FILE, bot.owned_characters)

    await msg.edit(content=character)
    await ctx.send(f"{rarity[character]} star character")

# f3r <subreddit>
@bot.command(name="r")
async def reddit(ctx, subreddit_name: str = None):
    if not subreddit_name:
        await ctx.send("Please provide a subreddit: `f3r subreddit_name`")
        return

    try:
        reddit = await ensure_reddit()
    except RuntimeError as e:
        await ctx.send(str(e))
        return

    loading = await ctx.send("Loading...")
    try:
        subreddit = await reddit.subreddit(subreddit_name)
        posts = [post async for post in subreddit.top(time_filter="week", limit=25)]
        random.shuffle(posts)
        async with aiohttp.ClientSession() as session:
            for post in posts:
                url = getattr(post, "url", "")
                if url and url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    try:
                        async with session.get(url) as resp:
                            if resp.status == 200:
                                data = await resp.read()
                                f = io.BytesIO(data)
                                ext = os.path.splitext(url)[1]
                                fname = f"{post.id}{ext}"
                                f.seek(0)
                                await loading.edit(content=post.title)
                                await ctx.send(file=discord.File(f, filename=fname))
                                return
                    except Exception as e:
                        # try next post
                        continue

        await loading.edit(content=f"No image posts found in r/{subreddit_name}")
    except Exception as e:
        await loading.edit(content=f"Failed to access subreddit: {e}")

# f3askme
@bot.command(name="askme")
async def askme(ctx):
    try:
        reddit = await ensure_reddit()
    except RuntimeError as e:
        await ctx.send(str(e))
        return

    try:
        sub = await reddit.subreddit("AskReddit")
        posts = [post async for post in sub.top(time_filter="week", limit=25)]
        if not posts:
            await ctx.send("Couldn't find questions right now.")
            return
        post = random.choice(posts)
        await ctx.send(post.title)
    except Exception as e:
        await ctx.send(f"Failed to gather questions: {e}")

# f3characters
@bot.command(name="characters")
async def view_characters(ctx):
    user_id = str(ctx.author.id)
    chars = bot.owned_characters.get(user_id, {})
    if not chars:
        await ctx.send("You don't own any characters yet.")
        return
    character_list = "\n".join([f"{char}: {count}" for char, count in chars.items()])
    await ctx.send(f"Your owned characters:\n{character_list}")

# f3leaderboard
@bot.command(name="leaderboard")
async def leaderboard(ctx):
    if not bot.scatter_highscores:
        await ctx.send("No data available.")
        return
    sorted_scatter = sorted(bot.scatter_highscores.items(), key=lambda x: int(x[1]), reverse=True)
    lines = ["**Scatter Highscores:**"]
    for i, (user_id, score) in enumerate(sorted_scatter[:5], start=1):
        try:
            user = await bot.fetch_user(int(user_id))
            name = user.name
        except Exception:
            name = f"<unknown {user_id}>"
        lines.append(f"{i}. {name}: {score}")
    await ctx.send("\n".join(lines))

# f3colorgame
@bot.command(name="colorgame")
async def colorgame(ctx):
    colors = {
        "🔴": "Red",
        "🔵": "Blue",
        "🟡": "Yellow",
        "🟢": "Green",
        "🟣": "Purple",
        "🟠": "Orange"
    }
    prompt = await ctx.send("Pick 1 color to join the game! You have 5 seconds...")
    emoji_users = await _gather_reactions(ctx, prompt, list(colors.keys()), wait_seconds=5)

    winning_emojis = [random.choice(list(colors.keys())) for _ in range(3)]
    winners = []
    for em in winning_emojis:
        winners.extend(emoji_users.get(em, []))

    win_names = ", ".join([f"{em} **{colors[em]}**" for em in winning_emojis])
    await ctx.send(
        f"🏁 The winning colors are {win_names}!\n"
        f"🏆 Winners: {', '.join([u.mention for u in winners]) if winners else 'No winners'}"
    )

# f3race
@bot.command(name="race")
async def race(ctx):
    cars = {
        "🚙": "Car1",
        "🚓": "Car2",
        "🏎️": "Car3",
        "🚗": "Car4"
    }
    prompt = await ctx.send("Pick 1 car to join the race! You have 5 seconds...")
    car_users = await _gather_reactions(ctx, prompt, list(cars.keys()), wait_seconds=5)

    racetrack = list(cars.keys())
    positions = [0] * len(racetrack)
    finish = 10

    board_msg = await ctx.send("Starting race...")
    winner_index = None
    while winner_index is None:
        await asyncio.sleep(1)
        move = random.randint(0, len(racetrack) - 1)
        positions[move] += 1

        board = ""
        for i, car in enumerate(racetrack):
            row = ""
            for j in range(finish + 1):
                if positions[i] == j:
                    row += car
                elif j == finish:
                    row += "🟩"
                else:
                    row += "⬛"
            board += row + "\n"
        try:
            await board_msg.edit(content=board)
        except Exception:
            pass

        for i, pos in enumerate(positions):
            if pos >= finish:
                winner_index = i
                break

    winning_car = racetrack[winner_index]
    winners = car_users.get(winning_car, [])
    if winners:
        await ctx.send(f"🏁 Winner: {winning_car} !\n🏆 Users who picked this car: {', '.join([u.mention for u in winners])}")
    else:
        await ctx.send(f"🏁 Winner: {winning_car} !\nNo one picked this car!")

# f3case
@bot.command(name="case")
async def case(ctx):
    items = ["🔪", "🧤", "🔫", "🏵️", "💿", "🔗"]
    itemsname = {"🔪": "Knife skin", "🧤": "Glove", "🔫": "Gun skin", "🏵️": "Sticker", "💿": "Music", "🔗": "Keychain"}
    weights = [1, 4, 5, 30, 30, 30]

    spin = await ctx.send("Spinning...")
    box = [random.choices(items, weights=weights)[0] for _ in range(5)]

    for _ in range(random.randrange(10, 15)):
        case_item = "".join(box)
        box.pop(0)
        box.append(random.choices(items, weights=weights)[0])
        case_item += "\n"
        case_item += " " * 27
        case_item += ":arrow_up_small:"
        try:
            await spin.edit(content=case_item)
        except Exception:
            pass
        await asyncio.sleep(0.5)

    won = itemsname.get(box[1], "item")
    await ctx.send(f"You won a {won}!")


if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: DISCORD_BOT_TOKEN not found in environment.")
        exit(1)
    bot.run(TOKEN)

