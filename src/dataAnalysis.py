import numpy as np; 
import matplotlib.pyplot as plt


def loadData(control,pushing,belnum):

	fileName = '../data/{}_bel{}_{}.npy'.format(control,belnum,pushing); 

	data = np.load(fileName);
	data = data[0]; 
	return data; 

def loadAllData():

	data = {"POMCP":{"NO":{},"MEH":{},"GOOD":{}},"MAP":{"NO":{},"MEH":{},"GOOD":{}}};

	types = ["POMCP","MAP"]; 
	goodness = ["NO","MEH","GOOD"]; 
	for t in types: 
		for g in goodness:
			data[t][g] = loadData(t,g,0); 

	return data; 



if __name__ == '__main__':
	# dataMAP = loadData('MAP','MEH',0); 
	# dataPOMCP = loadData("POMCP","MEH",0); 
	# print(len(dataMAP['positions'])); 
	# print(len(dataPOMCP['positions'])); 
	
	data = loadAllData(); 
	print(len(data['POMCP']['GOOD']['positions'])); 
	