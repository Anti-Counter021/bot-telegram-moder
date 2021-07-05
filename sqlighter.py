import logging

import sqlite3

logger = logging.getLogger('SQLite')


class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        pass


class UserTable(SQLighter):

    def create_table(self):
        table = """
                        CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id VARCHAR(255) NOT NULL UNIQUE,
                            count_warnings INTEGER NOT NULL DEFAULT 0
                        );
                    """

        with self.connection:
            self.cursor.execute(table)
            logger.info('Table "users" has been created')

    def get_id(self, user_id: int):

        with self.connection:
            user = self.cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]
            return user

    def exists(self, user_id: int):

        with self.connection:
            user_exists = bool(
                len(self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()))
            logger.info(f'User exists = {user_exists}')
            return user_exists

    def add_user(self, user_id: int):

        with self.connection:
            logger.info(f'Add new user ({user_id})')
            if not self.exists(user_id):
                return self.cursor.execute("INSERT INTO users (user_id) VALUES (?);", (user_id,))
            return

    def get_count_warnings(self, user_id: int):

        with self.connection:
            return int(
                self.cursor.execute(
                    "SELECT count_warnings FROM users WHERE user_id = (?);", (user_id,)
                ).fetchone()[0]
            )

    def add_new_warning(self, user_id: int, set_warnings=None):

        with self.connection:
            logger.info(f'Add new warning for user with id {user_id}')
            count_warnings = self.get_count_warnings(user_id) + 1
            if set_warnings is not None:
                count_warnings = set_warnings
            return self.cursor.execute(
                "UPDATE users SET count_warnings = (?) WHERE user_id = (?);", (count_warnings, user_id,)
            )


class VoteTable(SQLighter):

    def create_table(self):
        table_kick = """
                        CREATE TABLE IF NOT EXISTS vote_kick (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            kick_id INTEGER NOT NULL,
                            count_votes INTEGER DEFAULT 0 NOT NULL,
                            message_id VARCHAR(255) NOT NULL,
                            FOREIGN KEY (kick_id) REFERENCES users(id)
                        );
                     """

        table_votes = """
                          CREATE TABLE IF NOT EXISTS votes (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              user_id INTEGER NOT NULL UNIQUE,
                              vote_id INTEGER NOT NULL,
                              FOREIGN KEY (vote_id) REFERENCES vote_kick (id),
                              FOREIGN KEY (user_id) REFERENCES users (id)
                          );
                      """

        with self.connection:
            self.cursor.execute(table_kick)
            logger.info('Table "vote_kick" has been created')
            self.cursor.execute(table_votes)
            logger.info('Table "votes" has been created')

    def get_vote_id(self, message_id: int):

        with self.connection:

            return self.cursor.execute(
                "SELECT id FROM vote_kick WHERE message_id = ?;", (message_id,)
            ).fetchone()[0]

    def create_votes_user(self, user_id: int, message_id: int):

        with self.connection:

            vote_id: int = self.get_vote_id(message_id)
            return self.cursor.execute(
                "INSERT INTO votes (user_id, vote_id) VALUES (?, ?);", (user_id, vote_id)
            )

    def create_new_vote(self, user_id: int, message_id: int, kick_id: int):

        with self.connection:

            self.cursor.execute(
                "INSERT INTO vote_kick (kick_id, count_votes, message_id) VALUES (?, ?, ?);", (kick_id, 1, message_id)
            )
            return self.create_votes_user(user_id, message_id)


if __name__ == '__main__':
    sqLighter = UserTable('sql.db')
    sqLighter.add_user(5)
    sqLighter.add_user(6)
    sqLighter.add_user(7)
    sqLighter.add_new_warning(5)
    voteLighter = VoteTable('sql.db')
    user = sqLighter.get_id(5)
    kick = sqLighter.get_id(6)
    voteLighter.create_new_vote(user, 2, kick)
    new_user_vote = sqLighter.get_id(7)
    voteLighter.create_votes_user(new_user_vote, 2)
