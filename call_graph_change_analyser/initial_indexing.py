import os
import pandas as pd
from itertools import islice
import sqlite3
import git
import logging
#from stopwatch import Stopwatch

from models import ProjectPaths


def download_initial_cache_source(repo_url, path_to_cache_src_dir, only_in_branch):
    if not os.path.exists(os.path.dirname(path_to_cache_src_dir)):
        os.makedirs(os.path.dirname(path_to_cache_src_dir))
        logging.info("Start git clone")
    else:
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



def execute_intitial_indexing(proj_paths: ProjectPaths):
    create_file_pkg_table(proj_paths=proj_paths)

def create_file_pkg_table(proj_paths: ProjectPaths):
    f_list = []
    local_src_dir = os.path.normpath(proj_paths.get_path_to_cache_src_dir())
    for dirs, subdirs, files in os.walk(local_src_dir):
        for f in files:
            if '.java' in f:
                f_full_path = os.path.join(dirs, f)
                f_path = os.path.relpath(f_full_path, local_src_dir)
                f_dir_path = os.path.dirname(f_path)

                with open(f_full_path, "r", encoding='utf-8') as codefile:
                    not_found = True
                    while not_found:
                        try:
                            lines = list(islice(codefile, 100))
                            for code_line in lines:
                                if (code_line.lstrip()).startswith("package "):
                                    f_pkg = code_line[8:len(code_line.rstrip())].replace(';', '')
                                    f_list.append([f, f_dir_path, f_path, f_pkg])
                                    not_found = False
                            if not lines:
                                break
                        except UnicodeEncodeError:
                            not_found = False


    df = pd.DataFrame(f_list)
    df.columns = ['file_name', 'file_dir_path', 'file_path','file_pkg']
    conn = sqlite3.connect(proj_paths.get_path_to_project_db())
    cur = conn.cursor()

    try:
        cur.execute('''DROP TABLE file_pkg''')
    except Exception as error:
        print("file_pkg ", error)

    df.to_sql('file_pkg', conn, if_exists='replace', index=False)
    append_class_pkg(proj_paths)


def append_class_pkg(proj_paths: ProjectPaths):
    conn = sqlite3.connect(proj_paths.get_path_to_project_db())
    sql_statement = """SELECT * FROM file_pkg"""
    df = pd.read_sql_query(sql_statement, conn)
    df['class_pkg'] = df.apply(lambda row: ''.join([row.file_pkg, '.', row.file_name.replace('.java','')]), axis=1)
    df.to_sql('file_pkg', conn, if_exists='replace', index=False)
