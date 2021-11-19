#%%
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import pandas
import sqlite3

import sys, os
import datetime

from utils_sql import get_graph_edges
from models import ProjectPaths


def print_graph_stats(G):
    print("Number of nodes: ", nx.number_of_nodes(G))
    print("Number of edges: ", nx.number_of_edges(G))
    print("Density: ", nx.density(G))
    # print("Degree histogram: ", nx.degree_histogram(G))
    plt.plot(nx.degree_histogram(G))
    plt.show()

def get_call_graph(proj_paths: ProjectPaths):
    df = get_graph_edges(proj_paths.path_to_project_db)
    #g = nx.DiGraph((x, y, {'weight': v}) for (x, y), v in Counter(EDGES).items())
    G=nx.from_pandas_edgelist(df, 'source_node_id', 'target_node_id')
    return G

    #nx.draw(G)

def get_all_node_paths(G, node_id = int):
    p = nx.shortest_path(G, source=node_id)


#%%



# %%
"""

import networkx as nx

from bokeh.io import output_file, show
from bokeh.models import (BoxZoomTool, Circle, HoverTool,
                          MultiLine, Plot, Range1d, ResetTool)
from bokeh.palettes import Spectral4
from bokeh.plotting import from_networkx

# Prepare Data
G = nx.karate_club_graph()

SAME_CLUB_COLOR, DIFFERENT_CLUB_COLOR = "black", "red"
edge_attrs = {}

for start_node, end_node, _ in G.edges(data=True):
    edge_color = SAME_CLUB_COLOR if G.nodes[start_node]["club"] == G.nodes[end_node]["club"] else DIFFERENT_CLUB_COLOR
    edge_attrs[(start_node, end_node)] = edge_color

nx.set_edge_attributes(G, edge_attrs, "edge_color")

# Show with Bokeh
plot = Plot(width=400, height=400,
            x_range=Range1d(-1.1, 1.1), y_range=Range1d(-1.1, 1.1))
plot.title.text = "Graph Interaction Demonstration"

node_hover_tool = HoverTool(tooltips=[("index", "@index"), ("club", "@club")])
plot.add_tools(node_hover_tool, BoxZoomTool(), ResetTool())

graph_renderer = from_networkx(G, nx.spring_layout, scale=1, center=(0, 0))

graph_renderer.node_renderer.glyph = Circle(size=15, fill_color=Spectral4[0])
graph_renderer.edge_renderer.glyph = MultiLine(line_color="edge_color", line_alpha=0.8, line_width=1)
plot.renderers.append(graph_renderer)

output_file("interactive_graphs.html")
show(plot)

"""