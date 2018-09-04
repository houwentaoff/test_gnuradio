# ofdm 点对点数据测试

## 使用

### tx
`python benchmark_tx.py -s 128 -M 0.1 -v`

### rx
`python benchmark_rx.py  -v`

## 现象
1. 指定发送的包越大丢包越多
2. 丢包率随着发送的时间越长而逐渐上升最高能达到90%
