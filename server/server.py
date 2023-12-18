import os
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8117

os.system("rs485 /dev/ttyS2 1")
os.system("lsof -i :{port}".format(port = PORT))
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
DEVICENAME                  = '/dev/ttyS2'
DXL_ID = 3

module_data_file = open('./metadata.json')
module_data = json.load(module_data_file)

portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)



def scanDevices():
    if not portHandler.openPort():
        getch()
        quit()
    if not portHandler.setBaudRate(BAUDRATE):
        getch()
        quit()
    data = {
        "devices": []
    }
    device_index = 0
    for device in module_data["devices"]:
        id, dxl_comm_result, dxl_error = packetHandler.read1ByteTxRx(portHandler, device["id"], DXL_ID)
        if device["id"] == id:
            print(id)
            register_index = 0
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
                            value = "{:.2f}".format(round((value * 7.452) / 1000, 2))
                        if register["reg"] == 28:
                            value = "{:.2f}".format(round(float(value * 1.0) * 0.1 , 2))
                        if register["reg"] == 36:
                            value = value*0.1
                    elif id == 22:
                        if register["reg"] == 24:
                            humid_dec , dxl_comm_result, dxl_error = packetHandler.read1ByteTxRx(portHandler, id, 26)
                            value = "{val}".format(val =value + (humid_dec * 0.01))
                        if register["reg"] == 28:
                            temp_dec , dxl_comm_result, dxl_error = packetHandler.read1ByteTxRx(portHandler, id, 30)
                            value = "{val}.{dec}".format(val = value, dec = temp_dec)
                if colorSensorFlag == True:
                            packetHandler.write1ByteTxRx(portHandler, id, 42, 0)
                            colorSensorFlag = False
                register["value"] = value
                device["registers"][register_index] = register
                register_index = register_index + 1 
            data["devices"].append(device)
        device_index = device_index + 1
    return data


class CORSRequestHandler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        data = scanDevices()
        formatted_data = json.dumps(data)
        self.wfile.write(formatted_data.encode())

    def do_POST(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        data = self.rfile.read(content_length) # <--- Gets the data itself
        root = json.loads(data.decode())
        # print("JSON data:\n", json.dumps(root, indent = 4))
        print(root["register"]["bytes"], root["device"], root["register"]["reg"], root["value"])
        if root["register"]["bytes"] == 1:
            result , error = packetHandler.write1ByteTxRx(portHandler, int(root["device"]), int(root["register"]["reg"]), int(root["value"]))
        if root["register"]["bytes"] == 2:
            result , error = packetHandler.write2ByteTxRx(portHandler, int(root["device"]), int(root["register"]["reg"]), int(root["value"]))
        if root["register"]["bytes"] == 4:
            result , error = packetHandler.write4ByteTxRx(portHandler, int(root["device"]), int(root["register"]["reg"]), int(root["value"]))
        self.wfile.write("200".encode())

httpd = HTTPServer(('', PORT), CORSRequestHandler)
httpd.serve_forever()