
import time
import julia
import numpy as np; 
gate1 = time.clock(); 
j = julia.Julia();
gate2 = time.clock(); 
print("Julia Setup: {0:.4f} seconds".format(gate2-gate1))

#j.using("POMDPs"); 
# j.include("juliaBridge.jl"); 

# x = fn([1,2,3]);
# print(x); 

# foo = j.eval("f"); 

# print(foo([1,2,3]));


# h = j.eval("h"); 
# a = [[1,2],[3,4]]; 
# b = h(a); 
# print(b[0][0]);  

# start = j.eval('makeTheThing'); 
# change = j.eval('changeTheThing'); 
# report = j.eval('reportTheThing'); 
# a = start(); 
# report(a); 
# change(a); 
# report(a); 



j.include("julia_POMCP_Controller.jl"); 
gate3 = time.clock(); 
print("Julia include: {0:.4f} seconds".format(gate3-gate2)); 

makeSolver = j.eval("makeSolver"); 
getPOMCPAction = j.eval("getPOMCPAction"); 
initDist = j.eval('initial_state_distribution'); 

gate4 = time.clock(); 
print("Julia eval: {0:.4f} seconds".format(gate4-gate3)); 

[solver,pomdp,planner] = makeSolver();
gate5 = time.clock()
print("Julia Solver Make: {0:.4f}".format(gate5-gate4)); 

b = initDist(pomdp); 
act = getPOMCPAction(planner,b); 
gate6 = time.clock(); 
print("Chosen Action: {}".format(act)); 
print("Julia Action: {0:.4f} seconds".format(gate6-gate5)); 

