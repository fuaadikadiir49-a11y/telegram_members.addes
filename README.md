from telethon import TelegramClient, errors
from telethon.tl.functions.channels import InviteToChannelRequest
import csv
import asyncio
import os

api_id = 31443
api_hash = "11f104f3b18044056b9b24bbf"

client = TelegramClient("session", api_id, api_hash)

async def main():
    await client.start()
    
    # Kan namni irraa fudhatamu (Source Group/Channel) fi Kan itti galfamu (Target Group)
    source = input("Garee/Channel namoota irraa fuutan (fkn: @Ethiopisphon): ")
    target = input("Garee/Channel namoota itti dabalitan (fkn: @fuadethio_net): ")
    
    print("\nNamoota sassaabuu fi dabaluun eegalamee jira...")
    
    # Namoota source irra jiran hunda dubbisuuf
    async for user in client.iter_participants(source):
        try:
            # Channel irratti direct dabaluun hin danda'amu yoo channel ta'e (Group ta'uu qaba)
            await client(InviteToChannelRequest(target, [user]))
            print(f"Dabaluun milkaa'eera: {user.username or user.id}")
            await asyncio.sleep(1) # Ban irraa of eeguuf
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"Dogoggora mudateera: {e}")

with client:
    client.loop.run_until_complete(main())
