import socket
from contextlib import closing
import numpy as np
import pygame
from pygame.locals import *
import concurrent.futures
import Convert_format
import Transfer_function_plane
import sys
import pandas as import pd

pygame.joystick.init()
try:
    j = pygame.joystick.Joystick(0) # create a joystick instance
    j.init() # init instance

except pygame.error:
    print ('Joystickが見つかりませんでした。')

class TF_Simulator:
    def __init__(self):
        #xplane送信フォーマット用リスト
        first_DATA = [68, 65, 84, 65, 0, 11, 0, 0, 0]
        filght_con_DATA = [0, 192, 121, 196, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        throttle_con2_DATA = [0]*28
        throttle_con1_DATA = [25, 0, 0, 0]

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        host = '127.0.0.1'
        port = 49007
        sedport = 49000
        bufsize = 1024
        DATA_Xplane = [0]*72#初期データ
        Auto_comand_bin = []
        ip_sp = 0
        delta_A = np.asarray([0,0,0,0])
        delta_baffer = np.asarray([0,0,0,0])#微分計算用バッファ
        stop_program = True
        Save_xplane_data = pd.DataFrame()

    def read_xplane_DATA():
      global DATA_Xplane,stop_program
      with closing(sock):
        sock.bind((host, port))
        while stop_program == True:
          recive_xplane_data = sock.recv(bufsize)
          recive_xplane_data_int = [int(recive_xplane_data[i]) for i in range(5,len(recive_xplane_data))]
          recive_xplane_data_bin =  [bin(recive_xplane_data_int[ii]).zfill(8) for ii in range(0,len(recive_xplane_data_int))]
          DATA_Xplane = Convert_format.convert_IEEE2dec(Flip_bin_DATA)
          Flip_bin_DATA = recive_xplane_data_bin[::-1]

          Saave_xplane_data.append([DATA_Xplane])

    return


    def read_joystick_DATA():
        pygame.init()
        global delta_baffer,stop_program
        TF_start_switch = 1#初期スイッチ（joystickスルー）
        while stop_program == True:
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
                        write_flight_csv(Save_xplane_data)
                        stop_program = False

            if TF_start_switch & 1:#joystickのコマンドをXplaneにスルー出力
                control_comand_bin = [Convert_format.convert_Dec2bin(filcon_DATA[i4]) for i4 in range(0,4)]
                send_xplane_DATA(control_comand_bin)

            else:#Auto制御を実施
                D_delta_a = Dff(delta_baffer)#微分値計算
                Auto_comand_dec = Transfer_function_plane.transfer_fuction(DATA_Xplane,filcon_DATA,D_delta_a)#制御コマンドの計算
                delta_baffer = Auto_comand_dec
                Auto_comand_bin = [Convert_format.convert_Dec2bin(Auto_comand_dec[i4]) for i4 in range(0,4)]
                print(Auto_comand_dec)

                send_xplane_DATA(Auto_comand_bin)


    def send_xplane_DATA(filcon):

        senddata = bytes(first_DATA + filcon[0]+filcon[1]+filcon[2] + \
                   filght_con_DATA + throttle_con1_DATA + filcon[3] + throttle_con2_DATA)#Xplane送信フォーマットに代入

        sock.sendto(senddata, (host, sedport))

    def write_flight_csv(flight_data):
        flight_data.to_csv("xplane_Flight_data.csv")


    def Dff (delta_a):#微分関数
        global delta_A
        delta_a_D = delta_a - delta_A
        delta_A = np.asarray(delta_a)
        return delta_a_D


if __name__ == '__main__':
  executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
  executor.submit(TF_Simulator.ead_xplane_DATA)
  executor.submit(TF_Simulator.read_joystick_DATA)
  #read_joystick_DATA()
  #read_xplane_DATA()
