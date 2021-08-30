from os import environ
from typing import Optional

from discord import Client, Intents, RawReactionActionEvent, Message, TextChannel, Member, RawMessageUpdateEvent

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


def get_reactions_from_message(message: str) -> dict[str, str]:
    return {k: v for k, v in dict(line.strip().replace('  ', ' ').split(' for ', 1) for line in message.lower().split('\n') if ' for ' in line).items() if len(k) <= 4}


async def reaction_event(payload: RawReactionActionEvent):
    channel: TextChannel = client.get_channel(payload.channel_id)
    member: Member = payload.member or channel.guild.get_member(payload.user_id)
    if member.id == client.user.id:
        return
    if not member:
        # print('No member found')
        return
    message: Message = await channel.fetch_message(payload.message_id)
    if message.author.roles[-1].name != 'Admin':  # highest role is last
        # print('Non-admin message')
        return
    reaction_map: dict[str, str] = get_reactions_from_message(message.content)
    if not reaction_map:
        # print('Non-role message')
        return
    role = reaction_map.get(payload.emoji.name, None)
    if not role:
        print('No emoji found', repr(payload.emoji), len(payload.emoji.name), member.nick or member.display_name, message.content)
        return
    try:
        await getattr(member, f'{payload.event_type[9:].lower()}_roles')([r for r in channel.guild.roles if r.name.lower() == role][0])
    except IndexError:
        print('Role name mismatch:', role)


@client.event
async def on_message(message: Message):
    await message_event(None, message)


@client.event
async def on_message_edit(before: Message, after: Message):
    await message_event(before, after)


@client.event
async def on_raw_message_edit(payload: RawMessageUpdateEvent):
    if payload.cached_message:
        return
    channel: TextChannel = client.get_channel(payload.channel_id)
    await message_event(None, await channel.fetch_message(payload.message_id))


async def message_event(before: Optional[Message], after: Message):
    if after.author.roles[-1].name != 'Admin':  # highest role is last
        # print('Non-admin message')
        return
    before_reaction_map = {}
    if before:
        before_reaction_map = set(get_reactions_from_message(before.content).keys())
    reaction_map = set(get_reactions_from_message(after.content).keys())
    if not reaction_map:
        # print('Non-role message')
        return
    if before_reaction_map:
        for emoji in before_reaction_map - reaction_map:
            await after.remove_reaction(emoji, client.user)
    if reaction_map:
        for emoji in reaction_map:
            await after.add_reaction(emoji)

if __name__ == '__main__':
    client.run(environ['discord'])
