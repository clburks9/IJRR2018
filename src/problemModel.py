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
__version__ = "0.2.0"
__maintainer__ = "Luke Burks"
__email__ = "luke.burks@colorado.edu"
__status__ = "Development"

from gaussianMixtures import Gaussian,GM; 
from softmaxModels import Softmax;

import matplotlib.pyplot as plt
import numpy as np; 

from interfaceFunctions import distance

class Model:

	def __init__(self,params,size = [437,754],trueModel = False,):

		self.truth = trueModel

		#Cop Pose
		self.copPose = params['Model']['copInitPose'];

		self.ROBOT_VIEW_RADIUS = params['Model']['robotViewRadius']; 
		self.ROBOT_SIZE_RADIUS = params['Model']['robotSizeRadius']; 
		self.ROBOT_NOMINAL_SPEED = params['Model']['robotNominalSpeed']; 
		self.TARGET_SIZE_RADIUS = params['Model']['targetSizeRadius']; 

		self.MAX_BELIEF_SIZE = params['Model']['numRandBel']; 

		self.BREADCRUMB_TRAIL_LENGTH = params['Model']['breadCrumbLength']; 

		self.history = {'beliefs':[],'positions':[],'sketches':{},'humanObs':[]}; 

		belModel = params['Model']['belNum']

		#Make Target or Belief
		if(not self.truth):
			if(belModel == 'None'):
				self.belief = GM(); 

				for i in range(0,self.MAX_BELIEF_SIZE):
					self.belief.addNewG([np.random.randint(0,437),np.random.randint(0,754)],[[2000+500*np.random.normal(),0],[0,2000+500*np.random.normal()]],np.random.random()); 
				self.belief.normalizeWeights(); 
			else:
				self.belief = np.load("../models/beliefs{}.npy".format(belModel))[0]


		self.robPose = params['Model']['targetInitPose'];
		
		self.bounds = {'low':[0,0],'high':[437,754]}
		
		self.setupTransitionLayer(); 
		self.setupCostLayer(); 

		#TODO: Spatial Relations don't always map correctly, fix it....
		#self.spatialRealtions = {'Near':0,'South of':4,'West of':1,'North of':2,'East of':3}; 
		#self.spatialRealtions = {'Near':0,'South of':1,'West of':2,'North of':3,'East of':4}; 
		self.spatialRealtions = {'near':0,'south of':4,'west of':1,'north of':2,'east of':3}; 

		self.sketches = {};

		self.prevPoses = []; 


		

		
	def setupCostLayer(self):
		self.costLayer = np.zeros(shape=(self.bounds['high'][0],self.bounds['high'][1]));

		x = self.robPose[0]
		y = self.robPose[1]; 

		for i in range(self.bounds['low'][0],self.bounds['high'][0]):
			for j in range(self.bounds['low'][1],self.bounds['high'][1]):
				if(not (i==x and y==j)):
					self.costLayer[i,j] = 1/np.sqrt((x-i)*(x-i) + (y-j)*(y-j)); 



	def setupTransitionLayer(self):
		self.transitionLayer = np.zeros(shape=(self.bounds['high'][0],self.bounds['high'][1]));

		if(self.truth):
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

	def stateObsUpdate(self,name,relation,pos="Is"):
		if(name == 'You'):
			#Take Cops Position, builid box around it
			cp=self.copPose; 
			points = [[cp[0]-5,cp[1]-5],[cp[0]+5,cp[1]-5],[cp[0]+5,cp[1]+5],[cp[0]-5,cp[1]+5]]; 
			soft = Softmax()
			soft.buildPointsModel(points,steepness=3); 
		else:
			soft = self.sketches[name]; 
		softClass = self.spatialRealtions[relation]; 

		if(pos=="Is"):
			self.belief = soft.runVBND(self.belief,softClass); 
			self.belief.normalizeWeights(); 
		else:
			tmp = GM();
			for i in range(0,5):
				if(i!=softClass):
					tmp.addGM(soft.runVBND(self.belief,i));
			tmp.normalizeWeights(); 
			self.belief=tmp; 
		if(self.belief.size > self.MAX_BELIEF_SIZE):
			self.belief.condense(self.MAX_BELIEF_SIZE); 
			self.belief.normalizeWeights()



	def stateLWISUpdate(self):

		cp=self.prevPoses[-1]; 
		prev = self.prevPoses[-2]; 
		theta = np.arctan2([cp[1]-prev[1]],[cp[0]-prev[0]]);
		#print(theta);  
		radius = self.ROBOT_VIEW_RADIUS; 
		points = [[cp[0]-radius,cp[1]-radius],[cp[0]+radius,cp[1]-radius],[cp[0]+radius,cp[1]+radius],[cp[0]-radius,cp[1]+radius]]; 
		soft = Softmax()
		soft.buildPointsModel(points,steepness=1);
		#soft.buildTriView(pose = [cp[0],cp[1],theta],length=10,steepness=5); 
		change = False; 
		post = GM(); 
		for g in self.belief:
			if(distance(cp,g.mean) > self.ROBOT_VIEW_RADIUS+5):
				post.addG(g); 
			else:
				change = True; 
				tmp = soft.lwisUpdate(g,0,20,inverse=True);
				#self.bounds = {'low':[0,0],'high':[437,754]}
				tmp.mean[0] = max(self.bounds['low'][0]+1,tmp.mean[0]); 
				tmp.mean[1] = max(self.bounds['low'][1]+1,tmp.mean[1]); 
				tmp.mean[0] = min(self.bounds['high'][0]-1,tmp.mean[0]);
				tmp.mean[1] = min(self.bounds['high'][1]-1,tmp.mean[1]);  


				post.addG(tmp);
		self.belief = post; 
		self.belief.normalizeWeights(); 

		return change; 







