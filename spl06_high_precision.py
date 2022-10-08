import time
class SPL06:#4hz refresh rate, 64 times over-sampling
    def __init__(self,i2c,addr=0x76):#read:0xef write:0xee(也有可能是0x77,到时候scan一下) 
        self.i2c=i2c
        self.addr=addr
        meas_cfg=bytearray(1)
        meas_cfg=self.read_reg(b'\x08')
        meas_cfg=val=int.from_bytes(meas_cfg,'big')
        #while(((meas_cfg&0x80)==0)or((meas_cfg&0x40)==0)):#meas_cfg&0x50!=0 :sensor_ready ,0x80coef ready
        while(meas_cfg&0xC0!=0xC0):
            time.sleep_ms(2)
            meas_cfg=self.read_reg(b'\x08')
            meas_cfg=val=int.from_bytes(meas_cfg,'big')
        self.i2c.writeto(self.addr,b'\x08\xf7')#设置meas_cfg Continuous pressure and temperature measurement
        self.i2c.writeto(self.addr,b'\x09\x04')#设置cfg_reg 因为气压是过采样了
        self.i2c.writeto(self.addr,b'\x06\x26')#设置prs_cfg 4hz 64*sample
        self.i2c.writeto(self.addr,b'\x07\xA0')#设置tmp_cfg 4hz 1*sample
        self.calist=self.calibrate()#获取校准信息 calist=[c00,c10,c20,c30,c01,c11,c21]
        
    def read_reg(self,reg,num=1):
        temp=bytearray(1)
        self.i2c.writeto(self.addr,reg)
        temp=self.i2c.readfrom(self.addr,num)
        return temp
    
    def calibrate(self):#calist=[c00,c10,c20,c30,c01,c11,c21]
        reg=bytearray(3)#3bytes的数列
        #coef c00
        reg=self.read_reg(b'\x13',3)
        #print("coef_c00 %s"%reg)#debug
        c00=int.from_bytes(reg, "big")
        c00=c00>>4#丢掉低4位
        if (reg[0]&0x80!=0):#若符号位为1,将20位补码负数按原码转换的结果复原
            c00=c00-1048576#c00-2**20
        #coef c10
        reg=self.read_reg(b'\x15',3)
        c10=int.from_bytes(reg,'big')
        c10=c10&0x0fffff
        if(c10&0x080000!=0):#若符号位为1,将20位补码负数按原码转换的结果复原
            c10=c10-1048576#c10-2**20
        #c20,c30,c01,c11,c21
        calist=[c00,c10]#calist=[c00,c10,c20,c30,c01,c11,c21]
        del reg
        reg=bytearray(2)
        #regaddlist=((b'\x1c',b'\x1d'),(b'\x20',b'\x21'),(b'\x18',b'\x19'),(b'\x1a',b'\x1b'),(b'\x1e',b'\x1f'))#(msb0,lsb0),(msb1,lsb1)...
        regaddlist=(b'\x1c',b'\x20',b'\x18',b'\x1a',b'\x1e')
        for each in regaddlist:
            '''reg[0]=self.read_reg(each[0])#msb
            reg[1]=self.read_reg(each[1])#lsb'''
            reg=self.read_reg(each,2)
            coef=int.from_bytes(reg,'big')
            if (coef&0x8000):#若符号位为1
                coef=coef-65536#coef-2**16
            calist.append(coef)
        return calist
    
    def sc_temp(self):#Traw_sc=Traw/524288（单次采样）
        rawreg=bytearray(3)
        rawreg=self.read_reg(b'\x03',3)
        #print("tmp_bn %s"%rawreg)#debug
        traw=int.from_bytes(rawreg,'big')
        if(rawreg[0]&0x80!=0):#若符号位为1，需要从补码转为原码
            traw=traw-16777216#p-2**24
        temp_rawsc=traw/524288#scale
        return temp_rawsc
    
    def prse(self,comp=True):#Praw_sc=Praw/253952 (16倍过采样)
        #Pcomp(Pa)=c00+Praw_sc*(c10+Praw_sc*(c20+Praw_sc*c30))+Traw_sc*c01+Traw_sc*Praw_sc *(c11+Praw_sc*c21)
        rawreg=bytearray(3)
        rawreg=self.read_reg(b'\x00',3)
        #print("psr_bn %s"%rawreg)#debug
        p=int.from_bytes(rawreg,'big')#当p为正数时，忽略补码与原码的区别 if p>0, 2's complement is equal to trueform
        if(rawreg[0]&0x80!=0):#若符号位为1，需要从补码转为原码 if sign bit is 1, transfer to int
            p=p-16777216#p-2**24
        p=p/1040384#scale 64
        if (comp):#校准补偿
            t=self.sc_temp()
            cl=self.calist
            pres=cl[0]+p*(cl[1]+p*(cl[2]+p*cl[3]))+t*cl[4]+t*p*(cl[5]+p*cl[6])
        else:
            pres=p
        return pres
    
    def altitude(self):
        #P=Pcomp/100
        #altitude=44330*(1-(P/1013.25)^(1/5.255))
        p=self.prse()                          #p=self.prse()/100#Pa转为hPa
        alti=44330*(1-(p/101325)**0.1902949572)#alti=44330*(1-(p/1013.25)**(1/5.255))
        return alti