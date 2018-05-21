
from gaussianMixtures import GM,Gaussian
import numpy as np;

numBels = 10; 

for j in range(0,numBels):
	belief = GM(); 
	belief.addNewG([400,200],[[1000,0],[0,1000]],.25); 

	for i in range(0,20):
		belief.addNewG([np.random.randint(0,437),np.random.randint(0,754)],[[2000+500*np.random.normal(),0],[0,2000+500*np.random.normal()]],np.random.random()); 
	belief.normalizeWeights();
	np.save("../models/beliefs{}.npy".format(j),[belief]); 

