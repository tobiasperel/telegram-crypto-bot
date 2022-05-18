import buscarCrypto
import mandarTelegram
import telegram
import ast
import reloj 
from pycoingecko import CoinGeckoAPI
from pprint import pprint as print
import sqlite3
from create_database import convertirTablaADiccionario


conn = sqlite3.connect('database.db')
c = conn.cursor()

cg = CoinGeckoAPI()


token = ''

bot = telegram.Bot(token=token)

datos = convertirTablaADiccionario(c,'datos')

future = dict()


if(len(datos)>0):
    for name,array in datos.items():
        #print(array)
        horaVieja = reloj.hora()
        future[name] = reloj.agregarTiempo(horaVieja,int(array[3]))

#print(future)

hora = reloj.hora()
tiempofuturo = reloj.agregarTiempo(hora,1)



while True:
    try:
        datos = convertirTablaADiccionario(c,'datos')
        todasCryptos = convertirTablaADiccionario(c,'todas_cripto')
        datosCrypto = convertirTablaADiccionario(c,'datos_cripto')
        contador = convertirTablaADiccionario(c,'contador')
    except:
        continue

    
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


    for crypto in todasCryptos:
        precioCrypto = buscarCrypto.investigarPrecioParaNewCryto(crypto)
        #print(str(crypto) + " " + str(precioCrypto))
        if precioCrypto == 0:
            continue

        
        for idPersona,cryptoPersona in datosCrypto.items():
            
            if crypto in cryptoPersona.keys():

                hora = reloj.hora()
                if future[idPersona] > hora:
                    continue
                
                if contador[idPersona][1]>=contador[idPersona][2]:
                    print("el contador esta en: " + str(contador[idPersona][1]+1))
                    conn = sqlite3.connect('database.db')
                    c = conn.cursor()
                    c.execute(f'''UPDATE contador
                              SET contador = 0
                              WHERE FK_gente = (SELECT ID FROM GENTE WHERE telegram_id = {idPersona})''')
                    conn.commit()
                    future[idPersona] = reloj.agregarTiempo(hora,int(datos[idPersona][3]))
                    print(future)
                    continue

                precioRequeridoMinimo = datosCrypto[idPersona][crypto][0]
                precioRequeridoMaximo = datosCrypto[idPersona][crypto][1]

                print("El precio ideal es: " + str(precioRequeridoMinimo) +  " El precio es: " + str(precioCrypto) )
                c.execute(f'''UPDATE contador
                              SET contador = {contador[idPersona][0]+1}
                              WHERE FK_gente = (SELECT ID FROM GENTE WHERE telegram_id = {idPersona})''')
                conn.commit()
                if (float(precioCrypto) >= float(precioRequeridoMaximo) or float(precioCrypto) <= float(precioRequeridoMinimo)) and datos[idPersona][5] == True:
                    
                    text = text = "The price of " + str(crypto).capitalize()+ " is "+ str(precioCrypto) + "\n\nIf you have any question please see /info "
                    
                    mandarTelegram.send_message(idPersona,text)
