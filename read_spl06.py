from machine import Pin,I2C
import time
#from spl06 import SPL06
from SPL06_new import SPL06

i2c=I2C(0,sda=Pin(0),scl=Pin(1),freq=400_000)
baro=SPL06(i2c)
buff=baro.rListFReg(0x10,18)
#buff=baro.read_reg(b'\x13',3)
for each in buff:
    print("0x%02X"%each,end=",")
while(1):
    tstamp=time.ticks_us()
    print("altitude %.4f"%baro.altitude())
    print("get alti time %d us"%(time.ticks_us()-tstamp))
    print("compensated pressure:   %f"%baro.sampPres())
    #print("compensated pressure:   %f"%baro.prse())
    print("compensated temperature:%f"%baro.sampTemp())
    #print("calibrate data:",baro.calist)
    time.sleep(2)
