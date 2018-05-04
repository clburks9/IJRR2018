"""
***********************************************************
File: interface.py
Author: Luke Burks
Date: April 2018

Implements a PYQT5 interface that allows human aided 
target tracking through sketches, drone launches, 
and human push/robot pull semantic information

***********************************************************
"""

__author__ = "Luke Burks"
__copyright__ = "Copyright 2018"
__credits__ = ["Luke Burks"]
__license__ = "GPL"
__version__ = "0.1"
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


class SimulationWindow(QWidget):
	def __init__(self):
		super(SimulationWindow,self).__init__()
		self.setGeometry(1,1,900,800)
		self.layout = QGridLayout(); 
		self.layout.setColumnStretch(2,1); 
		self.layout.setColumnStretch(1,1);
		self.layout.setColumnStretch(3,1);
		self.setLayout(self.layout); 



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

		self.makeMapGraphics();
		self.populateInterface(); 
		self.connectElements(); 

		self.makeRobot();

		loadQuestions(self); 

		timerStart(self); 

		self.show()

	def makeRobot(self):
		self.robPose = [200,500,0]; 


	def makeMapGraphics(self):
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
		self.layout.addWidget(self.imageView,0,0,15,1); 




	def populateInterface(self):

		sectionHeadingFont = QFont(); 
		sectionHeadingFont.setPointSize(20); 
		sectionHeadingFont.setBold(True); 


		#Sketching Section
		#**************************************************************
		sketchLabel = QLabel("Sketching");
		sketchLabel.setFont(sectionHeadingFont); 
		self.layout.addWidget(sketchLabel,1,1); 

		self.startSketchButton = QPushButton("Start\nSketch"); 
		self.layout.addWidget(self.startSketchButton,2,1); 

		self.sketchName = QLineEdit();
		self.sketchName.setPlaceholderText("Sketch Name");  
		self.layout.addWidget(self.sketchName,2,2,1,2); 


		#Human Push Section
		#**************************************************************
		pushLabel = QLabel("Human Push"); 
		pushLabel.setFont(sectionHeadingFont);
		self.layout.addWidget(pushLabel,4,1); 

		self.relationsDrop = QComboBox();
		self.relationsDrop.addItem("North of"); 
		self.relationsDrop.addItem("South of");
		self.relationsDrop.addItem("East of");
		self.relationsDrop.addItem("West of");
		self.layout.addWidget(self.relationsDrop,5,1); 

		self.objectsDrop = QComboBox();
		self.objectsDrop.addItem("Sand"); 
		self.objectsDrop.addItem("Trees 1");
		self.objectsDrop.addItem("ROUS");
		self.objectsDrop.addItem("Trees 2");
		self.layout.addWidget(self.objectsDrop,5,2); 

		self.pushButton = QPushButton("Submit"); 
		self.pushButton.setStyleSheet("background-color: green"); 
		self.layout.addWidget(self.pushButton,5,3); 


		#Drone Launch Section
		#**************************************************************
		droneLabel = QLabel("Drone Controls"); 
		droneLabel.setFont(sectionHeadingFont);
		self.layout.addWidget(droneLabel,7,1); 

		self.updateTimerLCD = QLCDNumber(self); 
		self.updateTimerLCD.setSegmentStyle(QLCDNumber.Flat); 
		self.updateTimerLCD.setStyleSheet("background-color:rgb(255,0,0)"); 
		self.updateTimerLCD.setMaximumHeight(25);
		self.updateTimerLCD.setMinimumHeight(25);  
		self.layout.addWidget(self.updateTimerLCD,8,1); 

		self.droneButton = QPushButton("Launch\nDrone"); 
		self.layout.addWidget(self.droneButton,8,1); 


		#Robot Pull Section
		#**************************************************************
		pullLabel = QLabel("Robot Pull"); 
		pullLabel.setFont(sectionHeadingFont);
		self.layout.addWidget(pullLabel,10,1); 

		self.pullQuestion = QLineEdit("Robot Question");
		self.pullQuestion.setReadOnly(True); 
		self.pullQuestion.setAlignment(QtCore.Qt.AlignCenter); 
		self.layout.addWidget(self.pullQuestion,11,1,1,3); 

		self.yesButton = QPushButton("Yes");  
		self.yesButton.setStyleSheet("background-color: green"); 
		self.layout.addWidget(self.yesButton,12,1); 

		self.noButton = QPushButton("No");  
		self.noButton.setStyleSheet("background-color: red"); 
		self.layout.addWidget(self.noButton,12,3); 


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