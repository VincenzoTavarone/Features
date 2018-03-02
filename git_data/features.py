import re
from git import Repo, Blob, Tree

def getTreeContent(tree):
	files = {}
	java_file = re.compile(r'.+\.java$')
	for node in tree : 
		if isinstance(node, Tree):
			files.update(getTreeContent(node))
		else : 
			if java_file.match(node.path) : 
				files[str(node.path)] = {
					'obj_id' : str(node),
					'created_at' : 1,
					'last_edit' : 1,
					'modified_at' : []
				}
	return files

def getTreeForCC(tree) : 
	files = {}
	java_file = re.compile(r'.+\.java$')
	for node in tree : 
		if isinstance(node, Tree):
			files.update(getTreeForCC(node))
		else : 
			if java_file.match(node.path) : 
				files[str(node.path)] = {
					'lines' : 0,
					'modifications' : []
				}
	return files

def getTreeForBugginess(tree) : 
	files = {}
	java_file = re.compile(r'.+\.java$')
	for node in tree : 
		if isinstance(node, Tree):
			files.update(getTreeForBugginess(node))
		else : 
			if java_file.match(node.path) : 
				files[str(node.path)] = {
					'bugginess' : 0
				}
	return files

def instability(commits):
	#ricavo il primo commit
	first = commits[len(commits)-1]

	files = getTreeContent(first.tree)

	#bisogna contare anche il primo commit
	internal_clock = 2

	java_file = re.compile(r'.+\.java$')

	for i in xrange(len(commits) - 2, -1, -1):

		for diff in commits[i].diff(first) :
			# print diff.change_type, diff.a_rawpath
			#aggiunto al working tree
			if (diff.change_type == 'D' or diff.a_mode is None) and java_file.match(diff.a_rawpath) : 
				files[str(diff.a_rawpath)] = {
					'obj_id' : '',
					'created_at' : internal_clock,
					'last_edit' : internal_clock,
					'modified_at': []
				}

			#modificato
			if diff.change_type == 'M' and java_file.match(diff.a_rawpath) : 
				if str(diff.a_rawpath) in files : 
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
				else : 
					files[str(diff.a_rawpath)] = {
					'obj_id' : '',
					'created_at' : internal_clock,
					'last_edit' : internal_clock,
					'modified_at': []
				}

			#eliminato dal working tree
			if diff.change_type == 'A' and java_file.match(diff.a_rawpath) : 
				if str(diff.a_rawpath) in files : 
					del files[str(diff.a_rawpath)]

			#rinominato
			if diff.renamed and (java_file.match(diff.a_rawpath) and java_file.match(diff.b_rawpath)) :
				if str(diff.rename_to) in files :
					tmp = files[str(diff.rename_to)]
					del files[str(diff.rename_to)]
					files[str(diff.rename_from)] = tmp
				else : 
					files[str(diff.a_rawpath)] = {
						'obj_id' : '',
						'created_at' : internal_clock,
						'last_edit' : internal_clock,
						'modified_at': []
					}


		internal_clock+=1
		first = commits[i]

	# print json.dumps(files, indent = 4,  separators = (',',':'))
	return files

def changeComplexity(commits):
	
	stats = {}

	java_file = re.compile(r'.+\.java$')

	for i in xrange(len(commits) - 1, -1, -1):
		files =  commits[i].stats.files 
		for key, value in files.iteritems():
			if java_file.match(key) : 
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
	
	bugginess = getTreeForBugginess(commits[0].tree)

	java_file = re.compile(r'.+\.java$')

	#patterns
	close_pattern = re.compile(r'close(s|d)?', re.IGNORECASE)
	bug_pattern = re.compile(r'bug(fix)?', re.IGNORECASE)
	fix_pattern = re.compile(r'fix(es|ed|ing)?', re.IGNORECASE)
	resolve_pattern = re.compile(r'resolve(s|d)?', re.IGNORECASE)
	issue_pattern = re.compile(r'#[1-9][0-9]*', re.IGNORECASE)

	for i in xrange(1, len(commits)) :
		commit = commits[i]
		if 	close_pattern.search(commit.message) or \
			bug_pattern.search(commit.message) or \
			fix_pattern.search(commit.message) or \
			issue_pattern.search(commit.message) or \
			resolve_pattern.search(commit.message) :
				files = commit.stats.files
				for key, value in files.iteritems() : 
					if java_file.match(key) : 
						if str(key) in bugginess : 
							bugginess[str(key)] = {
								'bugginess' : bugginess[str(key)].get('bugginess') + 1
							}

	return bugginess


def change_complexity_fun(commits) :

	stats = {}

	java_file = re.compile(r'.+\.java$')

	stats = getTreeForCC(commits[0].tree)

	for i in xrange(1,len(commits)) : 
		files = commits[i].stats.files
		for key, value in files.iteritems():
			if java_file.match(key) : 
				if str(key) in stats : 
					lines = stats[str(key)].get('lines') + value.get('insertions') - value.get('deletions')
					modifications =  stats[str(key)].get('modifications')
					modifications.append(value.get('lines'))
					stats[str(key)] = {
						'lines' : lines,
						'modifications' : modifications
					}

	return stats