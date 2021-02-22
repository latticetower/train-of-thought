import argparse
import disjoint_set
from igraph import Graph

import numpy as np
# from igraph import *

import os
import pandas as pd

from utils.abstractions import get_roads_graph
from utils.common import *


def load_data(basedir="../data"):
    orders7 = pd.read_csv(os.path.join(basedir, "orders7.csv.gz"))
    orders8 = pd.read_csv(os.path.join(basedir, "orders8.csv.gz"))
    wagon_mode_compat = pd.read_csv(
        os.path.join(basedir, "wagon_mode_compat.csv.gz"))
    sources = pd.read_csv(os.path.join(basedir, "sources.csv.gz"))
    standplaces = pd.read_csv(
        os.path.join(basedir, "standplaces.csv.gz"))
    metrics = pd.read_csv(os.path.join(basedir, "metrics.csv.gz"))
    return orders7, orders8, wagon_mode_compat, sources, standplaces, metrics


def save_results(strategy, savedir="result"):
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    orders_path = os.path.join(savedir, "orders.csv")
    with open(orders_path, 'w') as orders:
        orders.write(
            "Код заказа,Станция старта,Станция финиша,"
            "Расчетная дата старта,Плановая дата старта,Время в пути,"
            "Мин допустимый объем,Запрошенный объем,Тарифы,"
            "Запрошенный тип вагона,Приоритет,Примененный тариф\n")
        for order in strategy.ord_log:
            orders.write(order + "\n")

    moves_path = os.path.join(savedir, "empty_moves.csv")
    with open(moves_path, 'w') as orders:
        orders.write(
            "Отправление,Прибытие,Тип простоя,Модель вагона,"
            "День отправления (от начала расчета),"
            "День прибытия (от начала расчета),Количество,"
            "Цена порожнего пробега (за вагон),Код следующего заказa,"
            "Расчитанный тариф следующего заказа\n")
        for order in strategy.stale_move_log:
            orders.write(order + "\n")


def main(args):
    print("Loading input data...")
    orders7, orders8, wagon_mode_compat, sources, standplaces, \
        metrics = load_data(basedir=args.datadir)
    print("Preparing roads graph...")
    graph, name2vertex = get_roads_graph(metrics, debug=False)
    print("Roads graph is loaded, computing wagon movements...")
    total_sum = 0

    stale_price = {}
    stale_move = {}
    for index, row in sources.iterrows():
        stale_price[row['Station']] = int(row['Stand']) 

    for index, row in metrics.iterrows():
        stale_move[str(row['From']) + "_" + str(row['To'])] = int(row['PriceUnit']) 
        stale_move[str(row['To']) + "_" + str(row['From'])] = int(row['PriceUnit']) 

    order_manager = OrderManager()
    for index, row in orders7.iterrows():
        order = Order2(
            row['Start'], row['Finish'], row['StartDate'], int(row['MaxUnit']),
            row['NeedWagonModel'], int(row['Tariff'].split(":")[0]),
            row['Dur'], row['ShortagePenalty'], row['OrderNum'])
        order_manager.add_order(order)
        total_sum += order.total_profit()
    print(total_sum)

    wagon_manager = WagonManager()
    for index, row in sources.iterrows():
        for units in range(row['Units']):
            occupied = True
            if int(row['Date']) == 0:
                occupied = False
            wagon = Wagon(
                row['WagonModel'],
                str(row['Station']),
                occupied,
                row['Date']
            )
            wagon_manager.add_wagon(wagon)

    print(wagon_manager.wagon_number())

    comp_wagon = set()
    for index, row in wagon_mode_compat.iterrows():
        comp_wagon.add(
            str(row['NeedWagonModel']) + "_" + str(row['CompatibleWagonModel'])
        )

    strategy =  Strategy(order_manager, wagon_manager, graph, comp_wagon,
                         name2vertex, stale_price, stale_move)
    print(strategy.compability_model)
    for day in range(28):
        strategy.run_day(day)
        print("Finished computing day №", day)
        # break
    print("Bad orders - " +  str(strategy.bad_orders))
    print("Total orders - " +  str(strategy.total_orders))

    print("Profit - " + str(strategy.total_profit))
    print("Stale stop - " + str(strategy.stale_stop))
    print("Stale move - " + str(strategy.stale_move))
    print("Profit per cat - " + str(strategy.profit_per_cat))

    save_results(strategy, args.savedir)
    # strategy.stale_moves_num


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--datadir", default="data",
        help="directory where prepared files are located")
    parser.add_argument(
        "--savedir", default=".",
        help="directory which will be created if not exist and will be "
        "used to saved resulting files")
    args = parser.parse_args()
    main(args)
