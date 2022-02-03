# *callgraphCA*
*callgraphCA* is a prototype tool to help the understanding of software evolution based on information extracted from Git repositories. It models change proneness, change coupling and call-graph evolution.

## Table of Contents

Table of Contents
*	[*callgraphCA* functionality](README.md#callgraphCA-functionality)
    *	[Contributions](README.md#contributions)
*	[*callgraphCA* architecture](https://github.com/GLopezMUZH/call_graph_change_analyser/blob/main/docs/arch.md)
* [Installation](README.md#Installation)
    * [Prerequisites](README.md#Prerequisites)
* [Quick-Start](README.md#Quick-Start)
    *	Pre-generated data
*	Quick notebooks
*	[How to analyze new projects](https://github.com/GLopezMUZH/call_graph_change_analyser/blob/main/docs/tutorial.md)
*	Memory requirements
*	How to use *callgraphCA* as a dockers container (optional)
*	Empirical research
    * [Motivation](https://github.com/GLopezMUZH/call_graph_change_analyser/blob/main/docs/research_motivation.md)
    * [Results](https://github.com/GLopezMUZH/call_graph_change_analyser/blob/main/docs/research_results.md)
*	[License](README.md#License)

--------------
## *callgraphCA* functionality
The main purpose of *callgraphCA* is to generate data to suppor the analysis and understanding of the evolution of softwrare projects. The major areas of analysis are: change proneness, change coupling both logical and structural, call graph evolution and change coupling within the call graphs.
In the [functionality](https://github.com/GLopezMUZH/call_graph_change_analyser/blob/main/docs/func.md) section, we explain how this areas of analysis are covered, and how the example notebooks can be used to understand the systems under study, and what is the support that our analytic libraries provide.
### Contributions


## Quick-Start


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


### License
-----------------
Copyright 2021 Gabriela E. López Magaña

Licensed under the GNU Lesser General Public License v2.1 (the "License"); You may obtain a copy of the License at

https://github.com/GLopezMUZH/call_graph_change_analyser/blob/main/LICENSE

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
