Motivation - Research results
---------------------
The development of *callgraphCA* was motivated by the following research questions:

* RQ1: To what extent is it possible to build evolutionary call-graphs based on software version management information?
* RQ2: What is the relation between structural coupling (on a function level) and the call-graphs software evolution?
* RQ3: Is there a relation between conceptual (non-structural) coupling and the call-graphs software evolution?


Systems under study
---------------------
The empirical approach of our research lead us to develop *callgraphCA* and to evaluate the research questions 
we searched for source code repositories that fulfiled our selection criteria based on a “criterion sampling" [103]. 
We focus our interest in the domains of cyber-physical systems and using the GitHub query search feature applied the following criteria:

* Domain selection: We focus on software that supports cyber-physical systems (CPSs). Since our goal is to identify projects belonging to different CPS domains, we experimented with specific GitHub queries: “IoT", robot, and health. In addition, we also considered homeautomation to explicitly target projects aimed to design and manufacture hardware and software for smart homes.
* Project Popularity: We sort the results by stars to focus on popular repositories. Note that, while selecting projects solely based on stars has been considered inaccurate [104], this selection criterion is enhanced with other criteria.
* Language selection: We selected projects having as object oriented languages main programming languages, mainly Java and C++, since, while querying GitHub for projects belonging to different domains, we realized that most of them use those languages. While the choice of Java can be considered obvious, the selection of C++ projects is pretty consistent with the finding from previous work that shows that most CPS development is performed in C++ program language [105], however, for the results presentation of this pilot project, we concentrate on Java systems.
* Projects size: Due to the scope of the project, we searched for systems that were not larger than 1.5 million LOC.

This is the list of the selected projects and in the Table 'Systems under study':

* Glucosio for Android - An open source diabetes tracker app for controlling blood glucose, HB1AC, Cholesterol, Blood Pressure, Ketones, Body Weight and more for diabetes type 1 and type 2. It can connect to Bluetooth devices for enabling the built of closed loop insulin management. [^1]
* OpenBot - A software stack for an Android smartphones to be connected to robots, that might be self made, and serve as the robot body for the smartphone. It allows complex workloads like following a person and autonomous navigation. [^2]
* Eclipse Concierge - Concierge is a small-footprint implementation of the OSGi Core Specification R5 standard optimized for mobile and embedded devices. [^3]
* GRIP Computer Vision Engine - GRIP (the Graphically Represented Image Processing engine) is an application for rapidly prototyping and deploying computer vision algorithms, primarily for robotics applications. [^4]


Systems under study[^5]

| Project Name              | Main programming language | LOC  | Nr. of commits | Stars | Nr. Tags | Topic             |
|---------------------------|---------------------------|------|----------------|-------|----------|-------------------|
| Glucosio/glucosio-android | java                      | 59K  |          1’166 |   332 |       31 | health automation |
| isl-org/OpenBot           | java                      | 191K |            730 |    2K |        7 | robots            |
| eclipse/concierge         | java                      | 62K  |            502 |    32 |        2 | iot               |
| WPIRoboticsProjects/GRIP  | java                      | 54K  |          1’170 |   334 |       26 | robotic vision    |



[^1]:https://github.com/Glucosio/glucosio-android
[^2]:https://github.com/isl-org/OpenBot
[^3]:https://github.com/eclipse/concierge
[^4]:https://github.com/WPIRoboticsProjects/GRIP
[^5]:According to GitHub data at 06.10.2021





