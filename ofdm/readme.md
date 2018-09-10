# ofdm 点对点数据测试

## 使用

### tx
`python benchmark_tx.py -s 128 -M 0.1 -v`  
`python send.py -v ` 接收用户输入并发送  
### rx
`python benchmark_rx.py  -v`  
`python recv.py  -v`  

### csmac + tx/rx
`python tunnel.py -v`  
`python ./tunnel.py  --ip=192.168.2.1 --nicname=tap1  -v`  

### qpsk
`python tunnel.py -m qpsk --tfreq=3500000000 --rfreq=3600000000  -v -W  500000`  
`python ./tunnel.py  -m qpsk    --ip=192.168.2.1 --nicname=tap1  -v -W 500000 --tfreq=3600000000 --rfreq=3500000000`  

## 资源
`https://blog.csdn.net/yuan1164345228/article/details/17584045`

## 现象
1. 指定发送的包越大丢包越多
2. 丢包率随着发送的时间越长而逐渐上升最高能达到90%
3. 使用`send.py` `recv.py`间断发送丢包率高达99%
4. 使用`tunnel.py`发送后，使用`wireshark`发现多次收到重复的包且`ping`延迟为`2-3s`超过`ping`命令的最大延迟，导致`ping 100% packet loss`.

## 高级术语

* 采样率  
* 增益控制模式`manual slow_attack hybrid fast_attack`  
* `source` 中的`Calibration Tracking Controls`:`in_voltage_quadrature_tracking_en` `in_voltage_rf_dc_offset_tracking_en` `in_voltage_bb_dc_offset_tracking_en`  
* 调制方式:`OFDM` `bpsk` `qpsk`  
* 载波侦听蹶值  
* `tx amplitude` `fft-length` `occupied-tones:num of occupied FFT bins` `num of bits in cyclic prefix` `snr estimate`  
* 带宽
