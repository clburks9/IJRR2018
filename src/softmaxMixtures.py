'''
***********************************************************
File: softmaxMixtures.py
Author: Luke Burks
Date: May 2018

Testing the dynamic creation of "relative" softmax classes
such as an observation that a target is between two objects
with known softmax models
***********************************************************
'''

__author__ = "Luke Burks"
__copyright__ = "Copyright 2018, Cohrint"
__credits__ = ["Luke Burks", "Nisar Ahmed"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Luke Burks"
__email__ = "luke.burks@colorado.edu"
__status__ = "Development"

import numpy as np; 
import matplotlib.pyplot as plt

from softmaxModels import Softmax
from gaussianMixtures import GM,Gaussian


class SM:

	def __init__(self,mods= {}):
		self.mods = mods; 
		self.size = len(mods.values());
		self.normalizeWeights();  


	def __getitem__(self,key):
		return self.mods[key]; 

	def __setitem__(self,key,value):
		self.mods[key] = value;

	def getWeights(self):
		'''
		Returns a list containing the weights
		of each mixand
		'''
		ans = [];
		for s in self.mods.values():
			ans.append(s.probWeight);
		return ans;


	def addSoft(self,name,soft):
		self.mods[name] = soft; 
		#self.normalizeWeights(); 
		self.size+=1; 

	def normalizeWeights(self):
		'''
		Normalizes the weights of the mixture such that they all add up to 1.
		'''
		suma = 0;
		for s in self.mods.values():
			suma += s.probWeight;
		for s in self.mods.values():
			s.probWeight = s.probWeight/suma;

	def plot2D(self,low = [0,0],high = [5,5],delta=0.1,retClasses = {},AND_OR = "AND"):
		#because its multiple models, require a list of classes to return

		if(self.size == 0):
			return None; 
		else:
			allDoms = {};
			for key in retClasses.keys():
				allDoms[key] = {}; 
				for v in retClasses[key]:
					[x,y,dom] = self.mods[key].plot2D(low,high,vis=False,delta=delta,retClass = v); 
					allDoms[key][v] = np.array(dom)*self.mods[key].probWeight; 
			
			if(AND_OR == "AND"):
				sumDom = None; 
				for v in allDoms.values():
					for v2 in v.values():
						if(sumDom is None):
							sumDom = v2; 
						else:
							sumDom = sumDom*v2; 
			else:
				sumDom = None;
				for v in allDoms.values():
					for v2 in v.values():
						if(sumDom is None):
							sumDom = v2; 
						else:
							sumDom += v2;

			return x,y,sumDom

	def OR_VBND(self,prior,softClasses):
		post = GM(); 
		for key in softClasses.keys():
			for v in softClasses[key]:
				tmp = self.mods[key].runVBND(prior,v); 
				tmp.scalarMultiply(self.mods[key].probWeight); 
				post.addGM(tmp); 
		post.normalizeWeights(); 
		return post; 

	def AND_VBND(self,prior,softClasses):
		post = prior 
		for key in softClasses.keys():
			for v in softClasses[key]:
				post = self.mods[key].runVBND(post,v); 
		post.normalizeWeights(); 
		return post; 

def testBetween():
	#np.random.seed(1); 

	lows = [0,0]; 
	highs = [10,10]; 
	#classes = [1,1,1,1]; 
	#classes = [4,1,None,None];
	#classes = [3,3,3,3];
	classes = {"A":[3],"B":[3],"C":[3],"D":[3]}; 
	#classes = {"A":4,"B":1}
	#classes = {"A":3,"B":3,"C":3,"D":3};
	#classes = {"A":[3,4]}
	steep = 3; 
	AND_OR = 'OR'

	prior = GM(); 
	prior.makeRandomMixture(size=5,perMax=0.2);
	[xprior,yprior,cprior] = prior.plot2D(low=lows,high=highs,vis=False);  

	A = Softmax(); 
	A.buildOrientedRecModel([4,5],0,1,1,steepness=steep); 

	B = Softmax(); 
	B.buildOrientedRecModel([6,5],180,1,1,steepness=steep); 

	C = Softmax(); 
	C.buildOrientedRecModel([5,6],270,1,1,steepness=steep); 

	D = Softmax(); 
	D.buildOrientedRecModel([5,4],90,1,1,steepness=steep); 



	like = SM({"A":A,"B":B,"C":C,"D":D}); 


	[xlike,ylike,dom] = like.plot2D(low=lows,high=highs,retClasses=classes,AND_OR = AND_OR); 
	
	print(like.getWeights());

	if(AND_OR == 'OR'):
		post = like.OR_VBND(prior,classes); 
	else:
		post = like.AND_VBND(prior,classes); 
	#post.display()
	[xpost,ypost,cpost] = post.plot2D(low=lows,high=highs,vis=False); 


	fig,axarr = plt.subplots(3); 
	axarr[0].contourf(xprior,yprior,cprior); 
	axarr[0].set_title('Prior'); 

	axarr[1].contourf(xlike,ylike,dom); 
	axarr[1].set_title('Likelihood'); 

	axarr[2].contourf(xpost,ypost,cpost); 
	axarr[2].set_title('Posterior'); 

	plt.show(); 




if __name__ == '__main__':
	testBetween(); 
