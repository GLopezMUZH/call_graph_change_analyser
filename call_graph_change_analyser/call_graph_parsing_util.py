# %%
import subprocess
from subprocess import *
from git import Repo
import os
from shutil import copy as shutil_copy

import time
from stopwatch import Stopwatch, profile


# %%
def sctWrapper(cgdbpath, *args):
    print("Exists dir: ", os.path.exists(cgdbpath))
    file_path = os.path.join(cgdbpath, args[len(args)-1])
    print("File path: ", file_path)
    print("Exists file: ", args[len(args)-1], os.path.exists(file_path))

    process = Popen(['sourcetrail', 'index']+list(args),
                    stdout=PIPE, stderr=PIPE, cwd=cgdbpath, shell=True)
    ret = []
    while process.poll() is None:
        line = process.stdout.readline()
        if line != '' and line.endswith(b'\n'):
            ret.append(line[:-1])
    stdout, stderr = process.communicate()
    ret += stdout.split(b'\n')
    if stderr != '':
        ret += stderr.split(b'\n')
    ret.remove(b'')
    return ret

# %%


def parse_source_for_call_graph(proj_name: str, path_to_cache_cg_dbs: str, commit_hash: str):
    proj_srctrl_config_file_name = proj_name + \
        '.srctrlprj'  # original file was copied to this path
    proj_commit_srctrl_config_file_name = proj_name + commit_hash + '.srctrlprj'

    make_config_file_copy(orig_file_dir=path_to_cache_cg_dbs, orig_file_name=proj_srctrl_config_file_name,
                          target_file_dir=path_to_cache_cg_dbs, target_file_name=proj_commit_srctrl_config_file_name)

    # creates srctrl db for the commit
    curr_src_args = [proj_commit_srctrl_config_file_name]
    result = sctWrapper(path_to_cache_cg_dbs, *curr_src_args)


def make_config_file_copy(orig_file_dir, orig_file_name, target_file_dir, target_file_name):
    source_file_path = os.path.join(orig_file_dir, orig_file_name)
    # print(source_file_path)
    # print(os.path.exists(source_file_path))
    target_file_path = os.path.join(target_file_dir, target_file_name)
    shutil_copy(source_file_path, target_file_path)
    # print(target_file_path)
    # print(os.path.exists(target_file_path))
