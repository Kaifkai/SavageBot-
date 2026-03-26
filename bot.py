import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import os
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash-lite")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)
                              
# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Bot setup
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None, chunk_guilds_at_startup=False)
welcome_channels = {}

@bot.event
async def on_message(message):
    print(f"Message received: {message.content}")
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online and ready to cause chaos!")
    try:
        synced = await bot.tree.sync()
        print(f"⚡ Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Sync failed: {e}")
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="you struggle | !help")
    )

@bot.event
async def on_member_join(member: discord.Member):
    guild_id = member.guild.id
    if guild_id in welcome_channels:
        channel = bot.get_channel(welcome_channels[guild_id])
        if channel:
            embed = discord.Embed(
                title="👋 Welcome to the server!",
                description=f"Oh great, **{member.mention}** decided to show up. we were fine without you. Welcome anyway. 💀",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"Member #{member.guild.member_count}")
            await channel.send(embed=embed)

# HELP
@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(
        title="📖 cafevibe Commands",
        description="Yeah yeah, here's what I can do. Try to keep up.",
        color=discord.Color.blurple(),
    )
    embed.add_field(
        name="🛡️ Moderation",
        value="`!kick` `!ban` `!unban` `!mute` `!unmute` `!clear` `!setwelcome`" ,
        inline=False,
    )
    embed.add_field(
        name="🎮 Fun & Games",
        value="`!roll` `!coinflip` `!8ball` `!rps` `!trivia` `!roast` `!chat`",
        inline=False,
    )
    embed.set_footer(text="subscribe to kaif44gamer on yt")
    await ctx.send(embed=embed)

# MODERATION
@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = "No reason given. Rude."):
    await member.kick(reason=reason)
    await ctx.send(f"🥾 **{member}** got the boot. Reason: *{reason}*. Bye! 👋")

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 You don't have permission to kick. Sit down.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❓ Can't find that member. They might've already run away.")

@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = "No reason given. Wild."):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 **{member}** has been BANNED. Reason: *{reason}*. Don't let the door hit you. 💀")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 You don't have ban powers. Go touch grass.")

@bot.command(name="unban")
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, username: str):
    banned = [entry async for entry in ctx.guild.bans()]
    for ban_entry in banned:
        if str(ban_entry.user) == username:
            await ctx.guild.unban(ban_entry.user)
            await ctx.send(f"✅ **{username}** has been unbanned. Don't make me regret this.")
            return
    await ctx.send(f"❓ Couldn't find **{username}** in the ban list. Double-check the spelling, genius.")

@bot.command(name="mute")
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason: str = "Time out."):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, send_messages=False, speak=False)
    await member.add_roles(muted_role, reason=reason)
    await ctx.send(f"🔇 **{member}** has been muted. Reason: *{reason}*. Finally, some peace and quiet.")

@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 You can't mute people. You're not even that loud yourself.")

@bot.command(name="unmute")
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if muted_role and muted_role in member.roles:
        await member.remove_roles(muted_role)
        await ctx.send(f"🔊 **{member}** can speak again. Please don't make us regret it.")
    else:
        await ctx.send(f"🤔 **{member}** wasn't muted. You good?")

@bot.command(name="clear")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    if amount > 100:
        await ctx.send("😤 Max is 100 messages. Calm down.")
        return
    deleted = await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🧹 Deleted **{len(deleted) - 1}** messages. Clean as a whistle.")
    await msg.delete(delay=3)

# FUN & GAMES
@bot.command(name="roll")
async def roll(ctx, dice: str = "1d6"):
    try:
        n, sides = map(int, dice.lower().split("d"))
        if n < 1 or n > 20 or sides < 2 or sides > 100:
            raise ValueError
        rolls = [random.randint(1, sides) for _ in range(n)]
        total = sum(rolls)
        result = " + ".join(str(r) for r in rolls)
        await ctx.send(f"🎲 **{ctx.author.display_name}** rolled {dice}: `{result}` = **{total}**")
    except (ValueError, AttributeError):
        await ctx.send("❌ Use the format `!roll 2d6`. It's not that hard.")

@bot.command(name="coinflip")
async def coinflip(ctx):
    result = random.choice(["Heads 🪙", "Tails 🪙"])
    await ctx.send(f"🪙 **{ctx.author.display_name}** flipped a coin... it's **{result}**!")

