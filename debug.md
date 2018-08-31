## 问题记录清单

### 使用环境

+ `ofdm`调制解调
+ 数据流图
```
 pc udp --iio--> device(tx)
 device(rx) --iio--> pc udp
```

### 用udp网络封装后出现问题清单

#### 配置
```
tx/rx bandwidth:1M
tx/rx packet_len:96
tx/rx freq:800M
```
* 接收端收不到包
   1. 调整udp发送间隔时候出现偶尔收到包的情况.
      * 原因:
   2. 修改频率为`500M`后收到包的概率大增
      * 原因: `800M`存在很多干扰杂波.比如手机`900M`等其它干扰信号

### 修改rx的packet_len后效果大为改善,丢包大幅降低

#### 配置
```
tx/rx bandwidth:20M
tx packet_len:96 rx packet_len:1000
tx/rx freq:500M
```
* 此时发送每包的数据越大越好(自定义网络包的数据)
* 发送端`packet_len`不能设置为`1024`会报错
`thread[thread-per-block[9]: <block ofdm_carrier_allocator_cvc (40)>]: Buffer too small for min_noutput_items
* `
* `rx`中`packet_len`的大小设置为`1000`后效果大为改善,而且`rx`中`packet_len`似乎大小越大越好并且不受什么限制
* `bandwidth`越宽表示该信号能分解成多个波形在不同的频率上->`频域图`,这些多个波形的频域能通过`低通滤波器`隔离出来，并通过`FFT`快速傅里叶转化为`时域图`.

### 疑问

* `rx`端的`packet_len`满足`tx`的`packet_len``2`倍关系即可?
* 由于`tx`中的`packet_len`是一次性设置的，该参数和自定义udp包中的载荷大小有关系?
* `rx`端收到数据解码后的大小总是等于`tx`端`packet_len`的大小,有什么联系?

### 可能存在的影响参数

+ 自定义发送数据包的大小和`tx`设备的`packet_len`之间关系.
+ 自定义发送数据包的间隔时间,如下图:
    ```
    data:xx
    nodata:----

        orgin:                       xx xx xx xx
        has smaller interval time:   xx--xx--xx
        has bigger  Interval time:   xx-----xx-----xx-----xx
    ```
    * 在图中`bigger`情况下接收端大部分时间都是解析的错误数据包,只有恰好命中才会解析到正确数据包?（有时间间断的波形图?）
