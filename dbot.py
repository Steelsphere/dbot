#https://discordapp.com/oauth2/authorize?client_id=284106906945978368&scope=bot&permissions=0

import discord, sys, re, urllib.request, datetime, random

bot = discord.Client()
server_api = 'https://mcapi.us/server/status?ip=167.114.1.89&port=25754'
server_api2 = 'https://eu.mc-api.net/v3/server/ping/167.114.1.89%3A25754'


@bot.event
async def on_ready():
    print('Logged in: {}'.format(bot.is_logged_in))
    info = await bot.application_info()
    print('ID: {}\nName: {}\nDescription: {}\nIcon: {}\nIcon URL: {}\nOwner: {}'.format(info.id,
                                                                                        info.name,
                                                                                        info.description,
                                                                                        info.icon,
                                                                                        info.icon_url,
                                                                                        info.owner.name,))


@bot.event
async def on_message(message):
    c = message.channel

    async def do_test():
        await bot.send_message(c, 'AAAAAAAAAAAAAAAAAAAAAAAAA!')

    async def do_help():
        cmdstr = 'Commands: '
        for i in cmd_dict:
            cmdstr += '{}, '.format(i)
        await bot.send_message(c, cmdstr)

    async def do_online():
        regex = re.compile(r'"online":true')
        download = urllib.request.urlopen(server_api)
        match = regex.search(str(download.read()))
        if match:
            await bot.send_message(c, 'The server is online.')
        else:
            await bot.send_message(c, 'The server is offline.')

    async def do_motd():
        regex = re.compile(r'"motd":"[A-z+ 0-9]+"')
        download = urllib.request.urlopen(server_api)
        match = regex.search((str(download.read())))
        if not match:
            await bot.send_message(c, 'Failed to get the MOTD.')
            return
        match = match.group()
        string = str(match).split(':')[1]
        await bot.send_message(c, 'The MOTD is: {}'.format(string))

    async def do_players():
        regex = re.compile(r'"players":{"max":[0-9]+,"now":[0-9]+}')
        download = urllib.request.urlopen(server_api)
        match = regex.search(str(download.read()))
        if not match:
            await bot.send_message(c, 'Failed to get the players.')
            return
        string = match.group()
        string = string.split(':', maxsplit=1)[1]
        strmax = string.split(',')[0].split(':')[1]
        strnow = string.split(',')[1].split(':')[1].strip('}')
        await bot.send_message(c, 'Now = {} / Max = {}'.format(strnow, strmax))

    async def do_lastonline():
        regex = re.compile(r'"last_online":"[0-9]+"')
        download = urllib.request.urlopen(server_api)
        match = regex.search(str(download.read()))
        if not match:
            await bot.send_message(c, 'Failed')
            return
        string = match.group()
        timestamp = string.split(':')[1].strip('"')
        time = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        await bot.send_message(c, 'The server was last online at: {}'.format(time))

    async def do_lastupdated():
        regex = re.compile(r'"last_updated":"[0-9]+"')
        download = urllib.request.urlopen(server_api)
        match = regex.search(str(download.read()))
        if not match:
            await bot.send_message(c, 'Failed')
            return
        string = match.group()
        timestamp = string.split(':')[1].strip('"')
        time = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        await bot.send_message(c, 'The last time the server API updated was at: {}'.format(time))

    async def do_playerlist():
        regex = re.compile(r'{"id":"[A-z 0-9 -]+","name":"[A-z 0-9]+"}')
        download = urllib.request.urlopen(server_api2)
        match_list = regex.findall(str(download.read()))
        if not match_list:
            await bot.send_message(c, 'There are no players online.')
            return
        for i in range(len(match_list)):
            match_list[i] = match_list[i].split(',')[1].split(':')[1].strip('}')
        string = 'Players online: '
        for i in match_list:
            string += '{}, '.format(i)
        await bot.send_message(c, string)

    async def do_coinflip():
        coin = ['heads', 'tails']
        rnd = random.choice(coin)
        await bot.send_message(c, '{} flipped a coin! It landed on {}.'.format(message.author.display_name, rnd))

    async def do_diceroll():
        rnd = random.randrange(1, 13)
        await bot.send_message(c, '{} rolled a die! It landed on {}.'.format(message.author.display_name, rnd))

    cmd_dict = {'!test': do_test,
                '!help':do_help,
                '!online':do_online,
                '!motd':do_motd,
                '!players':do_players,
                '!lastonline':do_lastonline,
                '!lastupdated':do_lastupdated,
                '!playerlist':do_playerlist,
                '!coinflip':do_coinflip,
                '!diceroll':do_diceroll,
                }

    print('{}: {}'.format(message.author, message.content))
    for i in cmd_dict:
        if message.content.startswith(i):
            print('Sending message to', message.channel)
            try:
                await cmd_dict[i]()
            except:
                await bot.send_message(c, 'Error! {}'.format(sys.exc_info()[1]))

bot.run('lol')
