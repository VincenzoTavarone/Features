import re
from git import Repo, Blob, Tree

def stats_files(commits) :

	stats = {
		"adds" : 0,
		"del"  : 0,
		"renamed" : 0,
		"modified" : 0
	}

	first = commits[-1]

	java_file = re.compile(r'.+\.java$')

	for i in xrange(len(commits) - 2, -1, -1):
		for diff in commits[i].diff(first) :
			if (diff.change_type == 'D' or diff.a_mode is None) and java_file.match(diff.a_rawpath) :
				stats["adds"] = stats.get("adds") + 1
			elif diff.change_type == 'M' and java_file.match(diff.a_rawpath) : 
				stats["modified"] = stats.get("modified") + 1
			elif diff.change_type == 'A' and java_file.match(diff.a_rawpath) : 
				stats["del"] = stats.get("del") + 1
			elif diff.renamed and (java_file.match(diff.a_rawpath) and java_file.match(diff.b_rawpath)) :
				stats["renamed"] = stats.get("renamed") + 1
		first = commits[i]

	return stats

def stats_bugs(commits):
	
	bug = 0

	java_file = re.compile(r'.+\.java$')

	#patterns
	close_pattern = re.compile(r'close(s|d)?', re.IGNORECASE)
	bug_pattern = re.compile(r'bug(fix)?', re.IGNORECASE)
	fix_pattern = re.compile(r'fix(es|ed|ing)?', re.IGNORECASE)
	resolve_pattern = re.compile(r'resolve(s|d)?', re.IGNORECASE)
	issue_pattern = re.compile(r'#[1-9][0-9]*', re.IGNORECASE)

	for commit in commits : 
		if 	close_pattern.search(commit.message) or \
			bug_pattern.search(commit.message) or \
			fix_pattern.search(commit.message) or \
			issue_pattern.search(commit.message) or \
			resolve_pattern.search(commit.message) :
				bug+=1

	return bug


def main() : 

	path = '/home/vincenzo/Scrivania/dataset/umlet'

	repository = Repo(path)

	if not repository.bare : 
		commits = list(repository.iter_commits('master'))
		files = stats_files(commits)
		print files

if __name__ == '__main__':
	main()