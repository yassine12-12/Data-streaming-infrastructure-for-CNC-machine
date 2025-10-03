from typing import Tuple
import psycopg2
from psycopg2 import extras


def create_db_manager():
    CONNECTION = "postgres://{username}:{password}@localhost:5432/{dbname}".format(
        username='postgres', password='postgres', dbname='postgres')

    return TimescaleDB(CONNECTION)


class TimescaleDB:
    def __init__(self, connection: str):
        # CONNECTION = "postgres://{}:{}@localhost:5432/{}".format(username,password,dbname)
        self.conn = psycopg2.connect(connection)
        print("Connected to DB")
        # return object to interact with the database
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def create_relational_table(self, table_name: str):

        query_create_table = """CREATE TABLE IF NOT EXISTS {} (
                                    id SERIAL PRIMARY KEY,
                                    type VARCHAR(50),
                                    location VARCHAR(50)
                                );
                                """.format(table_name)
        self.cursor.execute(query_create_table)
        self.conn.commit()
        print("Relational table is created")

    def drop_table(self, table_name: str):
        self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        self.conn.commit()

    def create_hypertable_table(self, table_name: str, sensor_columns: Tuple[str, str]):

        try:

            query_create_table = """CREATE TABLE IF NOT EXISTS {} (
                                            timestamp TIMESTAMPTZ NOT NULL,
                                            sensor_id INTEGER,
                                            {} DOUBLE PRECISION,
                                            {} DOUBLE PRECISION,
                                            FOREIGN KEY (sensor_id) REFERENCES sensors (id) ON DELETE CASCADE
                                        );
                                        """.format(table_name, sensor_columns[0], sensor_columns[1])

            self.cursor.execute(query_create_table)

            self.conn.commit()

            self.cursor.execute(
                "SELECT create_hypertable('{}', 'timestamp')".format(table_name))

            self.conn.commit()
            print("Hypertable is created")

        except Exception as e:
            print("Exception while creating hypertable")
            print(e)
            self.cursor.close()

    def create_new_sensor(self, sensor_name: str) -> int:
        try:
            self.cursor.execute(
                "INSERT INTO sensors (sensor_name) VALUES ('{}');".format(
                    sensor_name)
            )
        except (Exception) as error:
            print(error)

        self.conn.commit()

        self.cursor.execute(
            "SELECT id FROM sensors WHERE sensor_name = '{}';".format(
                sensor_name)
        )

        row = self.cursor.fetchone()

        print("Fetching sensor: ", row)

        return row[0]

    def insert_rows_into_db(self, table_name, sensors_data):
        for sensor_data in sensors_data:
            try:
                self.cursor.execute(
                    "INSERT INTO {} (type, location) VALUES (%s, %s);".format(
                        table_name),
                    (sensor_data[0], sensor_data[1])
                )
            except (Exception, psycopg2.Error) as error:
                print(error.pgerror)
            self.conn.commit()

    def select_all_data(self, table_name: str):
        query = "SELECT * FROM {};".format(table_name)
        self.cursor.execute(query)

        all_sensor_data = self.cursor.fetchall()

        return all_sensor_data

    def select_x_recent_data(self, table_name: str, sensor_column: str | int, number_of_recent_entries: int):
        sensor_data = None
        cur = self.conn.cursor(cursor_factory=extras.RealDictCursor)

        if sensor_column == 0:

            query = "SELECT * FROM {} ORDER BY timestamp DESC LIMIT {};".format(table_name,
                                                                                number_of_recent_entries)
            cur.execute(query)
            sensor_data = cur.fetchall()
        else:
            query = "SELECT {} FROM {} ORDER BY timestamp DESC LIMIT {};".format(sensor_column, table_name,
                                                                                 number_of_recent_entries)
            cur.execute(query)
            sensor_data = cur.fetchall()

        cur.close()

        return sensor_data

    def count_last_x_hours_data(self, table_name: str, sensor_column: str, last_hours: int):

        query = "SELECT COUNT({}) FROM {} Where timestamp > NOW() - INTERVAL '{} HOURS'".format(
            sensor_column, table_name, last_hours)

        self.cursor.execute(query)
        sensor_data = self.cursor.fetchall()
        return sensor_data

    def insert_single_row_data(self, table_name: str, sensor_column, values):
        try:
            insert = "INSERT INTO {} ({}) VALUES ({});".format(
                table_name, sensor_column, values)
            self.cursor.execute(insert)
            return
        except Exception as e:
            print(e)

    def conditionally_delete_data(self, table_name: str, sensor_column: str, bigger: bool, condition_number: float):
        if bigger == True:
            delete_data = "DELETE FROM {} WHERE {} > {};".format(
                table_name, sensor_column, condition_number)
        else:
            delete_data = "DELETE FROM {} WHERE {} < {}};".format(
                table_name, sensor_column, condition_number)
        self.cursor.execute(delete_data)
        return

    def delete_row_by_condition(self, table_name: str, condition: str):
        delete_data = "DELETE FROM {} WHERE {};".format(
            table_name, condition)
        self.cursor.execute(delete_data)
        return
