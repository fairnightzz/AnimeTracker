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
started = False
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

def get_ep(name):
    global animelist
    for i in range(len(animelist)):
        if name == animelist[i][0]:
            return animelist[i][2]
    return -1

def get_recent():
    soup = get_page("https://www19.gogoanime.io")
    recent = [[i.p.a["title"],i.find('p',class_="episode").string.split()[1]] for i in soup.find('div',class_="last_episodes loaddub").find_all('li')]
    return recent
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

def update():
    global animelist
    ans = ""
    for i in range(len(animelist)):
        ans+="#####\n"
        for noob in range(len(animelist[i])):
            ans+=animelist[i][noob]+"\n"
    file = open("animelist.txt","w",encoding = 'utf-8')
    file.write(ans.strip())
    file.close()
#-------Startup-------

animelist = []

client = commands.Bot(command_prefix="!")

@client.event
async def on_ready():
    global started
    global animelist
    print("Anime has logged in")
    print(client.user.name)
    print(client.user.id)
    print("-----")
    print("Anime bot is in the servers:")
    for server in client.guilds:
        print(server.name)
    print("Bot Status Set")

    if not started:
        started = True

        #Before you run tasks take the text file
        file = open("animelist.txt","r",encoding = 'utf-8')
        anime = file.read().split("\n")
        file.close()
        animelist = []
        
        for i in range(len(anime)):
            if anime[i] == "#####":
                animelist.append([])
            else:
                animelist[-1].append(anime[i])
        
        await client.change_presence(activity = discord.Game(name = '!help for a list of commands'))
        print("start task")
        check_list.start()
        print("end task")

class Commands(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.command(help = "Gets the user's watch list")
    async def view(self,ctx):
        await ctx.channel.send("User {}'s list: haha jokes on u i havent done this part yet".format(ctx.author))

    @commands.command(help = "[Anime Name] to add an anime to your watch list")
    async def sub(self,ctx,*name):
        #search and add the latest thing
        animename = " ".join(name)
        
        found = False
        for i in range(len(animelist)):
            if animelist[i][0] == animename:
                if not str(ctx.author.id) in animelist[i]:
                    animelist[i].append(str(ctx.author.id))
                    update()
                    await ctx.channel.send("User {}'s list will be updated to include {}.".format(ctx.author,animename))
                else:
                    await ctx.channel.send("You've already subbed to this anime.")
                found = True
                break
        if not found:
            closest = []
            for anime in animelist:
                animewords = anime[0].lower().split()
                for w in animewords:
                    if w.find(animename.lower())!=-1:
                        closest.append(anime[0])
                        break
            closest.sort()
            if len(closest)!=0:
                ans = "\n".join(closest)
                
                await ctx.channel.send("Name failure. Did you mean \n{}".format(ans))
            else:
                await ctx.channel.send("Name failure. No matches sorry :(")

    @commands.command(help = "[Anime Name] if you want to stop following this anime.")
    async def unsub(self,ctx,*name):
        animename = " ".join(name)
        found = False
        for i in range(len(animelist)):
            if animelist[i][0] == animename:
                if not str(ctx.author.id) in animelist[i]:
                    del animelist[i][animelist.index(str(ctx.author.id))]
                    update()
                    await ctx.channel.send("User {}'s list will be updated by removing {}.".format(ctx.author,animename))
                else:
                    await ctx.channel.send("You never subbed to this in the first place dummy.")
                found = True
                break
        if not found:
            await ctx.channel.send("Name failure. Pls type the EXACT NAME LMAOOOOO")
        
            
    @commands.command(help = "When you're a weeb and must have all the updates")
    async def suball(self,ctx):
        for i in range(len(animelist)):
            if not str(ctx.author.id) in animelist[i]:
                    animelist[i].append(str(ctx.author.id))
        update()
        await ctx.channel.send("Everything has been added. ".format(ctx.author))

    

#-------Background Tasks-------
        
@tasks.loop(minutes = 10)
async def check_list():
    global animelist

    recent_releases = get_recent()
    #Check if new episodes got updated
    for i in range(len(recent_releases)):
        name = recent_releases[i][0]
        updated_ep = recent_releases[i][1]
        if 1<int(updated_ep):
            ep = get_ep(name)
            if int(ep)!=-1 and int(ep)<int(updated_ep):
                #send update to ppl under name
                for person in animelist[i][3:]:
                    p = client.get_user(int(person))
                    channel = await p.create_dm()
                    await channel.send("{} got a new update!".format(name))
                    
                animelist[i][2] = updated_ep
    

    #update ongoing anime list
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
    for i in range(len(done_anime)):
        print("Removing",done_anime[i][0])
        del animelist[done_anime[i][1]-i]
    

    #add the new anime
    for i in new_anime:
        animelist.append([i[0],i[1],'1'])
        #also announce new anime hear with message

    #rewrite to file
    
    update()


    

        
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
