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
            logger.info('Table "users" created')

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


if __name__ == '__main__':
    sqLighter = UserTable('sql.db')
    sqLighter.add_user(5)
    sqLighter.add_new_warning(5)
