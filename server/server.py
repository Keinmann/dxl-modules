import os
import json
import sys
import socket


HOST, PORT = '', 8117
os.system("rs485 /dev/ttyS2 1")
os.system("lsof -i :{port}".format(port = PORT))


socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind((HOST, PORT))
socket.listen()
print("listening on eth0:{port}".format(host= HOST, port = PORT));

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

module_data_file = open('./metadata.json')

portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

def scanDevices():
    module_data = json.load(module_data_file)
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

    # print("Scanning port {port} with baudrate {baud}".format(port = DEVICENAME, baud = BAUDRATE ))
    deviceindex = 0
    for module in module_data["devices"]:
        id, dxl_comm_result, dxl_error = packetHandler.read1ByteTxRx(portHandler, module["id"], DXL_ID)
        if (id == module["id"]):
            for device in module_data["devices"]:
                if device["id"] == id:
                    print("[{id}]{device}".format(device = device["title"], id = id))
                    regindex = 0
                    for register in device["registers"]:
                        colorSensorFlag = False
                        if id == 4:
                            brightness , dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, id, 32)
                            if brightness > 200:
                                packetHandler.write1ByteTxRx(portHandler, id, 42, 1)
                                colorSensorFlag = True
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
                                if register["reg"] == 36:
                                    value /= 100.0
                            elif id == 22:
                                if register["reg"] == 24:
                                    humid_dec , dxl_comm_result, dxl_error = packetHandler.read1ByteTxRx(portHandler, id, 26)
                                    value = value + (humid_dec * 0.01)
                                if register["reg"] == 28:
                                    temp_dec , dxl_comm_result, dxl_error = packetHandler.read1ByteTxRx(portHandler, id, 30)
                                    value = value + (temp_dec * 0.01)
                        if colorSensorFlag == True:
                            packetHandler.write1ByteTxRx(portHandler, id, 42, 0)
                            colorSensorFlag = False
                        print("\t{title} : {val} {si}".format(title = register["name"], val = value, si = register["si"]))
                        device["registers"][regindex]['value'] = value
                        module_data["devices"][deviceindex] = device
                        regindex = regindex + 1
                        
            else:
                module_data["devices"].pop(deviceindex)
        deviceindex = deviceindex+1                   
    portHandler.closePort()
    print(module_data)

while True:
    conn, addr = socket.accept()
    print(f"Connected by {addr}")
    data = conn.recv(1024)
    print(f"Received {data.decode()}")
    if not data:
        break
    if data.decode() == "hello":
        conn.sendall("world".encode())
    elif data.decode() == "all":
        scanDevices()       
    else:
        conn.sendall(data)    

