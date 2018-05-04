from __future__ import division
import numpy as np; 
import matplotlib.pyplot as plt; 
from softmaxModels import Softmax; 
from gaussianMixtures import Gaussian,GM; 
import math
from sympy import *
from sympy.functions import exp
import time; 

def makeModel():

	#weight = [-10,0]; 
	#bias = [10,0]; 
	weight = [-3,-2,-1,0]; 
	bias = [6,5,3,0]; 


	a = Softmax(weight,bias); 

	return a; 

def discreteIntegral(a,softClass=0,low=0,high=1,res=100,vis=False):

	[x,classes] = a.plot1D(low=low,high=high,res=res,vis=False);
	c = classes[softClass]; 

	area = sum(c)*(high-low)/res; 

	print("Discrete Area under the curve: {0:.5f}".format(area)); 

	if(vis):
		plt.plot(x,c); 
		plt.ylim([0,1]); 
		plt.xlim([low,high]); 
		plt.show(); 


def firstAndLastTerms(a,softClass = 0, depth = 10,low=0,high=1):

	#Ok this is completely wrong

	allVals = []; 
	suma = 0; 

	upperTerms = []; 
	lowerTerms = []; 

	wi = a.weights; 
	b = a.bias; 

	gammaHigh = sum([math.exp(wi[i]*high + b[i]) for i in range(0,len(wi))]); 
	gammaLow = sum([math.exp(wi[i]*low + b[i]) for i in range(0,len(wi))]);

	wiGammaHigh = sum([wi[i]*math.exp(wi[i]*high + b[i]) for i in range(0,len(wi))]);
	wiGammaLow = sum([wi[i]*math.exp(wi[i]*low + b[i]) for i in range(0,len(wi))]);

	for i in range(0,depth):
		#upperTerm
		negTerm = (-1)**i; 
		
		intTermHigh = math.exp(wi[softClass]*high + b[softClass])/(wi[softClass]**(i+1)); 
		intTermLow= math.exp(wi[softClass]*low + b[softClass])/(wi[softClass]**(i+1));

		derTermFirstHigh = negTerm*math.factorial(i)*(wiGammaHigh**i)/(gammaHigh**(i+1)); 
		derTermFirstLow = negTerm*math.factorial(i)*(wiGammaLow**i)/(gammaLow**(i+1)); 
		
		if(i>1):
			derTermSecondHigh = -sum([(wi[i]**i)*math.exp(wi[i]*high + b[i]) for i in range(0,len(wi))]);
			derTermSecondLow = -sum([(wi[i]**i)*math.exp(wi[i]*low + b[i]) for i in range(0,len(wi))]);
		else:
			derTermSecondHigh = 0; 
			derTermSecondLow = 0; 


		derTermHigh = derTermFirstHigh + derTermSecondHigh; 
		derTermLow = derTermFirstLow + derTermSecondLow; 

		fullTermHigh = negTerm*derTermHigh*intTermHigh;
		fullTermLow= negTerm*derTermLow*intTermLow;  

		upperTerms.append(fullTermHigh); 
		lowerTerms.append(fullTermLow); 

		allVals.append(fullTermHigh-fullTermLow); 

	return allVals; 


def findAlphaInt(alpha,depth,val):
	x = Symbol('x'); 
	tmp = alpha; 
	for jk in range(0,depth):
		tmp = tmp.diff(x); 
	tmp = tmp.evalf(subs={x:val}); 
	return tmp; 

def findAlphaRecurse(alpha,val):
	x = Symbol('x'); 
	tmp = alpha.diff(x); 
	tmp2 = tmp.evalf(subs={x:val}); 
	return tmp,tmp2; 

def findBetaRecurse(beta,val):
	x = Symbol('x'); 
	tmp = integrate(beta,x); 
	tmp2 = tmp.evalf(subs={x:val}); 
	return tmp,tmp2; 


def findBetaInt(beta,depth,val):
	#return math.exp(a.weights[softClass]*val + a.bias[softClass])/(a.weights[softClass]**depth); 
	x = Symbol('x'); 
	tmp = beta; 
	for jk in range(0,depth):
		tmp = integrate(tmp,x); 

	tmp = tmp.evalf(subs={x:val}); 

	return tmp; 

def findBeta(a,softClass,depth,val):
	return math.exp(a.weights[softClass]*val + a.bias[softClass])/(a.weights[softClass]**depth); 

