import logging
from os import environ
from typing import Optional

from discord import Client, Intents, RawReactionActionEvent, Message, TextChannel, Member, RawMessageUpdateEvent

logger = logging.getLogger('ReactionClient')


class ReactionClient(Client):
    def __init__(self, *, loop=None, **options):
        if not options.get('intents'):
            options['intents'] = Intents(messages=True, reactions=True, guilds=True, members=True)
        super().__init__(loop=loop, **options)

    async def on_ready(self):
        logger.info('logged in', self.user)

    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        await self._reaction_event(payload)

    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        await self._reaction_event(payload)

    @staticmethod
    def _get_reactions_from_message(message: str) -> dict[str, str]:
        return {k: v for k, v in dict(line.strip().replace('  ', ' ').split(' for ', 1) for line in message.lower().split('\n') if ' for ' in line).items() if len(k) <= 4}

    async def _reaction_event(self, payload: RawReactionActionEvent):
        channel: TextChannel = self.get_channel(payload.channel_id)
        member: Member = payload.member or channel.guild.get_member(payload.user_id)
        if member.id == self.user.id:
            return
        if not member:
            logger.debug('No member found')
            return
        message: Message = await channel.fetch_message(payload.message_id)
        if message.author.roles[-1].name != 'Admin':  # highest role is last
            logger.debug('Non-admin message')
            return
        reaction_map: dict[str, str] = self._get_reactions_from_message(message.content)
        if not reaction_map:
            logger.debug('Non-role message')
            return
        role = reaction_map.get(payload.emoji.name, None)
        if not role:
            logger.info('No emoji found', repr(payload.emoji), len(payload.emoji.name), member.nick or member.display_name, message.content)
            return
        try:
            await getattr(member, f'{payload.event_type[9:].lower()}_roles')([r for r in channel.guild.roles if r.name.lower() == role][0])
        except IndexError:
            logger.info('Role name mismatch:', role)

    async def on_message(self, message: Message):
        await self._message_event(None, message)

    async def on_message_edit(self, before: Message, after: Message):
        await self._message_event(before, after)

    async def on_raw_message_edit(self, payload: RawMessageUpdateEvent):
        if payload.cached_message:
            return
        channel: TextChannel = self.get_channel(payload.channel_id)
        await self._message_event(None, await channel.fetch_message(payload.message_id))

    async def _message_event(self, before: Optional[Message], after: Message):
        if after.author.roles[-1].name != 'Admin':  # highest role is last
            logger.debug('Non-admin message')
            return
        reaction_map = set(self._get_reactions_from_message(after.content).keys())
        if not reaction_map:
            logger.debug('Non-role message')
            return
        if before:
            for emoji in set(self._get_reactions_from_message(before.content).keys()) - reaction_map:
                await after.remove_reaction(emoji, self.user)
        for emoji in reaction_map:
            await after.add_reaction(emoji)

if __name__ == '__main__':
    ReactionClient().run(environ['discord'])
