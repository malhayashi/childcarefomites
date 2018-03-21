import networkx as nx
import numpy.random as nr
import matplotlib.pyplot as pl
import itertools, copy
import random as pr
from scipy.special import comb
from scipy.stats import skew
from fomite_ABM import *

def create_fomite_graph(fomiteList,agentList,m,p):
    G0 = fomite_barabasi_albert_graph(fomiteList,agentList,m)
    G1 = rewire_fomite_graph(G0,p,fomiteList,agentList)
    return G1

def fomite_barabasi_albert_graph(fomiteList,agentList,m):
    G = nx.Graph()

    for fomite in fomiteList:
        G.add_node(fomite.id,bipartite=0)

    for agent in agentList:
        G.add_node(agent.id,bipartite=1)
        nEdges = 0
        possibleFomites = copy.deepcopy(fomiteList)
        while nEdges < m:
            #print nEdges
            proposedNeighbor = pr.choice(possibleFomites)
            k = G.degree(proposedNeighbor.id) + 1
            p = k/float(sum([G.degree(f.id) + 1 for f in fomiteList]))
            if nr.rand() < p:
                G.add_edge(agent.id,proposedNeighbor.id)
                possibleFomites.remove(proposedNeighbor)
                nEdges += 1
    return G

def rewire_fomite_graph(G,p,fomiteList,agentList):
    Gfinal = nx.Graph()
    for fomite in fomiteList:
        Gfinal.add_node(fomite.id,bipartite=0)

    for agent in agentList:
        Gfinal.add_node(agent.id,bipartite=1)

    for edge in G.edges():
        if nr.rand() < p:
            #print edge
            newF = pr.choice(fomiteList)
            newA = pr.choice(agentList)
            #print newF.id, newA.id
            Gfinal.add_edge(newF.id,newA.id)
        else:
            Gfinal.add_edge(*edge)
    return Gfinal

def gen_pseudo_preferential_graph(n, m, p):
    Ginit = nx.barabasi_albert_graph(n,m)
    combos = list(itertools.combinations(Ginit.nodes(),2))
    Gfinal = nx.Graph()
    Gfinal.add_nodes_from(Ginit.nodes())

    for edge in Ginit.edges():
        if nr.rand() < p:
            newEdge = pr.sample(combos,1)[0]
            Gfinal.add_edge(*newEdge)
        else:
            Gfinal.add_edge(*edge)
    return Gfinal

if __name__ == '__main__':
    nAgents = 25
    nFomites = 20
    m = 2
    p = 0
    fomiteList = []
    agentList = []
    for i in range(nFomites):
        fomiteList.append(Fomite(id=str(i)+'f'))
    for i in range(nAgents):
        agentList.append(Agent(id=i))

    G = create_fomite_graph(fomiteList,agentList,m,p)
    color = nx.get_node_attributes(G,'bipartite')
    nx.draw(G,node_color=[color[n] for n in G.nodes()],with_labels=True)
    pl.show()