

'''
Created on Apr 3, 2016

@author: Bill BEGUERADJ

Modified to return points from drawing

'''
import cv2
import numpy as np 

drawing=False # true if mouse is pressed
mode=True # if True, draw rectangle. Press 'm' to toggle to curve

allPoints = [[],[]]; 

# mouse callback function
def shapeDraw(event,former_x,former_y,flags,param):
    global current_former_x,current_former_y,drawing, mode

    if event==cv2.EVENT_LBUTTONDOWN:
        drawing=True
        current_former_x,current_former_y=former_x,former_y
        #allPoints[0].append(former_x); 
        #allPoints[1].append(former_y);

    elif event==cv2.EVENT_MOUSEMOVE:
        if drawing==True:
            if mode==True:
                cv2.line(im,(current_former_x,current_former_y),(former_x,former_y),(0,0,255),5)
                current_former_x = former_x
                current_former_y = former_y
                #print former_x,former_y
                allPoints[0].append(former_x); 
                allPoints[1].append(former_y); 
    elif event==cv2.EVENT_LBUTTONUP:
        drawing=False
        if mode==True:
            cv2.line(im,(current_former_x,current_former_y),(former_x,former_y),(0,0,255),5)
            current_former_x = former_x
            current_former_y = former_y


    return former_x,former_y    


def shapeRequest():
    global im
    im = cv2.imread("../img/testBel.png")
    #print(im.shape);
    cv2.namedWindow("Input Image")
    cv2.setMouseCallback('Input Image',shapeDraw)
    while(cv2.getWindowProperty("Input Image",cv2.WND_PROP_VISIBLE) > 0):
        cv2.imshow("Input Image",im) 
        k=cv2.waitKey(1)
        if k==27:
            break
    cv2.destroyAllWindows()
    return allPoints; 