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
from scipy.stats import linregress
from copy import deepcopy

def makeInitialBelief():
	bel = GM(); 
	numMix = 100; 
	varscale = .2; 
	for i in range(0,numMix):
		w = np.random.random(); 
		mean = [np.random.random()*8,np.random.random()*8];
		tmp = np.random.random()*varscale; 
		var = [[np.random.random()*1+varscale,0],[0,np.random.random()*1+varscale]]; 
		bel.addG(Gaussian(mean,var,w)); 

	bel.addG(Gaussian([4,7],[[1,0],[0,1]],4)); 

	bel.normalizeWeights(); 
	[x,y,belView] = bel.plot2D(low=[0,0],high=[10,10],vis=False); 
	plt.contourf(x,y,belView); 
	plt.savefig('../img/testBel.png'); 
	plt.cla(); 
	plt.clf(); 
	plt.close(); 
	return bel; 


def drawShape(sketch):
	[allPoints,l,w] = shapeRequest(sketch);
	for i in range(0,len(allPoints[0])):
		allPoints[0][i] = (allPoints[0][i])*10/w; 
	for i in range(0,len(allPoints[1])):
		allPoints[1][i] = 10-(allPoints[1][i])*10/l; 


	pairedPoints = np.zeros(shape=(len(allPoints[0]),2)); 
	for i in range(0,len(pairedPoints)): 
		pairedPoints[i][0] = allPoints[0][i]; 
		pairedPoints[i][1] = allPoints[1][i]; 

	return pairedPoints; 


def distance(p1,p2):
	return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2);

def angleOfThreePoints(a,b,c):
	ab = [b[0]-a[0],b[1]-a[1]]; 
	bc = [c[0]-b[0],c[1]-b[1]]; 
	num = ab[0]*bc[0] + ab[1]*bc[1]; 
	dem = distance([0,0],ab)*distance([0,0],bc); 
	theta = np.arccos(num/dem); 
	return theta; 

def polyArea(points):
	area = 0; 
	q = points[-1]; 
	for p in points:
		area += p[0]*q[1]-p[1]*q[0]; 
		q=p; 
	return area/2; 

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


def distanceAlongPoints(verts,i,j):

	dist = 0; 
	for k in range(i,j):
		dist += distance(verts[k],[k+1]); 
	return dist; 

def smoothAngles(verts,angs,normPer):
	newAngs = []; 

	#area = polyArea(verts); 

	G = Gaussian(0,.5*normPer,1); 

	for i in range(0,len(angs)):
		tmp=0; 
		for j in range(0,len(angs)):
			#tmp+= G.pointEval(distance(verts[i],verts[j]))*angs[j];
			tmp+= G.pointEval(distanceAlongPoints(verts,i,j))*angs[j];  
		newAngs.append(tmp); 
	return newAngs; 





def fitBestPolyToHull(cHull,pairedPoints):
	vertices = [];  

	for i in range(0,len(cHull.vertices)):
		vertices.append([pairedPoints[cHull.vertices[i],0],pairedPoints[cHull.vertices[i],1]]);

	initialArea = polyArea(vertices); 
	initialLen = len(vertices); 

	allPointSets = []; 
	allScores = []; 

	while(len(vertices) > 3):
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




		#remove the point with the smallest angle change
		smallest = min(allAngles); 
		vertices.remove(vertices[allAngles.index(smallest)]); 

		#score
		allPointSets.append(deepcopy(vertices)); 
		alpha = .5; 
		beta = 3; 

		score = alpha*(initialArea/polyArea(vertices))**2 + beta*(initialLen/len(vertices))**2;

		allScores.append(score); 

	print(allScores); 
	x = range(3,initialLen); 
	x = x[::-1]; 
	plt.plot(x,allScores); 
	plt.show(); 
	vertices = allPointSets[allScores.index(min(allScores))]; 

	return vertices;


if __name__ == '__main__':

	#How many points in the polygon

	#Turn off to select points manually
	sketch = True; 

	#Make initial belief
	prior = makeInitialBelief();

	#Draw a shape
	pairedPoints = drawShape(sketch); 



	#Get N Vertices of the shape
	cHull = ConvexHull(pairedPoints);
	vertices = fitSimplePolyToHull(cHull,pairedPoints,N=5); 
	#vertices = fitBestPolyToHull(cHull,pairedPoints); 

	#Show Vertices
	plt.scatter([vertices[i][0] for i in range(0,len(vertices))],[vertices[i][1] for i in range(0,len(vertices))])
	plt.show();
	


	#Make softmax model
	pz = Softmax(); 
	pz.buildPointsModel(vertices,steepness=5); 


	#Update belief
	post = pz.runVBND(prior,4); 


	#display
	fig,axarr = plt.subplots(3); 
	[xprior,yprior,cprior] = prior.plot2D(low=[0,0],high=[10,10],vis=False);
	[xobs,yobs,cobs] = pz.plot2D(low=[0,0],high=[10,10],delta=0.1,vis=False);
	[xpost,ypost,cpost] = post.plot2D(low=[0,0],high=[10,10],vis=False);  
	axarr[0].contourf(xprior,yprior,cprior,cmap='viridis'); 
	axarr[1].contourf(xobs,yobs,cobs,cmap='inferno'); 
	axarr[2].contourf(xpost,ypost,cpost,cmap='viridis'); 
	plt.show(); 

	#pz.plot2D(low=[0,0],high=[10,10],delta=0.1);

	# fig,ax = plt.subplots(); 
	# ax.contourf(xprior,yprior,cprior,cmap='viridis'); 
	# ax.set_xlabel('X/East Location (m)');
	# ax.set_ylabel('Y/West Location (m)');

	# fig,ax = plt.subplots(); 
	# ax.contourf(xpost,ypost,cpost,cmap='viridis'); 
	# ax.set_xlabel('X/East Location (m)');
	# ax.set_ylabel('Y/West Location (m)');

	plt.show(); 


