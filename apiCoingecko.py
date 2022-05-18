#https://pypi.org/project/pycoingecko/
from pycoingecko import CoinGeckoAPI
import pandas as pd
import plotly.graph_objects as go
from pprint import pprint as print
cg = CoinGeckoAPI()
import reloj
#print(cg.get_coins_list())

def graficarCoin(coin,dias):
    coin = getCoinId(coin)
    bitcoin_data = cg.get_coin_market_chart_by_id(id=coin, vs_currency='usd', days=dias)

    bitcoin_price_data = bitcoin_data['prices']

    data = pd.DataFrame(bitcoin_price_data, columns=['TimeStamp', 'Price'])
    data['Date'] = pd.to_datetime(data['TimeStamp'], unit='ms')

    candlestick_data = data.groupby(data.Date.dt.date, as_index=False).agg({"Price": ['min', 'max', 'first', 'last']})
    
    lista = reloj.listaDeDias(dias) 
    
    fig = go.Figure(data=[go.Candlestick(x=lista,
                    open=candlestick_data['Price']['first'], 
                    high=candlestick_data['Price']['max'],
                    low=candlestick_data['Price']['min'], 
                    close=candlestick_data['Price']['last'])
                    ])

    fig.update_layout(xaxis_rangeslider_visible=False)
    fig.write_image("fig1.png")
    #fig.show()
    return fig


    
def dataCrypto(coin):   
    coin = getCoinId(coin)
    bitcoin_data = cg.get_coin_market_chart_by_id(id=coin, vs_currency='usd', days=30)

    bitcoin_cap_data = bitcoin_data['market_caps']
    bitcoin_volume_data = bitcoin_data['total_volumes']
    datos = int(bitcoin_volume_data[-1][1])
    datos = '{0:,}'.format(datos)

    extra = int(bitcoin_cap_data[-1][1])
    extra = '{0:,}'.format(extra)

    extra = str(extra.replace(",","."))
    datos = str(datos.replace(",","."))

    datos = "\n\nMarket cap : " + extra + '\n\nVolume : '  + datos
    
    return datos



def getCoinId(coin):
    if coin in symbolToId:
        return symbolToId[coin]
    return coin

lista = cg.get_coins_list()

symbolToId = {}

for i in lista:
    symbolToId[i['symbol']] = i['id']








