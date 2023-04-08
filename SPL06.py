class SPL06:
    def __init__(self,i2c,addr=0x76):
        #get interface and info
        self.i2c=i2c
        self.slvAddr=addr
        #softReset
        #self.softReset()#will cause [Errno 5] EIO
        #wait
        meas_cfg=self.rListFReg(0x08)
        while(((meas_cfg[0]&0x80)==0) or ((meas_cfg[0]&0x40)==0)):
            meas_cfg=self.rListFReg(0x08)
        initList=[#start from reg 0x06
        0x44,#PRS_CFG:	16 measure/s, 16 times oversampling(cost 27.6ms)
        0xc0,#TMP_CFG:	16 measure/s, no oversampling(cost 3.6ms)
        0x07,#MEAS_CFG:	continuous pres and temp measurement
        0x04]#CFG_REG:	enable irq:0x46
        self.wList2Reg(0x06,initList)
        #get calibration list from registers
        self.calist=self.calibrate()#stored on initialize, save time for measure

    #write list to register inside device
    def wList2Reg(self,regAddr,dataList):#pointer,int,list
        dataList.insert(0,regAddr)
        self.i2c.writeto(self.slvAddr,bytearray(dataList))

    #read list from register inside device
    def rListFReg(self,regAddr,readNum=1):#pointer,int,int
        self.i2c.writeto(self.slvAddr,bytearray([regAddr]))
        return self.i2c.readfrom(self.slvAddr,readNum)

    def softReset(self):
        self.i2c.writeto(self.slvAddr,bytearray([0x0C,0x89]))#softReset

    def calibrate(self):
        buff=self.rListFReg(0x10,18)#type(buff): bytearray
        calist=[]#calist=[c0,c1,c00,c10,c01,c11,c20,c21,c30]
        if((buff[0]&0x80)!=0):
            calist.append(((buff[0]<<4)+(buff[1]>>4))-4096)
        else:
            calist.append((buff[0]<<4)+(buff[1]>>4))
        if((buff[1]&0x08)!=0):
            calist.append((((buff[1]&0x0F)<<8)+buff[2])-4096)
        else:
            calist.append(((buff[1]&0x0F)<<8)+buff[2])
        if((buff[3]&0x80)!=0):
            calist.append(((buff[3]<<12)+(buff[4]<<4)+(buff[5]>>4))-1048576)
        else:
            calist.append(((buff[3]<<12)+(buff[4]<<4)+(buff[5]>>4)))
        if((buff[5]&0x08)!=0):
            calist.append((((buff[5]&0x0F)<<16)|(buff[6]<<8)|buff[7])-1048576)
        else:
            calist.append(((buff[5]&0x0F)<<16)|(buff[6]<<8)|buff[7])
        #calist=[c0,c1,c00,c10]
        for i in range(8,18,2):
            if((buff[i]&0x80)!=0x00):
                calist.append(((buff[i]<<8)|buff[i+1])-65536)
            else:
                calist.append((buff[i]<<8)|buff[i+1])
            #calist.append((buff[i]<<8)|buff[i+1] if (buff[i]&0x80==0x00) else ((buff[i]<<8)|buff[i+1])-65536)
        return calist

    def sampTemp(self,comp=True):#comp: True:compensate, False:get ts
        buff=self.rListFReg(0x03,3)
        traw=(buff[0]<<16)|(buff[1]<<8)|buff[2] if(buff[0]&0x80==0x00) else ((buff[0]<<16)|(buff[1]<<8)|buff[2])-16_777_216
        ts=traw/524288#single, scale factor: 524288
        if(comp):
            return (self.calist[0]>>1)+self.calist[1]*ts
        else:
            return ts

    def sampPres(self):#16, scale factor: 253952
        buff=self.rListFReg(0x00,6)
        praw=(buff[0]<<16)|(buff[1]<<8)|buff[2] if(buff[0]&0x80==0x00) else ((buff[0]<<16)|(buff[1]<<8)|buff[2])-16_777_216
        ps=praw/253952#praw_sc
        traw=(buff[3]<<16)|(buff[4]<<8)|buff[5] if(buff[3]&0x80==0x00) else ((buff[3]<<16)|(buff[4]<<8)|buff[5])-16_777_216
        ts=traw/524288#single, scale factor: 524288 #save about 280us compared to #ts=self.sampTemp(comp=False)
        cl=self.calist#just for improve readability
        #return self.calist[2]+ps*(self.calist[3]+ps*(self.calist[6]+ps*self.calist[8]))+ts*self.calist[4]+ts*ps*(self.calist[5]+ps*self.calist[7])
        return cl[2]+ps*(cl[3]+ps*(cl[6]+ps*cl[8]))+ts*cl[4]+ts*ps*(cl[5]+ps*cl[7])

    def altitude(self):
        pres=self.sampPres()
        return 44330*(1-(pres/101325)**0.1902949572)#alti=44330*(1-(p/1013.25)**(1/5.255))