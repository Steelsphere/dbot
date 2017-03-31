#https://discordapp.com/oauth2/authorize?client_id=284106906945978368&scope=bot&permissions=0
#server_api = 'https://mcapi.us/server/status?ip=167.114.1.89&port=25754'
#server_api2 = 'https://eu.mc-api.net/v3/server/ping/167.114.1.89%3A25754'


import discord, sys, urllib.request, datetime, random, configparser, json

bot = discord.Client()
config = configparser.RawConfigParser()


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

    if not config.read('dbot_config.ini'):
        with open('dbot_config.ini', 'w') as f:
            f.write('#DBOT NOT CONFIGURED')


@bot.event
async def on_member_join(member):
    server_id = member.server.id
    c = member.server.default_channel
    try:
        if not config.get(server_id, 'welcome_msg_enabled'):
            return
        msg = config.get(server_id, 'welcome_msg')
    except configparser.NoSectionError:
        return
    await bot.send_message(c, f'<@{member.id}>, Welcome to the discord! {msg}')




@bot.event
async def on_message(message):
    c = message.channel

    async def do_help():
        """
        Shows the list of commands
        Can also do !help [command] for specific info
        """

        if len(message.content.split()) > 1:
            for i in cmd_dict:
                if message.content.split()[1] == i:
                    await bot.send_message(c, f'Help for {i}: {cmd_dict[i].__doc__}')
                    return

        cmdstr = 'Commands: '
        for i in cmd_dict:
            cmdstr += '{}, '.format(i)
        await bot.send_message(c, cmdstr)

    async def do_online():
        """
        Gets the status of the server
        """

        download = urllib.request.urlopen(server_api)
        data = json.loads(download.read())
        online = data['online']
        await bot.send_message(c, online)

    async def do_motd():
        """
        Gets the MOTD of the server
        """

        download = urllib.request.urlopen(server_api)
        data = json.loads(download.read())
        motd = data['motd']
        await bot.send_message(c, f'MOTD: {motd}')

    async def do_players():
        """
        Gets the maximum and current number of players on the server
        """

        download = urllib.request.urlopen(server_api)
        data = json.loads(download.read())
        max = data['players']['max']
        now = data['players']['now']
        await bot.send_message(c, f'Max: {max}')
        await bot.send_message(c, f'Now: {now}')

    async def do_lastonline():
        """
        Gets the time the server was last online
        """

        download = urllib.request.urlopen(server_api)
        data = json.loads(download.read())
        timestamp = data['last_online']
        time = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        await bot.send_message(c, 'The server was last online at: {}'.format(time))

    async def do_lastupdated():
        """
        Gets the last time the server API was updated
        """

        download = urllib.request.urlopen(server_api)
        data = json.loads(download.read())
        timestamp = data['last_updated']
        time = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        await bot.send_message(c, 'The last time the server API updated was at: {}'.format(time))

    async def do_playerlist():
        """
        Gets a list of the players currently online
        """

        download = urllib.request.urlopen(server_api2)
        data = json.loads(download.read())
        player_list = []
        try:
            for i in data['players']['sample']:
                player_list.append(i['name'])
        except KeyError:
            if data['online'] == False:
                await bot.send_message(c, 'Failed. The server is offline.')
                return
            else:
                await bot.send_message(c, 'There are no players online.')
                return
        string = ''
        for i in player_list:
            string += '{}, '.format(i)
        await bot.send_message(c, string)

    async def do_coinflip():
        """
        Simulates a coinflip
        """

        coin = ['heads', 'tails']
        rnd = random.choice(coin)
        await bot.send_message(c, '{} flipped a coin! It landed on {}.'.format(message.author.display_name, rnd))

    async def do_diceroll():
        """
        Simulates a dice roll
        """

        rnd = random.randrange(1, 13)
        await bot.send_message(c, '{} rolled a die! It landed on {}.'.format(message.author.display_name, rnd))

    async def do_config():
        """
        Configures the bot
        use !config add to add the discord server to the config
        use !config ip [ip] to set the MC server to pull data from
        use !config port [port] to set the port of the MC server
        Must have the \"Manage server\" permission or be the owner of the bot to use
        """


        async def cfg_add():
            try:
                if config[message.server.id]:
                    await bot.send_message(c, 'The channel is already configured.')
                    return
            except:
                config[message.server.id] = {
                    'server_api_1': '',
                    'server_api_2': '',
                    'welcome_msg enabled': False,
                    'welcome_msg': '',
                }

        async def cfg_ip():
            ip = message.content.split()[2]
            config[message.server.id]['server_api_1'] = f'https://mcapi.us/server/status?ip={ip}'
            config[message.server.id]['server_api_2'] = f'https://eu.mc-api.net/v3/server/ping/{ip}'

        async def cfg_port():
            port = message.content.split()[2]
            try:
                config.get(message.server.id, 'server_api_1')
                config.get(message.server.id, 'server_api_2')
            except:
                await bot.send_message(c, 'IP not configured.')
                return
            config[message.server.id]['server_api_1'] += f'&port={port}'
            config[message.server.id]['server_api_2'] += f'%3A{port}'

        async def cfg_wmsg():
            msg = message.content.split('wmsg')[1].strip()
            config[message.server.id]['welcome_msg'] = msg

        subcommands = {
            'add': cfg_add,
            'ip': cfg_ip,
            'port': cfg_port,
            'wmsg': cfg_wmsg,
        }

        appinfo = await bot.application_info()

        if message.author.display_name != appinfo.owner.name and not message.author.server_permissions.manage_server:
            await bot.send_message(c, 'You don\'t have the proper permissions to configure this bot.')
            return

        for i in subcommands:
            if message.content.split()[1] == i:
                await subcommands[i]()
                with open('dbot_config.ini', 'w') as f:
                    config.write(f)
                await bot.send_message(c, 'Success.')

    async def do_version():
        """
        Gets the Minecraft version of the server
        """

        download = urllib.request.urlopen(server_api2)
        data = json.loads(download.read())
        version = data['version']['name']
        await bot.send_message(c, f'Minecraft version {version}')

    async def do_modlist():
        """
        Gets a list of the mods the server has, if it has any
        """

        download = urllib.request.urlopen(server_api2)
        data = json.loads(download.read())
        mod_list = []
        string1 = ''
        string2 = ''
        for i in data['modinfo']['modList']:
            mod_list.append(i['modid'])
        for i in range(int(len(mod_list) / 2)):
            string1 += f'{mod_list[i]}, '
        for i in range(int(len(mod_list) / 2), len(mod_list)):
            string2 += f'{mod_list[i]}, '
        await bot.send_message(c, string1)
        await bot.send_message(c, string2)

    cmd_dict = {'!help': do_help,
                '!online': do_online,
                '!motd': do_motd,
                '!players': do_players,
                '!lastonline': do_lastonline,
                '!lastupdated': do_lastupdated,
                '!playerlist': do_playerlist,
                '!coinflip': do_coinflip,
                '!diceroll': do_diceroll,
                '!config': do_config,
                '!version': do_version,
                '!modlist': do_modlist,
                }

    print('{}: {}'.format(message.author, message.content))

    try:
        server_api = config.get(message.server.id, 'server_api_1')
        server_api2 = config.get(message.server.id, 'server_api_2')

    except configparser.NoSectionError:
        server_api = ''
        server_api2 = ''

    for i in cmd_dict:
        if message.content.startswith(i):
            print('Sending message to', message.channel.name)
            try:
                await bot.send_typing(c)
                await cmd_dict[i]()
            except:
                await bot.send_message(c, f'Error! {sys.exc_info()[1]} {sys.exc_info()[0]}')

bot.run('redacted')
