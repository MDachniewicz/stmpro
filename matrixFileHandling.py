# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 21:51:38 2022

TO-DO:
    1. (TEST) Obsługa plików o różnych kombinacjach skanowania góra-dół w przód- w tył
    2. (TEST) Obsługa plików niepełnych
    3. Obsługa plików I, I(V) i I(Z)


@author: marek
"""
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
from struct import unpack
from datetime import datetime as dt
import os


# import Exceptions


class Matrix():
    imageForwUp = []
    imageBackUp = []
    imageForwDown = []
    imageBackDown = []
    parameter = {'BREF': ''}
    parameter['XFER'] = {}
    parameter['DICT'] = {}
    parameter_marks = []
    axes = [[1, 0], [0, 0]]

    def __init__(self, file):
        self.file = file
        self.findHeader(file)
        self.openHeader()
        self.set_file_type()
        if (self.filetype == 'Z'):
            self.openTopoData()

    def openIVData(self):
        pass

    def openIZData(self):
        pass

    def openTopoData(self):
        f = open(self.file, mode='r+b')
        if f.read(12).decode() != 'ONTMATRX0101':
            print("Błędny plik z danymi.")

        datatag = f.read(4).decode()
        while len(datatag) == 4:

            if datatag == 'TLKB':
                file_size = unpack('<i', f.read(4))[0]
                self.timestamp = dt.fromtimestamp(unpack('<L', f.read(4))[0])
                f.read(8)

            if datatag == 'CSED':
                blocksize = unpack('<i', f.read(4))[0]
                csed = f.read(blocksize)

            if datatag == 'ATAD':
                datasize = unpack('<i', f.read(4))[0]
                data = f.read(datasize)

            try:
                datatag = f.read(4).decode()
                # print(datatag)
            except:
                print("Koniec pliku")
                datatag = ""
        f.close()

        dataformat = '<%di' % int(datasize / 4)

        self.data = np.array(unpack(dataformat, data))
        self.scale_data()
        self.reshape_data()

    def set_file_type(self):
        filename, file_extension = os.path.splitext(self.file)
        if file_extension == '.Z_mtrx':
            self.filetype = 'Z'

    # Calculate physical values
    def scale_data(self):

        for key in self.parameter['DICT'].keys():
            if self.parameter['DICT'][key][0] == self.filetype:
                break
        key = 'XFER' + key[4::]

        if self.parameter["XFER"][key][0] == 'TFF_Linear1D':
            self.data = (self.data - self.parameter["XFER"][key][2]['Factor']) / self.parameter["XFER"][key][2][
                'Factor']
        else:
            self.data = (self.parameter["XFER"][key][2]['Raw_1'] - self.parameter["XFER"][key][2]['PreOffset']) * \
                        (self.data - self.parameter["XFER"][key][2]['Offset']) / (
                                self.parameter["XFER"][key][2]['NeutralFactor'] * \
                                self.parameter["XFER"][key][2]['PreFactor'])
        width = self.parameter['XYScanner.Width'][0]
        height = self.parameter['XYScanner.Height'][0]
        points = self.parameter['XYScanner.Points'][0]
        lines = self.parameter['XYScanner.Lines'][0]
        self.x, self.y = np.meshgrid(np.linspace(0, width, points), np.linspace(0, height, lines))

    def findImageAxes(self):
        if self.parameter['XYScanner.X_Retrace'][0] == True:
            self.axes[1][0] = 1
        if self.parameter['XYScanner.Y_Retrace'][0] == True:
            self.axes[0][1] = 1
        if self.parameter['XYScanner.X_Retrace'][0] == True and self.parameter['XYScanner.Y_Retrace'][0] == True:
            self.axes[1][1] = 1

    def reshape_data(self):
        lines = self.parameter['XYScanner.Lines'][0]
        points = self.parameter['XYScanner.Points'][0]
        self.findImageAxes()

        expFileSize = sum(sum(self.axes, [])) * self.parameter['XYScanner.Lines'][0] * \
                      self.parameter['XYScanner.Points'][0]

        if expFileSize != self.data.size:
            self.fill_data(expFileSize)

        data = np.reshape(self.data, (-1, points))
        if self.axes == [[1, 0], [0, 0]]:
            self.imageForwUp = data[:lines:]
        if self.axes == [[1, 0], [1, 0]]:
            self.imageForwUp = data[:lines * 2:2]
            self.imageBackUp = data[1:lines * 2:2]
        if self.axes == [[1, 1], [0, 0]]:
            self.imageForwUp = data[:lines:]
            self.imageBackDwn = data[lines * 2 + 1:lines * 4 + 1:]
        if self.axes == [[1, 1], [1, 1]]:
            self.imageForwUp = data[:lines * 2:2]
            self.imageBackUp = data[1:lines * 2:2]
            self.imageForwDwn = data[lines * 2:lines * 4 + 1:2]
            self.imageBackDwn = data[lines * 2 + 1:lines * 4 + 1:2]

    # Filling missing data with mean value of existing data
    def fill_data(self, expFileSize):
        mean = [self.data.mean()] * (expFileSize - self.data.size)
        self.data = np.concatenate((self.data, mean))

    # Reading .mtrx header containing measurement parameters
    def openHeader(self):

        try:
            f = open(self.header, mode='r+b')

            if f.read(12).decode() != 'ONTMATRX0101':
                print("Błędny plik nagłówkowy.")

            datatag = f.read(4).decode()

            while len(datatag) == 4 and self.parameter['BREF'] != self.file:
                # print(datatag)
                if datatag == 'ATEM':
                    blocksize = unpack('<i', f.read(4))[0]
                    f.read(4)  # timestamp
                    f.read(blocksize)
                    f.read(4)

                elif datatag == 'DPXE':  # DPXE
                    blocksize = unpack('<i', f.read(4))[0]
                    f.read(4)  # timestamp
                    f.read(4)
                    f.read(blocksize)

                elif datatag == 'QESF':  # QESF
                    blocksize = unpack('<i', f.read(4))[0]
                    f.read(4)  # timestamp
                    f.read(4)
                    f.read(blocksize)

                elif datatag == 'SPXE':  # SPXE
                    blocksize = unpack('<i', f.read(4))[0]
                    f.read(4)  # timestamp
                    f.read(4)
                    f.read(blocksize).decode('utf-16')

                elif datatag == 'APEE':
                    block_size = unpack('<i', f.read(4))[0]
                    date = unpack('<L', f.read(4))[0]  # date
                    f.read(4)
                    apee = f.read(block_size)
                    num_parameters_groups = unpack('<i', apee[4:8])[0]  # ilosc grup parametrow
                    x = 8  # x => byte shift
                    for y in range(num_parameters_groups):
                        size = unpack('<i', apee[x:x + 4])[0]
                        x += 4
                        groupname = apee[x:x + size * 2].decode('utf-16')
                        x += size * 2
                        num_parameters = unpack('<i', apee[x:x + 4])[0]
                        x += 4

                        for z in range(num_parameters):
                            size = unpack('<i', apee[x:x + 4])[0]
                            x += 4
                            parameter = apee[x:x + size * 2].decode('utf-16')
                            x += size * 2
                            size = unpack('<i', apee[x:x + 4])[0]
                            x += 4
                            unit = apee[x:x + size * 2].decode('utf-16')
                            x += size * 2
                            x += 4
                            data, offset = self.readData(apee, x)
                            x = offset
                            name = groupname + "." + parameter
                            self.parameter[name] = [data, unit]


                elif datatag == 'ICNI' or datatag == 'WEIV' or datatag == 'CORP':

                    blocksize = unpack('<i', f.read(4))[0]
                    date = unpack('<L', f.read(4))[0]  # date
                    f.read(4)
                    f.read(blocksize)

                elif datatag == 'YSCC':
                    main_block_size = unpack('<i', f.read(4))[0]
                    date = unpack('<L', f.read(4))[0]  # date
                    f.read(4)
                    yscc = f.read(main_block_size)
                    x = 4

                    while x < main_block_size:
                        datatag = yscc[x:x + 4].decode()
                        x += 4
                        blocksize = unpack('<i', yscc[x:x + 4])[0]
                        x += 4
                        x0 = x
                        while (x - x0) < blocksize:
                            if datatag == 'REFX':

                                size1 = unpack('<i', yscc[x:x + 4])[0]  # blocksize
                                x += 4
                                group_number = unpack('<i', yscc[x:x + 4])[0]
                                x += 4
                                size = unpack('<i', yscc[x:x + 4])[0]
                                x += 4
                                groupname = yscc[x:x + size * 2].decode('utf-16')
                                x += size * 2
                                size = unpack('<i', yscc[x:x + 4])[0]
                                x += 4
                                unit = yscc[x:x + size * 2].decode('utf-16')
                                x += size * 2
                                num_parameters = unpack('<i', yscc[x:x + 4])[0]
                                x += 4
                                xfer_data = {}
                                for y in range(num_parameters):
                                    size = unpack('<i', yscc[x:x + 4])[0]
                                    x += 4
                                    parameter = yscc[x:x + size * 2].decode('utf-16')
                                    x += size * 2
                                    data, offset = self.readData(yscc, x)
                                    x = offset
                                    xfer_data[parameter] = [data]
                                self.parameter["XFER"].update(
                                    {"XFER_" + str(group_number): [groupname, unit, xfer_data]})
                            elif datatag == 'TCID':

                                x += 8
                                num_parameters = unpack('<i', yscc[x:x + 4])[0]
                                x += 4
                                for y in range(num_parameters):
                                    x += 16
                                    size = unpack('<i', yscc[x:x + 4])[0]
                                    x += 4
                                    parameter = yscc[x:x + size * 2].decode('utf-16')
                                    x += size * 2
                                    size = unpack('<i', yscc[x:x + 4])[0]
                                    x += 4
                                    parameter = yscc[x:x + size * 2].decode('utf-16')
                                    x += size * 2
                                num_parameters = unpack('<i', yscc[x:x + 4])[0]
                                x += 4
                                for y in range(num_parameters):
                                    x += 4
                                    channel = unpack('<i', yscc[x:x + 4])[0]
                                    x += 4

                                    x += 8
                                    size = unpack('<i', yscc[x:x + 4])[0]
                                    x += 4
                                    parameter = yscc[x:x + size * 2].decode('utf-16')
                                    x += size * 2
                                    size = unpack('<i', yscc[x:x + 4])[0]
                                    x += 4
                                    unit = yscc[x:x + size * 2].decode('utf-16')
                                    x += size * 2
                                    self.parameter['DICT']["DICT_" + str(channel)] = [parameter, unit, '']
                                num_parameters = unpack('<i', yscc[x:x + 4])[0]
                                x += 4
                                for i in range(num_parameters):
                                    x += 12
                                    channel = unpack('<i', yscc[x:x + 4])[0]
                                    x += 4
                                    size = unpack('<i', yscc[x:x + 4])[0]
                                    x += 4
                                    data = yscc[x:x + size * 2].decode('utf-16')
                                    x += size * 2
                                    self.parameter['DICT']["DICT_" + str(channel)][2] = data

                            else:
                                x += blocksize

                elif datatag == 'FERB':
                    blocksize = unpack('<i', f.read(4))[0]
                    date = unpack('<L', f.read(4))[0]  # date
                    f.read(4)
                    ferb = f.read(blocksize)
                    size = unpack('<i', ferb[4:8])[0]
                    self.parameter['BREF'] = ferb[8:8 + size * 2].decode('utf-16')

                elif datatag == 'DOMP':
                    blocksize = unpack('<i', f.read(4))[0]
                    date = unpack('<L', f.read(4))[0]  # date
                    f.read(4)
                    domp = f.read(blocksize)
                    x = 4
                    size = unpack('<i', domp[x:x + 4])[0]
                    x += 4
                    groupname = domp[x:x + size * 2].decode('utf-16')
                    x += size * 2
                    size = unpack('<i', domp[x:x + 4])[0]
                    x += 4
                    parameter = domp[x:x + size * 2].decode('utf-16')
                    x += size * 2
                    size = unpack('<i', domp[x:x + 4])[0]
                    x += 4
                    unit = domp[x:x + size * 2].decode('utf-16')
                    x += size * 2
                    x += 4
                    data, offset = self.readData(domp, x)
                    name = groupname + "." + parameter
                    self.parameter[name] = [data, unit]

                elif datatag == 'KRAM':
                    blocksize = unpack('<i', f.read(4))[0]
                    date = unpack('<L', f.read(4))[0]  # date
                    f.read(4)
                    kram = f.read(blocksize)
                    size = unpack('<i', kram[0:4])[0]
                    self.parameter_marks.append(kram[4:4 + size * 2].decode('utf-16'))

                try:
                    datatag = f.read(4).decode()
                except:
                    # print("End of File")
                    datatag = ""

            f.close()
        except FileNotFoundError:
            raise FileNotFoundError('NoHeader')

    def readData(self, datablock, offset):

        if datablock[offset:offset + 4].decode() == 'LOOB':
            offset += 4
            data = bool(unpack('<L', datablock[offset:offset + 4])[0])
            offset += 4
        elif datablock[offset:offset + 4].decode() == 'GNOL':
            offset += 4
            data = unpack('<l', datablock[offset:offset + 4])[0]
            offset += 4
        elif datablock[offset:offset + 4].decode() == 'BUOD':

            offset += 4
            data = unpack('<d', datablock[offset:offset + 8])[0]
            offset += 8

        elif datablock[offset:offset + 4].decode() == 'GRTS':
            offset += 4
            size = unpack('<i', datablock[offset:offset + 4])[0]
            offset += 4
            data = datablock[offset:offset + size * 2].decode('utf-16')
            offset += size * 2

        return data, offset

    def findHeader(self, filename):

        self.header = filename[:filename.rfind('--')] + "_0001.mtrx"

    def __repr__(self):
        return 'File: ' + self.parameter['BREF']

    def show(self):
        ax = plt.subplot()
        im = ax.pcolor(self.x * 10 ** 9, self.y * 10 ** 9, self.imageForwUp)
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        ax.axis('equal')
        plt.colorbar(im, cax=cax)
        plt.show()
        # plt.imshow(self.imageForwUp, origin = 'lower')

if __name__ == "__main__":
    mtrx = Matrix("Si(553)-PbSb--51_1.Z_mtrx")
    mtrx.show()
