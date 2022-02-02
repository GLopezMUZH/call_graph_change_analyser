.. _intro_toplevel:

==================
Overview
==================

call_graph_change_analyser is a Python tool that helps the understanding of software evolution. 
It is based on information extracted from any Git repository and method and function call-graphs.


Requirements
============

* `Python`_ 3.9
* `Git`_

.. _Python: https://www.python.org
.. _Git: https://git-scm.com/


Run
============
Ubuntu

``python .\app.py -init_db_yes -C ..\project_config\project_conf_file.pconfig``

``test_app_ubuntu.py -init_db_yes -P proj_name -from_tag tag -to_tag tag``

proj_name -> JKQtPlotter or PX4-Autopilot

eg. ``python .\app.py -init_db_yes -P JKQtPlotter -from_tag 'v2019.11.0' -to_tag 'v2019.11.3'``


Windows

``python .\app.py -init_db_yes -C ..\project_config\glucosio_small.pconfig``
