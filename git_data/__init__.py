import os, json
from collections import OrderedDict
from git import Repo
from features import instability, bugginess, change_complexity_fun

def medianNumber(modifications) :
	modifications.sort()
	median = 0
	if len(modifications) % 2 == 0 :
		median = (modifications[(len(modifications)/2)-1] + modifications[(len(modifications)/2)])/2
	else : 
		median = modifications[len(modifications)/2]
	return median

def avgComplexity(data) : 
	avg = 0.0
	if data['lines'] == 0 : 
		return 0
	else : 
		for number in data['modifications'] : 
			avg += number
		avg = avg/len(data['modifications'])
		return avg

#main definito per il testing
def main_instability():

	#repo for test
	path = '/home/vincenzo/Scrivania/dataset/camel'
	# path = '/home/vincenzo/compilatori'

	repository = Repo(path)

	if not repository.bare : 

		commits = list(repository.iter_commits('master'))
		features_one = instability(commits)
		# features_two = changeComplexity(commits)
		# features_three = bugginess(commits)

		# necessario
		result_as_json = json.dumps(features_one, sort_keys = True, indent = 4, separators = (',',':'))
		features_one = json.loads(result_as_json, object_pairs_hook = OrderedDict)

		with open("../csv/instability/camel-instability.csv", "w+") as csv :
			csv.write("filename;instability")
			for k,v in features_one.iteritems():
				class_name = k
				modifications = v.get("modified_at")
				median = 0
				if len(modifications) > 0 : 
					median = medianNumber(modifications) 
				else : 
					median = len(commits)
				line = "\n" + class_name + ";" + str(median)
				csv.write(line)


def main_changeComplexity() : 

	path = '/home/vincenzo/Scrivania/dataset/umlet'

	repository = Repo(path)

	if not repository.bare : 
		commits = list(repository.iter_commits('master'))
		features_two = change_complexity_fun(commits)
		result_as_json = json.dumps(features_two, sort_keys = True, indent = 4, separators = (',',':'))
		features_two = json.loads(result_as_json, object_pairs_hook = OrderedDict)

		with open("../csv/change_complexity_1/umlet-change_complexity.csv", "w+") as csv : 
			csv.write("filename;change complexity")
			for k,v in features_two.iteritems() : 
				class_name =  k
				change_complexity = avgComplexity(v)
				if change_complexity != 0 : 
					line = "\n" + class_name + ";" + str(change_complexity)
					csv.write(line)

def main_bugginess() : 
	
	path  = '/home/vincenzo/Scrivania/dataset/umlet'

	repository = Repo(path)

	if not repository.bare : 
		commits = list(repository.iter_commits('master'))
		features_three = bugginess(commits)
		result_as_json = json.dumps(features_three, sort_keys = True, indent = 4, separators = (',',':'))
		features_three = json.loads(result_as_json, object_pairs_hook = OrderedDict)

		with open("../csv/bugginess_1/umlet-bugginess.csv", "w+") as csv : 
			csv.write("filename;bugginess")
			for k, v in features_three.iteritems() :
				line = "\n" + k + ";" + str(v['bugginess'])
				csv.write(line)	

if __name__ == '__main__':
	main_bugginess()