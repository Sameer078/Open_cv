import cv2
import numpy as np
import mediapipe as mp                                          # library for detecting face, palm,body pose etc..
import math
from ctypes import cast, POINTER                                # provides C compatible data types and allow calling functions in DDLs or shared library 
from comtypes import CLSCTX_ALL  
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume    # library for audio control methods

def findPosition(img, handNo=0):
    lmList = []
    if results.multi_hand_landmarks:
        myHand = results.multi_hand_landmarks[handNo]
        for id, lm in enumerate(myHand.landmark):
            h, w, c = img.shape
            cx, cy = int(lm.x * w), int(lm.y * h)               # converting x,y values according to frame size
            lmList.append([id, cx, cy])
    return lmList

def Vol_con():
    global results
    wCam, hCam = 700, 500                                       # changing width and height of cam
    cap = cv2.VideoCapture(0)                                   # real time video capture from cam
    cap.set(3, wCam)                                            # setting width  (index==3)
    cap.set(4, hCam)                                            # setting height (index==4)
    mpHands=mp.solutions.hands
    hands=mpHands.Hands()
    mpDraw=mp.solutions.drawing_utils                           # use for drawing points/marks and connections on solution detected
    devices = AudioUtilities.GetSpeakers()                      # control of audio using pycaw 
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)    
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volRange = volume.GetVolumeRange()                          # gives range of volume (min and max value of volume)
    minVol = volRange[0] 
    maxVol = volRange[1]
    vol = 0
    volBar = 400
    volPer = 0
    while True:
        success, img = cap.read()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)          # coverting bgr to rgb because mediapipe use only rgb
        results = hands.process(img)
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                mpDraw.draw_landmarks(img, handLms,mpHands.HAND_CONNECTIONS)
        lmList = findPosition(img)
        if len(lmList) != 0:
            x1, y1 = lmList[4][1], lmList[4][2]             # 4= tip point of thumb 
            x2, y2 = lmList[8][1], lmList[8][2]             # 8= tip point of index finger
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            cv2.circle(img, (x1, y1), 15, (0,255, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (0,255, 0), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), ( 0,255,0), 3)
            length = math.hypot(x2 - x1, y2 - y1)
            vol = np.interp(length, [30, 220], [minVol, maxVol])    # interpolation is a method for generating points between given points 
            volBar = np.interp(length, [30, 220], [400, 150])
            volPer = np.interp(length, [30, 220], [0, 100])
            volume.SetMasterVolumeLevel(vol, None)          # setting volume according to distance between fingers
            if length <= 30:
                cv2.circle(img, (cx, cy), 15, ( 255, 0,0), cv2.FILLED)
        cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
        cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,1, (255, 0, 0), 3)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.imshow("Volume Controller", img)
        if cv2.waitKey(1) & 0xFF==ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    Vol_con()


