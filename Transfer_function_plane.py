# -*- coding: utf-8 -*-


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
    K_i = np.asarray([1, 1, 1, 1])
    K_p = np.asarray([0.2, 0.5, 1e-10, 0.2])
    K_ff = np.asarray([0.3, 0.5, 0.5, 0.5])
    buffer_a = 1e-10




    Phi = float(xplane2dec[42]) + buffer_a    # roll
    Theta = float(xplane2dec[43]) + buffer_a  #pitch
    Psi = float(xplane2dec[41]) + buffer_a    #yaw
    u = float(xplane2dec[13]) + buffer_a #x acxis speed
    v = float(xplane2dec[12]) + buffer_a #y acxis speed
    w = float(xplane2dec[11]) + buffer_a #z acxis speed
    p = float(xplane2dec[51]) + buffer_a #roll moment
    q = float(xplane2dec[52]) + buffer_a #roll moment
    r = float(xplane2dec[50]) + buffer_a #roll moment
    h = float(xplane2dec[23]) + buffer_a  #altitude


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


    R = create_state_array(Phi,Theta,Psi)
    R_sp = create_state_array(Phi_sp,Theta_sp,Psi_sp)

    R_z = np.asarray([R[0,2],R[1,2],R[2,2]])
    R_z_sp =np.asarray([R_sp[0,2],R_sp[1,2],R_sp[2,2]])

    C = np.cross(R_z,R_z_sp)
    e_R = np.dot(R.T,C)

    cos = np.dot(R_z , R_z_sp)
    sin = np.linalg.norm(e_R)


    tan = sin / cos
    angle = np.arctan(tan)
    axis = np.matrix(e_R) / sin
    e_R = axis * angle


    cp1 =np.asarray([0 , 0 , axis[0,1] ])
    cp2 =np.asarray([0, 0 , -1*axis[0,0] ])
    cp3 =np.asarray([-1*axis[0,1] , axis[0,0] , 0 ])

    e_R_cp = np.matrix([cp1,cp2,cp3])

    cos_theta = np.cos(angle)
    sin_theta = np.sin(angle)

    A = np.matrix([[1,0,0],[0,1,0],[0,0,1]])
    R_rp =R *(A + (e_R_cp * sin + (e_R_cp*e_R_cp*(1-cos) )))



    #yaw
    R_x_sp = np.asarray([1,0,0])
    R_x_rp = np.asarray([R_rp[0,0],R_rp[1,0],R_rp[2,0]])

    sinx = np.dot(np.cross(R_x_rp,R_x_sp),R_z_sp)
    cosx = np.dot(R_x_rp,R_x_sp)
    tanx = sinx/cosx

    yaw_w = A[2,2] * A[2,2]

    e_R[0,2] = np.arctan(tanx) * yaw_w

    eP = np.matrix([1,1,1])
    rates_sp = [e_R[0,0]*eP[0,0],e_R[0,1]*eP[0,1],e_R[0,2]*eP[0,2]]
    rates = np.matrix([q,p,r])
    rate_err = rates_sp - rates
    att_control = K_p[0:3]*np.asarray(rate_err) + K_ff[0:3] * delta_B[0:3]
    delta = [att_control[0,0],att_control[0,1],att_control[0,2], delta_th]
    #print(delta)

    #delta_2 = delta_a - float(att_control[0,1])
    #print(delta_2)


    return delta

def create_state_array(Phi,Theta,Psi):
    F1 = np.asarray([np.cos(Theta)*np.cos(Psi), np.cos(Theta)*np.sin(Psi), -1 * np.sin(Theta)])
    F2 = np.asarray([np.sin(Phi)*np.sin(Theta)*np.cos(Psi) - np.cos(Phi)*np.sin(Psi), np.sin(Phi)*np.sin(Theta)*np.sin(Psi) + np.cos(Phi)*np.cos(Psi), np.sin(Phi)*np.cos(Theta)])
    F3 = np.asarray([np.cos(Phi)*np.sin(Theta)*np.cos(Psi) + np.sin(Phi)*np.sin(Psi), np.cos(Phi)*np.sin(Theta)*np.sin(Psi) - np.sin(Phi)*np.cos(Psi), np.cos(Phi)*np.cos(Theta)])
    E = np.matrix([F1,F2,F3])
    return E
