import os
import json
from git import Repo, Blob, Tree

def getTreeContent(tree):
	files = {}
	for node in tree : 
		if isinstance(node, Tree):
			files.update(getTreeContent(node))
		else : 
			files[str(node.path)] = {
				'obj_id' : str(node),
				'created_at' : 1,
				'modified_at' : []
			}
	return files

def instability(commits):
	#ricavo il primo commit
	first = commits[len(commits)-1]

	files = getTreeContent(first.tree)

	# print json.dumps(files, indent = 4, separators = (',',':'))

	#bisogna contare anche il primo commit
	internal_clock = 2

	for i in xrange(len(commits) - 2, -1, -1):
		print internal_clock
		print commits[i].message
		for diff in commits[i].diff(first):
			print diff.change_type, diff.a_rawpath
			#aggiunto al working tree
			if diff.change_type == 'D' or diff.a_mode is None : 
				files[str(diff.a_rawpath)] = {
					'obj_id' : '',
					'created_at' : internal_clock,
					'modified_at': []
				}
			#modificato
			if diff.change_type == 'M': 
				created_at = files[str(diff.a_rawpath)].get('created_at')
				modified_at = files[str(diff.a_rawpath)].get('modified_at')
				if len(modified_at) == 0 : 
					modified_at.append(internal_clock-created_at)
				else :
					modified_at.append(internal_clock-modified_at[-1])
				files[str(diff.a_rawpath)] = {
					'obj_id' : str(diff.a_blob),
					'created_at' : created_at,
					'modified_at' : modified_at
				}
		internal_clock+=1
		first = commits[i]

	print json.dumps(files, indent = 4,  separators = (',',':'))
	return

def change_complexity():
	return

def bugginess():
	return

def main():

	#repo for test
	path = '/home/vincenzo/compressione_paper'

	repository = Repo(path)

	if not repository.bare : 
		commits = list(repository.iter_commits('master'))
		instability(commits)



if __name__ == '__main__':
	main()