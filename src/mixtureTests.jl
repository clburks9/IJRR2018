using Distributions

a = MvNormal([1.,2.],[1.,1.]); 
b = MvNormal([4.,3.],[1.,1.]); 

d = MvNormal[]; 
push!(d,a);
push!(d,b); 
print(d); 

c = MixtureModel(d,[.3,.7]); 
print(c); 