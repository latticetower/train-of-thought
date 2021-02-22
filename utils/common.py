"""Basic classes"""

class Order(object):
    def __init__(self, start_point, end_point, start_date, wagons, wagon_type, cost_per_wagon, days, priority):
        self.start_point = start_point
        self.end_point = end_point
        self.start_date = start_date
        self.wagons = wagons
        self.wagon_type = wagon_type
        self.cost_per_wagon = cost_per_wagon
        self.days = days
        self.priority = priority

    def total_profit(self):
        return self.wagons * self.cost_per_wagon


class Wagon(object):
    class_counter = 0

    def __init__(self, type_of_wagon, current_station, occupied, free_day):
        self.type_of_wagon = type_of_wagon
        self.occupied = occupied
        self.current_station = current_station
        self.free_day = free_day
        self.index = Wagon.class_counter
        Wagon.class_counter += 1

    def get_day_cost(self, stay_stations):
        if self.occupied:
            return 0
        else:
            return stay_stations[self.current_station]

class OrderManager(object):
    def __init__(self):
        self.orders = []
    
    def add_order(self, order):
        self.orders.append(order)
    

class WagonManager(object):
    def __init__(self):
        self.wagons_by_id = {}
        self.wagons_by_loc = {}
        self.wagons_by_loc_rev = {}

    def update_wagon(self, wagon, end_point, end_date):
        self.wagons_by_id[wagon].occupied = True
        self.wagons_by_loc[str(self.wagons_by_id[wagon].current_station)].remove(wagon)
        if str(end_point) not in self.wagons_by_loc:
            self.wagons_by_loc[str(end_point)] = set()      
        self.wagons_by_loc[str(end_point)].add(wagon)
        self.wagons_by_loc_rev[wagon] = str(end_point)
        self.wagons_by_id[wagon].current_station = end_point
        self.wagons_by_id[wagon].free_day = end_date


    def add_wagon(self, wagon):
        self.wagons_by_id[wagon.index] = wagon
        if str(wagon.current_station) not in self.wagons_by_loc:
            self.wagons_by_loc[str(wagon.current_station)] = set()     
        self.wagons_by_loc[str(wagon.current_station)].add(wagon.index) 
        self.wagons_by_loc_rev[wagon.index] = wagon.current_station
    
    def wagon_number(self):
        return len(self.wagons_by_id)


