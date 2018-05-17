


import julia

import time



def watch(j,solver,pomdp,planner):

	getPOMCPAction = j.eval("getPOMCPAction"); 
	makeDist = j.eval("makeDist"); 



	while(True):
		try:
			cp0 = float(raw_input());
			cp1 = float(raw_input()); 
			mmean0 = float(raw_input()); 
			mmean1 = float(raw_input()); 
			cov0 = float(raw_input()); 
			cov1 = float(raw_input());
		except IOError as e:
			if(e.errno == 11):
				time.sleep(0.1); 


		initDist = makeDist(cp0,cp1,mmean0,mmean1,cov0,cov1); 
		act = getPOMCPAction(planner,initDist); 

		print(act); 

def main():
	j = julia.Julia(); 
	j.include("julia_POMCP_Controller.jl");
	makeSolver = j.eval("makeSolver"); 

	[solver,pomdp,planner] = makeSolver();

	watch(j,solver,pomdp,planner); 


if __name__ == '__main__':
    main()