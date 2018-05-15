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
0.1.2: added automatic robot movement

***********************************************************
"""

__author__ = "Luke Burks"
__copyright__ = "Copyright 2018"
__credits__ = ["Luke Burks"]
__license__ = "GPL"
__version__ = "0.1.2"
__maintainer__ = "Luke Burks"
__email__ = "luke.burks@colorado.edu"
__status__ = "Development"


from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *; 
from PyQt5.QtGui import *;
from PyQt5.QtCore import *;
import sys

import numpy as np
import time

from matplotlib.backends.backend_qt4agg import FigureCanvas
from matplotlib.figure import Figure, SubplotParams
import matplotlib.pyplot as plt

from interfaceFunctions import *; 
from planeFunctions import *;
from problemModel import Model
from robotControllers import Controller; 

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


		#Make Models and Controller
		self.trueModel = Model(trueModel=True);
		self.assumedModel = Model(trueModel=False); 
		self.control = Controller(self.assumedModel); 
		self.makeBreadCrumbColors(); 

		#Sketching Params
		self.sketchListen=False; 
		self.sketchingInProgress = False; 
		self.allSketches = {}; 
		self.allSketchNames = []; 
		self.allSketchPaths = []; 
		self.allSketchPlanes = {}; 
		self.sketchLabels = {}; 
		self.sketchDensity = 5; 
		self.NUM_SKETCH_POINTS = 4; 

		#Drone Params
		self.droneClickListen = False; 
		self.DRONE_WAIT_TIME = 5; 
		self.timeLeft = self.DRONE_WAIT_TIME; 
		self.DRONE_VIEW_RADIUS = 75; 

		#Controller Paramas
		self.humanControl = False; 
		self.CONTROL_FREQUENCY = 10; #Hz


		self.makeMapGraphics();

		self.makeTabbedGraphics(); 

		self.populateInterface(); 
		self.connectElements(); 

		self.makeRobot();
		self.makeTarget();



		loadQuestions(self); 

		droneTimerStart(self); 

		if(not self.humanControl):
			controlTimerStart(self); 

		self.show()


	def makeBreadCrumbColors(self):
		self.breadColors = []; 
		num_crumbs = self.trueModel.BREADCRUMB_TRAIL_LENGTH; 

		for i in range(0,num_crumbs):
			alpha = 255*(i)/num_crumbs; 
			self.breadColors.append(QColor(150,0,0,alpha))


	def keyReleaseEvent(self,event):
		arrowEvents = [QtCore.Qt.Key_Up,QtCore.Qt.Key_Down,QtCore.Qt.Key_Left,QtCore.Qt.Key_Right]; 
		if(self.humanControl):
			if(event.key() in arrowEvents):
				moveRobot(self,event.key()); 
			if(event.key() == QtCore.Qt.Key_Space):
				moveRobot(self,arrowEvents[self.control.getActionKey_Greedy()]);


	def makeRobot(self):
		moveRobot(self,None); 
		 

	def makeTarget(self):
		points = []; 
		rad = self.trueModel.TARGET_SIZE_RADIUS; 
		for i in range(-int(rad/2)+self.trueModel.robPose[0],int(rad/2)+self.trueModel.robPose[0]):
			for j in range(-int(rad/2) + self.trueModel.robPose[1],int(rad/2)+self.trueModel.robPose[1]):
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
		self.sketchPlane = self.imageScene.addPixmap(makeTransparentPlane(self));


		#make robotPose plane
		self.robotPlane = self.imageScene.addPixmap(makeTransparentPlane(self));

		#make targetPose plane
		self.targetPlane = self.imageScene.addPixmap(makeTransparentPlane(self));

		#make click layer
		self.clickPlane = self.imageScene.addPixmap(makeTransparentPlane(self));

		#make comet trail layer
		self.trailLayer = self.imageScene.addPixmap(makeTransparentPlane(self)); 

		#Make goal layer
		self.goalLayer = self.imageScene.addPixmap(makeTransparentPlane(self)); 


		self.imageView.setScene(self.imageScene); 
		self.layout.addWidget(self.imageView,0,1,15,1); 





	def makeTabbedGraphics(self):
		
		self.tabs = QTabWidget(self); 

		#Belief Map
		#************************************************************
		self.beliefMapWidget = QLabel(self); 
		pm = makeBeliefMap(self); 
		self.beliefMapWidget.setPixmap(pm); 
		self.tabs.addTab(self.beliefMapWidget,'Belief'); 

		#Transitions Map
		#************************************************************
		# self.assumedModel.transitionLayer = convertPixmapToGrayArray(self.fogPlane.pixmap()); 
		# self.assumedModel.transitionLayer /= 255.0;
		# self.assumedModel.transitionLayer = np.amax(self.assumedModel.transitionLayer)  - self.assumedModel.transitionLayer; 
		# self.assumedModel.transitionLayer *= 15.0;
		# self.assumedModel.transitionLayer -= 10.0; 

		# self.trueModel.transitionLayer = convertPixmapToGrayArray(self.truePlane.pixmap());
		# self.trueModel.transitionLayer /= 255.0;
		# self.trueModel.transitionLayer = np.amax(self.trueModel.transitionLayer) - self.trueModel.transitionLayer; 
		# self.trueModel.transitionLayer *= 15.0;
		# self.trueModel.transitionLayer -= 10.0; 

		self.transMapWidget_true = QLabel(); 
		tm = makeModelMap(self,self.trueModel.transitionLayer); 
		self.transMapWidget_true.setPixmap(tm); 
		self.tabs.addTab(self.transMapWidget_true,'True Transitions'); 

		#self.tabs.setTabEnabled(1,False); 

		self.transMapWidget_assumed = QLabel(); 
		tm = makeModelMap(self,self.assumedModel.transitionLayer); 
		self.transMapWidget_assumed.setPixmap(tm); 
		self.tabs.addTab(self.transMapWidget_assumed,'Assumed Transitions'); 
		

	
		#Cost Map
		#************************************************************
		self.costMapWidget = QLabel(); 
		cm = makeModelMap(self,self.assumedModel.costLayer); 
		self.costMapWidget.setPixmap(cm); 
		self.tabs.addTab(self.costMapWidget,'Costs'); 



		self.layout.addWidget(self.tabs,0,0,15,1); 


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

		# self.sketchObs = QRadioButton("Observable",self); 
		# self.sketchObs.setChecked(True); 
		# self.sketchObs.setDisabled(True); 

		# self.layout.addWidget(self.sketchObs,3,2); 

		#A Label at 3,2
		#Two button groups
		#A group at 3,3 with Safe (Pre) and Dangerous
		#A group at 3,4 with Fast, nominal (Pre), and slow

		sketchButtonLabel = QLabel("Sketch Parameters"); 
		self.layout.addWidget(sketchButtonLabel,3,2); 

		self.costRadioGroup = QButtonGroup(self); 
		self.targetRadio = QRadioButton("Target"); 
		self.costRadioGroup.addButton(self.targetRadio,id=1); 
		self.safeRadio = QRadioButton("Nominal"); 
		self.safeRadio.setChecked(True); 
		self.costRadioGroup.addButton(self.safeRadio,id=0); 
		self.dangerRadio = QRadioButton("Dangerous"); 
		self.costRadioGroup.addButton(self.dangerRadio,id=-1); 
		self.layout.addWidget(self.targetRadio,3,3); 
		self.layout.addWidget(self.safeRadio,4,3);
		self.layout.addWidget(self.dangerRadio,5,3);  

		self.speedRadioGroup = QButtonGroup(self); 
		self.fastRadio = QRadioButton("Fast"); 
		self.speedRadioGroup.addButton(self.fastRadio,id=1); 
		self.nomRadio = QRadioButton("Nominal"); 
		self.nomRadio.setChecked(True); 
		self.speedRadioGroup.addButton(self.nomRadio,id=0); 
		self.slowRadio = QRadioButton("Slow"); 
		self.speedRadioGroup.addButton(self.slowRadio,id=-1); 
		self.layout.addWidget(self.fastRadio,3,4);
		self.layout.addWidget(self.nomRadio,4,4); 
		self.layout.addWidget(self.slowRadio,5,4);  




		#Human Push Section
		#**************************************************************
		pushLabel = QLabel("Human Push"); 
		pushLabel.setFont(sectionHeadingFont);
		self.layout.addWidget(pushLabel,6,2); 

		self.relationsDrop = QComboBox();
		self.relationsDrop.addItem("Near"); 
		self.relationsDrop.addItem("North of"); 
		self.relationsDrop.addItem("South of");
		self.relationsDrop.addItem("East of");
		self.relationsDrop.addItem("West of");
		self.layout.addWidget(self.relationsDrop,7,2); 

		self.objectsDrop = QComboBox();
		# self.objectsDrop.addItem("Sand"); 
		# self.objectsDrop.addItem("Trees 1");
		# self.objectsDrop.addItem("ROUS");
		# self.objectsDrop.addItem("Trees 2");
		self.objectsDrop.addItem("You"); 
		self.layout.addWidget(self.objectsDrop,7,3); 

		self.pushButton = QPushButton("Submit"); 
		self.pushButton.setStyleSheet("background-color: green"); 
		self.layout.addWidget(self.pushButton,7,4); 


		#Drone Launch Section
		#**************************************************************
		droneLabel = QLabel("Drone Controls"); 
		droneLabel.setFont(sectionHeadingFont);
		self.layout.addWidget(droneLabel,9,2); 

		self.updateTimerLCD = QLCDNumber(self); 
		self.updateTimerLCD.setSegmentStyle(QLCDNumber.Flat); 
		self.updateTimerLCD.setStyleSheet("background-color:rgb(255,0,0)"); 
		self.updateTimerLCD.setMaximumHeight(25);
		self.updateTimerLCD.setMinimumHeight(25);  
		self.layout.addWidget(self.updateTimerLCD,10,2); 

		self.droneButton = QPushButton("Launch\nDrone"); 
		self.layout.addWidget(self.droneButton,10,2); 


		#Robot Pull Section
		#**************************************************************
		pullLabel = QLabel("Robot Pull"); 
		pullLabel.setFont(sectionHeadingFont);
		self.layout.addWidget(pullLabel,12,2); 

		self.pullQuestion = QLineEdit("Robot Question");
		self.pullQuestion.setReadOnly(True); 
		self.pullQuestion.setAlignment(QtCore.Qt.AlignCenter); 
		self.layout.addWidget(self.pullQuestion,13,2,1,3); 

		self.yesButton = QPushButton("Yes");  
		self.yesButton.setStyleSheet("background-color: green"); 
		self.layout.addWidget(self.yesButton,14,2); 

		self.noButton = QPushButton("No");  
		self.noButton.setStyleSheet("background-color: red"); 
		self.layout.addWidget(self.noButton,14,4); 


	def connectElements(self):
		self.startSketchButton.clicked.connect(lambda:startSketch(self)); 

		self.droneButton.clicked.connect(lambda: launchDrone(self)); 

		self.yesButton.clicked.connect(lambda: getNewRobotPullQuestion(self)); 

		self.noButton.clicked.connect(lambda: getNewRobotPullQuestion(self)); 

		self.pushButton.clicked.connect(lambda: pushButtonPressed(self)); 

		self.imageScene.mousePressEvent = lambda event:imageMousePress(event,self); 
		self.imageScene.mouseMoveEvent = lambda event:imageMouseMove(event,self); 
		self.imageScene.mouseReleaseEvent = lambda event:imageMouseRelease(event,self);


		self.saveShortcut = QShortcut(QKeySequence("Ctrl+S"),self); 
		self.saveShortcut.activated.connect(self.saveTransitions); 


	def saveTransitions(self):
		np.save('../models/trueTransitions.npy',self.assumedModel.transitionLayer); 
		print("Saved Transition Model");

if __name__ == '__main__':
	app = QApplication(sys.argv); 
	ex = SimulationWindow(); 
	sys.exit(app.exec_()); 