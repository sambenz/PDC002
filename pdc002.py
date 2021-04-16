#!/usr/bin/env python3
import hid
import time
from datetime import datetime

global init
init = datetime.now().timestamp()


def setTiming(msg):
  global init
  # timing
  abs = datetime.now().timestamp()
  a1 = int(abs) & 0XFF
  a2 = int(abs * 1000) & 0XFF
  a3 = int(abs * 1000000) & 0XFF
  if a1 == 255:
    init = datetime.now().timestamp()
  rel = abs - init
  r1 = int(rel * 100) & 0XFF
  r2 = int(rel * 1000) % 100 & 0XFF
  r3 = int(rel * 1000000) & 0XFF
  msg[2] = a1
  msg[3] = a2
  msg[4] = a3
  msg[5] = r1
  msg[6] = r2
  msg[7] = r3
  # checksum
  msg[62] = sum(msg[8:62]) & 0xFF
  msg[63] = sum(msg[0:62]) & 0xFF


def readFirmware():
  firmware = []
  msg = [0xFF, 0x55, 0x7D, 0x09, 0xFA, 0xE4, 0x41, 0x9D, 0x0B, 0x06, 0x00,
         0x2C, 0x00, 0x08, 0x00, 0x04, 0x78, 0x2F, 0xCA, 0x02, 0x30, 0xD0,
         0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x76,
         0xC8, 0xC0, 0x71, 0x18, 0x6E, 0x5D, 0x02, 0x98, 0xF7, 0x7E, 0x04,
         0x00, 0x00, 0x00, 0x00, 0x18, 0x00, 0x00, 0x00, 0x05, 0x00, 0x00,
         0x00, 0x00, 0x00, 0x00, 0x00, 0x30, 0xD0, 0x3E, 0xD4]
  addr = 0x2C
  # 52 * (25 * 40 + 24 = 1024 bytes) = 52kb
  while addr < 0xF8 + 1:
    msg[11] = addr
    setTiming(msg)
    #print("OUT" + str(msg))
    addr = addr + 4
    device.write(bytearray(msg))
    time.sleep(0.05)
    i = 0
    while i < 25:
      resp = device.read(64)
      data = resp[10:50]
      #print("IN" + str(data))
      firmware.append(data)
      i = i + 1
    resp = device.read(64)
    data = resp[10:34]
    #print("IN" + str(data))
    firmware.append(data)
  return firmware


def delete():
  msg = [255, 85, 206, 72, 50, 15, 28, 19, 8, 4, 0, 44, 0, 8, 0, 0, 60, 48, 225,
         0, 0, 0, 0, 0, 176, 242, 118, 0, 192, 3, 59, 117, 130, 60, 206, 180,
         176, 242, 118, 0, 151, 50, 221, 0, 226, 4, 5, 0, 128, 1, 0, 0, 0, 0, 0,
         0, 60, 48, 225, 0, 40, 243, 234, 196]
  addr = 0x2C
  while addr < 0xF8 + 1:
    msg[11] = addr
    setTiming(msg)
    print("OUT" + str(msg))
    addr = addr + 4
    device.write(bytearray(msg))
    time.sleep(0.05)


def write(firmware):
  msg = [255, 85, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 8, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0]
  addr0 = 0
  addr1 = 0x2C
  msg[8] = 9  # write
  for l in firmware:
    msg[9] = len(l) + 5  # payload length
    msg[10] = addr0
    addr0 = addr0 + len(l)
    msg[11] = addr1
    if addr0 > 255:
      addr0 = addr0 - 256
      addr1 = addr1 + 1
    msg[14] = len(l)  # data length
    n = 15
    for d in l:
      msg[n] = d
      n = n +1
    setTiming(msg)
    #print(msg)
    device.write(bytearray(msg))

