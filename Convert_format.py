# -*- coding: utf-8 -*-
import pandas as pd

class Convert_format:
    def __init__(self):
        self.hex2bin = dict('{:x} {:04b}'.format(x,x).split() for x in range(16))
        self.index_data =['real', 'total', 'missn', 'timer', ' ', 'zulu', 'local', 'hobbs',\
                       'Vind_kias', 'Vind_keas', 'Vtrue_ktas', 'Vtrue_ktgs', ' ',\
                       'Vind', 'Vtrue_mphas', 'Vtrue_mphgs',\
                       'AMprs', 'AMtmp', 'LEtmp', 'dens', 'A', 'Q', '', 'gravi',\
                       'elev', 'ailrn', 'ruddr', ' ', 'nwhel', ' ', ' ', ' ',\
                       'Q_rad/s', 'P_rad/s', 'R_rad/s', ' ', ' ', ' ', ' ', ' ',\
                       'pitch', 'roll', 'hding_true', 'hding_mag', ' ', ' ', ' ', ' ',\
                       'mag', 'mavar', ' ', ' ', ' ', ' ', ' ', ' ',\
                       'lat', 'lon', 'alt_ftmsl', 'alt_ftagl', 'on', 'alt_ind', 'lat_south', 'lon_west',\
                       'X', 'Y', 'Z', 'vX', 'vY', 'vZ', 'dist_ft','dist_nm',\
                       'throl1','throl2','throl3','throl4','throl5','throl6','throl7','throl8',]


    def float_dec2bin(self, n):
        neg = False
        if n < 0:
            n = -n
            neg = True
        hx = float(n).hex()
        p = hx.index('p')
        bn = ''.join(self.hex2bin.get(char, char) for char in hx[2:p])
        return (('1' if neg else '0') + bn.strip('0') + hx[p:p+2]
                + bin(int(hx[p+2:]))[2:])

    def IEEE2dec(self, Flip_bin_DATA):
        DATA_Xplane_dec = []
        Dn = int(len(Flip_bin_DATA) / 4)
        for c in range(0,Dn):
            c = 4*c
            cA =''
            for ci in range(0,4):
                if len(Flip_bin_DATA[c+ci]) == 8:
                    DATA_bin_zfill8 = Flip_bin_DATA[c+ci].replace('b', '0')
                elif len(Flip_bin_DATA[c+ci]) == 9:
                     DATA_bin_zfill8 = Flip_bin_DATA[c+ci].replace('b', '')
                elif len(Flip_bin_DATA[c+ci]) == 10:
                     DATA_bin_zfill8 = Flip_bin_DATA[c+ci].replace('0b', '')
                cA += DATA_bin_zfill8
            cA = str(cA)

        #IEEE754の計算
            c_sign = -2*int(cA[0])+1      #符号計算
            c_index = int(cA[1:9],2)-127    #指数計算
            c_mantissa = [float(cA[i3+8])*(2 ** (-i3)) for i3 in range(1,23)]    #仮数計算
            c_Decimal = 1 + sum(c_mantissa)    #少数計算
            Vaue = c_sign * float(c_Decimal)*2**c_index   #値計算
            #Vaue = "%.6f" % Vaue
            DATA_Xplane_dec.append(Vaue)
        return(DATA_Xplane_dec)

    def Dec2bin(self, bin2data):#10進数をFloat２進数に変換
        bin_data = self.float_dec2bin(bin2data)
        pt = bin_data.index('p')
        dt = bin_data.index('.')
        if bin_data[pt+1] == '+':
            p_bin_data = format(int(bin_data[pt+2:],2)+int(127), 'b')
        else:
            p_bin_data = format((-1 * (int(bin_data[pt+2:],2))+int(127)) , 'b')
        l_bin_p=len(p_bin_data)

        if l_bin_p < 8 :
             p_bin_data = p_bin_data.zfill(8)
        elif l_bin_p > 8 :
             p_bin_data = p_bin_data[0:7]

        v_bin_data = bin_data[dt+1:pt]
        l_bin_v = len(v_bin_data)

        if l_bin_v < 23:
            for i in range(1,24 - l_bin_v):
                v_bin_data = v_bin_data + '0'
        elif l_bin_v > 23:
            v_bin_data = bin_data[dt+1:24]
        bin_cov_data = bin_data[0] + p_bin_data + v_bin_data
        byn_data =[int(bin_cov_data[25:],2) , int(bin_cov_data[17:24],2) , int(bin_cov_data[9:16],2) , int(bin_cov_data[0:8],2)]
        return byn_data

    def layout_data(self, raw_data):
        UDP_raw_data = raw_data[::-1]
        UDP_raw_data = [UDP_raw_data[d] for d in range(len(UDP_raw_data)) if not d%9 == 0]
        flight_data = pd.DataFrame([UDP_raw_data])
        flight_data.columns = self.index_data
        return flight_data
