"""
***********************************************************
File: testArena.py
Author: Luke Burks
Date: March 2018

Making figures and testing ideas for ICRA 2017 Workshop

Citations:
For drawing
https://stackoverflow.com/questions/36381684/how-to-make-a-free-hand-shaperandom-on-an-image-in-python-using-opencv

Grabbing Polygons
https://stackoverflow.com/questions/7198144/how-to-draw-a-n-sided-regular-polygon-in-cartesian-coordinates

***********************************************************
"""



from __future__ import division
import numpy as np;
import matplotlib.pyplot as plt; 
from gaussianMixtures import GM,Gaussian; 
from softmaxModels import Softmax; 
from drawing import shapeRequest
from scipy.spatial import ConvexHull



def makeInitialBelief():
	bel = GM(); 
	numMix = 100; 
	for i in range(0,numMix):
		w = np.random.random(); 
		mean = [np.random.random()*8+2,np.random.random()*8+2];
		tmp = np.random.random()*1; 
		var = [[np.random.random()*1+1,0],[0,np.random.random()*1+1]]; 
		bel.addG(Gaussian(mean,var,w)); 
	bel.normalizeWeights(); 
	[x,y,belView] = bel.plot2D(low=[0,0],high=[10,10],vis=False); 
	plt.contourf(x,y,belView); 
	plt.savefig('../img/testBel.png'); 
	plt.cla(); 
	plt.clf(); 
	plt.close(); 
	return bel; 


def drawShape(sketch):
	allPoints = shapeRequest(sketch);
	for i in range(0,len(allPoints[0])):
		allPoints[0][i] = (allPoints[0][i])*10/640; 
	for i in range(0,len(allPoints[1])):
		allPoints[1][i] = 10 - (allPoints[1][i])*10/480; 


	pairedPoints = np.zeros(shape=(len(allPoints[0]),2)); 
	for i in range(0,len(pairedPoints)): 
		pairedPoints[i][0] = allPoints[0][i]; 
		pairedPoints[i][1] = allPoints[1][i]; 

	return pairedPoints; 


def subsampleHull(cHull,pairedPoints,N = 3):
	vertices = [];  

	for i in range(0,N):
		ind = int(i*len(cHull.vertices)/N)
		vertices.append([pairedPoints[cHull.vertices[ind],0],pairedPoints[cHull.vertices[ind],1]])
	return vertices

if __name__ == '__main__':

	#Turn off to select points manually
	sketch = True; 

	#Make initial belief
	prior = makeInitialBelief();

	#Draw a shape
	pairedPoints = drawShape(sketch); 

	#Get points
	if(sketch):
		#Get convex hull
		cHull = ConvexHull(pairedPoints);
		#Get N separated points
		vertices = subsampleHull(cHull,pairedPoints,4); 
	else:
		vertices = pairedPoints;


	#Make softmax model
	pz = Softmax(); 
	pz.buildPointsModel(vertices,steepness=2); 


	#Update belief
	post = pz.runVBND(prior,1); 


	#display
	fig,axarr = plt.subplots(3); 
	[xprior,yprior,cprior] = prior.plot2D(low=[0,0],high=[10,10],vis=False);
	[xobs,yobs,cobs] = pz.plot2D(low=[0,0],high=[10,10],delta=0.1,vis=False);
	[xpost,ypost,cpost] = post.plot2D(low=[0,0],high=[10,10],vis=False);  
	axarr[0].contourf(xprior,yprior,cprior,cmap='viridis'); 
	axarr[1].contourf(xobs,yobs,cobs,cmap='inferno'); 
	axarr[2].contourf(xpost,ypost,cpost,cmap='viridis'); 
	plt.show(); 

