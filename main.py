token = '토큰'

import discord, asyncio, re, os, json, shutil
from discord_components import DiscordComponents, Button, ButtonStyle, Select, SelectOption
from collections import OrderedDict

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
DiscordComponents(client)
data = OrderedDict()

@client.event
async def on_connect():
    print(client.user)
    if not os.path.isdir('발급'):
        os.mkdir('발급')
    if not os.path.isfile('white.txt'):
        f = open('white.txt', 'w')
        f.close()

@client.event
async def on_message(message):
    if message.content.startswith('!화이트리스트'):
        if not message.author.guild_permissions.administrator:
            return
        try:
            target = message.content.split(' ')[1]
        except:
            await message.reply('아이디가 입력되지 않았습니다')
            return

        with open('white.txt', 'a') as f:
            f.write(f"{target}\n")
        await message.reply('추가 성공')
        
    if message.content == '!등록':
        if not message.author.guild_permissions.administrator:
            return

        guilds = []
        for guild in client.guilds:
            if not guild.id == message.guild.id:
                guilds.append(f"{guild.id} / {guild.name}")

        if len(guilds) == 1:
            data['main'] = re.findall(r'\d+', str(guilds))[0]
            with open('id.json', 'w') as f:
                json.dump(data, f)

            ann = await message.reply(f"`{guilds[0]}` 서버로 설정되었습니다")
            await asyncio.sleep(2)
            await ann.delete()

        elif len(guilds) == 0:
            await message.reply('봇이 접속해 있는 서버가 하나 밖에 없습니다')
            return

        else:
            guild_list = "\n".join(guilds)
            msg = await message.channel.send('서버선택', components=[Select(placeholder='SelectMenu',
                                                                  options=[SelectOption(label=guilds[0],
                                                                                        value='1',
                                                                                        emoji='1️⃣'),
                                                                           SelectOption(label=guilds[1],
                                                                                        value='2',
                                                                                        emoji='2️⃣')])])

            def check(interact):
                return interact.message.id == msg.id and interact.user.id == message.author.id

            try:
                event = await client.wait_for('select_option', check=check, timeout=10)
                label = event.component[0].label
                data['main'] = re.findall(r'\d+', str(label))[0]
                with open('id.json', 'w') as f:
                    json.dump(data, f)
                await msg.delete()

                ann = await message.reply(f"`{label}` 서버로 설정되었습니다")
                await asyncio.sleep(2)
                await ann.delete()
            except asyncio.TimeoutError:
                await message.delete()
                await msg.delete()
                return

        await message.delete()
        await message.channel.send('**버튼 클릭**', components=[Button(style=ButtonStyle.green, label="참가", custom_id="1")])

@client.event
async def on_button_click(interaction):
    if interaction.custom_id == "1":
        if os.path.isdir(f'발급/{interaction.user.id}/w'):
            await interaction.respond(content="마지막 발급 60초 이후 발급이 가능합니다")
            return

        with open('id.json', 'r') as f:
            data = json.load(f)

        main_id = data['main']
        main_guild = client.get_guild(int(main_id))
        try:
            channel = main_guild.text_channels[0]
        except:
            await interaction.respond(content="서버를 불러올 수 없습니다")

        invite_code = await channel.create_invite(max_age=20, max_uses=1, reason=str(interaction.user.id))
        await interaction.respond(content=f"20초 후 만료됩니다\n{invite_code}")

        if not os.path.isdir(f'발급/{interaction.user.id}'):
            os.mkdir(f'발급/{interaction.user.id}')
        os.mkdir(f'발급/{interaction.user.id}/w')
        await asyncio.sleep(60)
        shutil.rmtree(f'발급/{interaction.user.id}/w')

@client.event
async def on_member_join(member):
    if not os.path.isdir(f'발급/{member.id}/w'):
        with open('white.txt', 'r') as f:
            list = f.read()
        if not str(member.id) in str(list):
            await member.kick(reason='초대주소 발급명단에 미존재함')
            

client.run(token)

# 입장 초대주소 확인 > https://stackoverflow.com/questions/67498590/see-the-invite-code-used-by-a-person-who-joins-with-discord-py
