from os import environ

from discord import Client, Intents, RawReactionActionEvent, Message, TextChannel, Member

intents = Intents(messages=True, reactions=True, guilds=True, members=True)
client = Client(intents=intents)


@client.event
async def on_ready():
    print('logged in', client.user)


@client.event
async def on_raw_reaction_add(payload: RawReactionActionEvent):
    await reaction_event(payload)


@client.event
async def on_raw_reaction_remove(payload: RawReactionActionEvent):
    await reaction_event(payload)


async def reaction_event(payload: RawReactionActionEvent):
    channel: TextChannel = client.get_channel(payload.channel_id)
    member: Member = payload.member or channel.guild.get_member(payload.user_id)
    if not member:
        print('No member found')
        return
    message: Message = await channel.fetch_message(payload.message_id)
    reaction_map: dict[str, str] = dict(line.split(' for ', 1) for line in message.content.lower().split('\n'))
    role = reaction_map.get(payload.emoji.name, None)
    if not role:
        print('No emoji found')
        return
    await getattr(member, f'{payload.event_type[9:].lower()}_roles')([r for r in channel.guild.roles if r.name.lower() == role][0])


client.run(environ['discord'])