class Strategy(object):
    def __init__(self, order_manager, wagon_manager, graph, compability_model, name2vertex, stale_prices, stale_moves):
        self.order_manager = order_manager
        self.wagon_manager = wagon_manager
        self.graph = graph
        self.compability_model = compability_model
        self.total_cost = 0
        self.current_order = 0
        self.djkstra = graph.shortest_paths_dijkstra(weights="time")
        self.name2vertex = name2vertex
        self.total_orders = {}
        self.bad_orders = {}
        self.wagons_per_cat = {}
        self.profit_per_cat = {}

        self.total_profit = 0
        self.stale_stop = 0
        self.stale_move = 0
        self.stale_prices = stale_prices
        self.stale_moves = stale_moves
        self.stale_moves_num = 0
        self.inv_name2vertex = {v: k for k, v in name2vertex.items()}


    def are_compatible(self, type1, type2):
        return (str(type1) + "_" + str(type2)) in self.compability_model or (str(type2) + "_" + str(type1)) in self.compability_model or type1 == type2

    def start_order(self, order):
        if order.priority not in self.total_orders:
            self.total_orders[order.priority] = 0    
        self.total_orders[order.priority] += 1

        wagons_to_send = []
        self.ok = 0
        if str(order.start_point) not in self.wagon_manager.wagons_by_loc:
            self.wagon_manager.wagons_by_loc[str(order.start_point)] = set()
        
        #print(self.wagon_manager.wagons_by_loc[str(order.start_point)])
        for wagon in self.wagon_manager.wagons_by_loc[str(order.start_point)]:
           #print(self.wagon_manager.wagons_by_id[wagon].type_of_wagon)
           if not self.wagon_manager.wagons_by_id[wagon].occupied and self.are_compatible(order.wagon_type, self.wagon_manager.wagons_by_id[wagon].type_of_wagon):
               wagons_to_send.append(wagon)
               if len(wagons_to_send) == order.wagons:
                   break
        if len(wagons_to_send) < order.wagons:
            #print(len(wagons_to_send))
            for wagon_id in self.wagon_manager.wagons_by_id:
                wagon = self.wagon_manager.wagons_by_id[wagon_id]
                if wagon_id in wagons_to_send:
                    continue
                if str(wagon.current_station) not in self.name2vertex or str(order.start_point) not in self.name2vertex:
                    continue
                if wagon.occupied or not self.are_compatible(order.wagon_type, wagon.type_of_wagon) or wagon.free_day + self.djkstra[self.name2vertex[str(order.start_point)]][self.name2vertex[str(wagon.current_station)]] > order.start_date:
                    continue
                if str(wagon.current_station) + "_" + str(order.start_point) not in self.stale_moves:
                    continue

                wagons_to_send.append(wagon_id)
                
                if order.start_point not in self.stale_prices:
                     self.stale_prices[order.start_point] = 50
                self.stale_move += self.stale_moves[str(wagon.current_station) + "_" + str(order.start_point)]
                self.stale_moves_num += 1
                self.stale_stop -= (order.start_date - wagon.free_day) * self.stale_prices[wagon.current_station]
                self.stale_stop += min (self.stale_prices[wagon.current_station], self.stale_prices[order.start_point]) * (order.start_date - wagon.free_day - self.djkstra[self.name2vertex[str(order.start_point)]][self.name2vertex[str(wagon.current_station)]])
                if len(wagons_to_send) == order.wagons:
                    break
            if len(wagons_to_send) < order.wagons:
                if order.priority not in self.bad_orders:
                    self.bad_orders[order.priority] = 0    
                self.bad_orders[order.priority] += 1

                return
        for wagon in wagons_to_send:
            self.wagon_manager.update_wagon(wagon, order.end_point, order.days + order.start_date)
        self.total_profit += order.total_profit()
        if order.priority not in self.profit_per_cat:
            self.profit_per_cat[order.priority] = 0     
            self.wagons_per_cat[order.priority] = 0     

        self.profit_per_cat[order.priority] += order.total_profit()
        self.wagons_per_cat[order.priority] += order.wagons


    def run_day(self, day_num):
        for i in self.wagon_manager.wagons_by_id:
            if self.wagon_manager.wagons_by_id[i].free_day == day_num:
                self.wagon_manager.wagons_by_id[i].occupied = False
        while self.current_order < len(self.order_manager.orders) and self.order_manager.orders[self.current_order].start_date == day_num:
            self.start_order(self.order_manager.orders[self.current_order])
            self.current_order += 1
            #print("Current order - " + str(self.current_order))
        for i in self.wagon_manager.wagons_by_id:
            if not self.wagon_manager.wagons_by_id[i].occupied:
                if self.wagon_manager.wagons_by_id[i].current_station not in self.stale_prices:
                     self.stale_prices[self.wagon_manager.wagons_by_id[i].current_station] = 50
                if self.stale_prices[self.wagon_manager.wagons_by_id[i].current_station] == 100000:
                    if str(self.wagon_manager.wagons_by_id[i].current_station) not in self.name2vertex:
                        self.stale_stop += 50
                        continue   

                    neighbours = self.djkstra[self.name2vertex[str(self.wagon_manager.wagons_by_id[i].current_station)]]                        
                    m = min(i for i in neighbours if i > 0)
                    min_ind = neighbours.index(m)
                    self.stale_move += self.stale_moves[str(self.wagon_manager.wagons_by_id[i].current_station) + "_" + str(self.inv_name2vertex[min_ind])]
                    self.stale_moves_num += 1
                    self.wagon_manager.update_wagon(i, self.inv_name2vertex[min_ind], day_num + int(neighbours[min_ind]))
                else:
                    self.stale_stop += self.stale_prices[self.wagon_manager.wagons_by_id[i].current_station]


