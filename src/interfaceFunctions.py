from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *; 
from PyQt5.QtGui import QIcon, QPixmap, QBitmap, QPainter, QPen, QImage, QColor
from PyQt5.QtCore import QRect,QPoint,QPointF,QLineF; 
import sys
import numpy as np
from scipy.spatial import ConvexHull




# def imageKeyRelease(QKeyEvent,wind):

# 	print("Key Pressed: {}".format(QKeyEvent.key())); 

# 	speed = 10; 
# 	if(QKeyEvent.key() == QtCore.Qt.Key_Up):
# 		wind.robPose[1] = wind.robPose[1] - speed; 
# 	elif(QKeyEvent.key() == QtCore.Qt.Key_Left):
# 		wind.robPose[0] = wind.robPose[0] - speed;
# 	elif(QKeyEvent.key() == QtCore.Qt.Key_Down):
# 		wind.robPose[1] = wind.robPose[1] + speed; 
# 	elif(QKeyEvent.key() == QtCore.Qt.Key_Right):
# 		wind.robPose[0] = wind.robPose[0] + speed;

# 	print("RobPose: {}".format(wind.robPose)); 

# 	radius = 25; 

# 	for i in range(-int(radius/2)+wind.robPose[0],int(radius/2)+wind.robPose[0]):
# 		for j in range(-int(radius/2) + wind.robPose[1],int(radius/2)+wind.robPose[1]):
# 			#if(i>0 and j>0 and i<wind.imgHeight and j<wind.imgWidth):
# 			tmp1 = min(wind.imgWidth-1,max(0,i)); 
# 			tmp2 = min(wind.imgHeight-1,max(0,j)); 
# 			wind.boolmask[tmp1,tmp2] = False; 

# 	updateImage(wind); 



def startSketch(wind):
	wind.sketchListen=True;
	wind.allSketchPaths.append([]); 

def imageMousePress(QMouseEvent,wind):
	if(wind.droneClickListen):
		wind.droneClickListen = False; 
		tmp = [QMouseEvent.scenePos().x(),QMouseEvent.scenePos().y()]; 
		wind.timeLeft = wind.DRONE_WAIT_TIME;
		revealMapDrone(wind,tmp);
		updateTimer(wind);   
	elif(wind.sketchListen):
		wind.sketchingInProgress = True; 
		name = wind.sketchName.text(); 
		if(name not in wind.allSketchPlanes.keys()):
			wind.allSketchPlanes[name] = makeTransparentPlane(wind); 
		else:
			planeFlushPaint(wind.allSketchPlanes[name],[]);

def imageMouseMove(QMouseEvent,wind):
	if(wind.sketchingInProgress):
		tmp = [int(QMouseEvent.scenePos().x()),int(QMouseEvent.scenePos().y())]; 
		wind.allSketchPaths[-1].append(tmp); 
		#add points to be sketched
		points = []; 
		si = wind.sketchDensity;
		for i in range(-si,si+1):
			for j in range(-si,si+1):
				points.append([tmp[0]+i,tmp[1]+j]); 

		name = wind.sketchName.text(); 
		planeAddPaint(wind.allSketchPlanes[name],points); 

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
		updateModels(wind,tmp);

def updateModels(wind,name):
	pairedPoints = np.array(wind.allSketches[name]); 
	cHull = ConvexHull(pairedPoints); 
	xFudge = len(name)*10/2; 

	#fitSimplePolyToHull
	vertices = fitSimplePolyToHull(cHull,pairedPoints,N=5); 


	centx = np.mean([vertices[i][0] for i in range(0,len(vertices))])-xFudge; 
	centy = np.mean([vertices[i][1] for i in range(0,len(vertices))]) 
	wind.sketchLabels[name] = [centx,centy]; 


	planeFlushPaint(wind.allSketchPlanes[name]); 

	pm = wind.allSketchPlanes[name].pixmap(); 
	painter = QPainter(pm); 
	pen = QPen(QColor(255,0,0,255)); 
	pen.setWidth(10); 
	painter.setPen(pen); 
	painter.setFont(QtGui.QFont('Decorative',20)); 
	painter.drawText(QPointF(centx,centy),name); 
	
	for i in range(0,len(vertices)):
		painter.drawLine(QLineF(vertices[i-1][0],vertices[i-1][1],vertices[i][0],vertices[i][1])); 

	painter.end(); 
	wind.allSketchPlanes[name].setPixmap(pm); 


