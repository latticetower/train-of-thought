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

    def add_wagon(self, wagon):
        self.wagons_by_id[wagon.index] = wagon
        self.wagons_by_loc[wagon.current_station] = wagon.index 
    
    def wagon_number(self):
        return len(self.wagons_by_id)


class Strategy(object):
    pass