import pathlib
import os
import csv

path = 'c:/Users/Jacob/PycharmProjects/KryptoSkatt/Data/'
formated_file = list()
trans_in = list()
trans_out = list()

with open(pathlib.PureWindowsPath(path + 'electrum-history.csv'), 'r') as f:
    x = f.read().split('\n')
    for line in x:
        new_line = line.split(',')
        if(len(new_line) > 3):
            if(new_line[3][0] == '+'):
                trans_in.append(new_line)
            if(new_line[3][0] == '-'):
                trans_out.append(new_line)

with open(pathlib.PureWindowsPath(path + 'market-price_all_time.csv'), 'r') as f:

