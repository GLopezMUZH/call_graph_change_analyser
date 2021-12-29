#%%
import subprocess
from subprocess import *
from git import Repo
import os

import time
from stopwatch import Stopwatch, profile


#%%
def sctWrapper(cgdbpath, *args):
    print("Exists dir: ", os.path.exists(cgdbpath))
    file_path = os.path.join(cgdbpath, args[len(args)-1])
    print("File path: ",file_path)
    print("Exists file: ", args[len(args)-1], os.path.exists(file_path))


    process = Popen(['sourcetrail', 'index']+list(args), stdout=PIPE, stderr=PIPE, cwd=cgdbpath, shell=True)
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

#%%
def parse_source_for_call_graph(path_to_cache_src_dir):
    curr_src_args_init = [
    '--full', 'call_graph_change_analyser.srctrlprj' ]
    curr_src_args = [
        ' call_graph_change_analyser.srctrlprj' ]

    result = sctWrapper(path_to_cache_src_dir, *curr_src_args)