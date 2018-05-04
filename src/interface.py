"""
***********************************************************
File: interface.py
Author: Luke Burks
Date: April 2018

Implements a PYQT5 interface that allows human aided 
target tracking through sketches, drone launches, 
and human push/robot pull semantic information

Using Model-View-Controller Architecture

Version History (Sort of):
0.1.1: added robot movement


***********************************************************
"""

__author__ = "Luke Burks"
__copyright__ = "Copyright 2018"
__credits__ = ["Luke Burks"]
__license__ = "GPL"
__version__ = "0.1.1"
__maintainer__ = "Luke Burks"
__email__ = "luke.burks@colorado.edu"
__status__ = "Development"


from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *; 
from PyQt5.QtGui import *;
from PyQt5.QtCore import *;
import sys

from interfaceFunctions import *; 
from planeFunctions import *;
import numpy as np
import time

from matplotlib.backends.backend_qt4agg import FigureCanvas
from matplotlib.figure import Figure, SubplotParams
import matplotlib.pyplot as plt

from problemModel import Model

class SimulationWindow(QWidget):
	def __init__(self):
		super(SimulationWindow,self).__init__()
		self.setGeometry(1,1,1250,800)
		self.layout = QGridLayout(); 
		self.layout.setColumnStretch(0,2); 
		self.layout.setColumnStretch(1,2);
		# self.layout.setColumnStretch(2,1); 
		# self.layout.setColumnStretch(3,1);
		# self.layout.setColumnStretch(4,1);
		self.setLayout(self.layout); 


		self.trueModel = Model(trueModel=True);
		self.assumedModel = Model(trueModel=False); 

		self.sketchListen=False; 
		self.sketchingInProgress = False; 
		self.allSketches = {}; 
		self.allSketchNames = []; 
		self.allSketchPaths = []; 
		self.allSketchPlanes = {}; 
		self.sketchLabels = {}; 
		self.sketchDensity = 5; 

		self.droneClickListen = False; 
		self.DRONE_WAIT_TIME = 5; 
		self.timeLeft = self.DRONE_WAIT_TIME; 
		self.DRONE_VIEW_RADIUS = 75; 

		self.ROBOT_VIEW_RADIUS = 25; 
		self.ROBOT_SIZE_RADIUS = 10; 
		self.ROBOT_NOMINAL_SPEED = 10; 
		self.TARGET_SIZE_RADIUS = 10; 

		self.makeMapGraphics();

		self.populateInterface(); 
		self.connectElements(); 

		self.makeRobot();
		self.makeTarget();

		loadQuestions(self); 

		timerStart(self); 

		self.show()


	def keyReleaseEvent(self,event):
		arrowEvents = [QtCore.Qt.Key_Up,QtCore.Qt.Key_Down,QtCore.Qt.Key_Left,QtCore.Qt.Key_Right]; 
		if(event.key() in arrowEvents):
			moveRobot(self,event); 
		
	def makeRobot(self):
		self.copPose = [200,500,0]; 
		moveRobot(self,None); 

	def makeTarget(self):
		self.robPose = [400,200,0]; 
		points = []; 
		rad = self.TARGET_SIZE_RADIUS; 
		for i in range(-int(rad/2)+self.robPose[0],int(rad/2)+self.robPose[0]):
			for j in range(-int(rad/2) + self.robPose[1],int(rad/2)+self.robPose[1]):
				#if(i>0 and j>0 and i<self.imgHeight and j<self.imgWidth):
				tmp1 = min(self.imgWidth-1,max(0,i)); 
				tmp2 = min(self.imgHeight-1,max(0,j)); 
				points.append([tmp1,tmp2]); 
		planeAddPaint(self.truePlane,points,QColor(255,0,255,255)); 


	def makeMapGraphics(self):

		#Image View
		#************************************************************
		self.imageView = QGraphicsView(self); 
		self.imageScene = QGraphicsScene(self); 

		makeTruePlane(self); 

		makeFogPlane(self);

		#make sketchPlane
		self.sketchPlane = makeTransparentPlane(self); 

		#make robotPose plane
		self.robotPlane = makeTransparentPlane(self); 

		#make targetPose plane
		self.targetPlane = makeTransparentPlane(self);

		#make click layer
		self.clickPlane = makeTransparentPlane(self); 

		self.imageView.setScene(self.imageScene); 
		self.layout.addWidget(self.imageView,0,1,15,1); 


		#Belief Map
		#************************************************************
		print("Make beliefs a tabbed widget with transitions"); 
		print("In places visisted change assumed transition to value of true transition");
		self.beliefMapWidget = QLabel(); 

		pm = self.makeBeliefMap(); 
		self.beliefMapWidget.setPixmap(pm); 

		self.layout.addWidget(self.beliefMapWidget,0,0,15,1); 

	def makeBeliefMap(self):
		[x,y,c] = self.assumedModel.belief.plot2D(low=[0,0],high=[self.imgWidth,self.imgHeight],vis=False);
		sp = SubplotParams(left=0.,bottom=0.,right=1.,top=1.); 
		fig = Figure(subplotpars=sp); 
		canvas = FigureCanvas(fig); 
		ax = fig.add_subplot(111); 
		ax.contourf(x,y,c,cmap='inferno'); 
		ax.set_axis_off(); 
		canvas.draw(); 
		size=canvas.size(); 
		width,height = size.width(),size.height(); 
		im = QImage(canvas.buffer_rgba(),width,height,QtGui.QImage.Format_ARGB32); 
		im = im.mirrored(horizontal = True); 

		self.beliefMapWidget = QLabel(self); 
		pm = QPixmap(im); 
		pm = pm.scaled(self.imgWidth,self.imgHeight); 
		return pm; 

		


	def populateInterface(self):

		sectionHeadingFont = QFont(); 
		sectionHeadingFont.setPointSize(20); 
		sectionHeadingFont.setBold(True); 


		#Sketching Section
		#**************************************************************
		sketchLabel = QLabel("Sketching");
		sketchLabel.setFont(sectionHeadingFont); 
		self.layout.addWidget(sketchLabel,1,2); 

		self.startSketchButton = QPushButton("Start\nSketch"); 
		self.layout.addWidget(self.startSketchButton,2,2); 

		self.sketchName = QLineEdit();
		self.sketchName.setPlaceholderText("Sketch Name");  
		self.layout.addWidget(self.sketchName,2,3,1,2); 


		#Human Push Section
		#**************************************************************
		pushLabel = QLabel("Human Push"); 
		pushLabel.setFont(sectionHeadingFont);
		self.layout.addWidget(pushLabel,4,2); 

		self.relationsDrop = QComboBox();
		self.relationsDrop.addItem("North of"); 
		self.relationsDrop.addItem("South of");
		self.relationsDrop.addItem("East of");
		self.relationsDrop.addItem("West of");
		self.layout.addWidget(self.relationsDrop,5,2); 

		self.objectsDrop = QComboBox();
		self.objectsDrop.addItem("Sand"); 
		self.objectsDrop.addItem("Trees 1");
		self.objectsDrop.addItem("ROUS");
		self.objectsDrop.addItem("Trees 2");
		self.layout.addWidget(self.objectsDrop,5,3); 

		self.pushButton = QPushButton("Submit"); 
		self.pushButton.setStyleSheet("background-color: green"); 
		self.layout.addWidget(self.pushButton,5,4); 


		#Drone Launch Section
		#**************************************************************
		droneLabel = QLabel("Drone Controls"); 
		droneLabel.setFont(sectionHeadingFont);
		self.layout.addWidget(droneLabel,7,2); 

		self.updateTimerLCD = QLCDNumber(self); 
		self.updateTimerLCD.setSegmentStyle(QLCDNumber.Flat); 
		self.updateTimerLCD.setStyleSheet("background-color:rgb(255,0,0)"); 
		self.updateTimerLCD.setMaximumHeight(25);
		self.updateTimerLCD.setMinimumHeight(25);  
		self.layout.addWidget(self.updateTimerLCD,8,2); 

		self.droneButton = QPushButton("Launch\nDrone"); 
		self.layout.addWidget(self.droneButton,8,2); 


		#Robot Pull Section
		#**************************************************************
		pullLabel = QLabel("Robot Pull"); 
		pullLabel.setFont(sectionHeadingFont);
		self.layout.addWidget(pullLabel,10,2); 

		self.pullQuestion = QLineEdit("Robot Question");
		self.pullQuestion.setReadOnly(True); 
		self.pullQuestion.setAlignment(QtCore.Qt.AlignCenter); 
		self.layout.addWidget(self.pullQuestion,11,2,1,3); 

		self.yesButton = QPushButton("Yes");  
		self.yesButton.setStyleSheet("background-color: green"); 
		self.layout.addWidget(self.yesButton,12,2); 

		self.noButton = QPushButton("No");  
		self.noButton.setStyleSheet("background-color: red"); 
		self.layout.addWidget(self.noButton,12,4); 


	def connectElements(self):
		self.startSketchButton.clicked.connect(lambda:startSketch(self)); 

		self.droneButton.clicked.connect(lambda: launchDrone(self)); 

		self.yesButton.clicked.connect(lambda: getNewRobotPullQuestion(self)); 

		self.noButton.clicked.connect(lambda: getNewRobotPullQuestion(self)); 

		self.imageScene.mousePressEvent = lambda event:imageMousePress(event,self); 
		self.imageScene.mouseMoveEvent = lambda event:imageMouseMove(event,self); 
		self.imageScene.mouseReleaseEvent = lambda event:imageMouseRelease(event,self);


if __name__ == '__main__':
	app = QApplication(sys.argv); 
	ex = SimulationWindow(); 
	sys.exit(app.exec_()); 