def fitSimplePolyToHull(cHull,pairedPoints,N = 4):
	vertices = [];  

	for i in range(0,len(cHull.vertices)):
		vertices.append([pairedPoints[cHull.vertices[i],0],pairedPoints[cHull.vertices[i],1]]);

	
	while(len(vertices) > N):
		allAngles = []; 
		#for each point, find the angle it forces between the two points on either side
		#find first point
		a = vertices[-1]; 
		b = vertices[0]; 
		c = vertices[1]; 
		allAngles.append(abs(angleOfThreePoints(a,b,c))); 
		for i in range(1,len(vertices)-1):
			#find others
			a = vertices[i-1];
			b = vertices[i]; 
			c = vertices[i+1]; 
			allAngles.append(abs(angleOfThreePoints(a,b,c)));
		#find last point
		a = vertices[-2]; 
		b = vertices[-1]; 
		c = vertices[0]; 
		allAngles.append(abs(angleOfThreePoints(a,b,c))); 

		#Experimental:
		#Smooth angles with gaussian convolution
		#Mean: 0, SD: perimeter/N
		# perimeter = distanceAlongPoints(vertices,-1,len(vertices)); 

		# allAngles = smoothAngles(vertices,allAngles,perimeter/N); 


		#remove the point with the smallest angle change
		smallest = min(allAngles); 
		vertices.remove(vertices[allAngles.index(smallest)]); 

		#repeat until number is equal to N


	return vertices;

def distance(p1,p2):
	return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2);

def angleOfThreePoints(a,b,c):
	ab = [b[0]-a[0],b[1]-a[1]]; 
	bc = [c[0]-b[0],c[1]-b[1]]; 
	num = ab[0]*bc[0] + ab[1]*bc[1]; 
	dem = distance([0,0],ab)*distance([0,0],bc); 
	theta = np.arccos(num/dem); 
	return theta; 

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
		wind.droneClickListen = True; 


def revealMapDrone(wind,point):

	rad = wind.DRONE_VIEW_RADIUS;
	points=[]; 

	print()
	for i in range(-int(rad/2)+int(point[0]),int(rad/2)+int(point[0])):
		for j in range(-int(rad/2) + int(point[1]),int(rad/2)+int(point[1])):
			tmp1 = min(wind.imgWidth-1,max(0,i)); 
			tmp2 = min(wind.imgHeight-1,max(0,j)); 
			points.append([tmp1,tmp2]); 

	defog(wind,points); 


def updateTimer(wind):
	rcol = 255*wind.timeLeft/wind.DRONE_WAIT_TIME; 
	gcol = 255*(wind.DRONE_WAIT_TIME-wind.timeLeft)/wind.DRONE_WAIT_TIME; 

	wind.updateTimerLCD.setStyleSheet("background-color:rgb({},{},0)".format(rcol,gcol)); 
	wind.updateTimerLCD.display(wind.timeLeft); 

	if(wind.timeLeft == 0):
		wind.droneButton.show(); 
	else:
		wind.droneButton.hide(); 


def getNewRobotPullQuestion(wind):
	wind.pullQuestion.setText(np.random.choice(wind.questions)); 



#Start New Functions
def makeTruePlane(wind):

	wind.trueImage = QPixmap('../img/eastCampus_2017_2.jpg'); 
	wind.imgWidth = wind.trueImage.size().width(); 
	wind.imgHeight = wind.trueImage.size().height(); 

	wind.truthWidget = wind.imageScene.addPixmap(wind.trueImage); 


def makeFogPlane(wind):
	fI = QPixmap('../img/eastCampus_1999_2.jpg')
	wind.fogImage = QImage(wind.imgWidth,wind.imgHeight,QtGui.QImage.Format_ARGB32);
	paintMask = QPainter(wind.fogImage);  
	paintMask.drawPixmap(0,0,fI);
	paintMask.end();

	wind.fogPlane = wind.imageScene.addPixmap(QPixmap.fromImage(wind.fogImage)); 


def makeTransparentPlane(wind):
	
	testMap = QPixmap(wind.imgWidth,wind.imgHeight); 
	testMap.fill(QtCore.Qt.transparent); 
	
	tmp = wind.imageScene.addPixmap(testMap); 

	return tmp; 



def defog(wind,points):

	for p in points:
		wind.fogImage.setPixelColor(p[0],p[1],QColor(0,0,0,0)); 

	wind.fogPlane.setPixmap(QPixmap.fromImage(wind.fogImage));

def planeAddPaint(planeWidget,points):

	pm = planeWidget.pixmap(); 

	painter = QPainter(pm); 
	pen = QPen(QColor(0,0,0,255)); 
	painter.setPen(pen)
	
	for p in points:
		painter.drawPoint(p[0],p[1]); 
	painter.end(); 
	planeWidget.setPixmap(pm); 

def planeFlushPaint(planeWidget,points=[]):
	pm = planeWidget.pixmap(); 
	pm.fill(QColor(0,0,0,0)); 

	painter = QPainter(pm); 
	pen = QPen(QColor(0,0,0,255)); 
	painter.setPen(pen)
	
	for p in points:
		painter.drawPoint(p[0],p[1]); 
	painter.end(); 
	planeWidget.setPixmap(pm); 


def loadQuestions(wind):
	f = open('../data/Questions.txt','r'); 
	lines = f.read().split("\n"); 
	wind.questions = lines; 