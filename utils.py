import random 

#tools functions
def partition (list_in, n):
	"""Slice a list into n randomly-sized parts.
	"""
	random.shuffle(list_in)
	#return [list_in[0::n] , list_in[n::]]
	return [list_in[x::n] for x in range(n)]
	#return [list_in[i:i+6] for i in x range(n)]

