from logging import error
import mandarTelegram
import telegram
import ast

from pycoingecko import CoinGeckoAPI
import apiCoingecko 
import pandas as pd
import plotly.graph_objects as go
from pprint import pprint as print
import time
import reloj
cg = CoinGeckoAPI()
token = ''
bot = telegram.Bot(token=token)


def investigarPrecio(coin):
    try:
        price= cg.get_price(ids=coin, vs_currencies='usd')
        precioCrypto = price[coin]['usd']
        return True
    except:
        return False

def investigarPrecioParaNewCryto(coin):
    try:
        price= cg.get_price(ids=coin, vs_currencies='usd')
        precioCrypto = price[coin]['usd']
        return precioCrypto
    except:
        return 0
    


def investigarYmandarPrecio(id,coin,quiereGrafico,dias):
    try:
        price= cg.get_price(ids=coin, vs_currencies='usd')
        precioCrypto = price[coin]['usd']
        text = apiCoingecko.dataCrypto(coin)
        mandarTelegram.send_message(id,"The price of "  + str(coin).capitalize() + " is " + str(precioCrypto) + " usd" + text)
        if quiereGrafico == 1:
            grafico = apiCoingecko.graficarCoin(coin,dias)
            mandarTelegram.mandarImagen(id, grafico)
    except Exception as e:
        print(e)
        enviado = False
        return enviado

def investigarYmandarPrecioConCantidad(id,coin,cantidad,quiereGrafico,dias):
    try:

        price= cg.get_price(ids=coin, vs_currencies='usd')
        precioCrypto = price[coin]['usd']
        total = float(cantidad) * float(precioCrypto)

        total = '{0:,}'.format(total)
        total = str(total.replace(",","."))
        
        mandarTelegram.send_message(id,"The price of "+ str(cantidad)+" "+ str(coin).capitalize() + " is " + str(total) + " usd")
        if quiereGrafico == 1:
            grafico = apiCoingecko.graficarCoin(coin,dias)
            mandarTelegram.mandarImagen(id, grafico)
        return True
    except:
        return False
