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

def get_episode(url):
    soup = get_page("https://www19.gogoanime.io"+url)
    last = soup.find('ul', id = "episode_page").li.a["ep_end"]
    return last
    
def first_time():
    file = open("animelist.txt","w",encoding = 'utf-8')
    animelist = []

    soup = get_page("https://gogoanime.io/")
    online_list = get_list(soup)

    for i in online_list:
        animelist.append([i[0],i[1],get_episode(i[1])])
        print("done")

    ans = ""
    for i in range(len(animelist)):
        ans+="#####\n"
        for things in animelist[i]:
            ans+=things+"\n"
    print(ans)
    file.write(ans.strip())
    file.close()
#-------Startup-------

animelist = []

client = commands.Bot(command_prefix="!")

@client.event
async def on_ready():
    global animelist
    print("Anime has logged in")
    print(client.user.name)
    print(client.user.id)
    print("-----")
    print("Anime bot is in the servers:")
    for server in client.guilds:
        print(server.name)
    print("Bot Status Set")



    #Before you run tasks take the text file
    file = open("animelist.txt","r",encoding = 'utf-8')
    anime = file.read().split("\n")
    print(anime)
    file.close()
    animelist = []
    
    for i in range(len(anime)):
        if anime[i] == "#####":
            animelist.append([])
        else:
            animelist[-1].append(anime[i])

    check_list.start()



    
    await client.change_presence(activity = discord.Game(name = '!help for a list of commands'))


class Commands(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.command(help = "Gets the user's watch list")
    async def view(self,ctx):
        await ctx.channel.send("User {}'s list: haha jokes on u i havent done this part yet".format(ctx.author))

    @commands.command(help = "[Anime Name] to add an anime to your watch list")
    async def add(self,ctx,name):
        #search and add the latest thing
        
        try:
            await ctx.channel.send("User {}'s list will be updated to include {}.".format(ctx.author,anime))
            for i in range(len(animelist)):
                if animelist[i][0] == name:
                    animelist[i].append(ctx.author)
            
        except:
            await ctx.channel.send("Name failure. Pls type the EXACT NAME LMAOOOOO")
    @commands.command(help = "When you're a weeb and must have all the updates")
    async def suball(self,ctx):
        for i in range(len(animelist)):
            animelist[i].append(ctx.author)
        await ctx.channel.send("Everything has been added. ".format(ctx.author))

#-------Background Tasks-------
@tasks.loop(minutes = 10)
async def check_list():
    global animelist
    #Check if new episodes got updated
    """
    for i in range(len(animelist)):
        link = animelist[i][1]
        name = animelist[i][0]
        ep = animelist[i][2]
        updated_ep = get_episode(link)
        if int(ep)<int(updated_ep):
            #send update to ppl under name
            for person in animelist[i][4:]:
                await client.send_message(person,"{} got a new update!".format(name))
                print(person)
            animelist[i][2] = updated_ep
    """

    #update ongoing anime list
    print("Checking")
    soup = get_page("https://gogoanime.io/")
    online_list = get_list(soup)
    
    #Cross reference with current list
    new_anime = []
    done_anime = []
    ongoing = []
    for stuff in online_list:
        name = stuff[0]
        link = stuff[1]

        found = False
        for search in animelist:
            if search[0] == name:
                found = True
                ongoing.append(name)
                break
        if not found:
            new_anime.append(stuff)

    for stuff in range(len(animelist)):
        name = animelist[stuff][0]
        link = animelist[stuff][1]

        if not name in ongoing:
            done_anime.append([name,stuff])

    #remove the done anime
    print(done_anime)
    for i in range(len(done_anime)):
        print("Removing",done_anime[i][0])
        del animelist[done_anime[i][1]-i]
    

    #add the new anime
    print(new_anime)
    for i in new_anime:
        animelist.append([i[0],i[1],1])
        #also announce new anime hear with message

    #rewrite to file
    file = open("animelist.txt","w",encoding = 'utf-8')
    ans = ""
    for i in range(len(animelist)):
        ans+="#####\n"
        for things in animelist[i]:
            ans+=things+"\n"
    file.write(ans.strip())
    file.close()

    

        
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
