
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *; 
from PyQt5.QtGui import QIcon, QPixmap, QBitmap, QPainter, QFont
from PyQt5.QtCore import QRect,QPoint; 
import sys

from interfaceFunctions import *; 
import numpy as np


class SimulationWindow(QWidget):
	def __init__(self):
		super(SimulationWindow,self).__init__()
		self.setGeometry(1,1,1000,700)
		self.layout = QGridLayout(); 
		self.layout.setColumnStretch(2,1); 
		self.layout.setColumnStretch(1,1);
		self.layout.setColumnStretch(3,1);
		self.setLayout(self.layout); 

		self.DRONE_WAIT_TIME = 5; 
		self.droneClickListen = False; 
		self.sketchListen=False; 
		self.sketchingInProgress = False; 
		self.allSketches = {}; 
		self.allSketchNames = []; 
		self.allSketchPaths = []; 
		self.sketchLabels = {}; 

		self.timeLeft = self.DRONE_WAIT_TIME; 

		self.populateInterface(); 

		self.loadQuestions(); 

		self.makeRobot();

		self.show()

	def makeRobot(self):
		self.robPose = [200,500,0]; 


	def loadQuestions(self):
		f = open('../data/Questions.txt','r'); 
		lines = f.read().split("\n"); 
		self.questions = lines; 

	def populateInterface(self):

		sectionHeadingFont = QFont(); 
		sectionHeadingFont.setPointSize(20); 
		sectionHeadingFont.setBold(True); 

		self.trueImage = QPixmap('../img/eastCampus_2017_2.jpg'); 
		# self.trueMapWidget = QLabel(self); 
		# self.trueMapWidget.setPixmap(self.trueImage); 
		# self.layout.addWidget(self.trueMapWidget,0,0,15,1); 

		self.imgWidth = self.trueImage.size().width(); 
		self.imgHeight = self.trueImage.size().height(); 
		self.boolmask = np.ones((self.trueImage.size().width(),self.trueImage.size().height()),dtype=bool); 
		self.sketchMask = np.zeros((self.trueImage.size().width(),self.trueImage.size().height())); 
		#print(self.bitmask); 
		#self.bitmask.clear();

		self.fogMapWidget = QLabel(self); 
		self.fogImage = QPixmap('../img/eastCampus_1999_2.jpg'); 
		self.fogMapWidget.setPixmap(self.fogImage); 
		self.fogMapWidget.setMouseTracking(True); 
		self.fogMapWidget.mousePressEvent = lambda event:imageMousePress(event,self); 
		self.fogMapWidget.mouseMoveEvent = lambda event:imageMouseMove(event,self); 
		self.fogMapWidget.mouseReleaseEvent = lambda event:imageMouseRelease(event,self); 
		#self.fogMapWidget.keyPressEvent = lambda event:imageKeyPress(event,self); 
		self.fogMapWidget.keyReleaseEvent = lambda event:imageKeyRelease(event,self); 
		self.layout.addWidget(self.fogMapWidget,0,0,15,1); 

		# self.fogImage.setMask(self.bitmask); 
		# self.fogMapWidget.setPixmap(self.fogImage); 


		sketchLabel = QLabel("Sketching");
		sketchLabel.setFont(sectionHeadingFont); 
		self.layout.addWidget(sketchLabel,1,1); 

		self.startSketchButton = QPushButton("Start\nSketch"); 
		self.startSketchButton.clicked.connect(lambda:startSketch(self)); 
		self.layout.addWidget(self.startSketchButton,2,1); 

		# self.stopSketchButton = QPushButton("Submit\nSketch"); 
		# self.layout.addWidget(self.stopSketchButton,3,1); 
		
		self.sketchName = QLineEdit();
		self.sketchName.setPlaceholderText("Sketch Name");  
		self.layout.addWidget(self.sketchName,2,2,1,2); 




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


		droneLabel = QLabel("Drone Controls"); 
		droneLabel.setFont(sectionHeadingFont);
		self.layout.addWidget(droneLabel,7,1); 




		self.updateTimerLCD = QLCDNumber(self); 
		self.updateTimerLCD.setSegmentStyle(QLCDNumber.Flat); 
		self.updateTimerLCD.setStyleSheet("background-color:rgb(255,0,0)"); 
		self.layout.addWidget(self.updateTimerLCD,8,1); 

		# self.progressBar = QProgressBar(self); 
		# self.progressBar.setValue(0); 
		# self.progressBar.setStyleSheet("background-color: red");
		# self.layout.addWidget(self.progressBar,9,1,1,3); 


		self.droneButton = QPushButton("Launch\nDrone"); 
		self.droneButton.clicked.connect(lambda: launchDrone(self)); 
		self.layout.addWidget(self.droneButton,8,1); 


		pullLabel = QLabel("Robot Pull"); 
		pullLabel.setFont(sectionHeadingFont);
		self.layout.addWidget(pullLabel,10,1); 

		self.pullQuestion = QLineEdit("Robot Question");
		self.pullQuestion.setReadOnly(True); 
		self.pullQuestion.setAlignment(QtCore.Qt.AlignCenter); 
		self.layout.addWidget(self.pullQuestion,11,1,1,3); 

		self.yesButton = QPushButton("Yes");  
		self.yesButton.setStyleSheet("background-color: green"); 
		self.yesButton.clicked.connect(lambda: getNewRobotPullQuestion(self)); 

		self.noButton = QPushButton("No");  
		self.noButton.setStyleSheet("background-color: red"); 
		self.noButton.clicked.connect(lambda: getNewRobotPullQuestion(self)); 


		self.layout.addWidget(self.yesButton,12,1); 
		self.layout.addWidget(self.noButton,12,3); 



		timerStart(self);  




if __name__ == '__main__':
	app = QApplication(sys.argv); 
	ex = SimulationWindow(); 
	sys.exit(app.exec_()); 