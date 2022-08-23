                           ##########################  VOLUME AND BRIGHTNESS CONTROLLER  ###########################

import cv2
import mediapipe as mp
import numpy as np
import screen_brightness_control as sbc
import math
from ctypes import cast, POINTER                                # provides C compatible data types and allow calling functions in DDLs or shared library 
from comtypes import CLSCTX_ALL  
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume    # library for audio control methods
upcount=0
def Vol_con():
    devices = AudioUtilities.GetSpeakers()                      # control of audio using pycaw 
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)    
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volRange = volume.GetVolumeRange()                          # gives range of volume (min and max value of volume)
    minVol = volRange[0] 
    maxVol = volRange[1]
    vol = 0
    volBar = 400
    volPer = 0
    if len(lmlist) != 0:
        x1, y1 = lmlist[4][1], lmlist[4][2]             # 4= tip point of thumb 
        x2, y2 = lmlist[8][1], lmlist[8][2]             # 8= tip point of index finger
        cv2.circle(img, (x1, y1), 10, (0,0, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0,0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), ( 255,0,0), 3)
        length = math.hypot(x2 - x1, y2 - y1)
        vol = np.interp(length, [30, 220], [minVol, maxVol])    # interpolation is a method for generating points between given points 
        volBar = np.interp(length, [30, 220], [400, 150])
        volPer = np.interp(length, [30, 220], [0, 100])
        volume.SetMasterVolumeLevel(vol, None)          # setting volume according to distance between fingers
    cv2.rectangle(img, (40, 150), (70, 400), (255, 0, 0), 2)
    cv2.rectangle(img, (40, int(volBar)), (70, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'Volume {int(volPer)} %', (30, 430), cv2.FONT_HERSHEY_SIMPLEX,1, (255, 0, 0), 2)

def Bright_con():
    scBar=400
    scPer=0
    if len(lmlist)!=0:
        x1,y1=lmlist[4][1],lmlist[4][2]
        x2,y2=lmlist[12][1],lmlist[12][2]
        cv2.circle(img,(x1,y1),10,(0,0,0),-1)
        cv2.circle(img,(x2,y2),10,(0,0,255),-1)
        cv2.line(img,(x1,y1),(x2,y2),(0,0,255),3)
        length=math.hypot(x2-x1,y2-y1)
        bright=np.interp(length,[50,180],[0,100])
        scPer=np.interp(length,[50,180],[0,100])
        scBar=np.interp(length,[50,180],[400,150])
        sbc.set_brightness(int(bright))
    cv2.rectangle(img,(570,150),(600,400),(0,0,255),2)
    cv2.rectangle(img,(570,int(scBar)),(600,400),(0,0,255),-1)
    cv2.putText(img,f'Brightness: {int(scPer)} %',(380,430),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)


cap=cv2.VideoCapture(0)
cap.set(3, 900)
cap.set(4, 600)
mpHands=mp.solutions.hands
hands=mpHands.Hands()
mpDraw=mp.solutions.drawing_utils
fing_cord=[(8,6),(12,10),(16, 14),(20,18)]
thumb_cord=(4,2)
while True:
    success,img=cap.read()
    img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    results=hands.process(img)
    lmlist=[]
    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:
            for id, lm in enumerate(hand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)               # converting x,y values according to frame size
                lmlist.append([id, cx, cy])
            mpDraw.draw_landmarks(img,hand,mpHands.HAND_CONNECTIONS)
            upcount=0
            for cord in fing_cord:
                if lmlist[cord[0]][2]<lmlist[cord[1]][2]:           # if y value of tip of finger is less than y value of middle point of finger than finger count is incrementd
                    upcount+=1
            if lmlist[thumb_cord[0]][1]>lmlist[thumb_cord[1]][1]:   # thumb count depends upon x value for left hand( use < ) and for right hand (use > )
                upcount+=1
    cv2.putText(img,f'Finger count:{upcount}',(30,40),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)



    #############################################
    '''Using both volume and brightness controller by directly calling the function'''
    #############################################
    '''
    Bright_con()
    Vol_con()
    '''



    #############################################
    '''Using both volume and brightness controller with finger counts
        NOTE:: move thumb towards finger for better results
    '''
    #############################################
    '''
    x=upcount
    if x==5:
        Bright_con()
    elif x==3:
        Vol_con()
    '''

    img=cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
    cv2.imshow("controller",img)
    if cv2.waitKey(1) & 0xFF==ord('q'):
            break
cap.release()
cv2.destroyAllWindows()
