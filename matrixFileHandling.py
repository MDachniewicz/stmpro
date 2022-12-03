# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 21:51:38 2022

@author: marek
"""
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
from struct import unpack
from datetime import datetime as dt


class Matrix():
    imageForwUp=[]
    imageBackUp=[]
    imageForwDown=[]
    imageBackDown=[]
    parameter={'BREF':''}
    parameter_marks=[]
    parameter_xfer={}
    parameter_dict={}
    
    def __init__(self, file):
        self.file=file
        self.findHeader(file)
        self.openHeader()
        self.openTopoData()
    
        
    def openIVData(self):
        pass
    
    def openIZData(self):
        pass
    
        
    def openTopoData(self):        
        f = open(self.file, mode = 'r+b')
        if f.read(12).decode() != 'ONTMATRX0101':
            print("Błędny plik z danymi.")
            
        datatag=f.read(4).decode()    
        while len(datatag)==4:
            
            if datatag=='TLKB':
                file_size=unpack('<i',f.read(4))[0]
                self.timestamp=dt.fromtimestamp(unpack('<L',f.read(4))[0])
                f.read(8)
                
            if datatag=='CSED':
                blocksize=unpack('<i',f.read(4))[0]
                csed=f.read(blocksize)
                #bricklet_size=unpack('<i',csed[24:28])[0]
                #data_item_count=unpack('<i',csed[28:32])[0]
                
            if datatag=='ATAD':
                datasize=unpack('<i',f.read(4))[0]
                data=f.read(datasize)
                
                
            try:                                   
                datatag=f.read(4).decode()
                #print(datatag) 
            except:
                print("Koniec pliku") 
                datatag=""
        f.close()        
                
        

        
        dataformat = '<%di' % int(datasize/4)
        
        self.data = np.array(unpack(dataformat, data))
        self.scale_data()
        self.reshape_data()
        
        
    def scale_data(self):
        self.data=(self.data-self.parameter_xfer['XFER_5'][2]['Factor'])/self.parameter_xfer['XFER_5'][2]['Factor']
        width=self.parameter['XYScanner.Width'][0]
        height=self.parameter['XYScanner.Height'][0]
        poitns=self.parameter['XYScanner.Points'][0]
        lines=self.parameter['XYScanner.Lines'][0]
        self.x, self.y =  np.meshgrid(np.linspace(0, width, 400), np.linspace(0, height, 400))
        
    def reshape_data(self):
        lines=self.parameter['XYScanner.Lines'][0]       
        points=self.parameter['XYScanner.Points'][0] 
        
        data= np.reshape(self.data, (-1, points))
        self.imageForwUp=data[:lines*2:2]
        self.imageBackUp=data[1:lines*2:2]
        #tmp=0
        #for x in self.data:
        #    tmp=tmp+1
        #    if (tmp//400)%2==0:
        #        self.imageForwUp.append(x)
        #    else:
        #        self.imageBackUp.append(x)
        #self.imageForwUp = np.reshape(self.imageForwUp, (-1, 400))
        
    def openHeader(self):
        f = open(self.header, mode = 'r+b')
        if f.read(12).decode() != 'ONTMATRX0101':
            print("Błędny plik nagłówkowy.")
            
        datatag=f.read(4).decode()
        
        while len(datatag)==4 and self.parameter['BREF'] != self.file:
            #print(datatag)
            if datatag=='ATEM':
                
                blocksize=unpack('<i',f.read(4))[0]
                timestamp=dt.fromtimestamp(unpack('<L',f.read(4))[0])
                #f.read(4)
                atem=f.read(blocksize)
                f.read(4)
                
                
            
            elif datatag=='DPXE': #DPXE
                
                blocksize=unpack('<i',f.read(4))[0]
                timestamp=dt.fromtimestamp(unpack('<L',f.read(4))[0]) #data
                f.read(4)
                dpxe=f.read(blocksize)
            
            elif datatag=='QESF': #QESF
                blocksize=unpack('<i',f.read(4))[0]
                
                timestamp=dt.fromtimestamp(unpack('<L',f.read(4))[0]) #data
                f.read(4)
                qesf=f.read(blocksize)
            
            elif datatag=='SPXE': #SPXE
                blocksize=unpack('<i',f.read(4))[0]
                
                timestamp=dt.fromtimestamp(unpack('<L',f.read(4))[0]) #data
                f.read(4)
                spxe=f.read(blocksize).decode('utf-16')
            
            elif datatag=='APEE':
                block_size=unpack('<i',f.read(4))[0]
                date=unpack('<L',f.read(4))[0] #date
                f.read(4)
                apee=f.read(block_size)
                num_parameters_groups=unpack('<i',apee[4:8])[0] #ilosc grup parametrow
                x=8 #x => byte shift
                for y in range(num_parameters_groups):
                    size=unpack('<i',apee[x:x+4])[0]
                    x+=4
                    
                    
                    groupname=apee[x:x+size*2].decode('utf-16')
                    x+=size*2
                    num_parameters=unpack('<i',apee[x:x+4])[0]
                    x+=4
                    
                    for z in range(num_parameters):
                        
                        size=unpack('<i',apee[x:x+4])[0]
                        
                        x+=4
                        
                        parameter=apee[x:x+size*2].decode('utf-16')
                        
                        x+=size*2
                        
                        size=unpack('<i',apee[x:x+4])[0]
                        x+=4
                        
                        unit=apee[x:x+size*2].decode('utf-16')
                        x+=size*2
                        x+=4
                        
                        data, offset = self.readData(apee, x)
                        x=offset
                            
                        name=groupname+"."+parameter    
                        self.parameter[name] = [data, unit]
            
                        
            elif datatag=='ICNI' or datatag=='WEIV' or datatag=='CORP':
                
                blocksize=unpack('<i',f.read(4))[0]
                date=unpack('<L',f.read(4))[0] #date
                f.read(4)
                tmp = f.read(blocksize)
                
                
            elif datatag=='YSCC':
                main_block_size=unpack('<i',f.read(4))[0]
                date=unpack('<L',f.read(4))[0] #date
                f.read(4)
                yscc = f.read(main_block_size)
                x=4
                
                while x<main_block_size:
                    datatag=yscc[x:x+4].decode()
                    x+=4
                    blocksize=unpack('<i',yscc[x:x+4])[0]
                    x+=4
                    x0=x
                    while (x-x0)<blocksize:
                        if datatag=='REFX':
                            size1=unpack('<i',yscc[x:x+4])[0] #blocksize
                            x+=4
                            group_number=unpack('<i',yscc[x:x+4])[0]
                            x+=4
                            size=unpack('<i',yscc[x:x+4])[0]
                            x+=4
                            groupname=yscc[x:x+size*2].decode('utf-16')
                            x+=size*2
                            size = unpack('<i',yscc[x:x+4])[0]
                            x+=4
                            unit=yscc[x:x+size*2].decode('utf-16')
                            x+=size*2
                            num_parameters=unpack('<i',yscc[x:x+4])[0]
                            x+=4
                            xfer_data = {}
                            for y in range(num_parameters):
                                size=unpack('<i',yscc[x:x+4])[0]
                                x+=4
                                parameter=yscc[x:x+size*2].decode('utf-16')
                                x+=size*2
                                data, offset = self.readData(yscc, x)
                                x=offset
                                xfer_data[parameter]=[data]
                            self.parameter_xfer["XFER_"+str(group_number)] = [groupname, unit, xfer_data]
                        elif datatag=='TCID':
                            
                            x+=8
                            num_parameters=unpack('<i',yscc[x:x+4])[0]
                            x+=4
                            for y in range(num_parameters):
                                
                                x+=16
                                size=unpack('<i',yscc[x:x+4])[0]
                                x+=4
                                parameter=yscc[x:x+size*2].decode('utf-16')
                                x+=size*2
                                size=unpack('<i',yscc[x:x+4])[0]
                                x+=4
                                parameter=yscc[x:x+size*2].decode('utf-16')
                                x+=size*2
                            num_parameters=unpack('<i',yscc[x:x+4])[0]
                            x+=4
                            for y in range(num_parameters):
                                
                                x+=4
                                channel = unpack('<i',yscc[x:x+4])[0]
                                x+=4
                                
                                x+=8
                                size=unpack('<i',yscc[x:x+4])[0]
                                x+=4
                                parameter=yscc[x:x+size*2].decode('utf-16')
                                x+=size*2
                                size=unpack('<i',yscc[x:x+4])[0]
                                x+=4
                                unit=yscc[x:x+size*2].decode('utf-16')
                                x+=size*2
                                self.parameter_dict["DICT_"+str(channel)] = [parameter, unit,'']
                            num_parameters=unpack('<i',yscc[x:x+4])[0]
                            x+=4
                            for i in range(num_parameters):
                                
                                x+=12
                                channel = unpack('<i',yscc[x:x+4])[0]
                                x+=4
                                size=unpack('<i',yscc[x:x+4])[0]
                                x+=4
                                data=yscc[x:x+size*2].decode('utf-16')
                                x+=size*2
                                self.parameter_dict["DICT_"+str(channel)][2] = data
                                
                            
                            
                  
                        else:
                            x+=blocksize
                        
                    
                
               
            elif datatag=='FERB':
                #print('AAAAAAAAA')
                blocksize=unpack('<i',f.read(4))[0]
                date=unpack('<L',f.read(4))[0] #date
                f.read(4)
                ferb = f.read(blocksize)
                size = unpack('<i',ferb[4:8])[0]
                self.parameter['BREF']=ferb[8:8+size*2].decode('utf-16')
                
                
            #elif datatag=='REFX':
                #print("AAAAAA")
                
            elif datatag=='DOMP':
                
                blocksize=unpack('<i',f.read(4))[0]
                date=unpack('<L',f.read(4))[0] #date
                f.read(4)
                domp = f.read(blocksize) 
                x=4
                size = unpack('<i',domp[x:x+4])[0]
                x+=4
                groupname=domp[x:x+size*2].decode('utf-16')
                
                x+=size*2
                size = unpack('<i',domp[x:x+4])[0]
                
                x+=4
                parameter=domp[x:x+size*2].decode('utf-16')
                
                x+=size*2
                size = unpack('<i',domp[x:x+4])[0]
                
                x+=4
                unit=domp[x:x+size*2].decode('utf-16')
                
                x+=size*2
                x+=4
                data, offset = self.readData(domp, x)
                
                name=groupname+"."+parameter  
                self.parameter[name] = [data, unit]
                
            elif datatag=='KRAM':
                
                blocksize=unpack('<i',f.read(4))[0]
                date=unpack('<L',f.read(4))[0] #date
                f.read(4)
                kram = f.read(blocksize)
                size = unpack('<i',kram[0:4])[0]
                self.parameter_marks.append(kram[4:4+size*2].decode('utf-16')) 
                
                
            try:                                   
                datatag=f.read(4).decode()
                #print(datatag) 
            except:
                print("Koniec pliku") 
                datatag=""
        f.close()
            
            
    def readData(self, datablock, offset):
        #print(datablock[offset:offset+4].decode())
        if datablock[offset:offset+4].decode()=='LOOB':
            offset+=4
            data=bool(unpack('<L', datablock[offset:offset+4])[0])
            offset+=4
            #print("AAAAAAAAAAAAAAAAAAAAAAAAA")
        elif datablock[offset:offset+4].decode()=='GNOL':
            offset+=4
            data=unpack('<l', datablock[offset:offset+4])[0]
            offset+=4
        elif datablock[offset:offset+4].decode()=='BUOD':
            
            offset+=4
            data=unpack('<d', datablock[offset:offset+8])[0]
            offset+=8
            
        elif datablock[offset:offset+4].decode()=='GRTS':
            offset+=4
            size=unpack('<i',datablock[offset:offset+4])[0]
            offset+=4
            data=datablock[offset:offset+size*2].decode('utf-16')
            offset+=size*2
            
        #print(offset)
        return data, offset
        
    def findHeader(self, filename):
        self.header=filename[:filename.rfind('--')]+"_0001.mtrx" #"Si(553)-Pb2_0001.mtrx"
        try:
            pass
        except:
            print("Nie znaleziono pliku .mtrx")
        
        
    def __repr__(self):
        print(self.data)

    def show(self):
        
        
        ax = plt.subplot()
        im = ax.pcolor(self.x*10**9, self.y*10**9, self.imageForwUp)
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        plt.colorbar(im, cax=cax)
        plt.show()
        #plt.imshow(self.imageForwUp, origin = 'lower')
        

if __name__ == "__main__":
    mtrx=Matrix("Si(553)-Pb2--29_1.Z_mtrx")
    mtrx.show()