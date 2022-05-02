from leer import *
import requests
import telegram
import reloj 
import mandarTelegram
import sqlite3
from create_database import convertirTablaADiccionario


token = '1902593010:AAGl1Uoh_LDzj_7qu-Ror3jAQcUzQ2zmCjo'

conn = sqlite3.connect('database.db')
c = conn.cursor()
    
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
tiempofuturo = reloj.agregarTiempo(hora,1) # 1 minuto

while True:

    for name,array in datos.items():
        if name not in future.keys():
            horaVieja = reloj.hora()
            future[name] = reloj.agregarTiempo(horaVieja,int(array[3]))

        hora = reloj.hora()
        if tiempofuturo > hora:
            #print(tiempofuturo)
            #print(hora)
            continue

    tiempofuturo = reloj.agregarTiempo(hora,1)

    response = requests.get('https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=CQHB165JYY6BEIBSWV2R4X46E7XM9QPDMR')
    response.raise_for_status()  
    if response.status_code != 204:
        data = response.json()
        
    gasBajo = int(data["result"]["SafeGasPrice"])
    gasMedio = int(data["result"]["ProposeGasPrice"])
    gasAlto = int(data["result"]["FastGasPrice"])
    texto = str([gasBajo, gasMedio, gasAlto ])
    #print(texto)

    c.execute(f'''UPDATE gas
                SET bajo = {gasBajo}, 
                medio = {gasMedio},
                alto = {gasAlto}
                ''')
    conn.commit()

    conn = sqlite3.connect('database.db')
    c = conn.cursor()   
    datos = convertirTablaADiccionario(c,'datos')


    if(len(datos)>0):
        for name,array in datos.items():
            hora = reloj.hora()
            if future[name] > hora:
                continue
            future[name] = reloj.agregarTiempo(hora,int(datos[name][3]))
            tipoDeGas = datos[name][7] 

            if(tipoDeGas=='safe'):
                gas = gasBajo
            elif(tipoDeGas=='medium'):
                gas = gasMedio
            else:
                gas = gasAlto

            gasIdeal = array[1]
            print(gasIdeal,gas)

            if (gasIdeal==None):
                continue
            elif(int(gasIdeal) >= gas ):
                if datos[name][5] == True:
                    mandarTelegram.send_message(name,"The gas is cheap: " + texto)


