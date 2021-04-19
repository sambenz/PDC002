#!/usr/bin/env python3
import hid
import time
from datetime import datetime


class PDC002:
  def __init__(self, vid, pid, verbose):
    self.verbose = verbose
    self.ts = datetime.now().timestamp()
    device_list = hid.enumerate(vid, pid)
    path = device_list[0]['path']
    self.device = hid.device()
    self.device.open_path(path)
    print(
        self.device.get_manufacturer_string() + " " + self.device.get_product_string())

  def close(self):
    self.device.close()

  def send(self, command, payload):
    # message (2 bytes fixed header)
    msg = [255, 85, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    # timing (6 bytes)
    absts = datetime.now().timestamp()
    msg[2] = int(absts) & 0XFF
    msg[3] = int(absts * 1000) & 0XFF
    msg[4] = int(absts * 1000000) & 0XFF
    if msg[2] == 255:
      self.ts = datetime.now().timestamp()
    rel = absts - self.ts
    msg[5] = int(rel * 100) & 0XFF
    msg[6] = int(rel * 1000) % 100 & 0XFF
    msg[7] = int(rel * 1000000) & 0XFF
    # command, size (2 bytes)
    msg[8] = command
    if command == 23:  # reset command is different?
      msg[9] = 250
    else:
      msg[9] = len(payload)
    o = 10
    for d in payload:  # payload
      msg[o] = d
      o = o + 1
    # checksum (2 bytes)
    msg[62] = sum(msg[8:62]) & 0xFF
    msg[63] = sum(msg[0:62]) & 0xFF
    if self.verbose:
      print("OUT " + str(msg))
    self.device.write(bytearray(msg))

  def receive(self, count):
    time.sleep(0.08)
    if count > 1:
      data = []
      for i in range(0, count):
        msg = self.device.read(64)
        data.append(msg)
        if self.verbose:
          print("IN " + str(msg))
      return data
    else:
      msg = self.device.read(64)
      if self.verbose:
        print("IN " + str(msg))
      return msg

  def reset(self):
    command = 23
    payload = [133, 4, 239, 56, 210, 118, 176, 156, 34, 1, 0, 0, 0, 0, 24, 49,
               225, 0, 0, 0, 0, 0, 176, 242, 118, 0, 192, 3, 59, 117, 255, 255,
               255, 255, 176, 242, 118, 0, 151, 50, 221, 0, 226, 4, 5, 0, 128,
               1, 0, 0, 0, 0]  # and the size of the payload is set to 250?
    self.send(command, payload)
    return self.receive(1)

  def startWrite(self):
    command = 5
    payload = []
    self.send(command, payload)
    return self.receive(1)

  def endWrite(self):
    command = 4
    payload = []
    self.send(command, payload)
    return self.receive(1)

  def progMode(self):
    command = 3
    payload = []
    self.send(command, payload)
    return self.receive(1)

  def readPpsName(self):
    command = 10
    payload = [0, 56, 0, 8, 15]
    self.send(command, payload)
    data = self.receive(1)[10:25]
    name = ""
    return name.join([chr(c) for c in data])

  def readPpsModes(self):
    command = 10
    payload = [0, 252, 0, 8, 52]
    self.send(command, payload)
    data = self.receive(1)[10:62]
    # TODO: decode https://github.com/JaCzekanski/pdc-control/blob/1db343cdd725c551d18eb0dd8e105a065344833b/src/main.cpp#L83

  def readFirmware(self):
    command = 11
    payload = [0, 44, 0, 8, 0, 4]
    firmware = []
    addr = 0x2C
    # 52 * (25 * 40 + 24 = 1024 bytes) = 52kb
    while addr < 0xF8 + 1:
      payload[1] = addr
      addr = addr + 4
      self.send(command, payload)
      answer = self.receive(26)
      i = 0
      while i < 25:
        data = answer[i][10:50]
        firmware.append(data)
        i = i + 1
      data = answer[i][10:34]
      firmware.append(data)
    return firmware

  def delete(self):
    command = 8
    payload = [0, 44, 0, 8]
    addr = 0x2C
    while addr < 0xF8 + 1:
      payload[1] = addr
      addr = addr + 4
      self.send(command, payload)

  def write(self, firmware):
    command = 9
    payload = [0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
               0]
    addr0 = 0
    addr1 = 0x2C
    payload[2] = 0
    payload[3] = 8
    for l in firmware:
      payload[0] = addr0
      addr0 = addr0 + len(l)
      payload[1] = addr1
      if addr0 > 255:
        addr0 = addr0 - 256
        addr1 = addr1 + 1
      payload[4] = len(l)  # data length
      n = 5
      for d in l:
        payload[n] = d
        n = n + 1
      self.send(command, payload)


def main():
  write_enabled = False
  verbose = True
  pdc002 = PDC002(0x0716, 0x5036, verbose)
  f = open("firmware/9V.raw", "r")
  firmware_in = []
  for l in f:
    firmware_in.append([int(i) for i in l.split(" ")])
  f.close()
  print("Enter Prog Mode ...")
  pdc002.progMode()
  if write_enabled:
    print("Delete Firmware ...")
    pdc002.startWrite()
    pdc002.delete()
    pdc002.endWrite()
    print("Write Firmware ...")
    pdc002.startWrite()
    pdc002.write(firmware_in)
    pdc002.endWrite()
    time.sleep(1)
    print("Reset ...")
    pdc002.reset()
  else:
    print("Read Firmware ...")
    firmware_read = pdc002.readFirmware()
    if firmware_in == firmware_read:
      print("Validated.")
    print(pdc002.readPpsName())  # shows something usable for PPS firmware


if __name__ == "__main__":
  main()
