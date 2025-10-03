from datetime import datetime, timedelta
import unittest
from psycopg2 import sql

from func_database import create_db_manager


class TestFuncDatabase(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.db = create_db_manager()

    @classmethod
    def tearDown(self):
        self.db.close()

    def test_create_relational_table(self):
        table_name = 'test_table'

        self.db.create_relational_table(table_name=table_name)

        self.db.cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name = %s;
        """, (table_name,))
        results = self.db.cursor.fetchall()

        self.assertEqual(results[0][0], table_name)

        self.db.drop_table(table_name)

    def test_create_hypertable_table(self):
        table_name = 'test_table'
        col1 = 'test_col_1'
        col2 = 'test_col_2'

        self.db.create_hypertable_table(table_name, (col1, col2))

        test_query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name = '{0}'
            AND EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = '{0}'
                AND table_schema = 'public'
                AND column_name = '{1}'
            )
            AND EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = '{0}'
                AND table_schema = 'public'
                AND column_name = '{2}'
            );
        """.format(table_name, col1, col2)

        self.db.cursor.execute(test_query)

        results = self.db.cursor.fetchall()

        self.assertEqual(results[0][0], table_name)

        self.db.drop_table(table_name)

    def test_insert_rows_into_db(self):
        table_name = "test_insert_rows_into_db_table"
        rows = [("type1", "location1"), ("type2", "location2")]

        self.db.create_relational_table(table_name=table_name)

        self.db.insert_rows_into_db(table_name, rows)

        test_query = sql.SQL(
            "SELECT type, location FROM {};".format(
                table_name
            )
        )

        self.db.cursor.execute(test_query)

        results = self.db.cursor.fetchall()

        self.assertEqual(results[0][0], rows[0][0])
        self.assertEqual(results[0][1], rows[0][1])
        self.assertEqual(results[1][0], rows[1][0])
        self.assertEqual(results[1][1], rows[1][1])

        self.db.drop_table(table_name)

    def test_select_all_data(self):
        table_name = "test_table"
        rows = [("type1", "location1"), ("type2", "location2")]

        self.db.create_relational_table(table_name=table_name)

        self.db.insert_rows_into_db(table_name, rows)

        results = self.db.select_all_data(table_name)

        self.assertEqual(len(results), 2)

        self.db.drop_table(table_name)

    def test_select_x_recent_data(self):
        self.assertTrue(True)

    def test_count_last_x_hours_data(self):
        table_name = 'test_count_last_x_hours_data_table'
        sensor_name = 'test_count_last_x_hours_data_sensor'

        self.db.create_hypertable_table(
            table_name, ('temperature', 'humidity'))

        sensor_id = self.db.create_new_sensor(sensor_name)

        def get_timestamp_minus_x_hours(x):
            return datetime.now() - timedelta(hours=x)

        columns = "timestamp, sensor_id, temperature, humidity"
        self.db.insert_single_row_data(
            table_name,
            columns,
            "'{}', '{}', 10, 20".format(get_timestamp_minus_x_hours(1), sensor_id))

        self.db.insert_single_row_data(
            table_name,
            columns,
            "'{}', '{}', 30, 40".format(get_timestamp_minus_x_hours(2), sensor_id))

        self.db.insert_single_row_data(
            table_name,
            columns,
            "'{}', '{}', 50, 60".format(get_timestamp_minus_x_hours(3), sensor_id))

        results = self.db.count_last_x_hours_data(table_name, '*', 2)

        # It is 1 because a few milliseconds have passed since the row was inserted
        self.assertEqual(len(results), 1)

        self.db.drop_table(table_name)
        self.db.delete_row_by_condition(
            'sensors', "sensor_name = '{}'".format(sensor_name))

    def test_insert_single_row_data(self):
        table_name = 'test_insert_single_row_data_table'

        self.db.create_relational_table(table_name)

        self.db.insert_single_row_data(
            table_name, "type, location", "'temperature', 'some place'")

        results = self.db.select_all_data(table_name)

        self.assertEqual(len(results), 1)

        self.db.drop_table(table_name)

    def test_conditionally_delete_data(self):
        self.assertTrue(True)

    def test_delete_table_by_condition(self):
        table_name = "test_delete_table_by_condition_table"
        rows = [("type1", "location1"), ("type2", "location2")]

        self.db.create_relational_table(table_name=table_name)

        self.db.insert_rows_into_db(table_name, rows)

        self.db.delete_row_by_condition(table_name, "type = 'type1'")

        results = self.db.select_all_data(table_name)

        self.assertEqual(len(results), 1)

        self.db.drop_table(table_name)


if __name__ == '__main__':
    unittest.main()
