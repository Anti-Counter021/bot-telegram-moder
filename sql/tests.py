import os

import unittest

from .sqlighter import UserTable, VoteTable


class UserTableCase(unittest.TestCase):

    def setUp(self) -> None:
        self.db = UserTable('sql.db')

    def tearDown(self) -> None:
        os.remove('/home/counter/programming_projects/telegram_bots/bot_telegram_moder/sql.db')

    def test_create_user(self):
        self.db.add_user(1)
        self.assertEqual(self.db.exists(1), True)
        self.assertEqual(self.db.exists(2), False)
        self.assertEqual(self.db.get_id(1), 1)

    def test_add_warnings_for_user(self):
        self.db.add_user(1)
        self.assertEqual(self.db.get_count_warnings(1), 0)
        self.db.add_new_warning(1)
        self.assertEqual(self.db.get_count_warnings(1), 1)
        self.db.add_new_warning(1)
        self.assertEqual(self.db.get_count_warnings(1), 2)
        self.db.add_new_warning(1, 0)
        self.assertEqual(self.db.get_count_warnings(1), 0)


class VoteTableTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.message = 1
        self.user_db = UserTable('sql.db')
        self.user_id = 3545
        self.kick_id = 46848
        self.new_user_id = 464862313
        self.user_false_id = 4646843242234
        self.user_db.add_user(self.user_id)
        self.user_db.add_user(self.user_false_id)
        self.user_db.add_user(self.kick_id)
        self.user_db.add_user(self.new_user_id)
        self.user = self.user_db.get_id(self.user_id)
        self.user_false = self.user_db.get_id(self.user_false_id)
        self.kick = self.user_db.get_id(self.kick_id)
        self.new_user = self.user_db.get_id(self.new_user_id)
        self.db = VoteTable('sql.db')

    def tearDown(self) -> None:
        os.remove('/home/counter/programming_projects/telegram_bots/bot_telegram_moder/sql.db')

    def test_add_new_votes(self):
        self.db.create_new_vote(self.user, self.message, self.kick)
        self.assertEqual(self.db.exists(self.user, self.message), True)
        self.assertEqual(self.db.count_votes_for_kick(self.message), 1)
        self.db.create_votes_user(self.new_user, self.message)
        self.assertEqual(self.db.exists(self.new_user, self.message), True)
        self.assertEqual(self.db.exists(self.kick, self.message), True)
        self.assertEqual(self.db.count_votes_for_kick(self.message), 2)
        self.assertEqual(self.db.get_kick_user_id(self.message), self.kick_id)
        self.assertEqual(self.db.count_votes_for_kick(self.message, False), 1)
        self.db.create_votes_user(self.user_false, self.message, False)
        self.assertEqual(self.db.count_votes_for_kick(self.message, False), 2)


if __name__ == '__main__':
    unittest.main()
