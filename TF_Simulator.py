import socket
from contextlib import closing
import numpy as np
import pygame
from pygame.locals import *
import concurrent.futures
import Convert_format
import Transfer_function_plane
import sys
import pandas as pd

pygame.joystick.init()
try:
    j = pygame.joystick.Joystick(0) # create a joystick instance
    j.init() # init instance

except pygame.error:
    print ('Joystickが見つかりませんでした。')

class TF_Simulator:
    def __init__(self):
        #xplane送信フォーマット用リスト
        self.first_DATA = [68, 65, 84, 65, 0, 11, 0, 0, 0]
        self.filght_con_DATA = [0]*20
        self.throttle_con2_DATA = [0]*28
        self.throttle_con1_DATA = [25, 0, 0, 0]
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = '127.0.0.1'
        self.port = 49007
        self.sedport = 49000
        self.bufsize = 1024
        self.DATA_Xplane = [0]*72#初期データ
        self.Auto_comand_bin = []
        self.ip_sp = 0
        self.delta_A = np.asarray([0,0,0,0])
        self.delta_baffer = np.asarray([0,0,0,0])#微分計算用バッファ
        self.stop_program = False
        self.output_data_name = ['roll','pitch','yaw',\
                                 'vX','vY','vZ',\
                                 'roll moment','pitch moment','yaw moment',\
                                 'con ailrn','con elev','con ruddr',\
                                 'lat','lon','alt',\
                                 'mag_comp','craft airspeed','con throttle']
        self.save_xplane_data = pd.DataFrame([], columns = self.output_data_name)

    def read_xplane_DATA(self):
      with closing(self.sock):
        self.sock.bind((self.host, self.port))
        while self.stop_program == False:
          recive_xplane_data = self.sock.recv(self.bufsize)

          recive_xplane_data_int = [int(recive_xplane_data[i]) for i in range(5,len(recive_xplane_data))]
          recive_xplane_data_bin =  [bin(recive_xplane_data_int[ii]).zfill(8) for ii in range(0,len(recive_xplane_data_int))]
          Flip_bin_DATA = recive_xplane_data_bin[::-1]

          self.DATA_Xplane = Convert_format.IEEE2dec(Flip_bin_DATA)
          self.save_xplane_data = self.save_xplane_data.append(pd.DataFrame([[self.DATA_Xplane[42] , self.DATA_Xplane[43] , self.DATA_Xplane[41],\
                                                                self.DATA_Xplane[13] , self.DATA_Xplane[12] , self.DATA_Xplane[11],\
                                                                self.DATA_Xplane[51] , self.DATA_Xplane[52] , self.DATA_Xplane[50],\
                                                                self.DATA_Xplane[60] , self.DATA_Xplane[61] , self.DATA_Xplane[59],\
                                                                self.DATA_Xplane[25] , self.DATA_Xplane[24] , self.DATA_Xplane[22],\
                                                                self.DATA_Xplane[34] , self.DATA_Xplane[77] , self.DATA_Xplane[7]]],\
                                                                columns = self.output_data_name) , ignore_index=True)

      return


    def read_joystick_DATA(self):
        pygame.init()
        TF_start_switch = 1#初期スイッチ（joystickスルー）

        while self.stop_program == False:
            for e in pygame.event.get(): # イベントチェック
                x9 , y9 = 0.999*j.get_axis(0), 0.999*j.get_axis(1)
                x10 , y10 = -0.999 * j.get_axis(3), 0.999*j.get_axis(4)
                RL = j.get_axis(2)
                throttecon_DATA = 0.5*x10+0.5
                filcon_DATA = [y9, x9, y10, throttecon_DATA] #[elv/ail/rud]←リトルエンディアンなので逆

                if  e.type == pygame.locals.JOYBUTTONDOWN:
                    if e.button == 1:
                        TF_start_switch += 1
                    elif e.button == 7:
                        self.write_flight_csv(self.save_xplane_data)
                        self.stop_program = True

            if TF_start_switch & 1:#joystickのコマンドをXplaneにスルー出力
                control_comand_bin = [Convert_format.Dec2bin(filcon_DATA[i4]) for i4 in range(0,4)]
                self.send_xplane_DATA(control_comand_bin)

            else:#Auto制御を実施
                D_delta_a = self.Dff(self.delta_baffer)#微分値計算
                Auto_comand_dec = Transfer_function_plane.transfer_fuction(self.DATA_Xplane,filcon_DATA,D_delta_a)#制御コマンドの計算
                self.delta_baffer = Auto_comand_dec
                self.Auto_comand_bin = [Convert_format.Dec2bin(Auto_comand_dec[i4]) for i4 in range(0,4)]
                print(Auto_comand_dec)

                self.send_xplane_DATA(self.Auto_comand_bin)
        return

    def send_xplane_DATA(self,filcon):
        send_data = bytes(self.first_DATA + filcon[0] + filcon[1] + filcon[2] + \
                   self.filght_con_DATA + self.throttle_con1_DATA + filcon[3] + self.throttle_con2_DATA)#Xplane送信フォーマットに代入
        self.sock.sendto(send_data, (self.host, self.sedport))

    def write_flight_csv(self,flight_data):
        flight_data.to_csv("xplane_Flight_data.csv")

    def Dff (self,delta_a):#微分関数
        delta_a_D = delta_a - self.delta_A
        self.delta_A = np.asarray(delta_a)
        return delta_a_D


if __name__ == '__main__':
    tf_simulator = TF_Simulator()
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
    executor.submit(tf_simulator.read_xplane_DATA)
    executor.submit(tf_simulator.read_joystick_DATA)
    #tf_simulator.read_joystick_DATA()
    #tf_simulator.read_xplane_DATA()
