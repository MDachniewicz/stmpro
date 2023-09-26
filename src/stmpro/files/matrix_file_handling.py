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
import re


class Matrix:
    def __init__(self, file):
        self.imageForwUp = []
        self.imageBackUp = []
        self.imageForwDown = []
        self.imageBackDown = []
        self.V = None
        self.refFile = None
        self.mtrxRef = None
        self.currentForw = np.array([])
        self.currentBack = np.array([])
        self.parameter = {'BREF': '', 'XFER': {}, 'DICT': {}}
        self.parameter_marks = []
        self.axes = [[1, 0], [0, 0]]
        self.prev_files = []
        self.next_files = []

        self.file = file
        self.findHeader(file)
        self.openHeader()
        self.set_file_type()
        if self.datatype == 'Z':
            self.openTopoData()
        if self.datatype == 'I':
            self.openTopoData()
        if self.datatype == 'I(V)-curve':
            self.openCurveData()
        if self.datatype == 'I(V)-map':
            self.openMapData()

    def openMapData(self):
        f = open(self.file, mode='r+b')
        if f.read(12).decode() != 'ONTMATRX0101':
            print("Błędny plik z danymi.")

        datatag = f.read(4).decode()
        while len(datatag) == 4:
            if datatag == 'TLKB':
                f.read(4)  # filesize
                self.timestamp = dt.fromtimestamp(unpack('<L', f.read(4))[0])
                f.read(8)
            if datatag == 'CSED':
                blocksize = unpack('<i', f.read(4))[0]
                f.read(blocksize)  # desc
            if datatag == 'ATAD':
                datasize = unpack('<i', f.read(4))[0]
                data = f.read(datasize)

            try:
                datatag = f.read(4).decode()
            except:
                datatag = ""
        f.close()

        dataformat = '<%di' % int(datasize / 4)

        self.data = np.array(unpack(dataformat, data))
        self.scale_data()
        self._processCurve()
        self._reshapeMapData()
        self._getReferenceFileMap()
        if self.refFile != None:
            self._openRefFile()

    def _reshapeMapData(self):
        points = self.parameter['XYScanner.Points'][0]
        subgridx = self.parameter['XYScanner.Subgrid_X'][0]
        xpoints = int(np.ceil(points / subgridx))
        lines = self.parameter['XYScanner.Lines'][0]
        subgridy = self.parameter['XYScanner.Subgrid_Y'][0]
        ypoints = int(np.ceil(lines / subgridy))
        vpoints = self.parameter['Spectroscopy.Device_1_Points'][0]
        rampReversal = self.parameter['Spectroscopy.Enable_Device_1_Ramp_Reversal'][0]

        width = self.parameter['XYScanner.Width'][0]
        height = self.parameter['XYScanner.Height'][0]
        self.x, self.y = np.meshgrid(np.linspace(0, width, xpoints), np.linspace(0, height, ypoints))

        if self.datatype == 'I(V)-map' and not rampReversal:
            expectedNumOfPoints = xpoints * ypoints * vpoints
            if self.data.size < expectedNumOfPoints:
                self.fill_data(expectedNumOfPoints)
            self.currentForw = self.data.reshape(xpoints, ypoints, vpoints)
        if self.datatype == 'I(V)-map' and rampReversal:
            expectedNumOfPoints = xpoints * ypoints * vpoints * 2
            if self.data.size < expectedNumOfPoints:
                self.fill_data(expectedNumOfPoints)
            data = self.data.reshape(-1, vpoints)
            dataForw = data[::2]
            dataBack = data[1::2]

            self.currentForw = dataForw.reshape(xpoints, ypoints, vpoints)
            self.currentBack = dataBack.reshape(xpoints, ypoints, vpoints)
            self.currentBack = self.currentBack[:, :, ::-1]

    def openCurveData(self):
        f = open(self.file, mode='r+b')
        if f.read(12).decode() != 'ONTMATRX0101':
            print("Błędny plik z danymi.")

        datatag = f.read(4).decode()
        while len(datatag) == 4:
            if datatag == 'TLKB':
                f.read(4)  # filesize
                self.timestamp = dt.fromtimestamp(unpack('<L', f.read(4))[0])
                f.read(8)
            if datatag == 'CSED':
                blocksize = unpack('<i', f.read(4))[0]
                f.read(blocksize)  # desc
            if datatag == 'ATAD':
                datasize = unpack('<i', f.read(4))[0]
                data = f.read(datasize)

            try:
                datatag = f.read(4).decode()
            except:
                datatag = ""
        f.close()

        dataformat = '<%di' % int(datasize / 4)

        self.data = np.array(unpack(dataformat, data))
        self.scale_data()
        self._processCurve()
        self._getReferenceFile()
        if self.refFile != None:
            self._openRefFile()

    def _processCurve(self):
        rampReversal = self.parameter['Spectroscopy.Enable_Device_1_Ramp_Reversal'][0]
        vstart = self.parameter['Spectroscopy.Device_1_Start'][0]
        vend = self.parameter['Spectroscopy.Device_1_End'][0]
        vpoints = self.parameter['Spectroscopy.Device_1_Points'][0]

        if self.datatype == 'I(V)-curve' or self.datatype == 'I(V)-map':
            if self.datatype == 'I(V)-curve' and not rampReversal:
                if self.data.size < vpoints:
                    self.fill_data(vpoints)
                self.currentForw = self.data
            if self.datatype == 'I(V)-curve' and rampReversal:
                if self.data.size < 2 * vpoints:
                    self.fill_data(2 * vpoints)
                self.currentForw = self.data[:vpoints]
                self.currentBack = self.data[:vpoints - 1:-1]

            self.V = np.linspace(vstart, vend, vpoints)

    def _getReferenceFileMap(self):
        for x in self.next_files:
            if x[-6:] == 'Z_mtrx':
                self.refFile = os.path.split(self.file)[0] + os.path.sep + x
                return

    def _getReferenceFile(self):
        location = [x for x in self.parameter_marks if x[0:17] == 'MTRX$STS_LOCATION'][-1][18:]
        location = re.split(',|;|%%', location)
        xloc, yloc, xpos, ypos, ref, _ = location
        self.xloc, self.yloc = int(xloc), int(yloc)
        ref = re.split('-', ref)
        channel_id, bricklet, run_cycle, _ = ref
        channel = self._channelId2channel(channel_id)
        self.refFile = self._findRefFile(channel, run_cycle, int(bricklet))

    def _channelId2channel(self, channel_id):
        for x in self.parameter['DICT']:
            if self.parameter['DICT'][x][2][2:] == channel_id:  # Omit 0x when comparing hex numbers
                return self.parameter['DICT'][x][0]

    def _findRefFile(self, channel, run_cycle, bricklet):
        path = os.path.split(self.file)[0]
        file = os.path.split(self.file)[1]
        filename_start = file.rsplit('--', 1)[0] + '--' + run_cycle
        filename_end = channel + '_mtrx'
        for filename in os.listdir(path):
            if filename.startswith(filename_start) and filename.endswith(filename_end):
                file = path + os.path.sep + filename
                f = open(file, mode='r+b')
                f.read(48)
                if bricklet == unpack('<b', f.read(1))[0]:
                    f.close()
                    return file
                f.close()
        return None

    def _openRefFile(self):
        self.mtrxRef = Matrix(self.refFile)

    def openIZData(self):
        pass

    def openTopoData(self):
        f = open(self.file, mode='r+b')
        if f.read(12).decode() != 'ONTMATRX0101':
            print("Błędny plik z danymi.")
        datatag = f.read(4).decode()
        while len(datatag) == 4:
            if datatag == 'TLKB':
                f.read(4)  # filesize
                self.timestamp = dt.fromtimestamp(unpack('<L', f.read(4))[0])
                f.read(8)
            if datatag == 'CSED':
                blocksize = unpack('<i', f.read(4))[0]
                f.read(blocksize)  # desc
            if datatag == 'ATAD':
                datasize = unpack('<i', f.read(4))[0]
                data = f.read(datasize)

            try:
                datatag = f.read(4).decode()
            except:
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
            self.datatype = 'Z'
        if file_extension == '.I_mtrx':
            self.filetype = 'I'
            self.datatype = 'I'
        if file_extension == '.I(V)_mtrx' and self.parameter['XYScanner.Enable_Subgrid'][0] == False:
            self.filetype = 'I(V)'
            self.datatype = 'I(V)-curve'
        if file_extension == '.I(V)_mtrx' and self.parameter['XYScanner.Enable_Subgrid'][0] == True:
            self.filetype = 'I(V)'
            self.datatype = 'I(V)-map'

    # Calculate physical values
    def scale_data(self):
        for key in self.parameter['DICT'].keys():
            if self.parameter['DICT'][key][0] == self.filetype:
                break
        key = 'XFER' + key[4::]

        if self.parameter["XFER"][key][0] == 'TFF_Linear1D':
            self.data = (self.data - self.parameter["XFER"][key][2]['Offset']) / self.parameter["XFER"][key][2][
                'Factor']
        else:
            self.data = (self.parameter["XFER"][key][2]['Raw_1'][0] - self.parameter["XFER"][key][2]['PreOffset'][0]) * \
                        (self.data - self.parameter["XFER"][key][2]['Offset']) / (
                                self.parameter["XFER"][key][2]['NeutralFactor'][0] * \
                                self.parameter["XFER"][key][2]['PreFactor'][0])
        # width = self.parameter['XYScanner.Width'][0]
        # height = self.parameter['XYScanner.Height'][0]
        # points = self.parameter['XYScanner.Points'][0]
        # lines = self.parameter['XYScanner.Lines'][0]
        # self.x, self.y = np.meshgrid(np.linspace(0, width, points), np.linspace(0, height, lines))

    def findImageAxes(self):
        if self.parameter['XYScanner.X_Retrace'][0] == True:
            self.axes[1][0] = 1
        if self.parameter['XYScanner.Y_Retrace'][0] == True:
            self.axes[0][1] = 1
        if self.parameter['XYScanner.X_Retrace'][0] == True and self.parameter['XYScanner.Y_Retrace'][0] == True:
            self.axes[1][1] = 1

    # Reshaping data to rectangular arrays (points x lines)
    def reshape_data(self):
        width = self.parameter['XYScanner.Width'][0]
        height = self.parameter['XYScanner.Height'][0]
        lines = self.parameter['XYScanner.Lines'][0]
        points = self.parameter['XYScanner.Points'][0]
        self.x, self.y = np.meshgrid(np.linspace(0, width, points), np.linspace(0, height, lines))
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

            while len(datatag) == 4 and self.parameter['BREF'] != os.path.split(self.file)[-1]:
                # print(datatag)
                if datatag == 'ATEM':
                    blocksize = unpack('<i', f.read(4))[0]
                    f.read(4)  # timestamp
                    f.read(4)
                    f.read(blocksize)


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
                    self.date = unpack('<L', f.read(4))[0]  # date
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
                    f.read(4)  # date
                    f.read(4)
                    f.read(blocksize)

                elif datatag == 'YSCC':
                    main_block_size = unpack('<i', f.read(4))[0]
                    f.read(4)  # date
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

                                # size1 = unpack('<i', yscc[x:x + 4])[0]  # blocksize
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
                                    x += 12
                                    size = unpack('<i', yscc[x:x + 4])[0]
                                    x += 4
                                    parameter = yscc[x:x + size * 2].decode('utf-16')
                                    x += size * 2
                                    size = unpack('<i', yscc[x:x + 4])[0]
                                    x += 4
                                    unit = yscc[x:x + size * 2].decode('utf-16')
                                    x += size * 2
                                    self.parameter['DICT']["DICT_" + str(channel)] = [parameter, unit, '', '']
                                num_parameters = unpack('<i', yscc[x:x + 4])[0]
                                x += 4
                                for i in range(num_parameters):
                                    channel_id = hex(unpack('<q', yscc[x:x + 8])[0])
                                    x += 12
                                    channel = unpack('<i', yscc[x:x + 4])[0]
                                    x += 4
                                    size = unpack('<i', yscc[x:x + 4])[0]
                                    x += 4
                                    data = yscc[x:x + size * 2].decode('utf-16')
                                    x += size * 2
                                    self.parameter['DICT']["DICT_" + str(channel)][2] = channel_id
                                    self.parameter['DICT']["DICT_" + str(channel)][3] = data

                            else:
                                x += blocksize

                elif datatag == 'FERB':
                    blocksize = unpack('<i', f.read(4))[0]
                    f.read(4)  # date
                    f.read(4)
                    ferb = f.read(blocksize)
                    size = unpack('<i', ferb[4:8])[0]
                    self.parameter['BREF'] = ferb[8:8 + size * 2].decode('utf-16')
                    self.prev_files.append(self.parameter['BREF'])

                elif datatag == 'DOMP':
                    f.tell()
                    blocksize = unpack('<i', f.read(4))[0]
                    f.read(4)  # date
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
                    f.tell()

                elif datatag == 'KRAM':
                    blocksize = unpack('<i', f.read(4))[0]
                    f.read(4)  # date
                    f.read(4)
                    kram = f.read(blocksize)
                    size = unpack('<i', kram[0:4])[0]
                    self.parameter_marks.append(kram[4:4 + size * 2].decode('utf-16'))

                try:
                    datatag = f.read(4).decode()
                except:
                    datatag = ""

            while len(datatag) == 4:
                if datatag == 'FERB':
                    blocksize = unpack('<i', f.read(4))[0]
                    f.read(4)  # date
                    f.read(4)
                    ferb = f.read(blocksize)
                    size = unpack('<i', ferb[4:8])[0]
                    self.next_files.append(ferb[8:8 + size * 2].decode('utf-16'))

                else:
                    blocksize = unpack('<i', f.read(4))[0]
                    f.seek(8, 1)
                    f.seek(blocksize, 1)

                try:
                    datatag = f.read(4).decode()
                except:
                    datatag = ""

            f.close()
        except FileNotFoundError:
            raise FileNotFoundError('NoHeader')

    # Reading data from data blocks
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

    def _plotTopo(self, xloc, yloc):
        ax = plt.subplot()
        im = ax.pcolor(self.x * 10 ** 9, self.y * 10 ** 9, self.imageForwUp)
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        ax.axis('equal')
        if xloc != None and yloc != None:
            ax.plot([self.x[yloc, xloc] * 10 ** 9], [self.y[yloc, xloc] * 10 ** 9], marker='s', markersize=10)
        plt.colorbar(im, cax=cax)
        plt.show()
        # plt.imshow(self.imageForwUp, origin = 'lower')

    def _plotCurve(self):
        ax = plt.subplot()
        if self.currentBack.any():
            ax.plot(self.V, self.currentForw * 10 ** 9, self.V, self.currentBack * 10 ** 9)
        else:
            ax.plot(self.V, self.currentForw * 10 ** 9)
        plt.show()
        # plt.imshow(self.imageForwUp, origin = 'lower')

    def _plotLoc(self):
        if self.mtrxRef:
            self.mtrxRef.show(self.xloc, self.yloc)

    def show(self, xloc=None, yloc=None):
        if self.datatype == 'Z' or self.datatype == 'I':
            self._plotTopo(xloc, yloc)
        if self.datatype == 'I(V)-curve' or self.datatype == 'I(Z)-curve':
            self._plotCurve()
            self._plotLoc()


if __name__ == "__main__":

    # mtrx = Matrix("test_files/2021-04-08/Si(553)-AuSb--34_9.I(V)_mtrx")
    mtrx = Matrix("test_files/Si(553)_Au_krakerSb--3_1.I(V)_mtrx")
    # mtrx = Matrix("test_files/Si(111)-6x6 + 140Hz Au--4_1.Z_mtrx")
    mtrx.show()