@bot.command(name="8ball")
async def eight_ball(ctx, *, question: str = None):
    if not question:
        await ctx.send("😐 You forgot to ask a question. Typical.")
        return
    responses = [
        "It is certain. Obviously. 💯",
        "Without a doubt. Are you even surprised?",
        "Yes, definitely. Get it together.",
        "Most likely. Use your brain next time.",
        "Ask again later. I'm busy judging you.",
        "Cannot predict now. Stop bothering me.",
        "Don't count on it. Yikes.",
        "My sources say no. And my sources are always right.",
        "Very doubtful. Like, extremely.",
        "Outlook not so good. Sorry not sorry.",
    ]
    embed = discord.Embed(color=discord.Color.dark_purple())
    embed.add_field(name="❓ Question", value=question, inline=False)
    embed.add_field(name="🎱 Answer", value=random.choice(responses), inline=False)
    await ctx.send(embed=embed)

@bot.command(name="rps")
async def rps(ctx, choice: str = None):
    options = ["rock", "paper", "scissors"]
    if not choice or choice.lower() not in options:
        await ctx.send("🤦 Pick one: `rock`, `paper`, or `scissors`. Not that difficult.")
        return
    player = choice.lower()
    bot_choice = random.choice(options)
    emojis = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
    wins = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
    if player == bot_choice:
        result = "It's a tie! You're equally mediocre. 😐"
    elif wins[player] == bot_choice:
        result = "You win. Don't let it go to your head. 🙄"
    else:
        result = "I win. Predictably ab baap bol. 😈"
    await ctx.send(
        f"{emojis[player]} You chose **{player}** | I chose **{bot_choice}** {emojis[bot_choice]}\n{result}"
    )

TRIVIA_QUESTIONS = [
    {"q": "What is the capital of Australia?", "a": "canberra"},
    {"q": "How many sides does a hexagon have?", "a": "6"},
    {"q": "What planet is known as the Red Planet?", "a": "mars"},
    {"q": "What is 7 x 8?", "a": "56"},
    {"q": "Who wrote Romeo and Juliet?", "a": "shakespeare"},
    {"q": "What gas do plants absorb from the air?", "a": "carbon dioxide"},
    {"q": "How many bones are in the human body?", "a": "206"},
    {"q": "What is the largest ocean on Earth?", "a": "pacific"},
    {"q": "How many continents are there?", "a": "7"},
    {"q": "What is the chemical symbol for water?", "a": "h2o"},
    {"q": "kaif kiska papa ha ?", "a": "is duniya ka"},
]

active_trivia: dict[int, dict] = {}

@bot.command(name="trivia")
async def trivia(ctx):
    if ctx.channel.id in active_trivia:
        await ctx.send("⚠️ There's already a trivia question going on. Finish that one first.")
        return
    q = random.choice(TRIVIA_QUESTIONS)
    active_trivia[ctx.channel.id] = q
    embed = discord.Embed(
        title="🧠 TRIVIA TIME",
        description=q["q"],
        color=discord.Color.gold(),
    )
    embed.set_footer(text="Type your answer in chat! You have 30 seconds.")
    await ctx.send(embed=embed)

    def check(m):
        return (
            m.channel == ctx.channel
            and not m.author.bot
            and m.content.lower().strip() == q["a"].lower()
        )

    try:
        msg = await bot.wait_for("message", check=check, timeout=30.0)
        del active_trivia[ctx.channel.id]
        await ctx.send(
            f"✅ **{msg.author.display_name}** got it right! The answer was **{q['a']}**. "
            "I guess you're not completely hopeless. 🎉"
        )
    except asyncio.TimeoutError:
        del active_trivia[ctx.channel.id]
        await ctx.send(f"⏰ Time's up! The answer was **{q['a']}**. Embarrassing, fr fr. 💀")

