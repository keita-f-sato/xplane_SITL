import numpy as np

def transfer_fuction(xplane2dec,control_DATA,delta_B) :
    Phi_sp = control_DATA[1] * 180   #roll
    Theta_sp = control_DATA[0] * 180 #pitch
    Psi_sp = control_DATA[2] *180  #yaw
    throtte = control_DATA[3]
    buffer_a = 0.0001

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


    R =(A + (e_R_cp * sin + (e_R_cp*e_R_cp*(1-cos) )))
    R_rp = E * R


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
    att_control = k_p*rate_err + k_D * delta_b
    












def create_state_array(Phi,Theta,Psi):
    F1 = np.asarray([np.cos(Theta)*np.cos(Psi), np.cos(Theta)*np.sin(Psi), -1 * np.sin(Theta)])
    F2 = np.asarray([np.sin(Phi)*np.sin(Theta)*np.cos(Psi) - np.cos(Phi)*np.sin(Psi), np.sin(Phi)*np.sin(Theta)*np.sin(Psi) + np.cos(Phi)*np.cos(Psi), np.sin(Phi)*np.cos(Theta)])
    F3 = np.asarray([np.cos(Phi)*np.sin(Theta)*np.cos(Psi) + np.sin(Phi)*np.sin(Psi), np.cos(Phi)*np.sin(Theta)*np.sin(Psi) - np.sin(Phi)*np.cos(Psi), np.cos(Phi)*np.cos(Theta)])
    E = np.matrix([F1,F2,F3])
    return E
