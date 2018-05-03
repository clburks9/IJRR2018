from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *; 
from PyQt5.QtGui import QIcon, QPixmap, QBitmap, QPainter, QPen
from PyQt5.QtCore import QRect,QPoint,QPointF; 
import sys
import numpy as np
from scipy.spatial import ConvexHull


def timerStart(wind):
	wind.myTimer = QtCore.QTimer(wind); 
	wind.timeLeft = wind.DRONE_WAIT_TIME; 

	wind.myTimer.timeout.connect(lambda: timerTimeout(wind)); 
	wind.myTimer.start(1000); 

	updateTimer(wind); 


def timerTimeout(wind):
	if(wind.timeLeft > 0):	
		wind.timeLeft -= 1; 
	updateTimer(wind); 



def launchDrone(wind):
	if(wind.timeLeft==0):
		#print("Drone Launched"); 
		#wind.timeLeft = wind.DRONE_WAIT_TIME;
		wind.droneClickListen = True; 

	updateTimer(wind); 


def imageMousePress(QMouseEvent,wind):
	if(wind.droneClickListen):
		wind.droneClickListen = False; 
		tmp = [QMouseEvent.pos().x(),QMouseEvent.pos().y()]; 
		wind.timeLeft = wind.DRONE_WAIT_TIME;
		revealMapDrone(wind,tmp);  
	elif(wind.sketchListen):
		wind.sketchingInProgress = True; 
	else:
		wind.fogMapWidget.setFocus(True); 


def startSketch(wind):
	wind.sketchListen=True;
	wind.allSketchPaths.append([]);  

def imageMouseMove(QMouseEvent,wind):
	if(wind.sketchingInProgress):
		#print(QMouseEvent.pos());
		tmp = [QMouseEvent.pos().x(),QMouseEvent.pos().y()]; 
		wind.allSketchPaths[-1].append(tmp); 
		wind.sketchMask[tmp[0],tmp[1]] = 1; 

def imageMouseRelease(QMouseEvent,wind):

	if(wind.sketchingInProgress):
		#make shape
		#add name to list
		tmp = wind.sketchName.text(); 
		wind.sketchName.clear();
		wind.sketchName.setPlaceholderText("Sketch Name");
		wind.objectsDrop.addItem(tmp);
		wind.allSketchNames.append(tmp); 
		wind.allSketches[tmp] = wind.allSketchPaths[-1]; 

		wind.sketchListen = False; 
		wind.sketchingInProgress = False; 
		#print("Added name to list");
		updateModels(wind,tmp);
		updateImage(wind); 
		

		#print(wind.allSketches); 


def imageKeyRelease(QKeyEvent,wind):

	print("Key Pressed: {}".format(QKeyEvent.key())); 

	speed = 10; 
	if(QKeyEvent.key() == QtCore.Qt.Key_Up):
		wind.robPose[1] = wind.robPose[1] - speed; 
	elif(QKeyEvent.key() == QtCore.Qt.Key_Left):
		wind.robPose[0] = wind.robPose[0] - speed;
	elif(QKeyEvent.key() == QtCore.Qt.Key_Down):
		wind.robPose[1] = wind.robPose[1] + speed; 
	elif(QKeyEvent.key() == QtCore.Qt.Key_Right):
		wind.robPose[0] = wind.robPose[0] + speed;

	print("RobPose: {}".format(wind.robPose)); 

	radius = 25; 

	for i in range(-int(radius/2)+wind.robPose[0],int(radius/2)+wind.robPose[0]):
		for j in range(-int(radius/2) + wind.robPose[1],int(radius/2)+wind.robPose[1]):
			#if(i>0 and j>0 and i<wind.imgHeight and j<wind.imgWidth):
			tmp1 = min(wind.imgWidth-1,max(0,i)); 
			tmp2 = min(wind.imgHeight-1,max(0,j)); 
			wind.boolmask[tmp1,tmp2] = False; 

	updateImage(wind); 


def imageKeyPress(QKeyEvent,wind):
	#wind.fogMapWidget.setFocus(True); 
	pass; 

def revealMapDrone(wind,point):

	radius = 75; 
	for i in range(-int(radius/2)+point[0],int(radius/2)+point[0]):
		for j in range(-int(radius/2) + point[1],int(radius/2)+point[1]):
			#if(i>0 and j>0 and i<wind.imgHeight and j<wind.imgWidth):
			tmp1 = min(wind.imgWidth-1,max(0,i)); 
			tmp2 = min(wind.imgHeight-1,max(0,j)); 
			wind.boolmask[tmp1,tmp2] = False; 

	#print("Mask Updated"); 
	updateImage(wind); 





def updateTimer(wind):
	rcol = 255*wind.timeLeft/wind.DRONE_WAIT_TIME; 
	gcol = 255*(wind.DRONE_WAIT_TIME-wind.timeLeft)/wind.DRONE_WAIT_TIME; 
	#wind.progressBar.setValue(int(100*gcol/255)); 

	wind.updateTimerLCD.setStyleSheet("background-color:rgb({},{},0)".format(rcol,gcol)); 
	wind.updateTimerLCD.display(wind.timeLeft); 

	if(wind.timeLeft == 0):
		wind.droneButton.show(); 
	else:
		wind.droneButton.hide(); 

def updateModels(wind,name):

	cHull = ConvexHull(wind.allSketches[name]); 

	#vertices = fitSimplePolyToHull(cHull,wind.allSketches[wind],N=5); 

	xFudge = len(name)*10/2; 

	centx = np.mean(cHull.points[cHull.vertices,0]-xFudge); 
	centy = np.mean(cHull.points[cHull.vertices,1]); 

	wind.sketchLabels[name] = [centx,centy]; 




def updateImage(wind):

	paintMask = QPainter(wind.fogImage);  
	pen = QPen(); 
	pen.setWidth(10); 
	paintMask.setPen(pen)

	for i in range(0,wind.imgWidth):
		for j in range(0,wind.imgHeight):
			#if boolmask is false, change pixel at (i,j) in fog image to true image
			if(wind.boolmask[i,j] == False):
				paintMask.drawPixmap(QPoint(i,j),wind.trueImage,QRect(QPoint(i,j),QPoint(i,j))); 
			if(wind.sketchMask[i,j] != 0):
				paintMask.drawPoint(QPoint(i,j)); 
	paintMask.end(); 

	paintText = QPainter(wind.fogImage); 
	paintText.setPen(QtGui.QColor(255,0,0)); 
	paintText.setFont(QtGui.QFont("Decorative",20)); 
	#print(wind.sketchLabels);
	for key in wind.sketchLabels.keys():
		#print(key); 
		[centx,centy] = wind.sketchLabels[key]; 
		print("Painting: {}".format(key)); 
		paintText.drawText(QPointF(centx,centy),key); 
		 
		wind.fogMapWidget.setPixmap(wind.fogImage); 
	paintText.end();

	wind.fogMapWidget.setPixmap(wind.fogImage); 



def getNewRobotPullQuestion(wind):
	wind.pullQuestion.setText(np.random.choice(wind.questions)); 

