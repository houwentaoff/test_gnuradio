# ofdm 点对点数据测试

## 使用

### tx
`python benchmark_tx.py -s 128 -M 0.1 -v`
`python send.py -v ` 接收用户输入并发送
### rx
`python benchmark_rx.py  -v`
`python recv.py  -v`

## 资源
`https://blog.csdn.net/yuan1164345228/article/details/17584045`

## 现象
1. 指定发送的包越大丢包越多
2. 丢包率随着发送的时间越长而逐渐上升最高能达到90%
3. 使用`send.py` `recv.py`间断发送丢包率高达99%