def symbolicSum(a,softClass=0,depth=10,low=0,high=1,vis=False):
	x = Symbol('x'); 
	n = Symbol('n'); 

	alpha = sum([exp(a.weights[i]*x + a.bias[i]) for i in range(0,len(a.weights))])**-1;
	beta = exp(a.weights[softClass]*x + a.bias[softClass]); 
	#print(alpha); 
	#print(beta); 

	f_alpha = lambdify([x,n],alpha.diff(x,n=n),'numpy');
	#f_beta = lambdify([x,n],findBetaInt(beta,n,x),'numpy'); 

	upperTerms = []; 
	lowerTerms = []; 
	allTerms = []; 
	sumSoFar = []; 

	allIntTerms = {'pos':[],'neg':[]}; 
	allDerTerms = {'pos':[],'neg':[]}; 


	allAlphas = [alpha]; 
	allBetas = []; 


	#upper
	newAlpha = alpha; 
	newBeta = beta; 
	for i in range(0,depth): 
		#print(i); 
		negTerm = (-1)**i; 
		#intTerm = findBeta(a,softClass,i+1,high); 
		#intTerm = f_beta(high,i+1);
		#intTerm = findBetaInt(beta,i+1,high) 
		[newBeta,intTerm] = findBetaRecurse(newBeta,high); 
		#print(intTerm); 
		

		#derTerm = f_alpha(high,i); 
		#derTerm = findAlphaInt(alpha,i,high); 
		if(i!=0):
			[newAlpha,derTerm] = findAlphaRecurse(newAlpha,high); 
		else:
			derTerm = alpha.evalf(subs={x:high}); 

		upperTerms.append(negTerm*intTerm*derTerm); 
		allIntTerms['pos'].append(intTerm); 
		allDerTerms['pos'].append(derTerm);

	#lower
	newAlpha=alpha; 
	newBeta = beta; 
	for i in range(0,depth):
		#print(i); 
		negTerm = (-1)**i; 
		#intTerm = findBeta(a,softClass,i+1,low); 
		#intTerm = f_beta(low,i+1);
		#intTerm = findBetaInt(beta,i+1,low) 
		[newBeta,intTerm] = findBetaRecurse(newBeta,low); 
		#print(intTerm); 

		

		#derTerm = f_alpha(low,i); 
		#derTerm = findAlphaInt(alpha,i,low); 
		if(i!=0):
			[newAlpha,derTerm] = findAlphaRecurse(newAlpha,low); 
		else:
			derTerm = alpha.evalf(subs={x:low}); 

		lowerTerms.append(negTerm*intTerm*derTerm);
		allIntTerms['neg'].append(intTerm); 
		allDerTerms['neg'].append(derTerm);

	for i in range(0,depth):
		allTerms.append(upperTerms[i]-lowerTerms[i]); 
		sumSoFar.append(sum(allTerms)); 


	#print(allTerms); 
	#print(sumSoFar); 

	#print(upperTerms); 
	#print(lowerTerms); 

	print("Summation Area Under Curve: {0:.5f}".format(sumSoFar[-1])); 

	if(vis):
		#plt.plot(sumSoFar); 
		plt.plot(upperTerms,c='b'); 
		plt.plot(lowerTerms,c='r');
		plt.plot(allTerms,c='g');  
		plt.plot(sumSoFar,c='k'); 
		plt.show(); 

		plt.plot(allIntTerms['pos'],'b'); 
		plt.plot(allIntTerms['neg'],'g'); 

		plt.show(); 
		plt.plot(allDerTerms['pos'],'r'); 
		plt.plot(allDerTerms['neg'],'k'); 
		plt.show(); 




if __name__ == '__main__':
	a = makeModel();
	#a.plot1D(low=0,high=5); 
	high = 1; 
	low = 0; 
	softClass = 0; 


	start = time.clock(); 
	discreteIntegral(a,softClass=softClass,low=low,high=high,res=10000); 
	stop = time.clock(); 
	print("Discrete Time: {0:.3f} seconds".format(stop-start)); 

	start = time.clock(); 
	symbolicSum(a,softClass=softClass,depth=13,low=low,high=high,vis=True);
	stop = time.clock(); 
	print("Symbolic Sum Time: {0:.3f} seconds".format(stop-start)); 



	x = Symbol('x'); 
	n = Symbol('n'); 

	y = 1/sum([exp(a.weights[i]*x + a.bias[i]) for i in range(0,len(a.weights))]);
	y2 =  exp(a.weights[0]*x + a.bias[0])/sum([exp(a.weights[i]*x + a.bias[i]) for i in range(0,len(a.weights))]);

	# upper = integrate(y2,x).evalf(subs={x:1}); 
	# lower = integrate(y2,x).evalf(subs={x:0});
	# print(re(upper-lower)); 

	start = time.clock(); 
	full = re(integrate(y2,(x,low,high)).evalf()); 
	stop = time.clock(); 
	print('Sympy Approximation: {0:.5f}'.format(full)); 
	print("Sympy Time: {0:.3f} seconds".format(stop-start)); 


