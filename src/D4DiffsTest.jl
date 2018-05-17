importall POMDPs
using Distributions

type D4Diffs <: POMDPs.POMDP{Float64,Int,Int}
	discount_factor::Float64
	found_r::Float64
	lost_r::Float64
	step_size::Int
	movement_cost::Float64
end


D4Diffs() = D4Diffs(0.9,5,0,1,0); 
discount(p::D4Diffs) = p.discount_factor; 

#observations, function of state only
function generate_o(p::D4Diffs, s::Array, a::Int, sp::Array, rng::AbstractRNG)

	if sqrt(s[1]*s[1] + s[2]*s[2]) < 1
		return 4
	elseif abs(s[1]) > abs(s[2])
		if s[1] < 0
			return 0
		else
			return 1
		end
	else
		if s[2] > 0
			return 2
		else
			return 3
		end
	end
end

#state transitions, function of state and action
function generate_s(p::D4Diffs, s::Array, a::Int, rng::AbstractRNG)
	sig_0 = [1,1,sqrt(0.00001),sqrt(0.00001)]
	sig_stationary = [sqrt(0.00001),sqrt(0.00001),sqrt(0.00001),sqrt(0.00001)]
	d= MvNormal(sig_stationary)
    noise = rand(d::MvNormal) 


    if a == 0
        s= s + [-1,0,0,0] + noise
    elseif a == 1
        s= s + [1,0,0,0] + noise
    elseif a == 2
    	s= s + [0,1,0,0] + noise
    elseif a == 3
    	s= s + [0,-1,0,0] + noise
    else 
    	s= s + noise
    end

    s[1] = max(-10,s[1])
    s[1] = min(10,s[1]); 
    s[2] = max(-10,s[2])
    s[2] = min(10,s[2]);
    s[3] = max(-10,s[3])
    s[3] = min(10,s[3]);
    s[4] = max(-0.25,s[4])
    s[4] = min(0.25,s[4])

    return s   
    

end


function reward(p::D4Diffs, s::Array, a::Int, sp::Array)
   	if sqrt(s[1]*s[1] + s[2]*s[2]) < 1
		return p.found_r
	else
		return p.lost_r
	end
end;


actions(::D4Diffs) = [0,1,2,3,4] # Left Stop Right
n_actions(::D4Diffs) = 5

function initial_state_distribution(pomdp::D4Diffs)
    sig_0 = [10,10,sqrt(0.00001),sqrt(0.00001)]
    return MvNormal(sig_0)
end;


using BasicPOMCP
using POMDPToolbox
importall Base
using Dates

#1second = 42000
#2second = 78000
#3second = 110000
solver = POMCPSolver(tree_queries=42000, c=10)
pomdp = D4Diffs()
planner = solve(solver, pomdp);

allRewards = []

numSims = 2; 
simLength = 5; 

for i in 1:numSims
	println("Starting simulation $i of $numSims"); 
	tmpRewards = []; 
	stepCount = 0; 
	totalReward = 0; 
	for (s,a,r,sp,o) in stepthrough(pomdp, planner, "sarspo")
	    push!(tmpRewards,totalReward); 
	    #println(allRewards)
	    totalReward = totalReward + r; 
	    stepCount = stepCount + 1; 
	    if stepCount >= simLength
	    	break; 
	    else
	    	sdfkj=0
	    	#print(stepCount);
	    	#print(": ")
	    	#println(Dates.Time(now()))
	    end
	end
	push!(allRewards,tmpRewards); 
end

println("Simulations Complete, saving results.")

open("oneSecondPOMCP_stationary.txt","w") do f
	writedlm(f,allRewards); 
end


