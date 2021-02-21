"""Basic classes"""

class Order(object):
    def __init__(self, start_point, end_point, start_date, wagons, wagon_type, cost_per_wagon, days):
        self.start_point = start_point
        self.end_point = end_point
        self.start_date = start_date
        self.wagons = wagons
        self.wagon_type = wagon_type
        self.cost_per_wagon = cost_per_wagon
        self.days = days

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
        self.wagons_by_loc[self.wagons_by_id[wagon].current_station].remove(wagon)
        if end_point not in self.wagons_by_loc:
            self.wagons_by_loc[end_point] = set()      
        self.wagons_by_loc[end_point].add(wagon)
        self.wagons_by_loc_rev[wagon] = end_point
        self.wagons_by_id[wagon].current_station = end_point
        self.wagons_by_id[wagon].free_day = end_date

    def add_wagon(self, wagon):
        self.wagons_by_id[wagon.index] = wagon
        if wagon.current_station not in self.wagons_by_loc:
            self.wagons_by_loc[wagon.current_station] = set()     
        self.wagons_by_loc[wagon.current_station].add(wagon.index) 
        self.wagons_by_loc_rev[wagon.index] = wagon.current_station
    
    def wagon_number(self):
        return len(self.wagons_by_id)


class Strategy(object):
    def __init__(self, order_manager, wagon_manager, graph, compability_model, name2vertex):
        self.order_manager = order_manager
        self.wagon_manager = wagon_manager
        self.graph = graph
        self.compability_model = compability_model
        self.total_cost = 0
        self.current_order = 0
        self.bad_orders = 0
        self.djkstra = graph.shortest_paths_dijkstra(weights="time")
        self.name2vertex = name2vertex
        self.total_orders = {}
        self.bad_orders = {}
        self.total_profit = 0
        self.stale_stop = 0
        self.stale_move = 0


    def are_compatible(self, type1, type2):
        return (str(type1) + "_" + str(type2)) in self.compability_model or (str(type2) + "_" + str(type1)) in self.compability_model or type1 == type2

    def start_order(self, order):
        wagons_to_send = []
        self.ok = 0
        if order.start_point not in self.wagon_manager.wagons_by_loc:
            self.wagon_manager.wagons_by_loc[order.start_point] = set()
        

        for wagon in self.wagon_manager.wagons_by_loc[order.start_point]:
           #print(self.wagon_manager.wagons_by_id[wagon].type_of_wagon)
           if not self.wagon_manager.wagons_by_id[wagon].occupied and self.are_compatible(order.wagon_type, self.wagon_manager.wagons_by_id[wagon].type_of_wagon):
               wagons_to_send.append(wagon)
               if len(wagons_to_send) == order.wagons:
                   break
        if len(wagons_to_send) < order.wagons:
            #print(len(wagons_to_send))
            for wagon_id in self.wagon_manager.wagons_by_id:
                wagon = self.wagon_manager.wagons_by_id[wagon_id]
                if str(wagon.current_station) not in self.name2vertex or str(order.start_point) not in self.name2vertex:
                    continue
                if wagon.occupied or not self.are_compatible(order.wagon_type, wagon.type_of_wagon) or wagon.free_day + self.djkstra[self.name2vertex[str(order.start_point)]][self.name2vertex[str(wagon.current_station)]] > order.start_date:
                    continue
                wagons_to_send.append(wagon_id)
                if len(wagons_to_send) == order.wagons:
                    break
            if len(wagons_to_send) < order.wagons:
                self.bad_orders += 1
                return
        
        for wagon in wagons_to_send:
            self.wagon_manager.update_wagon(wagon, order.end_point, order.days + order.start_date)

    def run_day(self, day_num):
        for i in self.wagon_manager.wagons_by_id:
            if self.wagon_manager.wagons_by_id[i].free_day == day_num:
                self.wagon_manager.wagons_by_id[i].occupied = False
        while self.current_order < len(self.order_manager.orders) and self.order_manager.orders[self.current_order].start_date == day_num:
            self.start_order(self.order_manager.orders[self.current_order])
            self.current_order += 1
            print("Current order - " + str(self.current_order))

