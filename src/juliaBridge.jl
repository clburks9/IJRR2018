importall POMDPs
using Distributions

type D4Diffs <: POMDPs.POMDP{Float64,Int,Int}
	discount_factor::Float64
	found_r::Float64
	lost_r::Float64
	step_size::Int
	movement_cost::Float64
end



function f(x)
	return sum(x);
end

function g(x)
	return mean(x); 
end


function h(x)
	return [x,x[1],sum(x)]; 
end

function makeTheThing()
	return D4Diffs(0.9,5,0,1,0); 
end

function changeTheThing(x)
	x.discount_factor = .8;
end

function reportTheThing(x) 
	println(x.discount_factor); 
end