package main

import (
	"fmt"
	"net"
	"os"
	"time"
)

func udp_source() {
	conn, err := net.Dial("udp", "127.0.0.1:8088")
	defer conn.Close()
	if err != nil {
		fmt.Println("udp err")
		os.Exit(1)
	}
	for {
		conn.Write([]byte("00000"))

		time.Sleep(1 * time.Second)
	}
}
func udp_sink() {
	data := make([]byte, 1024)

	addr, err := net.ResolveUDPAddr("udp", "127.0.0.1:8088")
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
		go func() {
			fmt.Printf("<%s> %s\n", remoteAddr, data[:n])

			//defer listener.Close()
		}()
	}

}
func main() {
	fmt.Println("send data")
	go udp_source()
	go udp_sink()
	for {
		time.Sleep(1 * time.Second)
	}
}
