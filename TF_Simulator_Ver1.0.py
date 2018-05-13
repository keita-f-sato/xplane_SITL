#-*- coding: utf-8 -*-
import socket
from contextlib import closing
import numpy as np
import pygame
import Convert_format
import Transfer_function_plane
import pandas as pd
import pygame
from pygame.locals import *
import concurrent.futures

pd.set_option("display.max_rows", 101)

pygame.joystick.init()
try:
    j = pygame.joystick.Joystick(0) # create a joystick instance
    j.init() # init instance

except pygame.error:
    print ('Joystickが見つかりませんでした。')

class TF_Simulator:
    def __init__(self):
        #xplane送信フォーマット用リスト
        self.convert_format = Convert_format.Convert_format()
        self.first_DATA = [68, 65, 84, 65, 0, 11, 0, 0, 0]
        self.filght_con_DATA = [0]*20
        self.throttle_con2_DATA = [0]*28
        self.throttle_con1_DATA = [25, 0, 0, 0]
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = '127.0.0.1'
        self.port = 49007
        self.sedport = 49000
        self.bufsize = 1024
        self.DATA_Xplane = [0]*90#初期データ
        self.DATA_Xplane = self.convert_format.layout_data(self.DATA_Xplane)
        self.Auto_comand_bin = []
        self.ip_sp = 0
        self.delta_x_h = np.asarray([0,0,0,0])
        self.delta_baffer = np.asarray([0,0,0,0])#微分計算用バッファ
        self.flight_data_for_integrate = pd.DataFrame([[0,0,0,0,0],[0,0,0,0,0]],columns = ['roll','pitch','yaw','altitude','time'])
        self.test1 = list([[0,0,0,0,0],[0,0,0,0,0]])
        self.stop_program = False
        self.control_status = 'hand control'
        self.filcon_DATA = [0,0,0,0]

    def sim_main(self):
        pygame.init()
        TF_start_switch = 1#初期スイッチ（joystickスルー）
        with closing(self.sock):
          self.sock.bind((self.host , self.port))
          while self.stop_program == False :
              recive_xplane_data = self.sock.recv(self.bufsize)
              recive_xplane_data_int = [int(recive_xplane_data[i]) for i in range(5,len(recive_xplane_data))]
              recive_xplane_data_bin =  [bin(recive_xplane_data_int[ii]).zfill(8) for ii in range(0,len(recive_xplane_data_int))]
              Flip_bin_DATA = recive_xplane_data_bin[::-1]


              self.DATA_Xplane = self.convert_format.IEEE2dec(Flip_bin_DATA)
              self.DATA_Xplane = self.convert_format.layout_data(self.DATA_Xplane)
              #print(DATA_Xplane)

              self.delta_baffer = np.asarray([float(self.DATA_Xplane['roll']) , float(self.DATA_Xplane['pitch']) , float(self.DATA_Xplane['hding_true']), float(self.DATA_Xplane['alt_ftagl'])])

              self.flight_data_for_integrate = self.flight_data_for_integrate.append(pd.DataFrame(\
                  [[float(self.DATA_Xplane['roll']) , float(self.DATA_Xplane['pitch']) , float(self.DATA_Xplane['hding_true']), float(self.DATA_Xplane['alt_ftagl']), float(self.DATA_Xplane['real'])]],\
                  columns = ['roll','pitch','yaw','altitude','time']))
              self.test1.append([float(self.DATA_Xplane['roll']) , float(self.DATA_Xplane['pitch']) , float(self.DATA_Xplane['hding_true']) , float(self.DATA_Xplane['alt_ftagl']) , float(self.DATA_Xplane['real'])])
              test = Transfer_function_plane.diff_inte(self.test1)


              for e in pygame.event.get(): # イベントチェック
                  x9 , y9 = 1E-5+j.get_axis(0), 1E-5+j.get_axis(1) #
                  x10 , y10 = -1 * j.get_axis(3)+1E-5, 1E-5+j.get_axis(4)
                  #RL = j.get_axis(2)
                  throttecon_DATA = 0.5*x10+0.5
                  self.filcon_DATA = [y9, x9, y10, throttecon_DATA] #[elv/ail/rud]←リトルエンディアンなので逆

                  if  e.type == pygame.locals.JOYBUTTONDOWN:
                      if e.button == 1:
                          TF_start_switch += 1
                      elif e.button == 7:
                          self.write_flight_csv(self.DATA_Xplane)
                          self.stop_program = True
                  #print("a")

              if TF_start_switch & 1:#joystickのコマンドをXplaneにスルー出力
                  self.control_status = 'hand control'
                  control_comand_bin = [self.convert_format.Dec2bin(self.filcon_DATA[i4]) for i4 in range(0,4)]
                  self.send_xplane_DATA(control_comand_bin)
                  print('manual')

              else:#Auto制御を実施
                  self.control_status = 'PID control'
                  Auto_comand_dec = Transfer_function_plane.transfer_fuction(self.DATA_Xplane,self.filcon_DATA,self.flight_data_for_integrate)#制御コマンドの計算
                  print('b')
                  self.Auto_comand_bin = [self.convert_format.Dec2bin(Auto_comand_dec[i4]) for i4 in range(0,4)]
                  #print(Auto_comand_dec)

                  self.send_xplane_DATA(self.Auto_comand_bin)

    def send_xplane_DATA(self,filcon):
        send_data = bytes(self.first_DATA + filcon[0] + filcon[1] + filcon[2] + \
                   self.filght_con_DATA + self.throttle_con1_DATA + filcon[3] + self.throttle_con2_DATA)#Xplane送信フォーマットに代入
        self.sock.sendto(send_data, (self.host, self.sedport))

    def write_flight_csv(self,flight_data):
        flight_data.to_csv("xplane_Flight_data.csv")

if __name__ == '__main__':
    tf_simulator = TF_Simulator()
    tf_simulator.sim_main()
