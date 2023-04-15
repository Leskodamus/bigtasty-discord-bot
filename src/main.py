import random
import math
import openai
import requests
import discord
from discord.commands.context import ApplicationContext as Context
from creds import *     # API keys/tokens


# Helper functions

async def ask_chatgpt(text: str):
    openai.api_key = OPENAI_API_KEY
    res = openai.Completion.create(
        engine = "text-davinci-003",
        prompt = text,
        temperature = 0.5,
        max_tokens = 2000,
        n = 1
    )

    return res.choices[0].text


async def get_weather(city: str):
    embed = discord.Embed(
        title="Weather",
    )

    url = "https://api.openweathermap.org/data/2.5/weather?q=" 
    
    if city == "":
        embed.add_field(name="Error!",
            value="Please submit a city.")
        return embed 
    
    url += city + "&APPID=" + WEATHER_API_KEY
    
    response = requests.get(url)
    if response.status_code == 404:
        embed.add_field(name="Error!",
            value=f"Could not find data for {city}.")
        return embed 
    elif response.status_code != 200:
        embed.add_field(name="Error!",
            value="There was a problem with the weather API.")
        return embed 

    try:
        data = response.json()
        temp = "{:.2f}".format(data['main']['temp'] - 273.15)
        title = data['weather'][0]['main'].strip()
        desc = data['weather'][0]['description'].strip()
        humid = int(data['main']['humidity'])
        wind = "{:.2f}".format(data['wind']['speed'] * 3.6)

        embed.add_field(name=f"Result for {data['name']}",
            value=f"""
                Weather: {title} ({desc}) 
                Temperature: {temp}°C 
                Humidity: {humid}% 
                Wind: {wind} km/h 
            """
        )
    except Exception:
        embed.add_field(name="Error!",
            value="Failed to process data."
        )
    
    return embed


async def get_meme():
    subreddits = [
        "r/memes",
        "r/dankmemes",
        "r/me_irl"
    ]

    sub = subreddits[random.randint(0, len(subreddits)-1)]
    url = f"https://www.reddit.com/{sub}/.json"

    response = requests.get(url, headers={'User-agent': 'Big Tasty Discord Bot'})
    answ = "<No meme>"

    try:
        data = response.json()
        n_posts = len(data['data']['children'])
        post = data['data']['children'][random.randint(0, n_posts-1)]['data']
        answ = f"{post['url']}"
    except Exception:
        answ = "Failed to process data."
    
    return answ


async def get_crypto(currency: str):
    currency = currency.upper()
    url = "https://api.bitpanda.com/v1/ticker"

    response = requests.get(url)
    if response.status_code != 200:
        return "There was an error with the currency API."

    try:
        data = response.json()
        return f"1 {currency} = {data[currency]['EUR']}€"
    except Exception:
        return "Failed to process data."


# Discord Bot 

bot = discord.Bot(intents=discord.Intents.all())

GUILDS=[696704049252270131, 768932461710540810]


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.slash_command(guild_ids=GUILDS, description="Big Tasty Help")
async def tasty(ctx):
    embed = discord.Embed(
        title="Big Tasty - Brother of Big Mac",
        description="Big Tasty Help Menu"
    )

    embed.add_field(name="Casual commands:",
        value="""
            `/tasty`
            This help menu
            `/meme`
            Get a random meme
            `/weather <city>`
            Get the current weather
        """)

    embed.add_field(name="Math commands:",
        value="""
            `/math add <v1> <v2>`
            Add <v2> to <v1>
            `/math sub <v1> <v2>`
            Subtract <v2> from <v1>
            `/math mul <v1> <v2>`
            Multiply <v1> with <v2>
            `/math div <v1> <v2>`
            Divide <v1> by <v2>
            `/math sqrt <value>`
            Get square root of <value>
            `/math sin <value>`
            Get sinus of <value>
            `/math cos <value>`
            Get cosinus of <value>
            `/math tan <value>`
            Get tangens of <value>
        """,
        inline=False)

    embed.add_field(name="ChatGPT command:",
        value="""
            `!gpt <message>`
            Ask ChatGPT anything
        """)
    embed.set_thumbnail(url=bot.user.avatar.url)
    await ctx.respond(embed=embed)


