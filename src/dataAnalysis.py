import numpy as np; 
import matplotlib.pyplot as plt


def loadData(control,pushing,belnum):

	fileName = '../data/lengthOnly/{}_bel{}_{}.npy'.format(control,belnum,pushing); 

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


def findMixtureParams(mixture):

	#cut the mixture to just the robber dimensions
	newMixture = GM(); 
	for g in mixture:
		tmpMean = [g.mean[2],g.mean[3]]; 
		tmpVar = [[g.var[2][2],g.var[2][3]],[g.var[3][2],g.var[3][3]]]; 
		newMixture.addG(Gaussian(tmpMean,tmpVar,g.weight)); 

	#mean is a weighted average of means
	mixMean = np.zeros(2);
	for g in newMixture:
		mixMean += np.array(g.mean)*g.weight; 

	#Variance is the weighted sum of variances plus the weighted sum of outer products of the difference of the mean and mixture mean
	mixVar = np.zeros(shape=(2,2)); 
	for g in newMixture:
		mixVar += np.matrix(g.var)*g.weight; 
		mixVar += (np.matrix(g.mean)-np.matrix(mixMean)).T*(np.matrix(g.mean)-np.matrix(mixMean))*g.weight; 

	return mixMean,mixVar;

def showBoundedRobberEstimate(data,obs=False,useFullXAxis=True):



	dist = {}; 
	for key in data.keys():
		dist[key] = {}; 
		for key2 in data[key].keys():
			dist[key][key2] = {'means':[],'vars':[]}; 
			
			bels = data[key][key2]['beliefs'];

			for i in range(0,len(bels)):
				mixMean,mixVar = findMixtureParams(bels[i]); 
				dist[key][key2]['means'].append(mixMean); 
				dist[key][key2]['vars'].append([mixVar[0][0],mixVar[1][1]]); 

	
	fig,axarr = plt.subplots(6,2); 
	fig.text(0.5,0.04,'Seconds',ha='center'); 
	legend = []; 
	colors = {'NoHuman':'b','HumanPush':'g','RobotPull':'r','Both':'k'};
	keys = data.keys(); 

	if(mapType=='a'):
		runTimes = [{'NoHuman':307,'HumanPush':80,'RobotPull':51,'Both':69},{'NoHuman':191,'HumanPush':132,'RobotPull':42,'Both':61},{'NoHuman':123,'HumanPush':87,'RobotPull':75,'Both':40}]
	else:
		runTimes= [{'NoHuman':176,'HumanPush':86,'RobotPull':87,'Both':46},{'NoHuman':214,'HumanPush':183,'RobotPull':99,'Both':35}]
	maxRunTime = runTimes[run]['NoHuman'];



	for key in keys:
		secondsPerStep = runTimes[run][key]/len(dist[key]['means']);
		#secondsPerStep=1; 
		x = [i*secondsPerStep for i in range(0,len(dist[key]['means']))]; 
		ind = keys.index(key); 

		# error0 = [dist[key]['means'][i][0] - data[key]['RobberPose'][run][i][0] for i in range(0,len(x))]; 
		# error1 = [dist[key]['means'][i][1] - data[key]['RobberPose'][run][i][1] for i in range(0,len(x))];
		robs0 = [data[key]['RobberPose'][run][i][0] for i in range(0,len(x))];
		robs1 = [data[key]['RobberPose'][run][i][1] for i in range(0,len(x))];  
		m0 = [dist[key]['means'][i][0] for i in range(0,len(x))]; 
		m1 = [dist[key]['means'][i][1] for i in range(0,len(x))]; 
		upperBound0 = [dist[key]['means'][i][0] + 2*np.sqrt(dist[key]['vars'][i][0]) for i in range(0,len(x))];
		upperBound1 = [dist[key]['means'][i][1] + 2*np.sqrt(dist[key]['vars'][i][1]) for i in range(0,len(x))]; 
		lowerBound0 = [dist[key]['means'][i][0] - 2*np.sqrt(dist[key]['vars'][i][0]) for i in range(0,len(x))]; 
		lowerBound1 = [dist[key]['means'][i][1] - 2*np.sqrt(dist[key]['vars'][i][1]) for i in range(0,len(x))];  

		axarr[ind][0].plot(x,m0,c=colors[key]); 
		axarr[ind][1].plot(x,m1,c=colors[key]); 
		#axarr[ind][0].set_ylim([-10,10]); 
		#axarr[ind][1].set_ylim([-10,10]); 
		axarr[ind][0].plot(x,robs0,colors[key]+'-.'); 
		axarr[ind][1].plot(x,robs1,colors[key]+'-.'); 

 
		#axarr[ind][0].plot(x,upperBound0,colors[key]+'--'); 
		#axarr[ind][0].plot(x,lowerBound0,colors[key]+'--');
		axarr[ind][0].fill_between(x,lowerBound0,upperBound0,color=colors[key],alpha=0.25);
		#axarr[ind][1].plot(x,upperBound1,colors[key]+'--'); 
		#axarr[ind][1].plot(x,lowerBound1,colors[key]+'--');
		axarr[ind][1].fill_between(x,lowerBound1,upperBound1,color=colors[key],alpha=0.25); 

		axarr[ind][0].set_ylabel(key); 

		if(not useFullXAxis):
			axarr[ind][0].set_xlim([0,maxRunTime]); 
			axarr[ind][1].set_xlim([0,maxRunTime]);
		#axarr[ind][0].set_xlim([0,70]);
		#axarr[ind][1].set_xlim([0,70]);

		if(obs):
			hobs = data[key]['obs'][run]; 
			#print(hobs); 
			for i in range(0,len(robs0)):
				h = hobs[i]; 
			#for h in hobs:
				h1 = h.split('\n');
				for hprime in h1:
					if(hprime is not ''):
						if('False' in hprime or 'not' in hprime):
							axarr[ind][0].axvline(x=hobs.index(h)*secondsPerStep + h1.index(hprime)*2,c='r');
							axarr[ind][1].axvline(x=hobs.index(h)*secondsPerStep+ h1.index(hprime)*2,c='r');  
							# axarr[0].scatter(hobs.index(h),0,marker='*',c='r')
							# axarr[1].scatter(hobs.index(h),0,marker='*',c='r')
						else:
							# axarr[0].scatter(hobs.index(h),0,marker='*',c='g')
							# axarr[1].scatter(hobs.index(h),0,marker='*',c='g')
							axarr[ind][0].axvline(x=hobs.index(h)*secondsPerStep+ h1.index(hprime)*2,c='g');
							axarr[ind][1].axvline(x=hobs.index(h)*secondsPerStep+ h1.index(hprime)*2,c='g');  

	axarr[0][0].set_title('X Estimate'); 
	axarr[0][1].set_title('Y Estimate'); 

	if(mapType == 'a'):
		runKeys = ['Library','Study','Kitchen'];
		plt.suptitle('First Map: Robber Position Estimates starting from ' + runKeys[run]) 
	else:
		runKeys = ['Billiard Room', 'Study'];
		plt.suptitle('Second Map: Robber Position Estimates starting from ' + runKeys[run]) 

	

	# fig = plt.gcf(); 
	# fig.set_size_inches(10,8); 

	# if(mapType=='a'):
	# 	plt.savefig('./figures/mapA/{}_positionEstimates.png'.format(runKeys[run]),bbox_inches='tight',pad_inches=0,dpi=300);
	# else:
	# 	plt.savefig('./figures/mapC/{}_positionEstimates.png'.format(runKeys[run]),bbox_inches='tight',pad_inches=0,dpi=300);
	# #plt.show(); 




if __name__ == '__main__':

	# data = loadData("MAP","NO",0); 

	# print(len(data['positions'])); 
	# print(data['positions']); 

	data = loadAllData(); 
	print(len(data['POMCP']['GOOD']['positions'])); 

	types = ["POMCP","MAP"]; 
	goodness = ["NO","MEH","GOOD"]; 

	for t in types:
		print("For Method: {}".format(t)); 
		for g in goodness:
			print("With {} Human: {}".format(g,len(data[t][g]['positions']))); 