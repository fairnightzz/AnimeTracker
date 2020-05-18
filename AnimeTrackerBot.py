import discord
import os
import time
import random
import logging
from discord.ext import commands, tasks
from bs4 import BeautifulSoup
import requests
from privatekeylmao import token
TOKEN = token

#-------Scraping-------
def get_page(url):
    url = url
    data = requests.get(url)
    soup = BeautifulSoup(data.text,'lxml')
    return soup

def get_list(soup):
    newsoup = soup.find('div',class_ = "series")
    llist = [[i.a["title"],i.a["href"]] for i in newsoup.find_all('li')]
    return llist

def get_episode(soup):
    episodes = soup.find('div', id = "stats")
    

#-------Startup-------    
client = commands.Bot(command_prefix="!")

@client.event
async def on_ready():
    print("Anime has logged in")
    print(client.user.name)
    print(client.user.id)
    print("-----")
    print("Anime bot is in the servers:")
    for server in client.guilds:
        print(server.name)
    print("Bot Status Set")
    check_list.start()
    await client.change_presence(activity = discord.Game(name = '!help for a list of commands'))


class Commands(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.command(help = "Gets the user's watch list")
    async def user(self,ctx):
        await ctx.channel.send("User {}'s list:".format(ctx.author))

    @commands.command(help = "[Anime Name] to add an anime to your watch list")
    async def add(self,ctx,anime):
        #search and add the latest thing
        
        try:
            
            
            
            await ctx.channel.send("User {}'s list will be updated to include {}.".format(ctx.author,anime))
        except:
            await ctx.channel.send("Link failure")

#-------Background Tasks-------
@tasks.loop(minutes = 10)
async def check_list():
    print("Checking")
    soup = get_page("https://gogoanime.io/")
    anime_list = get_list(soup)

    #Cross reference with current list

    #then loop thru and get all da episodes
    #anime_list = get_episode(soup)

        
#To do:
"""
In order:
Every 30 mins:
Look in list and see if the ep # has increased. If so, ping all ppl under
Update the list:
What has ended, what is new, and tell ppl about those

Asynching:
User can add anime based on name
User can remove anime based on name

Maybe:
Ep number, excess stuff

"""
    
        

    
                
client.add_cog(Commands(client))
client.run(TOKEN)

