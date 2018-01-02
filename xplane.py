from __future__ import print_function
import socket
from contextlib import closing
import binascii
import numpy as np
import pygame
from pygame.locals import *
import concurrent.futures
import dec2bin
import Transfer_function_plane

pygame.joystick.init()
try:
    j = pygame.joystick.Joystick(0) # create a joystick instance
    j.init() # init instance

except pygame.error:
    print ('Joystickが見つかりませんでした。')


first_DATA = [68, 65, 84, 65, 0, 11, 0, 0, 0]
filght_con_DATA = [0, 192, 121, 196, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
throttle_con1_DATA = [25, 0, 0, 0]
throttle_con2_DATA = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = '127.0.0.1'
port = 49007
sedport = 49000
bufsize = 1024
DATA_Xplane = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
DATA_Xplane2 = []
Auto_comand_bin = []
ip_sp = 0
delta_a_A = 0
delta_a_baffer = 0

def read_xplane_DATA():
  global DATA_Xplane, Auto_comand_bin
  with closing(sock):
    sock.bind((host, port))
    while True:
      adder = sock.recv(bufsize)
      DATA10 = [int(adder[i]) for i in range(5,len(adder))]
      DATA1 =  [bin(DATA10[ii]).zfill(8) for ii in range(0,len(DATA10))]
      DATA2 = DATA1[::-1]
      DATA_Xplane = []
      DATA_Xplane2 = []
      DATA22 = []
      Dn = int(len(DATA2) / 4)
      for c in range(0,Dn):
          c = 4*c
          cA =''
          for ci in range(0,4):
              if len(DATA2[c+ci]) == 8:
                  DATA28 = DATA2[c+ci].replace('b', '0')
              elif len(DATA2[c+ci]) == 9:
                   DATA28 = DATA2[c+ci].replace('b', '')
              elif len(DATA2[c+ci]) == 10:
                   DATA28 = DATA2[c+ci].replace('0b', '')
              cA += DATA28
          cA = str(cA)

          c_sign = -2*int(cA[0])+1      #符号計算
          c_index = int(cA[1:9],2)-127    #指数計算
          c_mantissa = [float(cA[i3+8])*(2 ** (-i3)) for i3 in range(1,23)]    #仮数計算
          c_Decimal = 1 + sum(c_mantissa)    #少数計算
          Vaue = c_sign * float(c_Decimal)*2**c_index   #値計算
          Vaue = "%.3f" % Vaue
          DATA_Xplane2.append(Vaue)
          DATA_Xplane = DATA_Xplane2

      print(DATA_Xplane)


      #print('A'+str(len(adder)))


      #print(Auto_comand)
      #print('B'+str(len(DATA10)))
      #print('C'+str(len(DATA_Xplane)))


      #print(DATA_Xplane)

  return


def read_joystick_DATA():
    pygame.init()
    global delta_a_baffer


    while 1:
        for e in pygame.event.get(): # イベントチェック
            #if e.type == QUIT: # 終了が押された？
            #    return
            #if (e.type == KEYDOWN and
            #    e.key  == K_ESCAPE): # ESCが押された？
            #    return
            # Joystick関連のイベントチェック
            #if e.type == pygame.locals.JOYAXISMOTION: # 7
            x9 , y9 = 0.999*j.get_axis(0), 0.999*j.get_axis(1)
            x10 , y10 = -0.999 * j.get_axis(3), 0.999*j.get_axis(4)
            RL = j.get_axis(2)
            #elif e.type == pygame.locals.JOYBALLMOTION: # 8
            #    print ('ball motion')
            #elif e.type == pygame.locals.JOYHATMOTION: # 9
            #    print ('hat motion')
            #elif e.type == pygame.locals.JOYBUTTONDOWN: # 10
            #    print (str(e.button)+'番目のボタンが押された')
            #elif e.type == pygame.locals.JOYBUTTONUP: # 11
            #    print (str(e.button)+'番目のボタンが離された')
            filcon_DATA = [y9, x9, y10] #[elv/ail/rud]←リトルエンディアンなので逆
            throttecon_DATA = 0.5*x10+0.5
            #convert_bin2bytes(filcon_DATA[0])


        t_comand_bytes = convert_bin2bytes(throttecon_DATA)
        filcon_comand_bytes = []
        for i in range(0,3):
            filcon_comand_bytes = filcon_comand_bytes + convert_bin2bytes(filcon_DATA[i])

        D_delta_a = Dff(delta_a_baffer)
        Auto_comand_dec = Transfer_function_plane.transfer_fuction(DATA_Xplane,x9,D_delta_a)
        delta_a_baffer = Auto_comand_dec
        Auto_comand_bin = convert_bin2bytes(Auto_comand_dec)
        #print(Auto_comand_dec)

        Auto_filcon = []
        Auto_filcon = Auto_filcon + filcon_comand_bytes[0:4] + Auto_comand_bin + filcon_comand_bytes[8:]
        #print(Auto_filcon)

            #send_xplane_DATA(filcon_comand_bytes,t_comand_bytes)
        send_xplane_DATA(Auto_filcon,t_comand_bytes)



def send_xplane_DATA(filcon,throttle):

    senddata = bytes(first_DATA + filcon + filght_con_DATA + throttle_con1_DATA + throttle + throttle_con2_DATA)
    sock.sendto(senddata, (host, sedport))
    DATA10 = [int(senddata[i]) for i in range(5,len(senddata))]

def convert_bin2bytes(bin2data):
    bin_data = dec2bin.float_dec2bin(bin2data)
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

def Dff (delta_a):
    global delta_a_A
    delta_a_D = delta_a - delta_a_A
    delta_a_A = delta_a
    return delta_a_D


if __name__ == '__main__':
  executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
  executor.submit(read_xplane_DATA)
  executor.submit(read_joystick_DATA)
  #read_joystick_DATA()
  #read_xplane_DATA()
