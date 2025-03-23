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

# Tracker for f3ml
tracker = {
    "core": "",
    "exp": "",
    "gold": "",
    "mid": "",
    "roam": ""
}

blame_message = None
blame_thread = None

# x up list
def format_board():
    return "\n".join(
        f"{role}: {tracker[role] if tracker[role] else ''}"
        for role in tracker
    )

# When someone x up
async def xup(message):
    global blame_message

    msg = message.content.lower()
    updated = False

    user_has_role = False
    current_role = None
    for role in tracker:
        if tracker[role] == message.author.mention:
            user_has_role = True
            current_role = role
            break

    for role in tracker:
        if f"x {role}" in msg:
            if tracker[role] == "": 
                if user_has_role:
                    tracker[current_role] = "" 
                tracker[role] = message.author.mention
                updated = True

    for role in tracker:
        if f"x {role} out" in msg:
            if message.author.mention == tracker[role]:
                tracker[role] = ""
                updated = True
                break

    if blame_message and updated:
        await blame_message.edit(content=f"@everyone EMLEM!!!!!:\n\n{format_board()}")

# f3ml
async def handle_fml(message):
    global blame_message, blame_thread

    tracker.update({role: "" for role in tracker})

    blame_message = await message.channel.send(f"@everyone EMLEM!!!!!:\n\n{format_board()}")

    blame_thread = await blame_message.create_thread(
        name="Emlem X-UP",
        auto_archive_duration=60
    )
    await blame_thread.send("Assign roles here by typing `x core`, `x exp`, etc. `x (role) out` to out.")

# f3cf
async def coinflip(message):
    result = random.choice(["Heads", "Tails"])
    await message.channel.send(f"🎲 Coin flip result: **{result}**!")

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
            "***f3wonhee*** - made for kurto"
            )

    # f3ml
    if msg.strip() == "f3ml":
        await handle_fml(message)
        return
    # f3ml in thread
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

    await bot.process_commands(message)

    # other upcoming features goes here

# run
bot.run(TOKEN)