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


def create_station_graph(sources, name2vertex):
    #print(sources)
    columns = ["Units", "Stand", "WagonModel"]
    graph = Graph()
    graph.add_vertices(len(name2vertex))
    graph.vs['info'] = [dict()]*len(name2vertex)
    for station, row in sources.groupby("Station"):
        # print(station)
        station = str(station)
        i = name2vertex[station]
        wmodels = dict()
        for units, stand, wm in row[columns].values:
            (wm, units, stand)
            if wm not in wmodels:
                wmodels[wm] = []
            wmodels[wm].append((units, stand))
        graph.vs[i]['info'] = wmodels
    return graph


def init_stations(sources, name2vertex):
    """name2vertex gets modified"""
    columns = ["Station", "Date", "Units", "Stand", "WagonModel"]
    for station in np.unique(sources['Station'].values):
        station = str(station)
        if station not in name2vertex:
            index = len(name2vertex)
            name2vertex[station] = index
    graphs = dict()
    for d, arrivals in sources[columns].groupby("Date"):
        graph = create_station_graph(arrivals, name2vertex)
        # print(graph)
        graphs[d] = graph
    return graphs


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


def create_order_graph(orders, name2vertex):
    columns = [
        "OrderNum",
        "Start",
        "Finish",
        #"StartDate",
        "Dur",
        "MinUnit",
        "MaxUnit",
        "Tariff",
        "NeedWagonModel",
        "ShortagePenalty"
    ]
    vertices = np.unique(np.concatenate([
        orders.Start.values,
        orders.Finish.values
    ]))
    for v in vertices:
        v = str(v)
        if v not in name2vertex:
            index = len(name2vertex)
            name2vertex[v] = index
    graph = Graph()
    graph.add_vertices(len(name2vertex))
    edges = []
    for start, finish in orders[["Start", "Finish"]].values:
        start = str(start)
        finish = str(finish)
        u = name2vertex[start]
        v = name2vertex[finish]
        edges.append((u, v))
    # print(edges)
    graph.add_edges(edges)
    graph['order_num'] = orders["OrderNum"].values
    graph['dur'] = orders["Dur"].values
    graph['min_unit'] = orders["MinUnit"].values
    graph['max_unit'] = orders["MaxUnit"].values
    graph['tariff'] = orders["Tariff"].apply(lambda xs: [int(x) for x in xs.split(":")]).values
    graph["wagon_model"] = orders["NeedWagonModel"].values
    graph["penalty"] = orders["ShortagePenalty"].values
    return graph


def build_orders(orders, name2vertex):
    columns = [
        "OrderNum",
        "Start",
        "Finish",
        "StartDate",
        "Dur",
        "MinUnit",
        "MaxUnit",
        "Tariff",
        "NeedWagonModel",
        "ShortagePenalty"
    ]
    graphs = dict()
    for start_date, rows in orders7[columns].groupby("StartDate"):
        graph = create_order_graph(rows, name2vertex)
        graphs[start_date] = graph
    # return start_date, rows
    return graphs


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