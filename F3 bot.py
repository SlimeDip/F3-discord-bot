import discord
import random
from discord.ext import commands

# Config
TOKEN = ""
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.messages = True
intents.guild_messages = True
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
    await message.channel.send(
        "Isaw ni pinsan\n\nIsang hapon sa bahay ng aking pinsan. Naisip namin na kumain ng barbeque, "
        "saktong sakto katapat ng bahay nila ang tindahan nito. Agad nilang tinanong kung sa shortcut o "
        "sa longcut kami dadaan, syempre sa shortcut tayo, ang sagot ko. Aking nilista ang aming bibilhin. "
        "Nang kami ay papunta na, aking naisip na mas matagal ang shortcut dahil kami ay umakyat pa sa bundok, "
        "na kung ikukumpara sa longcut na patag at hindi nakaka pagod ang daan. Pagkadating namin agad naming "
        "pinaluto ang aming bibilhin. Dahil kami ay nagiintay napagkwentuhan namin ang magandang aso ng tindera. "
        "Pagkaluto ng aming barbeque kamiy handa na sa pag uwi sabay sabi ng isa naming pinsan na, pabili po ng isang isaw.")

# f3wonhee
async def wonhee(message):
    num = random.randrange(0, 7)
    image_path = fr"D:\Code shits\F3 discord bot\images\Kurto{str(num)}.jpg"
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
    time.sleep(0.5)
    await msggg.edit(content=":sparkles: :sparkles:")
    time.sleep(0.5)
    await msggg.edit(content=":sparkles: :sparkles: :sparkles:")
    time.sleep(0.5)
    if rarity[character] == 5:
        await msggg.edit(content=":sparkles: :sparkles: :sparkles: :star2:")
        time.sleep(0.5)
    await msggg.edit(content=character)
    await message.channel.send(f"{rarity[character]} star character")


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
            "***f3gacha*** - character gacha"
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
    

    await bot.process_commands(message)

# run
bot.run(TOKEN)
