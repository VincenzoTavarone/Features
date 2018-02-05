import os, json
from collections import OrderedDict
from git import Repo
from features import instability, changeComplexity, bugginess

def medianNumber(modifications) :
	modifications.sort()
	median = 0
	if len(modifications) % 2 == 0 :
		median = (modifications[(len(modifications)/2)-1] + modifications[(len(modifications)/2)])/2
	else : 
		median = modifications[len(modifications)/2]
	return median

#main definito per il testing
def test():

	#repo for test
	path = '/home/vincenzo/eclipse-workspace/compressione'

	repository = Repo(path)

	if not repository.bare : 

		commits = list(repository.iter_commits('master'))
		features_one = instability(commits)
		# features_two = changeComplexity(commits)
		# features_three = bugginess(commits)

		# necessario
		result_as_json = json.dumps(features_one, sort_keys = True, indent = 4, separators = (',',':'))
		features_one = json.loads(result_as_json, object_pairs_hook = OrderedDict)

		with open("../csv/test.csv", "w+") as csv :
			csv.write("filename, instability")
			for k,v in features_one.iteritems():
				class_name = k
				modifications = v.get("modified_at")
				median = 0
				if len(modifications) > 0 : 
					median = medianNumber(modifications) 
				else : 
					median = len(commits)
				line = "\n" + class_name + ", " + str(median)
				csv.write(line)

if __name__ == '__main__':
	test()