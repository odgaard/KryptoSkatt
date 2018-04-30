import pathlib
import datetime

path = 'c:/Users/Jacob/PycharmProjects/KryptoSkatt/Data/'
trans_in = list()
trans_out = list()

bitcoin_dict = dict()
ethereum_dict = dict()
USD_NOK_dict = dict()

def unix_time_to_date(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')

def populate_electrum_wallet_transactions(file):
    # Exported data from Bitcoin wallet
    # All incoming transactions to my wallet
    with open(pathlib.PureWindowsPath(path + file), 'r') as f:
        total = 0
        for line in f.read().split('\n'):
            new_line = line.split(',')
            if(len(new_line) > 3):
                if(new_line[3][0] == '+'): trans_in.append(new_line)
                if(new_line[3][0] == '-'): trans_out.append(new_line)

def populate_bitcoin_price_index(file):
    # Gather Bitcoin price index from
    # https://blockchain.info/charts/market-price?timespan=2years
    with open(pathlib.PureWindowsPath(path + file), 'r') as f:
        for line in f.read().split('\n'):
            line = line.split(' ')
            final_line = [line[0], line[1].split(',')[1]]

            bitcoin_dict[final_line[0]] = float(final_line[1])

def populate_ethereum_price_index(file):
    # Gather Ethereum price index from
    # https://www.etherchain.org/charts/priceUSD
    with open(pathlib.PureWindowsPath(path + file), 'r') as f:
        for line in f.read().split('\n')[1:]:
            line = line.split(',')
            new_line = [line[0].replace('"',''), line[1]]

            # Max one entry per day
            date = new_line[0].split(' ')[0]
            price = float(new_line[1])

            ethereum_dict[date] = float(price)

def populate_USD_NOK_conversion(file):
    # Gather USD to NOK conversion from
    # https://data.norges-bank.no/api/data/EXR/B.USD.NOK.SP?StartPeriod=2017&EndPeriod=2018&format=csv-:-comma-true-flat
    with open(pathlib.PureWindowsPath(path + file), 'r') as f:
        for line in f.read().split('\n'):
            line = line.split(',')
            USD_NOK_dict[line[5]] = float(line[6])

def get_bitcoin_income(year, start_value):
    # Calculate total income based on data
    total_NOK, total_BTC = 0, 0
    USD_NOK_exchange = start_value #First day of the year
    for trans in trans_in:
        date = trans[4].split(' ')[0]
        if(date.split('-')[0] != year): continue

        if(USD_NOK_dict.get(date)):
            USD_NOK_exchange = USD_NOK_dict[date]
        result = bitcoin_dict[date] * float(trans[3][1:]) * USD_NOK_exchange
        total_BTC += float(trans[3][1:])
        total_NOK += result
    return total_NOK, total_BTC

def get_ethereum_income(file, start_value):
    total = 0

    # Gather mining data from ethermine (my mining pool)
    # https://ethermine.org/api/miner
    with open(pathlib.PureWindowsPath(path + file), 'r') as f:
        total_NOK, total_ETH = 0, 0
        USD_NOK_exchange = start_value #First day of the year
        for line in f.read().split('\n')[1:]:
            new_line = [string.replace('"', '') for string in line.split(',')[1:]]

            amount = int(new_line[2])/10**18

            ## Calculate income
            date = unix_time_to_date(new_line[4])
            if(USD_NOK_dict.get(date)):
                USD_NOK_exchange = USD_NOK_dict[date]

            result = ethereum_dict[date]*amount*USD_NOK_exchange

            total_NOK += result
            total_ETH += amount
    return total_NOK, total_ETH

def setup():
    populate_USD_NOK_conversion('EXR.csv')
    populate_bitcoin_price_index('market-price-last-2-years.csv')
    populate_electrum_wallet_transactions('electrum-history.csv')
    populate_ethereum_price_index('ethereum-usd-price.csv')

def main():
    setup()

    # This should always be the last day of the year, or the first day of the next year.
    final_date_crypto = "2017-12-31"

    # This should always be the last working day for the Norwegian exchange,
    # or the first working day of the next year.
    final_date_USD_NOK = "2017-12-29"

    # The USD-NOK conversion for the first day of the year.
    # The Norwegian exchanges might be closes on this day, so it can't be computed directly
    start_value = 8.652

    income_btc_in_NOK, total_BTC = get_bitcoin_income("2017", start_value)
    income_eth_in_NOK, total_ETH = get_ethereum_income('payouts.csv', start_value)
    income_in_NOK = income_btc_in_NOK + income_eth_in_NOK

    # Remove this if your using this script, this is a hard-coded compensation for my taxes.
    total_BTC-=0.11362

    print("BTC Income:", round(income_btc_in_NOK, 2), "NOK")
    print("ETH Income:", round(income_eth_in_NOK, 2), "NOK")
    print("Total Income:", round(income_eth_in_NOK + income_btc_in_NOK), "NOK")
    print()

    capital_btc_in_NOK = USD_NOK_dict[final_date_USD_NOK]*bitcoin_dict[final_date_crypto]*total_BTC
    capital_eth_in_NOK = USD_NOK_dict[final_date_USD_NOK]*ethereum_dict[final_date_crypto]*total_ETH
    capital_in_NOK = capital_btc_in_NOK + capital_eth_in_NOK

    print("BTC Capital:")
    print(round(total_BTC, 6), "BTC")
    print(round(capital_btc_in_NOK, 2), "NOK")
    print()
    print("ETH Capital:")
    print(round(total_ETH, 4), "ETH")
    print(round(capital_eth_in_NOK, 2), "NOK")
    print()
    print("Total capital:", round(capital_in_NOK), "NOK")

main()