import random
import math
import requests
import discord
from discord.commands.context import ApplicationContext as Context
from creds import *     # API keys/tokens


async def get_weather(city: str):
    url = "https://api.openweathermap.org/data/2.5/weather?q=" 
    
    if city == "":
        return "Please submit a city."
    
    url += city + "&APPID=" + WEATHER_API_KEY
    
    response = requests.get(url)
    if response.status_code == 404:
        return f"Could not find data for {city}."
    elif response.status_code != 200:
        return "There was a problem with the weather API."

    answ = "<No data>"

    try:
        data = response.json()
        temp = "{:.2f}".format(data['main']['temp'] - 273.15)
        title = data['weather'][0]['main'].strip()
        desc = data['weather'][0]['description'].strip()
        humid = int(data['main']['humidity'])
        wind = "{:.2f}".format(data['wind']['speed'] * 3.6)
        answ = f"{data['name']}: {temp}°C {title} ({desc}) - {humid}% humidity - {wind} km/h wind"
    except Exception:
        answ = "Failed to process data."
    
    return answ


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
    except Exception as e:
        answ = "Failed to process data."
        print(e)
    
    return answ


bot = discord.Bot()

GUILDS=[696704049252270131, 768932461710540810]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.slash_command(guild_ids=GUILDS, description="Big Tasty Help")
async def tasty(ctx):
    await ctx.respond("""
        Commands: \n/tasty \n/weather <city>                  
    """)

# Random meme picker from reddit

@bot.slash_command(guild_ids=GUILDS, description="Get a random meme")
async def meme(ctx: Context):
    meme = await get_meme()
    await ctx.respond(meme)

# Weather command

@bot.slash_command(guild_ids=GUILDS, description="Get the current weather")
async def weather(ctx: Context, city: str):
    data = await get_weather(city)
    await ctx.respond(data, ephemeral=True)

# Poll command

@bot.slash_command(guild_ids=GUILDS, description="Create a simple poll")
async def poll(ctx: Context, question: str):
    if question == "":
        await ctx.respond("No empty questions allowed!", ephemeral=True)

    text = f"**Poll! @everyone**\n{question}\nReact with :arrow_up: for 'Yes' and :arrow_down: for 'No'"
    await ctx.respond(text, allowed_mentions = discord.AllowedMentions(everyone=True))

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
        await ctx.respond("You have destroyed the univsere. Oh no...", ephemeral=True)
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


bot.run(DISCORD_BOT_API_KEY)
