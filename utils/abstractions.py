"""Utility classes for my solution.
"""
from dataclasses import dataclass
import numpy as np
from igraph import *


def get_roads_graph(metrics, debug=True):
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
    return graph, name2vertex


def init_stations(sources, name2vertex=dict()):
    """name2vertex gets modified"""
    columns = ["Date", "Units", "Stand", "WagonModel"]
    stations = dict() # station by name
    max_date = sources.Date.max()
    new_vertices = 0
    station_days = dict()
    for s, data in sources.groupby("Station"):
        s = str(s)
        if s not in name2vertex:
            i = len(name2vertex)
            name2vertex[s] = i
            new_vertices += 1
        else:
            i = name2vertex[s]
        if i not in station_days:
            station_days[i] = []
        for d, u, c, wm in data[columns].values:
            station_days[i].append((d, u, c, wm))
    print(new_vertices)
    graph = Graph()
    graph.add_vertices(len(name2vertex))
    for i, j in name2vertex.items():
        graph.vs[j]['name'] = i
        graph.vs[j]['days'] = station_days.get(j, [])
    return graph


def get_wagon_graph(wagon_mode_compat):    
    wagon_names = np.unique(np.concatenate([
        wagon_mode_compat["NeedWagonModel"].values,
        wagon_mode_compat["CompatibleWagonModel"].values,
    ]))
    graph = Graph()
    graph.add_vertices(len(wagon_names))
    wagon2vertex = {str(x): i for i, x in enumerate(wagon_names)}
    edges = set()
    for need, compat in wagon_mode_compat[["NeedWagonModel", "CompatibleWagonModel"]].drop_duplicates().values:
        need = str(need)
        compat = str(compat)
        u = wagon2vertex[need]
        v = wagon2vertex[compat]
        edges.add((u, v))
    edges = sorted(edges)
    graph.add_edges(edges)
    return graph, wagon2vertex


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