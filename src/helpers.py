import math

def rotx(rx):
    r"""Returns a rotation matrix around the X axis (radians)
    
    .. math::
        
        R_x(\theta) = \begin{bmatrix} 1 & 0 & 0 & 0 \\
        0 & c_\theta & -s_\theta & 0 \\
        0 & s_\theta & c_\theta & 0 \\
        0 & 0 & 0 & 1
        \end{bmatrix}
    
    :param float rx: rotation around X axis in radians
    
    .. seealso:: :func:`~robodk.transl`, :func:`~robodk.roty`, :func:`~robodk.roty`
    """
    ct = math.cos(rx)
    st = math.sin(rx)
    return([[1,0,0,0],[0,ct,-st,0],[0,st,ct,0],[0,0,0,1]])

def roty(ry):
    r"""Returns a rotation matrix around the Y axis (radians)
    
    .. math::
        
        R_y(\theta) = \begin{bmatrix} c_\theta & 0 & s_\theta & 0 \\
        0 & 1 & 0 & 0 \\
        -s_\theta & 0 & c_\theta & 0 \\
        0 & 0 & 0 & 1
        \end{bmatrix}
    
    :param float ry: rotation around Y axis in radians
    
    .. seealso:: :func:`~robodk.transl`, :func:`~robodk.rotx`, :func:`~robodk.rotz`
    """
    ct = math.cos(ry)
    st = math.sin(ry)
    return([[ct,0,st,0],[0,1,0,0],[-st,0,ct,0],[0,0,0,1]])

def rotz(rz):
    r"""Returns a rotation matrix around the Z axis (radians)
    
    .. math::
        
        R_x(\theta) = \begin{bmatrix} c_\theta & -s_\theta & 0 & 0 \\
        s_\theta & c_\theta & 0 & 0 \\
        0 & 0 & 1 & 0 \\
        0 & 0 & 0 & 1
        \end{bmatrix}
    
    :param float ry: rotation around Y axis in radians
    
    .. seealso:: :func:`~robodk.transl`, :func:`~robodk.rotx`, :func:`~robodk.roty`
    """
    ct = math.cos(rz)
    st = math.sin(rz)
    return([[ct,-st,0,0],[st,ct,0,0],[0,0,1,0],[0,0,0,1]])

def transl(tx,ty=None,tz=None):
    r"""Returns a translation matrix (mm)
    
    .. math::
        
        T(t_x, t_y, t_z) = \begin{bmatrix} 1 & 0 & 0 & t_x \\
        0 & 1 & 0 & t_y \\
        0 & 0 & 1 & t_z \\
        0 & 0 & 0 & 1
        \end{bmatrix}
    
    :param float tx: translation along the X axis
    :param float ty: translation along the Y axis
    :param float tz: translation along the Z axis
    
    .. seealso:: :func:`~robodk.rotx`, :func:`~robodk.roty`, :func:`~robodk.rotz`
    """
    if ty is None:
        xx = tx[0]
        yy = tx[1]
        zz = tx[2]
    else:
        xx = tx
        yy = ty
        zz = tz    
    return([[1,0,0,xx],[0,1,0,yy],[0,0,1,zz],[0,0,0,1]])

def TxyzRxyz_2_Pose(xyzrpw):
    """Returns the pose given the position (mm) and Euler angles (rad) as an array [x,y,z,rx,ry,rz].
    The result is the same as calling: H = transl(x,y,z)*rotx(rx)*roty(ry)*rotz(rz)
    
    :param xyzrpw: [x,y,z,rx,ry,rz] in mm and radians
    :type xyzrpw: list of float
        
    .. seealso:: :class:`.Mat`, :func:`~robodk.TxyzRxyz_2_Pose`, :func:`~robodk.Pose_2_TxyzRxyz`, :func:`~robodk.Pose_2_ABB`, :func:`~robodk.Pose_2_Adept`, :func:`~robodk.Pose_2_Comau`, :func:`~robodk.Pose_2_Fanuc`, :func:`~robodk.Pose_2_KUKA`, :func:`~robodk.Pose_2_Motoman`, :func:`~robodk.Pose_2_Nachi`, :func:`~robodk.Pose_2_Staubli`, :func:`~robodk.Pose_2_UR`, :func:`~robodk.quaternion_2_pose`
    """
    [x,y,z,rx,ry,rz] = xyzrpw
    srx = math.sin(rx);
    crx = math.cos(rx);
    sry = math.sin(ry);
    cry = math.cos(ry);
    srz = math.sin(rz);
    crz = math.cos(rz);
    return([[ cry*crz, -cry*srz, sry, x],[crx*srz + crz*srx*sry, crx*crz - srx*sry*srz, -cry*srx, y],[srx*srz - crx*crz*sry, crz*srx + crx*sry*srz, crx*cry, z],[0,0,0,1]])

def Pose_2_TxyzRxyz(H):
    """Retrieve the position (mm) and Euler angles (rad) as an array [x,y,z,rx,ry,rz] given a pose. 
    It returns the values that correspond to the following operation: 
    H = transl(x,y,z)*rotx(rx)*roty(ry)*rotz(rz).
    
    :param H: pose
    :type H: :class:`.Mat`
    
    .. seealso:: :class:`.Mat`, :func:`~robodk.TxyzRxyz_2_Pose`, :func:`~robodk.Pose_2_TxyzRxyz`, :func:`~robodk.Pose_2_ABB`, :func:`~robodk.Pose_2_Adept`, :func:`~robodk.Pose_2_Comau`, :func:`~robodk.Pose_2_Fanuc`, :func:`~robodk.Pose_2_KUKA`, :func:`~robodk.Pose_2_Motoman`, :func:`~robodk.Pose_2_Nachi`, :func:`~robodk.Pose_2_Staubli`, :func:`~robodk.Pose_2_UR`, :func:`~robodk.quaternion_2_pose`
    """
    x = H[0,3]
    y = H[1,3]
    z = H[2,3]
    a = H[0,0]
    b = H[0,1]
    c = H[0,2]
    d = H[1,2]
    e = H[2,2]
    if c > (1.0 - 1e-10):
        ry1 = math.pi/2
        rx1 = 0
        rz1 = math.atan2(H[1,0],H[1,1])
    elif c < (-1.0 + 1e-10):
        ry1 = -math.pi/2
        rx1 = 0
        rz1 = math.atan2(H[1,0],H[1,1])
    else:
        sy = c
        cy1 = +math.sqrt(1-sy*sy)
        sx1 = -d/cy1
        cx1 = e/cy1
        sz1 = -b/cy1
        cz1 =a/cy1
        rx1 = math.atan2(sx1,cx1)
        ry1 = math.atan2(sy,cy1)
        rz1 = math.atan2(sz1,cz1)
    return [x, y, z, rx1, ry1, rz1]
