"""I2C master for Arduino communication-module
 uCT-project by A. Koehn, M. Riess, T. Grohe and U. Neumann
 V 1.0.0 11.02.2022 15:55
"""

import time
from smbus2 import SMBus


class I2CModule:

    slaveAddress = 0x0F  # default Address: 15

    def __init__(self, slave_address):
        self.slaveAddress = slave_address
        self.bus = SMBus(1)  # 1 indicates /dev/i2c-1 TODO does this work like this?

    def __del__(self):
        del self.bus

    # values and variables:
    sensorValues = {
        "airMoisture": 0,
        "brightness": 0,
        "soilMoisture": 0,
        "temperature": 0,
    }

    def read_sensor_data_i2c(self):
        data = self.bus.read_i2c_block_data(self.slaveAddr, 2, 4)
        self.sensorValues["airMoisture"] = data[0]
        self.sensorValues["brightness"] = data[1]
        self.sensorValues["soilMoisture"] = data[2]
        self.sensorValues["temperature"] = data[3]
        print(self.sensorValues)

        return self.sensorValues

    def send_setpoints_i2c(self, setpoints):  # param: setpoints: first Brightness (byte), second pumpOn (boolean)
        if setpoints[0] < 3:
            setpoints[0] = 3
        self.bus.write_byte(self.slaveAddr, setpoints[0])
        self.bus.write_byte(self.slaveAddr, setpoints[1])
        print("SentSetPoints :" + str(setpoints[0]) + "|" + str(setpoints[1]))
        # print(setpoints)

    while True:  # loop
        time.sleep(1)
        read_sensor_data_i2c()
        time.sleep(1)
        send_setpoints_i2c()
        time.sleep(1)

    # TODO:
    # Exception handling: New class after break
