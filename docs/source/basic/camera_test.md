# check camera list
```
sudo arduino-linux-config carrier list
```
# Run test script
```bash
sudo bash media_carrier_devices_test.sh
```

# change camera1 to 4 lane type
```bash
sudo arduino-linux-config carrier enable media-carrier camera0=none camera1=type1-4lanes
```
# change camera1 to 2 lane type
```bash
sudo arduino-linux-config carrier enable media-carrier camera0=none camera1=type1-2lanes
```
最新版本可以直接在IDE进行操作了。
Settings -> carriers ->Enable external carriers connected to your Arduino UNO Q->enable-> 选择Camera0/1 的type1-2lanes ->重启
# Reboot
```bash
sudo reboot
```

# i2c detected
```bash
sudo i2cdetect -l
```
```bash
sudo i2cdetect -y 1
```
# Check camera status
```bash
dmesg | grep imx219
```

摄像头显示(imx219 -->Geni-I2C )
```bash
arduino@www:~$ arduino@www:~$ sudo i2cdetect -l
i2c-0   i2c             Geni-I2C                                I2C adapter
i2c-1   i2c             Qualcomm-CCI                            I2C adapter
i2c-2   i2c             Geni-I2C                                I2C adapter
i2c-3   i2c             Qualcomm-CCI                            I2C adapter
i2c-4   i2c             anx7625-aux                             I2C adapter
arduino@www:~$ sudo i2cdetect -y 1
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- UU -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --                         
arduino@www:~$ sudo i2cdetect -y 3
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: UU -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -^C
arduino@www:~$ sudo cat /sys/class/i2c-dev/i2c-3/device/3-0010/name
imx219
```

# 检查可用摄像头
```bash
cam -l
```
Available后面的
或者
```
ls /dev/video*
```
拍照
```
cam -c 1 -C1 -s "width=1280,height=720,pixelformat=BGR888" -F"/home/arduino/frame_#.ppm"
```
或者

```bash
gst-launch-1.0 libcamerasrc camera-name=/base/soc@0/cci@5c1b000/i2c-bus@0/sensor@10 ! video/x-raw,width=1280,height=720 ! queue ! jpegenc ! multifilesink location=pattern1_%06d.jpg

# 更新系统
arduino-app-cli system update
```

在Applab使用CSI摄像头

初始化的时候调用摄像头改成
```
camera = Camera()
camera = Camera(adjustments=lambda frame: frame[::-1,:])
camera.start()
```
adjustments=lambda frame:frame[::-1,:]是上下反转画面