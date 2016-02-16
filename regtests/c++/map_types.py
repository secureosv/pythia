'''
std::map<KEY, VALUE>
'''
mymap = {
	'key1' : [1,2,3],
	'key2' : [4,5,6,7]
}

def main():
	print mymap
	assert mymap['key1'][0]==1
	assert mymap['key1'][1]==2
