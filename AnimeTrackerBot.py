import discord
import os
import time
import random
import logging
from discord.ext import commands
from bs4 import BeautifulSoup
import requests
from privatekeylmao import token
TOKEN = token

"""
#Actual interactions
@client.event
async def on_message(message):
    
    #to make sure it doesn't error
    if message.author == client.user:
        return
    else:
        m = str(message.content)
        if message.content.startswith("-test"):

            if m.find("top")!=-1:
"""

def get_page(url):
    url = url
    data = requests.get(url)
    soup = BeautifulSoup(data.text,'lxml')
    return soup

def get_episode(soup):
    episodes = soup.find('div', id = "stats")
    print(episodes)
    e = episodes.find_all('ul')
    print(e)
    
client = commands.Bot(command_prefix="!")

@client.event
async def on_ready():
    print("PH has logged in")
    print(client.user.name)
    print(client.user.id)
    print("-----")
    print("Anime bot is in the servers:")
    for server in client.guilds:
        print(server.name)
    print("Bot Status Set")
    await client.change_presence(activity = discord.Game(name = '!help for a list of commands'))
class Commands(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.command(help = "[name] Gets the user's watch list")
    async def user(self,ctx,arg):
        await ctx.channel.send("User {}'s list:".format(arg))

    @commands.command(help = "[Username] [Anime Name] to add an anime to your watch list")
    async def add(self,ctx,name,anime):
        #search and add the latest thing
        soup = get_page(anime)
        get_episode(soup)
        try:
            
            
            await ctx.channel.send("User {}'s list will be updated to include {}.".format(name,anime))
        except:
            await ctx.channel.send("Link failure")
        

    
        

    
                
client.add_cog(Commands(client))
client.run(TOKEN)

