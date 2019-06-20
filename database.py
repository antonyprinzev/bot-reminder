# -*- coding: UTF-8 -*-.
import sqlite3


class Database(object):
    # TODO fetch in all returning functions
    def __init__(self, database_link, table_name):
        self.database = database_link

        self.table_name = table_name

        self.columns = None
        self.connection = None
        self.cursor = None

    def get_all(self):
        self.connect()

        self.cursor.execute("SELECT * FROM {tn}".format(tn=self.table_name))

        fetch = self.cursor.fetchall()

        self.disconnect()

        return fetch

    def get_column(self, column):
        self.connect()

        self.cursor.execute("SELECT {name} FROM {tn}"
                            .format(name=column, tn=self.table_name)
                            )

        self.disconnect()

    def total_rows(self):
        self.connect()

        self.cursor.execute("SELECT COUNT(*) FROM {tn}"
                            .format(tn=self.table_name)
                            )
        count = self.cursor.fetchall()

        self.disconnect()

        return count[0][0]

    def create_table(self, table_name):
        self.connect()

        columns = ",".join(self.columns)
        self.cursor.execute("CREATE TABLE IF NOT EXISTS {tn} ({values})"
                            .format(tn=table_name, values=columns)
                            )

        self.disconnect()

    def add_column(self, name, values_type, default_value=""):
        self.connect()

        self.cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct} "
                            "DEFAULT '{df}'".format(
            tn=self.table_name, cn=name, ct=values_type, df=default_value)
        )

        self.disconnect()

    def connect(self, cursor_class=False):
        self.connection = sqlite3.connect(self.database)

        self.cursor = self.connection.cursor(cursor_class) if cursor_class \
            else self.connection.cursor()

    def disconnect(self):
        self.connection.commit()
        self.connection.close()

        self.connection = None
        self.cursor = None


class Timetable(Database):
    def __init__(self, database_link):
        super(Timetable, self).__init__(database_link, "timetable")

    def get_all(self):
        data = super().get_all()

        for i in range(len(data)):
            data[i] = {"peer_id": data[i][0], "time": data[i][1], "text": data[i][2]}

        return data
