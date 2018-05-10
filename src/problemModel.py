"""
***********************************************************
File: problemModel.py
Author: Luke Burks
Date: April 2018

Implements a Model class which contains information about 
rewards, transitions, and observations

Models may be either held or true

#Transition Layer defines the difference from nominal speed

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

from gaussianMixtures import Gaussian,GM; 
from softmaxModels import Softmax;

import matplotlib.pyplot as plt
import numpy as np; 

from interfaceFunctions import distance

class Model:

	def __init__(self,size = [437,754],trueModel = False):

		self.truth = trueModel

		#Cop Pose
		self.copPose = [200,500];

		self.ROBOT_VIEW_RADIUS = 25; 
		self.ROBOT_SIZE_RADIUS = 10; 
		self.ROBOT_NOMINAL_SPEED = 2; 
		self.TARGET_SIZE_RADIUS = 10; 

		self.BREADCRUMB_TRAIL_LENGTH = 100; 


		#Make Target or Belief
		if(not self.truth):
			self.belief = GM(); 
			# self.belief.addNewG([100,100],[[1000,0],[0,1000]],1); 
			# self.belief.addNewG([400,400],[[1000,0],[0,1000]],1); 
			# self.belief.addNewG([400,100],[[1000,0],[0,1000]],1); 
			# self.belief.addNewG([100,400],[[1000,0],[0,1000]],1); 
			# self.belief.addNewG([400,200],[[1000,0],[0,1000]],1); 
			#self.belief.addNewG([np.random.randint(0,437),np.random.randint(0,754)],[[1000,0],[0,1000]],1); 

			for i in range(0,15):
				self.belief.addNewG([np.random.randint(0,437),np.random.randint(0,754)],[[1000,0],[0,1000]],np.random.random()); 
			self.belief.normalizeWeights(); 
		else:
			self.robPose = [400,200];
		
		self.bounds = {'low':[0,0],'high':[437,754]}
		
		self.setupTransitionLayer(); 
		self.setupCostLayer(); 

		self.spatialRealtions = {'Inside':0,'South of':4,'West of':1,'North of':2,'East of':3}; 

		self.sketches = {};

		self.prevPoses = []; 


		

		
	def setupCostLayer(self):
		self.costLayer = np.zeros(shape=(self.bounds['high'][0],self.bounds['high'][1]));

		num_mines = 100; 

		#set some random mines:
		for i in range(0,num_mines):
			x = np.random.randint(self.bounds['low'][0],self.bounds['high'][0]-10)
			y = np.random.randint(self.bounds['low'][1],self.bounds['high'][1]-10)
			for j in range(0,10):
				for k in range(0,10):
					self.costLayer[x+j,y+k] = -10; 

		#set up a reward
		#x = np.random.randint(self.bounds['low'][0],self.bounds['high'][0]-10)
		#y = np.random.randint(self.bounds['low'][1],self.bounds['high'][1]-10)
		x,y = 400,200
		for j in range(0,10):
			for k in range(0,10):
				self.costLayer[x+j,y+k] = 10;


	def setupTransitionLayer(self):
		self.transitionLayer = np.zeros(shape=(self.bounds['high'][0],self.bounds['high'][1]));

		if(self.truth):
			# for i in range(200,400):
			# 	for j in range(200,400):
			# 		self.transitionLayer[i,j] = -8; 

			# for i in range(100,250):
			# 	for j in range(100,250):
			# 		self.transitionLayer[i,j] = 5; 
			self.transitionLayer = np.load('../models/trueTransitions.npy'); 



	def transitionEval(self,x):
		if(x[0] > self.bounds['low'][0] and x[1] > self.bounds['low'][1] and x[0] < self.bounds['high'][0] and x[1] < self.bounds['high'][1]):
			return self.transitionLayer[x[0],x[1]]; 
		else:
			return -1e10;  

	def costEval(self,x):
		if(x[0] > self.bounds['low'][0] and x[1] > self.bounds['low'][1] and x[0] < self.bounds['high'][0] and x[1] < self.bounds['high'][1]):
			return self.rewardLayer[x[0],x[1]]; 
		else:
			return 0;  




	def distance(self,x,y):
		return np.sqrt((x[0]-y[0])**2 + (x[1]-y[1])**2); 



	def makeSketch(self,vertices,name):
		pz = Softmax(); 
		vertices.sort(key=lambda x: x[1])

		pz.buildPointsModel(vertices,steepness=2); 
		self.sketches[name] = pz; 

	def stateObsUpdate(self,name,relation):
		if(name == 'You'):
			#Take Cops Position, builid box around it
			cp=self.copPose; 
			points = [[cp[0]-5,cp[1]-5],[cp[0]+5,cp[1]-5],[cp[0]+5,cp[1]+5],[cp[0]-5,cp[1]+5]]; 
			soft = Softmax()
			soft.buildPointsModel(points,steepness=3); 
		else:
			soft = self.sketches[name]; 
		softClass = self.spatialRealtions[relation]; 

		self.belief = soft.runVBND(self.belief,softClass); 
		self.belief.normalizeWeights(); 


	def stateLWISUpdate(self):

		cp=self.prevPoses[-1]; 
		prev = self.prevPoses[-2]; 
		theta = np.arctan2([cp[1]-prev[1]],[cp[0]-prev[0]]);
		#print(theta);  
		radius = 10; 
		points = [[cp[0]-radius,cp[1]-radius],[cp[0]+radius,cp[1]-radius],[cp[0]+radius,cp[1]+radius],[cp[0]-radius,cp[1]+radius]]; 
		soft = Softmax()
		soft.buildPointsModel(points,steepness=1);
		#soft.buildTriView(pose = [cp[0],cp[1],theta],length=10,steepness=5); 
		change = False; 
		post = GM(); 
		for g in self.belief:
			if(distance(cp,g.mean) > 20):
				post.addG(g); 
			else:
				change = True; 
				post.addG(soft.lwisUpdate(g,0,20,inverse=True));
		self.belief = post; 
		self.belief.normalizeWeights(); 

		return change; 







