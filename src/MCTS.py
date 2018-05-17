'''
######################################################

File: MCTS.py
Author: Luke Burks
Date: May 2018

Implements the Monte Carlo Tree Search algorithm in 
Kochenderfer chapter 6 

Reworked for ICRA 2018 Workshop 


######################################################
'''

from __future__ import division
from sys import path

path.append('../../src/');
path.append('./models'); 
from gaussianMixtures import GM, Gaussian 
from copy import deepcopy;
import matplotlib.pyplot as plt; 
import numpy as np; 
from scipy.stats import norm; 
import time; 
from anytree import Node,RenderTree
from anytree.dotexport import RenderTreeGraph
from anytree.iterators import PreOrderIter
from scipy.stats import multivariate_normal as mvn
import cProfile

class OnlineSolver():

	def __init__(self,assumedModel):
		modelModule = __import__('D4ICRAModel', globals(), locals(), ['ModelSpec'],0); 
		modelClass = modelModule.ModelSpec;
		self.model = modelClass();

		self.model.r = assumedModel.costLayer; 
		self.model.pz = assumedModel.sketches;
		self.model.obs = len(self.model.pz.keys()); 
		self.model.belief = assumedModel.belief; 
		self.model.copPose = assumedModel.copPose; 

		self.assumedModel = assumedModel; 

		self.N0 = 1; 
		self.Q0 = 100; 
		self.T = Node('',value = self.Q0,count=self.N0); 
		for a in range(0,self.model.acts):
			if(len([node for node in PreOrderIter(self.T,filter_=lambda n: n.name==self.T.name+str(a))]) == 0):
				tmp = Node(self.T.name + str(a),parent = self.T,value=self.Q0,count=self.N0); 
				for o in range(0,self.model.obs):
					if(len([node for node in PreOrderIter(self.T,filter_=lambda n: n.name==(self.T.name+str(a)+str(o)))]) == 0):
						tmp2 = Node(self.T.name+str(a)+str(o),parent=tmp,value = self.Q0,count=self.N0);  
		
		self.exploreParam = -1; 





	def getActionKey(self,d=3):
		bel = deepcopy(self.model.belief);
		self.model.copPose = self.assumedModel.copPose; 
		for g in bel:
			g.mean = [self.model.copPose[0],self.model.copPose[1],g.mean[0],g.mean[1]]; 
			g.var = [[1,0,0,0],[0,1,0,0],[0,0,g.var[0][0],g.var[0][1]],[0,0,g.var[1][0],g.var[1][1]]]; 

		h = self.T.name; 
		# for a in range(0,self.model.acts):
		# 	print(len([node for node in PreOrderIter(self.T,filter_=lambda n: n.name==self.T.name+str(a))]))
		# 	if(len([node for node in PreOrderIter(self.T,filter_=lambda n: n.name==self.T.name+str(a))]) == 0):
		# 		tmp = Node(self.T.name + str(a),parent = self.T,value=self.Q0,count=self.N0); 
		# 		for o in range(0,self.model.obs):
		# 			if(len([node for node in PreOrderIter(self.T,filter_=lambda n: n.name==(self.T.name+str(a)+str(o)))]) == 0):
		# 				tmp2 = Node(self.T.name+str(a)+str(o),parent=tmp,value = self.Q0,count=self.N0); 
		#RenderTreeGraph(self.T).to_picture('tree2.png'); 
		numLoops = 100; 

		for i in range(0,numLoops):
			#s = np.random.choice([i for i in range(0,self.model.N)],p=bel); 
			s = bel.sample(1)[0];  
			self.simulate(s,h,d); 
		#RenderTreeGraph(self.T).to_picture('tree1.png'); 
		#print(RenderTree(self.T)); 
		QH = [0]*self.model.acts; 
		for a in range(0,self.model.acts):
			QH[a] = [node.value for node in PreOrderIter(self.T,filter_=lambda n: n.name==h+str(a))][0]; 

		#for pre, fill, node in RenderTree(self.T):
			#print("%s%s" % (pre, node.name))

		act = np.argmax([QH[a] for a in range(0,self.model.acts)]);
		#return [act,QH[act]]; 
		return act

	def simulate(self,s,h,d):

		if(d==0):
			return 0; 
		if(len([node for node in PreOrderIter(self.T,filter_=lambda n: n.name==h)]) == 0):
			newRoot = [node for node in PreOrderIter(self.T,filter_=lambda n: n.name==h[0:len(h)-2])][0];
			newName = h[0:len(h)-2]; 
			for a in range(0,self.model.acts):
				if(len([node for node in PreOrderIter(self.T,filter_=lambda n: n.name==newName+str(a))]) == 0):
					tmp = Node(h + str(a),parent = newRoot,value=self.Q0,count=self.N0); 
					for o in range(0,self.model.acts):
						if(len([node for node in PreOrderIter(self.T,filter_=lambda n: n.name==newName+str(a)+str(o))]) == 0):
							tmp2 = Node(h+str(a)+str(o), parent = tmp,value = self.Q0,count=self.N0); 

			#tmp = Node(h,parent=newRoot,value = self.Q0,count=self.N0); 
			return self.getRolloutReward(s,d); 
		else:
			newRoot = [node for node in PreOrderIter(self.T,filter_=lambda n: n.name==h)][0];
			newName = h;
			for a in range(0,self.model.acts):
				if(len([node for node in PreOrderIter(self.T,filter_=lambda n: n.name==newName+str(a))]) == 0):
					tmp = Node(h + str(a),parent = newRoot,value=self.Q0,count=self.N0); 
					for o in range(0,self.model.acts):
						if(len([node for node in PreOrderIter(self.T,filter_=lambda n: n.name==newName+str(a)+str(o))]) == 0):
							tmp2 = Node(h+str(a)+str(o), parent = tmp,value = self.Q0,count=self.N0); 


			QH = [0]*self.model.acts; 
			NH = [0]*self.model.acts; 
			NodeH = [0]*self.model.acts;

			#print([node.name for node in PreOrderIter(self.T)])

			#RenderTreeGraph(self.T).to_picture('tree1.png'); 
			for a in range(0,self.model.acts):
				#print(h,a); 
				QH[a] = [node.value for node in PreOrderIter(self.T,filter_=lambda n: n.name==h+str(a))][0]; 
				NH[a] = [node.count for node in PreOrderIter(self.T,filter_=lambda n: n.name==h+str(a))][0]; 
				NodeH[a] = [node for node in PreOrderIter(self.T,filter_=lambda n: n.name==h+str(a))][0]; 

			aprime = np.argmax([QH[a] + self.exploreParam*np.sqrt(np.log(sum(NH)/NH[a])) for a in range(0,self.model.acts)]);  

			[sprime,o,r] = self.generate(s,aprime); 
			q = r + self.model.discount*self.simulate(sprime,h+str(aprime)+str(o),d-1); 
			NodeH[aprime].count += 1; 
			NodeH[aprime].value += (q-QH[a])/NH[a]; 
			return q; 

	def generate(self,s,a):
		#sprime = np.random.choice([i for i in range(0,self.model.N)],p=self.model.px[a][s]);

		#tmpGM = GM((np.array(s) + np.array(self.model.delA)).T.tolist(),self.model.delAVar,1); 
		# tmpGM = GM(); 
		# tmpGM.addG(Gaussian((np.array(s) + np.array(self.model.delA[a])).tolist(),self.model.delAVar,1))

		# sprime = tmpGM.sample(1)[0]; 
		sprime = (np.array(s)+np.array(self.model.delA[a])).tolist(); 
		ztrial = [0]*len(self.model.pz); 
		for i in range(0,len(self.model.pz)):
			ztrial[i] = self.model.pz[i].pointEvalND(sprime); 
		if(len(ztrial)>0):
			z = ztrial.index(max(ztrial)); 
		else:
			z = 0; 
		#reward = self.model.r[a].pointEval(s); 
		reward = self.model.r[int(s[0])][int(s[1])]; 
		
		

		return [sprime,z,reward]; 

	def getRolloutReward(self,s,d=1):
		reward = 0; 
		for i in range(0,d):
			a = np.random.randint(0,self.model.acts); 
			
			'''
			if(s < 13):
				a = 1; 
			elif(s>13):
				a = 0; 
			else:
				a = 2; 
			'''

			#reward += self.model.discount*self.model.r[a].pointEval(s); 
			#reward += self.model.discount*self.model.r[a].pointEval(s); 
			reward += self.model.discount*self.model.r[int(s[0])][int(s[1])]; 
			#s = np.random.choice([i for i in range(0,self.model.N)],p=self.model.px[a][s]);
			# tmpGM = GM(); 
			# tmpGM.addG(Gaussian((np.array(s) + np.array(self.model.delA[a])).tolist(),self.model.delAVar,1))

			# s = tmpGM.sample(1)[0];
			s = (np.array(s)+np.array(self.model.delA[a])).tolist();  
			s[0] = min(max(0,s[0]),437); 
			s[1] = min(max(0,s[1]),754); 

		return reward; 

	def normalize(self,a):
		suma = 0; 
		b=[0]*len(a); 
		for i in range(0,len(a)):
			suma+=a[i]
		for i in range(0,len(a)):
			b[i] = a[i]/suma; 
		return b; 


def testMCTS2D():
	a = OnlineSolver(); 
	b = GM([200,500,400,200],np.identity(4).tolist(),1); 

	action = a.getActionKey(b,d=3); 
	print(action); 





if __name__ == "__main__":

	testMCTS2D(); 
	#testMCTSSim2D(); 

	# f = Node("f")
	# b = Node("b", parent=f)
	# a = Node("a", parent=b)
	# d = Node("d", parent=b)
	# c = Node("c", parent=d)
	# e = Node("e", parent=d)
	# g = Node("g", parent=f)
	# i = Node("i", parent=g)
	# h = Node("h", parent=i)

	# from anytree.iterators import PreOrderIter
	# print([node for node in PreOrderIter(f,filter_=lambda n: n.name=='h')])


	
	
