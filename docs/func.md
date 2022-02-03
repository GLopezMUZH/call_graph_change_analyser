Functionality
---------------------
The main purpose of *callgraphCA* is to generate data to suppor the analysis and understanding of the evolution of softwrare projects. The major areas of analysis are: change proneness, change coupling both logical and structural, call graph evolution and change coupling within the call graphs.

The first process is the loading of the data from the version control repository. From this process, the information regarding the code changes that happened in each commit event on the repository are persisted in databases, additionally the source code structure is analyzed for each commit and the corresponding call graph is generated.  

After runing *callgraphCA* to analyze a selected project [^1] . There are two main databases that contain the necessary information the *analytics* and the *call_graph* database. The databases are saved in the folder `project_results`, inside a folder with the project name that is automatically generated when the analysis starts.

Database model
--------------
The main tables in the *analytics* database are:
* git_commit - list of all the commits that contained changes in source files
* file_commit - list of the files that were changed per commit
* function_commit - list of the functions that were changed per commit, having a reference to the file they belong
* file_import - list of imports that each file contains
* cg_statistics - statistics obtained from analyzing the changes in the call graph for each commit

The *call_graph* database contains one table for each commit that was analyzed. The callgraph is represented by edges, containing the source and target node fields (id, file_path, function_name).

The main fields that join the tables are the *commit_hash*, *file_path*, *function_name*.

Based on this databases *callgraphCA* supports the user with analytic libraries and example notebooks for an easy analysis of the projects. The following is a list of functionalities that are included in the libraries, but based on the generated databases, additional analysis can be executed by the user. 

Change proneness
-----------------



[^1]:https://github.com/GLopezMUZH/call_graph_change_analyser/blob/main/docs/tutorial.md

