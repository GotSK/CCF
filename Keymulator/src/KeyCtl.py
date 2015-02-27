#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: Christian
'''
import config

import ctypes as ct

from win32con import SW_MINIMIZE, SW_RESTORE
from win32ui import FindWindow, error as ui_err
from time import sleep


class cls_KeyBdInput(ct.Structure):
    _fields_ = [
        ("wVk", ct.c_ushort),
        ("wScan", ct.c_ushort),
        ("dwFlags", ct.c_ulong),
        ("time", ct.c_ulong),
        ("dwExtraInfo", ct.POINTER(ct.c_ulong) )
    ]

class cls_HardwareInput(ct.Structure):
    _fields_ = [
        ("uMsg", ct.c_ulong),
        ("wParamL", ct.c_short),
        ("wParamH", ct.c_ushort)
    ]

class cls_MouseInput(ct.Structure):
    _fields_ = [
        ("dx", ct.c_long),
        ("dy", ct.c_long),
        ("mouseData", ct.c_ulong),
        ("dwFlags", ct.c_ulong),
        ("time", ct.c_ulong),
        ("dwExtraInfo", ct.POINTER(ct.c_ulong) )
    ]

class cls_Input_I(ct.Union):
    _fields_ = [
        ("ki", cls_KeyBdInput),
        ("mi", cls_MouseInput),
        ("hi", cls_HardwareInput)
    ]

class cls_Input(ct.Structure):
    _fields_ = [
        ("type", ct.c_ulong),
        ("ii", cls_Input_I)
    ]


def find_window( s_app_name ):

    try:
        window1 = FindWindow(  None, s_app_name,)
        return window1
    except ui_err:
        pass
    except:
        raise

    try:
        window1 = FindWindow( s_app_name, None, )
        return window1
    except ui_err:
        return None
    except:
        raise


def make_input_objects( l_keys ):

    p_ExtraInfo_0 = ct.pointer(ct.c_ulong(0))

    l_inputs = [ ]
    for n_key, n_updown in l_keys:
        ki = cls_KeyBdInput( n_key, 0, n_updown, 0, p_ExtraInfo_0 )
        ii = cls_Input_I()
        ii.ki = ki
        l_inputs.append( ii )

    n_inputs = len(l_inputs)

    l_inputs_2=[]
    for ndx in range( 0, n_inputs ):
        s2 = "(1, l_inputs[%s])" % ndx
        l_inputs_2.append(s2)
    s_inputs = ', '.join(l_inputs_2)


    cls_input_array = cls_Input * n_inputs
    o_input_array = eval( "cls_input_array( %s )" % s_inputs )

    p_input_array = ct.pointer( o_input_array )
    n_size_0 = ct.sizeof( o_input_array[0] )

    # these are the args for user32.SendInput()
    return ( n_inputs, p_input_array, n_size_0 )

    '''It is interesting that o_input_array has gone out of scope
    by the time p_input_array is used, but it works.'''


def send_input( window1, t_inputs, b_minimize=False ):

    tpl1 = window1.GetWindowPlacement()
    was_min = False
    if tpl1[1] == 2:
        was_min = True
        window1.ShowWindow(SW_RESTORE)
        sleep(0.2)

    window1.SetForegroundWindow()
    sleep(0.2)
    window1.SetFocus()
    sleep(0.2)
    rv = ct.windll.user32.SendInput( *t_inputs )

    if was_min and b_minimize:
        sleep(0.3) # if the last input was Save, it may need time to take effect
        window1.ShowWindow(SW_MINIMIZE)

    return rv



# define some commonly-used key sequences
t_ctrl_s = (  # save in many apps
    ( 0x11, 0 ),
    ( 0x53, 0 ),
    ( 0x11, 2 ),
)
t_ctrl_r = (  # reload in some apps
    ( 0x11, 0 ),
    ( 0x52, 0 ),
    ( 0x11, 2 ),
)

#pokemon test run
t_circle = (
    (0x57, 0),
    (0x57, 2),
    (0x41, 0),
    (0x41, 2),
    (0x53, 0),
    (0x53, 2),
    (0x44, 0),
    (0x44, 2),
)
t_straight = (
    (0x57, 0),
    (0x57, 2),
    (0x57, 0),
    (0x57, 2),
    (0x57, 0),
    (0x57, 2),
    (0x57, 0),
    (0x57, 2),
    (0x57, 0),
    (0x57, 2),
)
def sendImmediateKeystroke(keystroke):
    i_interval = 0.5
    t_stroke = (
                (config.inputMap[keystroke],0),
                (config.inputMap[keystroke],2),
    )
    l_keys = []
    l_keys.extend(t_stroke)
    
    s_app_name = "DeSmuME 0.9.10 x86"

    window1 = find_window( s_app_name )
    if window1 == None:
        print( "%r has no window." % s_app_name )
        input( 'press enter to close' )
        exit()
    print('Select Focus Window! Input will commence in ')
    #for i in range (0,3):
    #    print((i-3) * -1)
     #   sleep(1)
    window1.SetForegroundWindow()
    for i in range (0,int(len(list(l_keys))/2)):
        l_input_part = l_keys[2*i:(2*i+ 2)]
        print(l_input_part)
           
        press = make_input_objects(l_input_part[0:1])
        release = make_input_objects(l_input_part[1:2])
        
        ct.windll.user32.SendInput( *press )
        sleep(0.1)
        ct.windll.user32.SendInput( *release )
        #n = send_input( window1, press)
        #sleep(0.05)
        #n = send_input( window1, release)
        sleep(i_interval)
    
    
def test():

    i_interval = 0.5

    l_keys = [ ]
    
    
    l_keys.extend(t_straight)


    #s_app_name = "Unbenannt - Editor"
    s_app_name = "DeSmuME 0.9.10 x86"

    window1 = find_window( s_app_name )
    if window1 == None:
        print( "%r has no window." % s_app_name )
        input( 'press enter to close' )
        exit()
    print('Select Focus Window! Input will commence in ')
    for i in range (0,3):
        print((i-3) * -1)
        sleep(1)
    window1.SetForegroundWindow()
    for i in range (0,int(len(list(l_keys))/2)):
        l_input_part = l_keys[2*i:(2*i+ 2)]
        print(l_input_part)
           
        press = make_input_objects(l_input_part[0:1])
        release = make_input_objects(l_input_part[1:2])
        
        ct.windll.user32.SendInput( *press )
        sleep(0.1)
        ct.windll.user32.SendInput( *release )
        #n = send_input( window1, press)
        #sleep(0.05)
        #n = send_input( window1, release)
        sleep(i_interval)

    ## print( "SendInput returned: %r" % n )
    ## print( "GetLastError: %r" % ct.windll.kernel32.GetLastError() )
    ## input( 'press enter to close' )



if __name__ == '__main__':
    test()