def startWrite():
  msg = [255, 85, 206, 72, 178, 15, 28, 19, 5, 0, 0, 0, 124, 250, 133, 4, 80,
         97, 223, 0, 208, 46, 115, 40, 254, 255, 255, 255, 75, 79, 223, 0, 159,
         241, 222, 0, 208, 116, 156, 2, 248, 250, 133, 4, 24, 33, 221, 0, 208,
         116, 156, 2, 176, 64, 23, 44, 40, 243, 118, 0, 1, 0, 41, 131]
  setTiming(msg)
  print("OUT" + str(msg[8:10]))
  device.write(bytearray(msg))
  time.sleep(0.05)
  resp = device.read(64)
  print("IN" + str(resp[8:10]))


def endWrite():
  msg = [255, 85, 207, 234, 209, 24, 34, 30, 4, 0, 0, 0, 124, 250, 133, 4, 80,
         97, 223, 0, 208, 46, 115, 40, 254, 255, 255, 255, 75, 79, 223, 0, 159,
         241, 222, 0, 112, 125, 156, 2, 248, 250, 133, 4, 24, 33, 221, 0, 112,
         125, 156, 2, 176, 64, 23, 44, 40, 243, 118, 0, 0, 208, 73, 127]
  setTiming(msg)
  print("OUT" + str(msg[8:10]))
  device.write(bytearray(msg))
  time.sleep(0.05)
  resp = device.read(64)
  print("IN" + str(resp[8:10]))


def prgMode():
  msg = [0xFF, 0x55, 0x7A, 0x6B, 0xAA, 0xCC, 0x4B, 0x7F, 0x03, 0x00, 0x00,
         0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
         0x00, 0x00, 0x70, 0xF6, 0x56, 0x00, 0x4D, 0x13, 0x00, 0x10, 0x06,
         0xCD, 0x00, 0x10, 0x00, 0x00, 0x00, 0xC0, 0x00, 0x00, 0x00, 0x00,
         0x00, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
         0x40, 0x00, 0x00, 0x00, 0x00, 0xF8, 0xCC, 0x19, 0x92]
  setTiming(msg)
  print("OUT" + str(msg[8:10]))
  device.write(bytearray(msg))
  time.sleep(0.05)
  resp = device.read(64)
  print("IN" + str(resp[8:10]))


def reset():
  msg = [0xFF, 0x55, 0x7E, 0xEE, 0xAB, 0xF3, 0x32, 0xB0, 0x17, 0xFB, 0x7E,
         0x04, 0xEF, 0x38, 0xD2, 0x76, 0xE0, 0xFB, 0x1E, 0x01, 0x00, 0x00,
         0x00, 0x00, 0x18, 0x31, 0x61, 0x00, 0x00, 0x00, 0x00, 0x00, 0x70,
         0xF6, 0x56, 0x00, 0xC0, 0x03, 0x3B, 0x75, 0xFF, 0xFF, 0xFF, 0xFF,
         0x70, 0xF6, 0x56, 0x00, 0x97, 0x32, 0x5D, 0x00, 0x90, 0x03, 0x05,
         0x00, 0x80, 0x01, 0x00, 0x00, 0x00, 0x00, 0xCD, 0x0D]
  setTiming(msg)
  print("OUT" + str(msg[8:10]))
  device.write(bytearray(msg))
  time.sleep(0.05)
  resp = device.read(64)
  print("IN" + str(resp[8:10]))


# open
vendor_id = 0x0716
product_id = 0x5036
device_list = hid.enumerate(vendor_id, product_id)
path = device_list[0]['path']
device = hid.device()
device.open_path(path)
print(device.get_manufacturer_string() + " " + device.get_product_string())

f = open("firmware/9V.raw", "r")
firmware = []
for l in f:
  firmware.append([int(i) for i in l.split(" ")])
f.close()

write_enabled = False

print("Enter Prog Mode ...")
prgMode()
if write_enabled:
  print("Delete ...")
  startWrite()
  delete()
  endWrite()
  print("Write ...")
  startWrite()
  write(firmware)
  endWrite()
  time.sleep(1)
  print("Reset ...")
  reset()
else:
  print("Read ...")
  firmware_read = readFirmware()
  if firmware == firmware_read:
    print("Validated.")

device.close()
