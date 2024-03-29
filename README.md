# *callgraphCA*
*callgraphCA* is a prototype tool to help the understanding of software evolution based on information extracted from Git repositories. It models change proneness, change-coupling, and call-graph evolution. It was developed as a base for the author's Master Thesis in Informatics Data Science at UZH.

## Table of Contents

Table of Contents
*	[*callgraphCA* functionality](README.md#callgraphCA-functionality)
    *	[Contributions](README.md#contributions)
*	[*callgraphCA* architecture](https://github.com/GLopezMUZH/call_graph_change_analyser/blob/main/docs/arch.md)
* [Installation](README.md#Installation)
    * [Prerequisites](README.md#Prerequisites)
    *	[Memory requirements](README.md#Memory-requirements)
* [Quick-Start](README.md#Quick-Start)
    *	[Replication packages](README.md#Replication-packages)
*	[Quick notebooks](https://github.com/GLopezMUZH/call_graph_change_analyser/tree/main/notebooks)
*	[How to analyze new projects](https://github.com/GLopezMUZH/call_graph_change_analyser/blob/main/docs/tutorial.md)
*	[Empirical research](README.md#Empirical-research)
    * [Motivation](https://github.com/GLopezMUZH/call_graph_change_analyser/blob/main/docs/research_motivation.md)
    * [Results](https://github.com/GLopezMUZH/call_graph_change_analyser/blob/main/docs/research_results.md)
*	[License](README.md#License)

--------------
## *callgraphCA* functionality
The main purpose of *callgraphCA* is to generate data to support the analysis and understanding of the evolution of software projects. The major areas of analysis are: change proneness, change coupling both logical and structural, call graph evolution, and change coupling within the call graphs.
In the [functionality](https://github.com/GLopezMUZH/call_graph_change_analyser/blob/main/docs/func.md) section, we explain how these areas of analysis are covered, how the example notebooks can be used to understand the systems under study, and what support our analytic libraries provide.
### Contributions
*callgraphCA* presents novel functionality with the focus of producing user-friendly processing and overview metrics that:

- combine graph analysis with code change analysis
- analyze the system’s call graph of the changed functions
- can be used as a proxy to measure change coupling of subsequent software
- changes is within the call graph and outside of it
- can be computed at different levels of granularity (commit or release tags, file, function, and call graph level)


## Quick-Start

### Replication packages
The results from the analysis of four systems ( Glucosio/glucosio-android[^6] , isl-org/OpenBot[^7], eclipse/concierge[^8], and WPIRoboticsProjects/GRIP[^9]) is available as a replication package in the following link:

https://zenodo.org/record/5923589#.YfuKsfvMIRQ

[^6]:https://github.com/Glucosio/glucosio-android
[^7]:https://github.com/isl-org/OpenBot
[^8]:https://github.com/eclipse/concierge
[^9]:https://github.com/WPIRoboticsProjects/GRIP

## Installation
- You can clone the OpenBot repository from GitHub with the following command:
    ```bash
    git clone https://github.com/GLopezMUZH/call_graph_change_analyser.git
    ```
- You can fork the OpenBot repository and then clone your local copy.
- You can download the repository as a [zip file](https://github.com/GLopezMUZH/call_graph_change_analyser/archive/refs/tags/v0.1.zip) and extract it into a folder of your choice.


### Prerequisites
The following tools need to be installed in order to use callgraphCA:

- python >= 3.9
- [Git][1]
- [srcML][2]
- [sourceTrail][3]

[1]: https://git-scm.com/
[2]: https://www.srcml.org/
[3]: https://github.com/CoatiSoftware/Sourcetrail

### Memory requirements
When analyzing complete histories of Java systems with over 50K LOC and over 500 commits, the two generated databases have sizes between 25MB and 1.3GB. In Ubuntu, the `project_result` folder for Glucosio/glucosio-android had a size of 1.7GB.

### Empirical research
In the [research motivation](https://github.com/GLopezMUZH/call_graph_change_analyser/blob/main/docs/research_motivation.md) section, we explain the goals and research questions that drive our research and the development of *callgraphCA*. In [research results](https://github.com/GLopezMUZH/call_graph_change_analyser/blob/main/docs/research_results.md), we present the outcomes of our research and how the system supports the analysis of software projects. 

### License
-----------------
Copyright 2021 Gabriela E. López Magaña

Licensed under the GNU Lesser General Public License v2.1 (the "License"); You may obtain a copy of the License at

https://github.com/GLopezMUZH/call_graph_change_analyser/blob/main/LICENSE

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
