#!/bin/env python3

import discord
import asyncio
import os
import re
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# https://stackoverflow.com/a/840110
regex=r"(?P<url>https?://[^\s]+)"


class MyClient(discord.Client):
    #def __init__(self, con):
    #    """Called upon instanciation"""
    #    self.con = con
    #    super().__init__()
        
    async def on_ready(self):
        print(f'Logged on as {self.user}')
    
    async def on_message(self, message):
        #don't send message if it's from the bot
        if self.user.id == message.author.id:
            return
        
        #Checking if the link is unembedded
        if (re.search(r"<.*>", message.content) != None):
            return
        
        #Checking if the link is hidden.
        if (re.search(r"\|\|.*\|\|", message.content) != None):
            return

        # find all urls in the message content, store them in
        # an array if they are twitter links
        matches = re.findall(regex, message.content)
        replacements = []
        for match in matches:
            if len(replacements) == 5:
                break
            url = self.handle_url(match)
            if url:
                replacements.append(url)
        
        # only send messages if there were matches
        if len(replacements) > 0:
            # join the urls together by newlines
            await message.reply(content = "\n".join(replacements), mention_author=False)
            await asyncio.sleep(4)
            await message.edit(suppress=True)
    
    # if url contains a twitter link, replace the hostname
    # with vxtwitter. Returns False if not a twitter link.
    def handle_url(self, url):
        link = urlparse(url)
        if (link.hostname == "twitter.com" or link.hostname == "x.com") and ((re.search(r"s=46", link.query) != None) or (re.search
        ("s=20", link.query) != None)):
            return link._replace(netloc='d.fxtwitter.com').geturl()

        #Detecting if the tiktok link is shortened.
        #If the link is shortened, obtain the unshortened URL.
        elif (re.search(r"tiktok\.com", link.hostname) != None) and not (re.search(r"vxtiktok\.com", link.hostname) != None):
            if ("@" in link.path):
                return link._replace(netloc='vxtiktok.com').geturl()
            else:
                expanded = requests.get(url, allow_redirects=False)
                link = urlparse(expanded.headers['location'])
                return link._replace(netloc='vxtiktok.com').geturl()
        
        elif (re.search(r"instagram\.com", link.hostname) != None) and not (re.search(r"ddinstagram\.com", link.hostname) != None):
            return link._replace(netloc='ddinstagram.com').geturl()
        
        elif (re.search(r"reddit\.com", link.hostname) != None):
            return "https://embed.works/" + link.geturl()
        
        else:
            return False


intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(TOKEN)



