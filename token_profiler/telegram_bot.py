from web3 import Web3
import datetime
from time import sleep
import os
import json
import asyncio

from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (
PeerChannel
)
import re


class Telegram:
    def __init__(self, connect_on_start=False):
        self.latest_token = ""
        try:
            # Load config file
            filepath = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            configFile = filepath + "/telegram_config.json"
            #Parse details from config file
            with open(configFile) as f:
                self.config = json.load(f)
                self.username = self.config["USERNAME"]
                self.app_id = int(self.config["APP_API_ID"])
                self.api_hash = self.config["APP_API_HASH"]
                self.phone = self.config["PHONE"]
        except:
            print("You must provide a telegram_config.json file with proper credentials.")
    
        # Create the client
        self.client = TelegramClient(self.username, self.app_id, self.api_hash)
        if connect_on_start:
            self.connect()

    async def connect(self):
        self.client.start()
        print("Client Created")
        # Ensure you're authorized
        if not await self.client.is_user_authorized():
            self.client.send_code_request(self.phone)
            try:
                self.client.sign_in(self.phone, input('Enter the code: '))
            except SessionPasswordNeededError:
                self.client.sign_in(password=input('Password: '))
        
        if self.client.is_connected():
            print("Successfully connected!")

    def listen_for_messages(self, telegram_url):
        with self.client:
            #Initialise event listener for given channel
            @self.client.on(events.NewMessage(chats=telegram_url))
            async def my_event_handler(event):
                print(event.raw_text)
                
                contractPattern = re.compile(r'0x[\da-f]{40}', flags=re.IGNORECASE)
                token_addresses = contractPattern.findall(event.raw_text)
                if len(token_addresses) > 0:
                    self.latest_token = token_addresses[0]
                    #End async polling loop
                    await self.client.disconnect()
                    raise Exception("Client disconnect")

            #Connect client and run event listener
            self.client.loop.run_until_complete(self.connect())
            self.client.run_until_disconnected()
        return self.latest_token
    

    def run_scraper(self, telegram_url):
        #'with' destroys the client after the code block
        with self.client:
            #I don't know async lol, this just runs once
            self.client.loop.run_until_complete(self.connect())
            #This contains a loop to poll for messages
            self.client.loop.run_until_complete(self.scrape_channel(telegram_url))

    async def scrape_channel(self,telegram_url):
        self.channel = await self.client.get_entity(telegram_url)
        offset_id = 0
        limit = 100
        all_messages = []
        total_messages = 0
        total_count_limit = 1000

        while True:
            print("Current Offset ID is:", offset_id, "; Total Messages:", total_messages)
            history = await self.client(GetHistoryRequest(
                peer=self.channel,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0
            ))
            if not history.messages:
                break
            messages = history.messages
            for message in messages:
                all_messages.append(message.to_dict())
            offset_id = messages[len(messages) - 1].id
            total_messages = len(all_messages)
            if total_count_limit != 0 and total_messages >= total_count_limit:
                break
        
        with open('channel_messages.json', 'w') as outfile:
            json.dump(all_messages, outfile, indent=4, sort_keys=True, default=str)
