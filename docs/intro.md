Overview
---------------------

call_graph_change_analyser is a Python tool that helps the understanding of software evolution. 
It is based on information extracted from any Git repository and method and function call-graphs.


Requirements
---------------------

- python >= 3.9[^1]
- [Git][^2]
- [srcML][^3]
- [sourceTrail][^4]

[^1]: https://www.python.org
[^2]: https://git-scm.com/
[^3]: https://www.srcml.org/
[^4]: https://github.com/CoatiSoftware/Sourcetrail


Run
---------------------
Ubuntu

``python .\app.py -init_db_yes -C ..\project_config\project_conf_file.pconfig``

``test_app_ubuntu.py -init_db_yes -P proj_name -from_tag tag -to_tag tag``

proj_name -> JKQtPlotter or PX4-Autopilot

eg. ``python .\app.py -init_db_yes -P JKQtPlotter -from_tag 'v2019.11.0' -to_tag 'v2019.11.3'``


Windows

``python .\app.py -init_db_yes -C ..\project_config\glucosio_small.pconfig``
