"""Utility classes for my solution.
"""
import numpy as np
from igraph import *


def get_roads_graph(metrics, debug=True):
    station_names = np.unique(
        np.concatenate([
            metrics.From.values,
            metrics.To.values
        ]))
    stations = []
    station2vertex = {str(x): i for i, x in enumerate(station_names)}
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

        u = station2vertex[s]
        v = station2vertex[e]
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
    return graph, station2vertex


def create_station_graph(sources, station2vertex, wagon2vertex=None):
    #print(sources)
    columns = ["Units", "Stand", "WagonModel"]
    graph = Graph()
    graph.add_vertices(len(station2vertex))
    graph.vs['info'] = [dict()]*len(station2vertex)
    for station, row in sources.groupby("Station"):
        # print(station)
        station = str(station)
        i = station2vertex[station]
        wmodels = dict()
        for units, stand, wm in row[columns].values:
            # (wm, units, stand)
            wm = str(wm)
            if wagon2vertex is not None:
                wm = wagon2vertex[wm]
            if wm not in wmodels:
                wmodels[wm] = []
            wmodels[wm].append((units, stand))
        graph.vs[i]['info'] = wmodels
    return graph


def init_stations(sources, station2vertex, wagon2vertex=None):
    """station2vertex gets modified"""
    columns = ["Station", "Date", "Units", "Stand", "WagonModel"]
    for station in np.unique(sources['Station'].values):
        station = str(station)
        if station not in station2vertex:
            index = len(station2vertex)
            station2vertex[station] = index
    if wagon2vertex is not None:
        for wagon in np.unique(sources['WagonModel'].values):
            wagon = str(wagon)
            if wagon not in wagon2vertex:
                index = len(wagon2vertex)
                wagon2vertex[wagon] = index
    graphs = dict()
    for d, arrivals in sources[columns].groupby("Date"):
        graph = create_station_graph(arrivals, station2vertex, wagon2vertex)
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


def create_order_graph(orders, station2vertex, wagon2vertex):
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
    for wm in np.unique(orders.NeedWagonModel.values):
        wm = str(wm)
        if wm not in wagon2vertex:
            index = len(wagon2vertex)
            wagon2vertex[wm] = index
    vertices = np.unique(np.concatenate([
        orders.Start.values,
        orders.Finish.values
    ]))
    for v in vertices:
        v = str(v)
        if v not in station2vertex:
            index = len(station2vertex)
            station2vertex[v] = index
    graph = Graph()
    graph.add_vertices(len(station2vertex))
    edges = []
    for start, finish in orders[["Start", "Finish"]].values:
        start = str(start)
        finish = str(finish)
        u = station2vertex[start]
        v = station2vertex[finish]
        edges.append((u, v))
    # print(edges)
    graph.add_edges(edges)
    graph.es['order_num'] = orders["OrderNum"].values
    graph.es['dur'] = orders["Dur"].values
    graph.es['min_unit'] = orders["MinUnit"].values
    graph.es['max_unit'] = orders["MaxUnit"].values
    graph.es['tariff'] = orders["Tariff"].apply(lambda xs: [int(x) for x in xs.split(":")]).values
    graph.es["wagon_model"] = orders["NeedWagonModel"].apply(lambda x: wagon2vertex[str(x)]).values
    graph.es["penalty"] = orders["ShortagePenalty"].values
    return graph


def build_orders(orders, station2vertex, wagon2vertex):
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
    for start_date, rows in orders[columns].groupby("StartDate"):
        graph = create_order_graph(rows, station2vertex, wagon2vertex)
        graphs[start_date] = graph
    # return start_date, rows
    return graphs



class Wagon:
    def __init__(self, index=0, wm_index=0, station=-1):
        self.index = index
        self.wm_index = wm_index
        self.station = station

    def set_station(self, station):
        self.station = station



class Station:
    def __init__(self, name="", index=0, stay_cost=0):
        self.name = name
        self.index = index
        self.stay_cost = stay_cost
        self.wagons = []

    def set_wagons(self, wagons):
        self.wagons = wagons

    def append_wagons(self, wagons):
        self.wagons.extend(wagons)


class Route:
    # start: int = 0
    # finish: int = 0
    # arrival day -> (start_day, wagon.index, cost)
    def __init__(self):
        self.arrivals = dict()
        self.history = dict()

    def at(self, day):
        if day in self.arrivals:
            data = self.arrivals.pop(day)
            self.history[day] = data
            for x in data:
                yield x


class MoveAction:
    def __init__(self, end_station=-1, order_num=""):
        self.end_station = end_station
        self.order_num = order_num


class WorldModelEnv:
    def __init__(self, orders=None, wagon_mode_compat=None, sources=None, metrics=None):
        self.roads_graph, self.station2vertex = get_roads_graph(metrics, debug=False)
        # self.roads_graph = roads_graph
        # self.station2vertex = station2vertex
        self.wagon_graph, self.wagon2vertex = get_wagon_graph(wagon_mode_compat)
        # self.wagon_graph = wagon_graph
        # self.wagon2vertex = wagon2vertex
        self.station_graph = init_stations(sources, self.station2vertex, self.wagon2vertex)
        self.orders = build_orders(orders, self.station2vertex, self.wagon2vertex)
        self.reset()

    def reset(self):
        "reset everything computed"
        self.moves_history = []
        self.wagons = []
        self.world_state = self.init_world_graph()
        self.current_step = 0

    def new_wagon(self, wm_index, station=None):
        new_index = len(self.wagons)
        w = Wagon(index=new_index, wm_index=wm_index)
        w.set_station(station)
        self.wagons.append(w)
        return w.index

    def init_world_graph(self):
        graph = Graph()
        graph.add_vertices(len(self.station2vertex))
        for station_name, i in self.station2vertex.items():
            station = Station(index=i, name=station_name)
            graph.vs[i]['info'] = station
        self.spawn_wagons(graph, step=0)
        # print(station.wagons)
        # graph.vs[i]['info'] = station
        edges = self.roads_graph.get_edgelist()
        graph.add_edges(edges)
        graph.es['route'] = [Route() for k in range(len(edges))]
        return graph

    def spawn_wagons(self, graph, step=0):
        # cost=0
        arrivals_graph = self.station_graph.get(step, Graph())
        for i, v in enumerate(arrivals_graph.vs):
            stay_cost = 0
            wagons = []
            for wm, data in v['info'].items():
                for n, cost in data:
                    stay_cost = cost
                    new_wagons = [
                        self.new_wagon(wm_index=wm, station=i)
                        for k in range(n)
                    ]
                    wagons.extend(new_wagons)
            station = graph.vs[i]['info']
            station.stay_cost = stay_cost
            # print(len(wagons))
            station.append_wagons(wagons)

    def update_world_graph(self, wagon_moves):
        self.spawn_wagons(self.world_state, step=self.current_step + 1)

    @property
    def available_orders(self):
        return self.orders.get(self.current_step, Graph())

    def step(self, actions):
        """Move to the next day, taking orders related to wagon placements.

        Returns reward for the step and computes different reward components, 
        which are stored in separate class. Also updates the world state graph.

        # 0. validate (? ignore!)
        # 1. add moves, move these wagons from stations to routes, compute
        tariff
        # 2. inc current day
        # 3. compute costs for the wagons which are at the stations
        # 4. check for the newly arrived wagons: move them to destination
        stations, mark order as done, add profit

        """
        self.update_world_graph(wagon_moves)
