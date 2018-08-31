package main

import (
	"fmt"
	"net"
	"os"
	"time"
)

func udp_source() {
	data := make([]byte, 100)
	//data := []byte("00000")
	for i := 0; i < len(data); i++ {
		data[i] = byte(i)
	}
	conn, err := net.Dial("udp", "193.168.2.126:1234")
	defer conn.Close()
	if err != nil {
		fmt.Println("udp err")
		os.Exit(1)
	}
	for {
		conn.Write(data)
		//fmt.Println("send", data)
		time.Sleep(50 * time.Millisecond) //time.Second)
	}
}
func udp_sink() {
	data := make([]byte, 1024)

	addr, err := net.ResolveUDPAddr("udp", "0.0.0.0:8088")
	if err != nil {
		fmt.Println(err)
		return
	}
	listener, err := net.ListenUDP("udp", addr)
	if err != nil {
		fmt.Printf("error during read: %s", err)
		return
	}
	for {
		n, remoteAddr, err := listener.ReadFrom(data)
		if err != nil {
			fmt.Printf("error during read: %s", err)
		}
		//go func() {

		fmt.Printf("\n<%s><%s>len[%d]\n", time.Now(), remoteAddr, n)
		for i := 0; i < n; i++ {
			fmt.Printf("0x%.2X ", data[i])
		}
		fmt.Println()

		//defer listener.Close()
		//}()
	}

	defer listener.Close()
}
func main() {
	fmt.Println("send data")
	go udp_source()
	go udp_sink()
	for {
		time.Sleep(1 * time.Second)
	}
}
