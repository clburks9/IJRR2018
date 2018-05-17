import time
import subprocess
#from subprocess import Popen,PIPE,STDOUT
import subprocess as sp
import sys


#Reference that finally worked:
#https://stackoverflow.com/questions/33886406/how-to-avoid-the-deadlock-in-a-subprocess-without-using-communicate

def main():

	child = sp.Popen(
	    ['python','-u','threadTestingChild.py'],
	    stdin = sp.PIPE,
	    stdout = sp.PIPE
	)

	# print_question = child.stdout.readline().decode('utf-8')  #PIPE's send a bytes type, 
	#                                                      #so convert to str type
	# #name = input(print_question)
	# name='l'; 
	# name = "{}\n".format(name)
	# child.stdin.write(
	#     name.encode('utf-8') #convert to bytes type
	# )
	# child.stdin.flush()

	# print_name = child.stdout.readline().decode('utf-8')
	# print("From client: {}".format(name))

	# print_question = child.stdout.readline().decode('utf-8')

	# #number = input(print_question)
	# number = '8';
	# number = "{}\n".format(number)
	# child.stdin.write(
	#     number.encode('utf-8')
	# )
	# child.stdin.flush()

	# print_number = child.stdout.readline().decode('utf-8')
	# print("From client: {}".format(print_number))

	# print_question = child.stdout.readline().decode('utf-8'); 

	# print(print_question); 
	a = '9\n'; 
	child.stdin.write(a.encode('utf-8')); 
	child.stdin.flush(); 
	b= '17\n'; 
	child.stdin.write(b.encode('utf-8')); 
	child.stdin.flush(); 

	print(child.stdout.readline().decode('utf-8')); 

	# a = '4\n'; 
	# child.stdin.write(a.encode('utf-8')); 
	# child.stdin.flush(); 
	# b= '17\n'; 
	# child.stdin.write(b.encode('utf-8')); 
	# child.stdin.flush(); 

	# print(child.stdout.readline().decode('utf-8')); 

if __name__ == '__main__':
    main()