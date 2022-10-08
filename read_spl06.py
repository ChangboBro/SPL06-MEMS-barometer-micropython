from machine import Pin,SoftI2C
import time
from spl06 import SPL06

i2c=SoftI2C(scl=Pin(1),sda=Pin(0),freq=100_000)
tmp=i2c.scan()
print(tmp[0])
baro=SPL06(i2c)
while(1):
    print("altitude %.4f"%baro.altitude())
    print("compensated pressure:   %f"%baro.prse())
    print("scaled raw pressure:    %f"%baro.prse(False))
    print("scaled raw temperature: %f"%baro.sc_temp())
    print("calibrate data:",baro.calist)
    time.sleep(2)