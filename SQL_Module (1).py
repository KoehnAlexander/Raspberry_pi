# Module Imports
import mariadb
import sys
import time


class Database:
    def __init__(self, user, password, host, port, database):
        # Connect to MariaDB Platform
        try:
            conn = mariadb.connect(
                user=user,
                password=password,
                host=host,
                port=port,
                database=database
            )
            self.connection = conn
            self.connection.autocommit = True
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Database: {e}")
            sys.exit(1)

    def __del__(self):
        self.connection.close()

    def safe_new_datapoint(self, brightness, temperature, air_moisture, soil_moisture):
        t = time.strftime('%Y-%m-%d %H:%M:%S')
        try:
            cursor = self.connection.cursor()
            query = "INSERT INTO sensordata (timestamp, brightness, temperature, air_moisture, soil_moisture) VALUES(?,?,?,?,?)"
            cursor.execute(query, (t, brightness, temperature, air_moisture, soil_moisture))
            cursor.close()
        except mariadb.Error as e:
            print(f"Error: {e}")

    def read_latest_datapoint(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT s.brightness FROM sensordata s LIMIT 1")
        brightness = cursor.fetchone()[0]
        cursor.close()  # TODO really needed?

        cursor = self.connection.cursor()
        cursor.execute("SELECT s.air_moisture FROM sensordata s LIMIT 1")
        air_moisture = cursor.fetchone()[0]
        cursor.close()

        cursor = self.connection.cursor()
        cursor.execute("SELECT s.soil_moisture FROM sensordata s LIMIT 1")
        soil_moisture = cursor.fetchone()[0]
        cursor.close()

        cursor = self.connection.cursor()
        cursor.execute("SELECT s.temperature FROM sensordata s LIMIT 1")
        temperature = cursor.fetchone()[0]
        cursor.close()

        return brightness, air_moisture, soil_moisture, temperature

    def safe_new_setpoints(self, brightness, pouring):
        t = time.strftime('%Y-%m-%d %H:%M:%S')
        try:
            cursor = self.connection.cursor()
            query = "INSERT INTO setpoints (timestamp, r_brightness, r_pouring) VALUES(?,?,?)"
            cursor.execute(query, (t, brightness, pouring))
            cursor.close()
        except mariadb.Error as e:
            print(f"Error: {e}")
        # TODO table setpoints -> Timestamp, r_brightness, r_pouring

    def read_latest_setpoints(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT s.r_brightness FROM setpoints p LIMIT 1")
        r_brightness = cursor.fetchone()[0]
        cursor.close()  # TODO really needed?

        cursor = self.connection.cursor()
        cursor.execute("SELECT s.r_pouring FROM setpoints p LIMIT 1")
        r_pouring = cursor.fetchone()[0]
        cursor.close()

        return r_brightness, r_pouring

    def read_latest_controldata(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT c.target_brightness FROM controldata c ORDER BY c.state_number DESC LIMIT 1")
        brightness = cursor.fetchone()[0]
        cursor.close()  # TODO really needed?
        # print("Brightness:",brightness)

        cursor = self.connection.cursor()
        cursor.execute("SELECT c.target_moisture FROM controldata c ORDER BY c.state_number DESC LIMIT 1")
        moisture = cursor.fetchone()[0]
        cursor.close()
        # print("Moisture:",moisture)

        return brightness, moisture
