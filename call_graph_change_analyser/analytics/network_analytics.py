import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

class NetworkValues:
    def __init__(self,  diameter: int, nrCC: int, degreedistribution, maxDegree: int, nrNodesLCC: int):
        self.diameter = diameter
        self.nrCC = nrCC
        self.degreedistribution = {} if (degreedistribution is None or len(
            degreedistribution) == 0) else degreedistribution
        self.maxDegree = maxDegree
        self.nrNodesLCC = nrNodesLCC

    def __str__(self):
        return("NetworkValues. Diameter: {0}, nrCC: {1}, DD nr degrees: {2}, maxDegree:{3}, nrNodesLCC: {4}".format(self.diameter,
                                                                                                                    self.nrCC, len(self.degreedistribution), self.maxDegree, self.nrNodesLCC))


def getNetworkValues(G, drawGraph = False):    

    maxDegree_values = 0    
    numberNodes = G.number_of_nodes()
    numberEdges = G.number_of_edges()
    
    #draw the graphs
    if(drawGraph and numberNodes < 1500):
        #for line in nx.generate_adjlist(G):
        #    print(line)
        # write edgelist to grid.edgelist
        nx.write_edgelist(G, path="grid.edgelist", delimiter=":")
        # read edgelist from grid.edgelist
        H = nx.read_edgelist(path="grid.edgelist", delimiter=":")

        nx.draw(H, node_color='b', node_size = 9)
        plt.show()

    # save the number of connected components
    #comps = len( [ _ for _ in nx.connected_components(G) ] )
    comps = nx.number_weakly_connected_components(G)

    # save the diameter
    #G.subgraph(c) for c in connected_components(G)
    #LCC =  G.subgraph(max(nx.connected_components(G), key=len))
    #currDiameter = nx.diameter(largest_cc) # diameter is inifinite for disconected/weakly connected graphs
    diameter = max([max(j.values()) for (i,j) in nx.shortest_path_length(G)])

    # size of LCC
    largest_cc = G.subgraph(max(nx.weakly_connected_components(G), key=len))
    nrNodesLCC = largest_cc.number_of_nodes()

    # save the degree distribution
    degreedistribution = nx.degree_histogram(G)

    # get the max degree
    # in the histogram, also the degree 0 is listed
    maxDegree = len(nx.degree_histogram(G))-1

    networkValues = NetworkValues(diameter=diameter, nrCC=comps, degreedistribution=degreedistribution, maxDegree=maxDegree, nrNodesLCC= nrNodesLCC)

    print("G: ", nx.info(G))
    print(networkValues)
    print("LCC: ", nx.info(largest_cc))

    return networkValues, largest_cc
