import reloj
import mandarTelegram
import telegram
from leer import *
from pycoingecko import CoinGeckoAPI
from pprint import pprint as print
from create_database import convertirTablaADiccionario
import sqlite3
cg = CoinGeckoAPI()

conn = sqlite3.connect('database.db')
c = conn.cursor()

token = '1156537678:AAG9MWA6APVAjfODTVZDovFbTr11dW-LtwU'

bot = telegram.Bot(token=token)

future = dict()
datos = convertirTablaADiccionario(c,'datos')

if(len(datos)>0):
    for name,array in datos.items():
        #print(array)
        horaVieja = reloj.hora()
        future[name] = reloj.agregarTiempo(horaVieja,int(array[3]))

print(future)

hora = reloj.hora()
tiempofuturo = reloj.agregarTiempo(hora,1)


while True:
    
    try:
        for name,array in datos.items():
            if name not in future.keys():
                horaVieja = reloj.hora()
                future[name] = reloj.agregarTiempo(horaVieja,int(array[3]))

            hora = reloj.hora()
            if tiempofuturo > hora:

                continue

        
        if reloj.hora() < tiempofuturo:
            continue
        tiempofuturo = reloj.agregarTiempo(hora,1)
        price= cg.get_price(ids='universal-basic-income', vs_currencies='usd')
        precio = price['universal-basic-income']['usd']  
        
        precioIdeal = float(precio)* 720
        

        c.execute(f'''UPDATE ubi_price
                  SET price = {precio}''')
        conn.commit()
       
        datos = convertirTablaADiccionario(c,'datos')
        
        if(len(datos)>0):
            for name,array in datos.items():
                
                hora = reloj.hora()
                
                if future[name] > hora:
                    continue
                future[name] = reloj.agregarTiempo(hora,int(datos[name][3]))
                
                precioMensual = array[2]

                print("El precio ideal es: " + str(precioMensual) +  " El precio mensual es: " + str(precioIdeal) )
        
                if (precioIdeal==None):
                    continue
            
                elif(float(precioIdeal) >= float(precioMensual) ):
                    if precioMensual == 10000.0:
                        continue
                    if datos[name][6] == True:
                        mandarTelegram.send_message(name,"The monthly ubi price is: " + str(precioIdeal))
                
    except:
        pass
