import os, json, re
from git import Repo, Blob, Tree

def getTreeContent(tree):
	files = {}
	for node in tree : 
		if isinstance(node, Tree):
			files.update(getTreeContent(node))
		else : 
			if ".java" in node.path : 
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
	
	#bisogna contare anche il primo commit
	internal_clock = 2

	for i in xrange(len(commits) - 2, -1, -1):

		for diff in commits[i].diff(first) :
			# print diff.change_type, diff.a_rawpath
			#aggiunto al working tree
			if (diff.change_type == 'D' or diff.a_mode is None) and ".java" in diff.a_rawpath : 
				files[str(diff.a_rawpath)] = {
					'obj_id' : '',
					'created_at' : internal_clock,
					'last_edit' : internal_clock,
					'modified_at': []
				}

			#modificato
			if diff.change_type == 'M' and ".java" in diff.a_rawpath : 
				if diff.renamed : 
					print 'file rinominato'
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

			#eliminato dal working tree
			if diff.change_type == 'A' and ".java" in diff.a_rawpath : 
				del files[str(diff.a_rawpath)]

			#rinominato
			if diff.renamed and ".java" in diff.a_rawpath : 
				tmp = files[str(diff.rename_to)]
				del files[str(diff.rename_to)]
				files[str(diff.rename_from)] = tmp


		internal_clock+=1
		first = commits[i]

	# print json.dumps(files, indent = 4,  separators = (',',':'))
	return files

def changeComplexity(commits):
	
	stats = {}

	for i in xrange(len(commits) - 1, -1, -1):
		files =  commits[i].stats.files 
		for key, value in files.iteritems():
			if ".java" in key : 
				if str(key) in stats : 
					lines = stats[str(key)].get('lines') + value.get('insertions') - value.get('deletions')
					modifications =  stats[str(key)].get('modifications')
					modifications.append(value.get('lines'))
					stats[str(key)] = {
						'lines' : lines,
						'modifications' : modifications
					}
				else :
					modifications = []
					modifications.append(value.get('lines'))
					stats[str(key)] = {
						'lines' : value.get('lines'),
						'modifications' :  modifications
					}
	return stats

# https://help.github.com/articles/closing-issues-using-keywords/
def bugginess(commits):
	
	bugginess = {}

	#patterns
	close_pattern = re.compile(r'close(s|d)?', re.IGNORECASE)
	bug_pattern = re.compile(r'bug(fix)?', re.IGNORECASE)
	fix_pattern = re.compile(r'fix(es|ed|ing)?', re.IGNORECASE)
	resolve_pattern = re.compile(r'resolve(s|d)?', re.IGNORECASE)
	issue_pattern = re.compile(r'#[1-9][0-9]*', re.IGNORECASE)

	for i in xrange(len(commits) - 1, -1, -1) :
		commit = commits[i]
		if 	close_pattern.search(commit.message) or \
			bug_pattern.search(commit.message) or \
			fix_pattern.search(commit.message) or \
			issue_pattern.search(commit.message) or \
			resolve_pattern.search(commit.message) :
				print commit.message
				files = commit.stats.files
				for key, value in files.iteritems() : 
					if ".java" in key : 
						if str(key) in bugginess : 
							bugginess[str(key)] = {
								'bugginess' : bugginess[str(key)].get('bugginess') + 1
							}
						else : 
							bugginess[str(key)] = {
								'bugginess' : 1
							}

	return bugginess

def main():

	#repo for test
	path = '/home/vincenzo/eclipse-workspace/compressione'

	repository = Repo(path)

	if not repository.bare : 
		commits = list(repository.iter_commits('master'))
		features_one = instability(commits)
		# features_two = changeComplexity(commits)
		# features_three = bugginess(commits)
		print json.dumps(features_one, sort_keys = True, indent = 4, separators = (',',':'))

if __name__ == '__main__':
	main()