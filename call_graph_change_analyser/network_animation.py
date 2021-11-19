#%%
import networkx as nx
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import random

#%%
import os
print(os.path.exists('C:\\ffmpeg\\bin'))

#%%
plt.rcParams['animation.ffmpeg_path']='C:\\ffmpeg\\bin\\ffmpeg.exe'



#%%
# Graph initialization
G = nx.Graph()
G.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9])
G.add_edges_from([(1,2), (3,4), (2,5), (4,5), (6,7), (8,9), (4,7), (1,7), (3,5), (2,7), (5,8), (2,9), (5,7)])

#%%
# Animation funciton
def animate(i):
    colors = ['r', 'b', 'g', 'y', 'w', 'm']
    nx.draw_circular(G, node_color=[random.choice(colors) for j in range(9)])
    #fig = plt.gcf()
    #return fig

#%%
nx.draw_circular(G)
fig = plt.gcf()

#%%
# Animator call
anim = animation.FuncAnimation(fig, animate, interval=50, frames=200, blit=False)

#%%
anim.save('growingCoil.mp4', writer = 'ffmpeg', fps = 30) 

# %%
writergif = animation.PillowWriter(fps=30)
anim.save('filename.gif',writer=writergif)


# %%
writer = animation.FFMpegWriter(fps=15, metadata=dict(artist='Me'), bitrate=1800)
anim.save('mv.mp4', writer=writer)
#anim.save('movie.mp4', writer=writer)

# %%
animate(1)

# %%
##############################
import numpy as np


# number of nodes
size = 10

# generate graph
G=nx.complete_graph(size)

# generating input frames here, since my data is too big
# its important that the frames go as input and is not generated
# on the fly
#frame = np.random.random_integers(0, 5, (size, size)) # random ndarray between 0 and 5, length and number of frames = number of nodes in the graph
frame = np.random.randint(0,5,(size,size))

# draw the topology of the graph, what changes during animation
# is just the color
pos = nx.spring_layout(G)
nodes = nx.draw_networkx_nodes(G,pos)
edges = nx.draw_networkx_edges(G,pos)
plt.axis('off')

# pass frames to funcanimation via update function
# this is where I get stuck, since I cannot break
# out of the loop, neither can I read every array of
# the ndarray without looping over it explicitly
def update(i):
    # for i in range(len(frame)):
    # instead of giving frame as input, if I randomly generate it, then it works
    nc = frame[i] # np.random.randint(2, size=200)
    nodes.set_array(nc)
    return nodes,

# output animation; its important I save it
fig = plt.gcf()
ani = animation.FuncAnimation(fig, update, interval=50, frames=range(size), blit=True)
ani.save('crap.gif', writer='imagemagick',  savefig_kwargs={'facecolor':'white'}, fps=1)
# %%
writer = animation.FFMpegWriter(fps=15, metadata=dict(artist='Me'), bitrate=1800)
ani.save('crap2.mp4', writer=writer)

# %%
import random
import pylab
from matplotlib.pyplot import pause
import networkx as nx
pylab.ion()

graph = nx.Graph()
node_number = 0
graph.add_node(node_number, Position=(random.randrange(0, 100), random.randrange(0, 100)))

def get_fig():
    global node_number
    node_number += 1
    graph.add_node(node_number, Position=(random.randrange(0, 100), random.randrange(0, 100)))
    graph.add_edge(node_number, random.choice(list(graph)))
    fig = pylab.figure()
    nx.draw(graph, pos=nx.get_node_attributes(graph,'Position'))
    return fig

num_plots = 50;
pylab.show()

for i in range(num_plots):
    fig = get_fig()
    fig.canvas.draw()
    pylab.draw()
    pause(2)
    pylab.close(fig)
# %%