# Random meme picker from reddit

@bot.slash_command(guild_ids=GUILDS, description="Get a random meme")
async def meme(ctx: Context):
    meme = await get_meme()
    await ctx.respond(meme)

# Weather command

@bot.slash_command(guild_ids=GUILDS, description="Get the current weather")
async def weather(ctx: Context, city: str):
    embed = await get_weather(city)
    await ctx.respond(embed=embed, ephemeral=True)

# Crypto price command

@bot.slash_command(guild_ids=GUILDS, description="Get the current price of <crypto>")
async def crypto(ctx: Context, currency: str):
    text = await get_crypto(currency)
    await ctx.respond(text, ephemeral=True)

# Poll command

@bot.slash_command(guild_ids=GUILDS, description="Create a simple poll")
async def poll(ctx: Context, question: str):
    if question == "":
        await ctx.respond("No empty questions allowed!", ephemeral=True)

    embed = discord.Embed(
        title="Poll",
        description=f"by {ctx.author.mention}"
    )
    embed.add_field(name="Subject", value=question)
    embed.add_field(name="Vote", 
        value="React with :arrow_up: for `Yes` and :arrow_down: for `No`",
        inline=False)

    msg = await ctx.channel.send("@here", embed=embed)
    await msg.add_reaction("⬆️")
    await msg.add_reaction("⬇️")
    await ctx.respond("Creating new poll.", ephemeral=True, delete_after=0)

# Math commands

math_cmds = discord.SlashCommandGroup("math", "Math related commands", guild_ids=GUILDS)

@math_cmds.command(description="Add two numbers")
async def add(ctx, v1: float, v2: float):
    await ctx.respond(f"{v1} + {v2} = {v1+v2}", ephemeral=True)

@math_cmds.command(description="Subtract two numbers")
async def sub(ctx, v1: float, v2: float):
    await ctx.respond(f"{v1} - {v2} = {v1-v2}", ephemeral=True)

@math_cmds.command(description="Multiply two numbers")
async def mul(ctx, v1: float, v2: float):
    await ctx.respond(f"{v1} * {v2} = {v1*v2}", ephemeral=True)

@math_cmds.command(description="Divide two numbers")
async def div(ctx, v1: float, v2: float):
    if v2 == 0:
        await ctx.respond("You have destroyed the universe. Oh no...", ephemeral=True)
    else:
        await ctx.respond(f"{v1} : {v2} = {v1/v2}", ephemeral=True)

@math_cmds.command(description="Square root of a number")
async def sqrt(ctx, value: float):
    await ctx.respond(f"Square root of {value} = {math.sqrt(value)}", ephemeral=True)

@math_cmds.command(description="Sinus of a number")
async def sin(ctx, value: float):
    await ctx.respond(f"Sinus of {value} = {math.sin(value)}", ephemeral=True)

@math_cmds.command(description="Cosinus of a number")
async def cos(ctx, value: float):
    await ctx.respond(f"Cosinus of {value} = {math.cos(value)}", ephemeral=True)

@math_cmds.command(description="Tangens of a number")
async def tan(ctx, value: float):
    await ctx.respond(f"Tangens of {value} = {math.tan(value)}", ephemeral=True)

bot.add_application_command(math_cmds)


# Reply on chat messages

@bot.event
async def on_message(msg: discord.Message):
    # Prevent bot from replying to itself
    if msg.author.id == bot.user.id:
        return

    # ChatGPT reply cmd
    if msg.content.startswith("!gpt"):
        text = msg.content[len("!gpt"):]
        gpt = await ask_chatgpt(text)
        await msg.reply(gpt, mention_author=True)


bot.run(DISCORD_BOT_API_KEY)
