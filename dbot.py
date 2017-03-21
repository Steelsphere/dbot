#https://discordapp.com/oauth2/authorize?client_id=284106906945978368&scope=bot&permissions=0
#server_api = 'https://mcapi.us/server/status?ip=167.114.1.89&port=25754'
#server_api2 = 'https://eu.mc-api.net/v3/server/ping/167.114.1.89%3A25754'


import discord, sys, re, urllib.request, datetime, random, configparser

bot = discord.Client()
config = configparser.RawConfigParser()


@bot.event
async def on_ready():
    if not config.read('dbot_config.ini'):
        with open('dbot_config.ini', 'w') as f:
            f.write('#DBOT NOT CONFIGURED')

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
            await bot.send_message(c, 'Failed.')
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
            await bot.send_message(c, 'Failed.')
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

    async def do_config():

        async def cfg_add():
            try:
                if config[message.channel.id]:
                    await bot.send_message(c, 'The channel is already configured.')
            except:
                config[message.channel.id] = {
                    'server_api_1': '',
                    'server_api_2': '',
                }
                with open('dbot_config.ini', 'w') as f:
                    config.write(f)
                await bot.send_message(c, 'Success.')

        async def cfg_ip():
            ip = message.content.split()[2]
            config[message.channel.id]['server_api_1'] = f'https://mcapi.us/server/status?ip={ip}'
            config[message.channel.id]['server_api_2'] = f'https://eu.mc-api.net/v3/server/ping/{ip}'
            with open('dbot_config.ini', 'w') as f:
                config.write(f)
            await bot.send_message(c, 'Success.')

        async def cfg_port():
            port = message.content.split()[2]
            try:
                config.get(message.channel.id, 'server_api_1')
                config.get(message.channel.id, 'server_api_2')
            except:
                await bot.send_message(c, 'IP not configured.')
                return
            config[message.channel.id]['server_api_1'] += f'&port={port}'
            config[message.channel.id]['server_api_2'] += f'%3A{port}'
            with open('dbot_config.ini', 'w') as f:
                config.write(f)
            await bot.send_message(c, 'Success.')

        appinfo = await bot.application_info()
        if message.author.display_name != appinfo.owner.name:
            await bot.send_message(c, f'Only the bot owner can configure this bot. The owner is {appinfo.owner.name}')

        subcommands = {
            'add': cfg_add,
            'ip': cfg_ip,
            'port': cfg_port,
        }

        if not config.read('dbot_config.ini'):
            return

        for i in subcommands:
            if message.content.split()[1] == i:
                await subcommands[i]()

    cmd_dict = {'!test': do_test,
                '!help': do_help,
                '!online': do_online,
                '!motd': do_motd,
                '!players': do_players,
                '!lastonline': do_lastonline,
                '!lastupdated': do_lastupdated,
                '!playerlist': do_playerlist,
                '!coinflip': do_coinflip,
                '!diceroll': do_diceroll,
                '!config': do_config,
                }

    print('{}: {}'.format(message.author, message.content))

    try:
        server_api = config.get(message.channel.id, 'server_api_1')[:-1]
        server_api2 = config.get(message.channel.id, 'server_api_2')[:-1]

    except configparser.NoSectionError:
        server_api = None
        server_api2 = None

    print(server_api, server_api2)

    for i in cmd_dict:
        if message.content.startswith(i):
            print('Sending message to', message.channel.name)
            try:
                await cmd_dict[i]()
            except:
                await bot.send_message(c, 'Error! {}'.format(sys.exc_info()[1]))

bot.run('redacted')