@bot.command(name="roast")
async def roast(ctx, member: discord.Member = None):
    target = member or ctx.author
    roasts = [
        f"**{target.display_name}** Tum itne confident ho jaise sab pata ho… problem bas itni hai ki kuch pata hi nahi.",
        f"**{target.display_name}** Tumhari planning itni strong hoti hai ki kabhi start hi nahi hoti.",
        f"**{target.display_name}** Tum argument nahi jeette… saamne wala bas thak ke chup ho jata hai.",
        f"**{target.display_name}** Tumhara dimaag airplane mode pe rehta hai.",
        f"**{target.display_name}** Tumhari speed dekh ke lagta hai tum buffering mein paida hue the.",
        f"**{target.display_name}** Tumhara confidence free WiFi jaisa hai… strong dikhta hai par kaam ka nahi.",
        f"**{target.display_name}** Tumhare ideas itne unique hote hain ki kisi ko samajh hi nahi aate.",
        f"**{target.display_name}** joke kya sunraha hai padhai krle jake. science le haina tune.",
        f"**{target.display_name}** Tumhari advice utni hi useful hai jitni exam ke baad padhai.",
        f"**{target.display_name}** tum wohi hona jo group me 'lol' likhta hai. Every single time.",
        f"**{target.display_name}** kya roast kam kr apna",
    ]
    await ctx.send(random.choice(roasts) + " 💀 (relax, it's a joke 🤝)")

# Slash commands
@bot.tree.command(name="roll", description="Roll dice, e.g. 2d6")
@app_commands.describe(dice="Dice format like 1d6 or 2d20")
async def slash_roll(interaction: discord.Interaction, dice: str = "1d6"):
    try:
        n, sides = map(int, dice.lower().split("d"))
        rolls = [random.randint(1, sides) for _ in range(n)]
        total = sum(rolls)
        await interaction.response.send_message(
            f"🎲 {interaction.user.display_name} rolled **{dice}**: `{' + '.join(map(str, rolls))}` = **{total}**"
        )
    except Exception:
        await interaction.response.send_message("❌ Invalid format. Try `1d6` or `2d20`.")

@bot.tree.command(name="roast", description="Get roasted (or roast someone else)")
@app_commands.describe(member="Who to roast (leave blank for yourself)")
async def slash_roast(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    roasts = [
        f"**{target.display_name}**, aj mood nhi .",
        f"**{target.display_name}** types with two fingers and is proud of it.",
        f"**{target.display_name}** still uses Internet Explorer unironically.",
        f"**{target.display_name}** sends 'k' and wonders why people are annoyed.",
        f"**{target.display_name}** you are not sigma you are ligma. ",
    ]
    await interaction.response.send_message(random.choice(roasts) + " 💀 (just jokes 🤝)")

@bot.tree.command(name="coinflip", description="Flip a coin")
async def slash_coinflip(interaction: discord.Interaction):
    result = random.choice(["Heads 🪙", "Tails 🪙"])
    await interaction.response.send_message(
        f"🪙 **{interaction.user.display_name}** flipped a coin... it's **{result}**!"
    )

# Run
@bot.command(name="setwelcome")
@commands.has_permissions(administrator=True)
async def setwelcome(ctx, channel: discord.TextChannel = None):
    if channel is None:
        await ctx.send("❌ Please mention a channel! Example: `!setwelcome #welcome`")
        return
    welcome_channels[ctx.guild.id] = channel.id
    await ctx.send(f"✅ Welcome channel set to {channel.mention}! 🎉")

@setwelcome.error
async def setwelcome_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 Only admins can set the welcome channel. Nice try. 😏")
        

@bot.command(name="chat")
async def chat(ctx, *, message: str = None):
    if not message:
        await ctx.send("💬 Say something then. `!chat <your message>`")
        return
    async with ctx.typing():
        prompt = (
            f"You are cafevibe SavageBot, created by kaifuddin. Your name is cafevibe SavageBot. NEVER say your name is SavageBot alone, always say cafevibe SavageBot. You were made by kaifuddin. Be bold, witty, brutally honest but never hateful. "
            f"Be savage and sarcastic but actually helpful. Keep replies short. "
            f"User said: {message}"
        )
        # Try Gemini first
        try:
            response = model.generate_content(prompt)
            reply = response.text
            await ctx.send(f"🤖 {reply}")
            return
        except Exception:
            pass
        # If Gemini fails, try Groq
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            reply = response.choices[0].message.content
            await ctx.send(f"🤖 {reply}")
            return
        except Exception as e:
            await ctx.send(f"❌ Both AIs are down. Try again later. Error: `{e}`")

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ DISCORD_TOKEN not set — open your .env file and paste your token!")
    else:
        bot.run(DISCORD_TOKEN)
