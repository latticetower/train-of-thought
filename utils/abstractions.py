"""Utility classes for my solution.
"""
from dataclasses import dataclass
import numpy as np
from igraph import *


def get_roads_graph(metrics, debug=False):
    station_names = np.unique(
        np.concatenate([
            metrics.From.values,
            metrics.To.values
        ]))
    stations = []
    name2vertex = {str(x): i for i, x in enumerate(station_names)}
    graph = Graph()
    graph.add_vertices(len(station_names))
    columns = ["From", "To", "Distance", "Time", "Group", "PriceUnit"]
    edges = []
    edges2index = dict()
    info = dict()
    distances = dict()
    times = dict()
    for j, (s, e, d, t, gr, pu) in enumerate(metrics[columns].drop_duplicates().values):
        s = str(s)
        e = str(e)

        u = name2vertex[s]
        v = name2vertex[e]
        graph.vs[u]['name'] = s
        graph.vs[v]['name'] = e
        # selection = graph.es.select(_from=s, _to=e)
        # if len(selection) < 1:
        if (u, v) not in edges2index:
            index = len(edges)
            edges2index[(u, v)] = index
            edges.append((u, v))
            info[index] = []
        else:
            index = edges2index[(u, v)]
        info[index].append((gr, pu))
        distances[index] = d
        times[index] = t
        #k = graph.add_edge(u, v)#, distance=d, time=t)
        if debug:
            if j%50000==0:
                print(j)
    graph.add_edges(edges)#, distance=d, time=t)
    for i, v in info.items():
        graph.es[i]['info'] = v
        graph.es[i]['distance'] = distances[i]
        graph.es[i]['time'] = times[i]
    return graph


def init_stations(sources):
    columns = ["Station", "Date", "Units", "Stand", "WagonModel"]
    stations = dict() #station by name
    for station, d, u, c, wm in sources[columns].values:
        st = Station(name=str(station))
    pass


@dataclass
class Station:
    """stores station information
    """
    name: str = "unknown" # numeric representation
    new_arrivals = dict()
    # unit_price: float
    # quantity_on_hand: int = 0
    # def total_cost(self) -> float:
    #     return self.unit_price * self.quantity_on_hand

    def reset(self): 
        pass


class World:
    def __init__(self):
        pass