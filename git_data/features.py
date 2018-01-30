import os, json, re
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
				'last_edit' : 1,
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

		# print internal_clock
		# print commits[i].message

		for diff in commits[i].diff(first):
			# print diff.change_type, diff.a_rawpath
			#aggiunto al working tree
			if diff.change_type == 'D' or diff.a_mode is None : 
				files[str(diff.a_rawpath)] = {
					'obj_id' : '',
					'created_at' : internal_clock,
					'last_edit' : internal_clock,
					'modified_at': []
				}
			#modificato
			if diff.change_type == 'M': 

				created_at = files[str(diff.a_rawpath)].get('created_at')
				modified_at = files[str(diff.a_rawpath)].get('modified_at')
				last_edit = files[str(diff.a_rawpath)].get('last_edit')
	
				modified_at.append(internal_clock-last_edit)

				files[str(diff.a_rawpath)] = {
					'obj_id' : str(diff.a_blob),
					'created_at' : created_at,
					'last_edit' : internal_clock,
					'modified_at' : modified_at
				}

		internal_clock+=1
		first = commits[i]

	# print json.dumps(files, indent = 4,  separators = (',',':'))
	return files

def change_complexity():
	return

# https://help.github.com/articles/closing-issues-using-keywords/
def bugginess(commits):
	
	bugginess = 0

	#pattern
	close_pattern = re.compile(r'close(s|d)?', re.IGNORECASE)
	bug_pattern = re.compile(r'bug(fix)?', re.IGNORECASE)
	fix_pattern = re.compile(r'fix(es|ed|ing)?', re.IGNORECASE)
	resolve_pattern = re.compile(r'resolve(s|d)?', re.IGNORECASE)

	for commit in commits:
		if 	close_pattern.search(commit.message) or \
			bug_pattern.search(commit.message) or \
			fix_pattern.search(commit.message) or \
			resolve_pattern.search(commit.message) :
				bugginess+=1

	return bugginess

def main():

	#repo for test
	path = '/home/vincenzo/compressione_paper'

	repository = Repo(path)

	if not repository.bare : 
		commits = list(repository.iter_commits('master'))
		features_one = instability(commits)
		# features_three = bugginess(commits)
		print json.dumps(features_one, indent = 4, separators = (',',':'))

if __name__ == '__main__':
	main()