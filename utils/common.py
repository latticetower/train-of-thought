"""Basic classes"""

class Order(object):
    def __init__(self, start_point, end_point, wagons, wagon_type, cost_per_wagon, days):
        self.start_point = start_point
        self.end_point = end_point
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


    def add_wagon(self, wagon):
        self.wagons_by_id[wagon.index] = wagon
        if wagon.current_station not in self.wagons_by_loc:
            self.wagons_by_loc[wagon.current_station] = set()     
        self.wagons_by_loc[wagon.current_station].add(wagon.index) 
        self.wagons_by_loc_rev[wagon.index] = wagon.current_station
    
    def wagon_number(self):
        return len(self.wagons_by_id)


class Strategy(object):
    def __init__(self, order_manager, wagon_manager, graph, compability_model):
        self.order_manager = order_manager
        self.wagon_manager = wagon_manager
        self.graph = graph
        self.compability_model = compability_model
        self.total_cost = 0
        self.current_order = 0
    
    def are_compatible(self, type1, type2):
        return (str(type1) + "_" + str(type2)) in self.compability_model

    def start_order(self, order):
        wagons_to_send = []
        for wagon in self.wagon_manager.wagons_by_loc[order.start_point]:
           if not wagon.occupied and self.are_compatible(wagon.type_of_wagon, order.wagon_type):
               wagons_to_send.append(wagon)
               if len(wagons_to_send) == order.wagons:
                   break
        if  len(wagons_to_send) < order.wagons:
            print("Problem")
            return
        
        for wagon in wagons_to_send:

    def run_day(self, day_num):
        while self.current_order < len(self.order_manager.orders) and self.order_manager.orders[self.current_order] == day_num:
            self.start_order(self.order_manager.orders[self.current_order])
            self.current_order += 1

