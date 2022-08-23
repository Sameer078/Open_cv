import screen_brightness_control as sbc
import cv2
import mediapipe as mp
import numpy as np
import math


def Bright_con():
    cap=cv2.VideoCapture(0)
    mpHands=mp.solutions.hands
    hands=mpHands.Hands()
    mpDraw=mp.solutions.drawing_utils
    scBar=350
    scPer=0
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
        if len(lmlist)!=0:
            x1,y1=lmlist[4][1],lmlist[4][2]
            x2,y2=lmlist[8][1],lmlist[8][2]
            cv2.circle(img,(x1,y1),10,(255,0,0),-1)
            cv2.circle(img,(x2,y2),10,(255,0,0),-1)
            cv2.line(img,(x1,y1),(x2,y2),(0,255,0),3)
            length=math.hypot(x2-x1,y2-y1)
            bright=np.interp(length,[20,180],[0,100])
            scPer=np.interp(length,[20,180],[0,100])
            scBar=np.interp(length,[20,180],[350,60])
            sbc.set_brightness(int(bright))
        cv2.rectangle(img,(30,60),(60,350),(0,255,0),2)
        cv2.rectangle(img,(30,int(scBar)),(60,350),(0,255,0),-1)
        cv2.putText(img,f'{int(scPer)} %',(30,400),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0),2)
        img=cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
        cv2.imshow("Brightness Controller",img)
        if cv2.waitKey(1) & 0xFF==ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__=="__main__":
    Bright_con()

