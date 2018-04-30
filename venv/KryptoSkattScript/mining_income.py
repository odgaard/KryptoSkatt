import pathlib
import datetime

path = 'c:/Users/Jacob/PycharmProjects/KryptoSkatt/Data/'
trans_in = list()
trans_out = list()
bitcoin_price = list()

bitcoin_dict = dict()
ethereum_dict = dict()
USD_NOK_dict = dict()

# Exported data from Bitcoin wallet
# All incoming transactions to my wallet
with open(pathlib.PureWindowsPath(path + 'electrum-history.csv'), 'r') as f:
    x = f.read().split('\n')
    total = 0
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
def get_bitcoin_income(year):
    total_NOK = 0
    total_BTC = 0
    USD_NOK_exchange = 8.652 #First day of the year
    for trans in trans_in:
        date = trans[4].split(' ')[0]
        check_date = date.split('-')
        if(check_date[0] != year):
            continue
        if(USD_NOK_dict.get(date)):
            USD_NOK_exchange = USD_NOK_dict[date]
        result = bitcoin_dict[date] * float(trans[3][1:]) * USD_NOK_exchange
        total_BTC += float(trans[3][1:])
        total_NOK += result
    return total_NOK, total_BTC

def get_ethereum_income():
    total = 0

    # Gather Ethereum price index from
    # https://www.etherchain.org/charts/priceUSD
    with open(pathlib.PureWindowsPath(path + 'ethereum-usd-price.csv'), 'r') as f:
        x = f.read().split('\n')[1:]
        last_date = "01"
        for line in x:
            line = line.split(',')
            new_line = [line[0].replace('"',''), line[1]]

            # Max one entry per day
            date = new_line[0].split(' ')[0]
            price = float(new_line[1])
            evaluate_date = date.split('-')
            if(evaluate_date == last_date): continue
            last_date = evaluate_date

            ethereum_dict[date] = float(price)

    # Gather mining data from ethermine (my mining pool)
    # https://ethermine.org/api/miner
    with open(pathlib.PureWindowsPath(path + 'payouts.csv'), 'r') as f:
        total_NOK = 0
        total_ETH = 0
        USD_NOK_exchange = 8.652 #First day of the year
        x = f.read().split('\n')
        for line in x[1:]:
            line = line.split(',')[1:]
            new_line = []
            for string in line:
                new_line.append(string.replace('"', ''))
            amount = int(new_line[2])/10**18
            date = unix_time_to_date(new_line[4])
            if(USD_NOK_dict.get(date)):
                USD_NOK_exchange = USD_NOK_dict[date]
            result = ethereum_dict[date]*amount*USD_NOK_exchange

            total_NOK += result
            total_ETH += amount
    return total_NOK, total_ETH

def unix_time_to_date(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')

total_income_btc_in_NOK, total_btc_in_BTC = get_bitcoin_income("2017")
total_btc_in_BTC-=0.11362
print("BTC Income:", round(total_income_btc_in_NOK, 2), "NOK")
print("BTC Capital:")
print(round(total_btc_in_BTC, 6), "BTC")
total_btc_in_NOK = USD_NOK_dict["2017-12-29"]*bitcoin_dict["2017-12-31"]*total_btc_in_BTC
print(round(total_btc_in_NOK, 2), "NOK")
print()
print()



total_income_eth_in_NOK, total_eth_in_ETH = get_ethereum_income()
print("ETH Income:", round(total_income_eth_in_NOK, 2), "NOK")
print("ETH Capital:")
print(round(total_eth_in_ETH, 4), "ETH")
total_eth_in_NOK = USD_NOK_dict["2017-12-29"]*ethereum_dict["2017-12-31"]*total_eth_in_ETH
print(round(total_eth_in_NOK, 2), "NOK")
print()
print()

print("Total Income:", round(total_income_eth_in_NOK + total_income_btc_in_NOK), "NOK")
print("Total capital:", round(total_eth_in_NOK + total_btc_in_NOK), "NOK")

