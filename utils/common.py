"""Basic classes"""

class Order(object):
    def __init__(self, start_point, end_point, wagons, wagon_type, cost_per_day, days):
        self.start_point = start_point
        self.end_point = end_point
        self.wagons = wagons
        self.wagon_type = wagon_type
        self.cost_per_wagon = cost_per_wagon
        self.days = days

    def total_profit(self):
        return self.wagons * self.cost_per_wagon


class Wagon(object):
    def __init__(self, type_of_wagon, current_station, occupied, free_day, free_station):
        self.type_of_wagon = type_of_wagon
        self.occupied = occupied
        self.current_station = current_station
        self.free_day = free_day
        self.free_station = free_station
        
    def get_day_cost(self, stay_stations):
        if self.occupied:
            return 0
        else:
            return stay_stations[self.current_station]:

    
class WagonManager(object):
    def __init__(self, wagons):
        pass
