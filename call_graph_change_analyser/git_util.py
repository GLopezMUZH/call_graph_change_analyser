import git
import logging
import os


def download_initial_cache_source(repo_url, path_to_cache_src_dir, only_in_branch):
    if not os.path.exists(os.path.dirname(path_to_cache_src_dir)):
        os.makedirs(os.path.dirname(path_to_cache_src_dir))
        logging.info("Start git clone")

    if os.path.exists(os.path.join(path_to_cache_src_dir,'.git')):
        logging.info("Reset cached source to current state")
        g = git.Git(path_to_cache_src_dir)
        g.checkout(only_in_branch)
    else:
        logging.error("path_to_cache_src_dir exist but not .git folder")
        #stopwatch = Stopwatch()
        #stopwatch.start()
        git.Repo.clone_from(repo_url, path_to_cache_src_dir)
        #stopwatch.stop()
        #print(stopwatch.elapsed) 
        #print(stopwatch.report())
        logging.info("End git clone")

def reset_git_to_hash(repo_url: str, path_to_cache_src_dir: str, commit_hash):
    if os.path.exists(os.path.join(path_to_cache_src_dir,'.git')):
        logging.info("Reset cached source to current state")
        g = git.Git(path_to_cache_src_dir)
        g.checkout(commit_hash)
    else:
        logging.error("path_to_cache_src_dir exist but not .git folder")
        #stopwatch = Stopwatch()
        #stopwatch.start()
        g = git.Repo.clone_from(repo_url, path_to_cache_src_dir)
        g.checkout(commit_hash)
        #stopwatch.stop()
        #print(stopwatch.elapsed) 
        #print(stopwatch.report())
        logging.info("End git clone")
  