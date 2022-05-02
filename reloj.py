from datetime import datetime
from datetime import timedelta

def hora():
    now = datetime.now() 
    #print (now.strftime("%Y-%m-%d %H:%M"))
    return(now)

def agregarTiempo(now,minutos):
    extra = timedelta(minutes=minutos)
    future = now + extra
    print (future.strftime("%Y-%m-%d %H:%M"))
    return future

def agregarDias(now,dias):
    extra = timedelta(days=dias)
    future = now - extra
    #print (future.strftime("%Y-%m-%d %H:%M"))
    return future


def listaDeDias(dias):

    now = datetime.now() 
    lista = list()
    for i in range(dias):
        lista.append(agregarDias(now,i))
    
    #print(lista)
    nuevaLista = list(reversed(lista))
    return nuevaLista

'''
now = hora()
future = agregarTiempo(now,minutos)

if future > now:
    print(1)

listaDeDias(30)
'''