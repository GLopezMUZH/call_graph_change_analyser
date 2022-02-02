.. highlight:: python

==================
Analysing new projects
==================

Running the analysis
============

For analysing new projects, or different ranges of the history of a project it is necessary to provide a configuration file and run the following command:

```
python .\callgraphCA.py -init_db_yes -C [PATH_TO_CONFIG_FILE]
```

example:

```
python .\callgraphCA.py -init_db_yes -C ..\project_config\GRIP.pconfig 
```

The arguments for starting the analysis are:

* -C [PATH_TO_CONFIG_FILE]: path where the configuration file is saved
* -init_db_yes: Optional  this option drops the previous data on the database and starts from scratch



Configuration file
============

In the configuration file, the following arguments must be set:
Project specifications:

* proj_name: name of the project, this name will be set in the folders and saved databases. 
* proj_lang: currently Java, with the possibility to extend it to C++ or C and other languages. 

Data sources and repository paths:

* repo_url: the https url path where the repository can be accessed
* path_to_proj_data_dir: target path where the analytics data will be saved
* srctrl_orig_config_file_path: source path where the configuration file for parsing the source graph


The following arguments are optional:
System changes time frame for analysis:
Only one kind of time setting can be used, either tags, commits or dates. When using tags or commits, both from and to values must be set. When using dates, it is possible to only set the since_date, the analysis will be done from the changes starting from the given *since_date* to either the *to_date* or the latest date in the repository.

* from_tag
* to_tag
* since_date
* to_date
* from_commit
* to_commit

Project specifications:

* repo_type: currently supporting only Git repositories
* only_in_branch: the default branch is “master”, in case the user needs to analyze another branch, this branch name has to be specified
* save_cache_files: [True|False], default False
* delete_cg_src_db: [True|False], default False
* cache_files_dir_path: target path to save cache files if persisted outside the container
