#!/usr/bin/env python3

file = "12V"

trace = []
f = open("traces/" + file + ".txt", "r")
f.readline()
cmd = ""
line = ""
for x in f:
  l = x.split(",")
  if l[1] in ["IN", "OUT", "SETUP"]:
    cmd = l[1]
  if l[1] in ["DATA0", "DATA1"]:
    line = l
  if l[1] == "ACK":
    trace.append(line[0] + "," + cmd + "," + line[1] + "," + line[5])
  elif l[1] == "NAK":
    cmd = ""
    line = ""
f.close()

def command(cmd):
  if int(cmd) == 2:
    return "ACK"
  elif int(cmd) == 3:
    return "UPGRADE MODE"
  elif int(cmd) == 5:
    return "START WRITE"
  elif int(cmd) == 4:
    return "END WRITE"
  elif int(cmd) == 9:
    return "WRITE"
  elif int(cmd) == 11:
    return "READ"  # read
  elif int(cmd) == 8:
    return "DELETE"
  elif int(cmd) == 23:
    return "RESET"
  elif int(cmd) == 10:
    return "INFO"  # read
  else:
    return str(cmd)

# communication
for x in trace:
  t = x.split(",")
  if t[3].startswith("0xFF"):  # just the pdc protocol
    data = [int(i, 16) for i in t[3].split(" ")]
    cmd = data[8]
    end = 10 + data[9]
    payload = data[10:end]
    if cmd == 10 and len(payload) == 52:
      print(t[1] + " " + command(cmd) + " (" + str(data[9]) + ") " + str(payload))
    elif cmd == 10 and len(payload) == 15:
      name = ""
      print("IN INFO " + name.join([chr(c) for c in payload]))
    else:
      print(t[1] + " " + command(cmd) + " (" + str(data[9]) + ") " + str(payload))

# firmware from write
firmware_write = []
for x in trace:
  t = x.split(",")
  if t[3].startswith("0xFF"):  # just the pdc protocol
    data = [int(i, 16) for i in t[3].split(" ")]
    end = 10 + data[9]
    if data[8] == 9:
      payload = data[10:end]
      firmware_write.append(payload[5:]) # -> firmware

# firmware from read
c = 0
firmware_read = []
for x in trace:
  t = x.split(",")
  if t[3].startswith("0xFF"):  # just the pdc protocol
    data = [int(i, 16) for i in t[3].split(" ")]
    end = 10 + data[9]
    if t[1] == "IN" and data[8] == 11:
      payload = data[10:end]
      if c < 25:
        c = c + 1
        firmware_read.append(payload) # -> firmware
      else:
        c = 0
        firmware_read.append(payload[:24]) # -> firmware

if firmware_read == firmware_write:
  print("firmware validated")
  #f = open("firmware/" + file + ".raw", "w")
  #for l in firmware_read:
  #  f.write(str(l[0]))
  #  for i in range(1,len(l)):
  #    f.write(" " + str(l[i]))
  #  f.write("\n")
  #f.close()
