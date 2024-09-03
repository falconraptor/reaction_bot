import unittest

from main import ReactionClient


class TestPrivateMethods(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.client = ReactionClient()

    async def test__get_reactions_from_message(self):
        message = """🥇 for Thtr 100
🎭 for Thtr 199
💃 for Thtr 230
🕺 for Thtr 424"""
        reactions = self.client._get_reactions_from_message(message)
        self.assertDictEqual(reactions, {'🥇': 'thtr 100', '🎭': 'thtr 199', '💃': 'thtr 230', '🕺': 'thtr 424'})

if __name__ == '__main__':
    unittest.main()
