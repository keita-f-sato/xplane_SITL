import numpy as np
import math

def transfer_fuction(xplane2dec,x9,delta_a_B):
    Phi_sp = x9*180
    Theta_sp = 0
    Psi_sp = 0.0001
    h_sp = 200
    T_roll = 1
    T_pitch = 1
    g = 9.8 #m/s**2
    K_i = [1, 1, 1, 1]
    K_p = [0.2, 1, 1, 1]
    K_ff = [0.5, 1, 1, 1]




    Phi = float(xplane2dec[42]) + 0.0001    # roll
    Theta = float(xplane2dec[43]) + 0.0001  #pitch
    Psi = float(xplane2dec[41]) + 0.0001    #yaw
    u = float(xplane2dec[13]) + 0.0001
    w = float(xplane2dec[11]) + 0.0001
    p = float(xplane2dec[51]) + 0.0001


#moment sp
    p_sp = (Phi_sp - Phi) / T_roll
    q_sp = (Theta_sp - Theta) / T_pitch
    r_sp = ((w*q_sp) + (g*np.sin(Phi)*np.cos(Theta)) + (u*q_sp*Phi))/((u*np.cos(Phi)*np.sin(Theta)) + (w*np.sin(Theta)))

#control roll
    #delta_a = ((p_sp - r_sp - p * np.sin(Theta)) * K_p[0] )
    #delta_a = -1*((p_sp - r_sp * np.sin(Theta)) * (K_p[0]-p + ((K_i[0]-p) * i_p_sp)))
    delta_a = p_sp * K_p[0] + delta_a_B*K_ff[0]
    print(delta_a)




    return delta_a
