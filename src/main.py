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


bot = discord.Bot()

GUILDS=["696704049252270131", "768932461710540810"]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.slash_command(guild_ids=GUILDS, description="Big Tasty Help")
async def tasty(ctx):
    await ctx.respond("""
        Commands: \n/tasty \n/weather <city>                  
    """)
    
@bot.slash_command(guild_ids=GUILDS, description="Get the current weather", hidden=True)
async def weather(ctx: Context, city: str):
    data = await get_weather(city)
    await ctx.respond(data, ephemeral=True)


bot.run(DISCORD_BOT_API_KEY)
