import os
import json
import sys

sys.path.append('./lib')

from lib.dynamixel_sdk import *

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

# Protocol version
PROTOCOL_VERSION            = 1.0
# Default setting
BAUDRATE                    = 57600
DEVICENAME                  = '/dev/ttyS2'\

DXL_ID = 3

module_data_file = open('./module_data.json')
module_data = json.load(module_data_file)



portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    getch()
    quit()
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    getch()
    quit()

print("Scanning port {port} with baudrate {baud}".format(port = DEVICENAME, baud = BAUDRATE ))
for module in module_data["devices"]:
    id, dxl_comm_result, dxl_error = packetHandler.read1ByteTxRx(portHandler, module["id"], DXL_ID)
    if (dxl_comm_result != COMM_SUCCESS) and (dxl_comm_result != COMM_RX_TIMEOUT):
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    if (id == module["id"]):
        for device in module_data["devices"]:
            if device["id"] == id:
                print("[{id}]{device}".format(device = device["title"], id = id))
                for register in device["registers"]:
                    colorSensorFlag = False
                    if id == 4:
                        brightness , dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, id, 32)
                        if brightness > 200:
                            packetHandler.write1ByteTxRx(portHandler, id, 42, 1)
                            colorSensorFlag = True
                    value = 0.0
                    if register["bytes"] == 2:
                        value, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, id, register["reg"])
                    elif register["bytes"] == 1:
                        value, dxl_comm_result, dxl_error = packetHandler.read1ByteTxRx(portHandler, id, register["reg"])
                    elif register["bytes"] == 4:
                        value, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, id, register["reg"])
                        if id == 20:
                            if register["reg"] == 24:
                                print("\t{title} : {val} {si}".format(title = register["name"], val = value/1000.0, si = "kPa"))
                                value = (float(value) * 7.452) / 1000

                            if register["reg"] == 28:
                                value = float(value * 1.0) * 0.1
                                print("\tBLYATPOINT")
                            if register["reg"] == 36:
                                value /= 100.0
                                print("\tBLYATPOINT")
                        elif id == 22:
                            if register["reg"] == 24:
                                humid_dec , dxl_comm_result, dxl_error = packetHandler.read1ByteTxRx(portHandler, id, 26)
                                value = "{i}.{d}".format(i=value, d=humid_dec)
                            if register["reg"] == 28:
                                temp_dec , dxl_comm_result, dxl_error = packetHandler.read1ByteTxRx(portHandler, id, 30)
                                value = "{i}.{d}".format(i=value, d=temp_dec)
                    if colorSensorFlag == True:
                        packetHandler.write1ByteTxRx(portHandler, id, 42, 0)
                        colorSensorFlag = False
                    print("\t{title} : {val} {si}".format(title = register["name"], val = value, si = register["si"]))





# Close port
portHandler.closePort()


