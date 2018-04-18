from PyQt5 import QtGui, QtCore
#from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QPushButton
from PyQt5.QtWidgets import *; 
from PyQt5.QtGui import QIcon, QPixmap
import sys




class Window(QWidget):
	def __init__(self):
		super(Window,self).__init__()
		self.setGeometry(1,1,1000,700)
		self.layout = QGridLayout(); 
		self.layout.setColumnStretch(2,1); 
		self.layout.setColumnStretch(1,1);
		#self.layout.setRowStretch(3,2); 
		self.setLayout(self.layout); 

		self.populateInterface(); 

		self.show()

	def populateInterface(self):

		self.mapWidget = QLabel(self); 
		image = QPixmap('../img/BlankMap.png'); 
		self.mapWidget.setPixmap(image); 
		self.layout.addWidget(self.mapWidget); 


		sketchLabel = QLabel("Sketching");
		self.layout.addWidget(sketchLabel,1,1); 

		self.startSketchButton = QPushButton("Start\nSketch"); 
		self.layout.addWidget(self.startSketchButton,2,1); 

		self.stopSketchButton = QPushButton("Submit\nSketch"); 
		self.layout.addWidget(self.stopSketchButton,3,2); 
		
		self.sketchName = QLineEdit("Sketch Name"); 
		self.layout.addWidget(self.sketchName,2,2); 




		pushLabel = QLabel("Human Push"); 
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
		self.layout.addWidget(self.pushButton,6,1); 

		droneLabel = QLabel("Drone Controls"); 
		self.layout.addWidget(droneLabel,7,1); 


		self.droneButton = QPushButton("Launch\nDrone"); 
		self.layout.addWidget(self.droneButton,8,1); 

		self.updateTimerLabel = QLabel(); 
		self.layout.addWidget(self.updateTimerLabel,8,2); 

		self.timerStart(); 
		self.updateGui(); 


	def timerStart(self):
		self.myTimer = QtCore.QTimer(self); 
		self.timeLeft = 5; 

		self.myTimer.timeout.connect(self.timerTimeout); 
		self.myTimer.start(1000); 

		self.updateGui(); 

	def timerTimeout(self):
		self.timeLeft -= 1; 

		if(self.timeLeft == 0):
			self.timeLeft = 5; 

		self.updateGui(); 

	def updateGui(self):
		self.updateTimerLabel.setText(str(self.timeLeft)); 



if __name__ == '__main__':
	app = QApplication(sys.argv); 
	ex = Window(); 
	sys.exit(app.exec_()); 