
import os
import sys
import time
import threading

import julia


# print("Name?"); 
# name = raw_input(); 
# print(name); 

# print("Number?");
# number = raw_input(); 
# print(number); 

#print("What are the numbers?"); 

def watch():
    #while(True):
    a = int(raw_input());
    b = int(raw_input());  

    print(a+b); 

def main():
    j = julia.Julia(); 
    watch(); 


if __name__ == '__main__':
    main()