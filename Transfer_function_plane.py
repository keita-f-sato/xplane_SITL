import numpy as np
import math

def transfer_fuction(xplane2dec,control_DATA,delta_B):
    Phi_sp = control_DATA[1]*180
    Theta_sp = control_DATA[0]*180
    Psi_sp = control_DATA[2]*180
    h_sp = 200 + 400*control_DATA[3]-200
    T_roll = 1
    T_pitch = 1
    g = 9.8 #m/s**2
    K_i = [1, 1, 1, 1]
    K_p = [0.2, 0.2, 0.2, 0.2]
    K_ff = [1, 0.5, 0.5, 0.5]




    Phi = float(xplane2dec[42]) + 0.0001    # roll
    Theta = float(xplane2dec[43]) + 0.0001  #pitch
    Psi = float(xplane2dec[41]) + 0.0001    #yaw
    u = float(xplane2dec[13]) + 0.0001
    w = float(xplane2dec[11]) + 0.0001
    p = float(xplane2dec[51]) + 0.0001
    h = float(xplane2dec[23]) + 0.0001


#moment sp
    p_sp = (Phi_sp - Phi) / T_roll
    q_sp = (Theta_sp - Theta) / T_pitch
    r_sp = ((w*q_sp) + (g*np.sin(Phi)*np.cos(Theta)) + (u*q_sp*Phi))/((u*np.cos(Phi)*np.sin(Theta)) + (w*np.sin(Theta)))
    t_sp = h_sp -h

#control roll
    #delta_a = ((p_sp - r_sp - p * np.sin(Theta)) * K_p[0] )
    #delta_a = ((p_sp - r_sp * np.sin(Theta)) * (K_p[0]-p + ((K_i[0]-p))))
    delta_a = p_sp * K_p[0] + delta_B[0]*K_ff[0]
    delta_e = control_DATA[0]
    #delta_e = q_sp * K_p[1] + delta_B[1]*K_ff[1]
    delta_r = control_DATA[2]
    #delta_r = q_sp * K_p[2] + delta_B[2]*K_ff[2]
    delta_th = control_DATA[3]#t_sp * K_p[3] + delta_B[3]*K_ff[3]

    delta = [delta_e, delta_a, delta_r, delta_th]

    print(r_sp)




    return delta
