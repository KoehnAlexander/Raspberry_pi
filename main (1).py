import signal
import sys
import RPi.GPIO as GPIO
from SQL_Module import *
from I2C_Module import *
import schedule


class Scheduler:
    database_credentials_dict = {
        "user": "root",
        "password": "1234",
        "host": "localhost",
        "port": 3306,
        "database": "project"
    }
    # flags:
    is_pouring_flag = False

    def poll_sensors(self):
        print("poll sensors")
        try:
            data = self.i2c_module.read_sensor_data_i2c() # TODO: gets Type dict - does work?
            self.database.safe_new_datapoint(**data)
            self.regulate()
            self.i2c_module.send_setpoints_i2c(self.database.read_latest_setpoints())
        except:  # TODO Error type?
            print("Error while receiving/sending over I2C:")
        else:
            print("Polled successfully")

    def check_for_new_commands(self):  # TODO do we really need?
        print("check for new commands")

        new = self.database.read_latest_controldata()
        if new != self.commands:
            commands = new

    def regulate(self):
        print("regulate")
        latest_sensor_data = self.database.read_latest_datapoint()  # Order: brghtnss, ar_mstr, sl_mstr, tmprtr
        latest_control_data = self.database.read_latest_controldata()  # Order: brghtnss, prng

        # Regulate Brightness:
        if latest_sensor_data[0] != latest_control_data[0]:
            delta = latest_control_data[0] - latest_sensor_data[0]
            tmp_brightness = latest_control_data[0] + delta * 0.75  # TODO cast?

        # Regulate Moisture:
        if latest_sensor_data[2] < latest_control_data[1]:  # Define how long system waits until plant gets water
            self.is_pouring_flag = True
        if self.is_pouring_flag:
            if latest_sensor_data[2] > 230:
                self.is_pouring_flag = False

        self.database.safe_new_setpoints(tmp_brightness, self.is_pouring_flag)
        pass

    def __init__(self):
        print("init")
        self._run = True
        self.database = Database(**self.database_credentials_dict)
        self.commands = (100, 100)
        self.i2c_module = I2CModule(0x0F)
        # schedule tasks:
        schedule.every(5).seconds.do(self.poll_sensors)
        schedule.every(15).seconds.do(self.check_for_new_commands)

    def __del__(self):
        del self.database

    @property
    def run(self):
        return self._run

    @run.setter
    def run(self, value):
        self._run = value


class InterruptHandler:
    BUTTON_GPIO_RESTART = 4

    def restart(self, channel):
        scheduler.run = False

    def __init__(self, scheduler):
        self.scheduler = scheduler
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.BUTTON_GPIO_RESTART, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.BUTTON_GPIO_RESTART, GPIO.FALLING,
                              callback=self.restart, bouncetime=100)

    def __del__(self):
        GPIO.cleanup()


# MAIN FUNCTION
scheduler = Scheduler()
InterruptHandler(scheduler)

while scheduler.run:
    schedule.run_pending()
    time.sleep(1)

del scheduler
sys.exit(0)
