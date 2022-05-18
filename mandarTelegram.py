import telegram
from telegram.ext import *
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


#configuraciones del bot
token = '1902593010:AAGl1Uoh_LDzj_7qu-Ror3jAQcUzQ2zmCjo'
chat_id = '1094333353'
bot = telegram.Bot(token=token)
#------------------------------

def send_message(group_id, text):
    bot.send_message(group_id, text)

def mandarImagen(group_id, imagen):
    bot.send_photo(chat_id = group_id,photo = open("fig1.png","rb"))

#send_message(chat_id,'hola chino')
