import pathlib
import os
import csv

path = 'c:/Users/Jacob/PycharmProjects/KryptoSkatt/Data/'
formated_file = list()
trans_in = list()
trans_out = list()
bitcoin_price = list()
bitcoin_dict = dict()
USD_NOK_dict = dict()

# Exported data from Bitcoin wallet
# All incoming transactions to my wallet
with open(pathlib.PureWindowsPath(path + 'electrum-history.csv'), 'r') as f:
    x = f.read().split('\n')
    for line in x:
        new_line = line.split(',')
        if(len(new_line) > 3):
            if(new_line[3][0] == '+'):
                trans_in.append(new_line)
            if(new_line[3][0] == '-'):
                trans_out.append(new_line)

# Gather Bitcoin price index from
# https://blockchain.info/charts/market-price?timespan=2years
with open(pathlib.PureWindowsPath(path + 'market-price-last-2-years.csv'), 'r') as f:
    x = f.read().split('\n')
    for line in x:
        line = line.split(' ')
        final_line = [line[0], line[1].split(',')[1]]
        bitcoin_price.append(final_line)
        bitcoin_dict[final_line[0]] = float(final_line[1])


# Gather USD to NOK conversion from
# https://data.norges-bank.no/api/data/EXR/B.USD.NOK.SP?StartPeriod=2017&EndPeriod=2018&format=csv-:-comma-true-flat
with open(pathlib.PureWindowsPath(path + 'EXR.csv'), 'r') as f:
    x = f.read().split('\n')
    for line in x:
        line = line.split(',')
        USD_NOK_dict[line[5]] = float(line[6])

# Calculate total income based on data
def total_income(year):
    total = 0
    USD_NOK_exchange = 8.652 #First day of the year
    for trans in trans_in:
        date = trans[4].split(' ')[0]
        check_date = date.split('-')
        if(check_date[0] != year): continue
        if(USD_NOK_dict.get(date)):
            USD_NOK_exchange = USD_NOK_dict[date]
        result = bitcoin_dict[date] * float(trans[3][1:]) * USD_NOK_exchange
        total += result
    return total

total = total_income("2017")
print(round(total, 2), "NOK")



