import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import time
import buscarCrypto
import apiCoingecko
from create_database import *
# configuraciones del bot
token = '1902593010:AAGl1Uoh_LDzj_7qu-Ror3jAQcUzQ2zmCjo'

bot = telegram.Bot(token=token)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


# ------------------------------------------------------------------------------------------------------------

def start(update, context):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    text_startUp = ' Hi ' + update.message.from_user.first_name + \
        '<a id="emoji-html">&#128075;</a>, welcome to crypto bot'', what do you need?'
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text_startUp, parse_mode=telegram.ParseMode.HTML)

    datos = convertirTablaADiccionario(c, 'datos')
    print(datos)
    contador = convertirTablaADiccionario(c, 'contador')
    gente = convertirTablaADiccionario(c, 'gente')
    text = '<b> These are the possible commands:</b> \n\n<strong>ACCOUNT: <a id="emoji-html">&#128188;</a> </strong>\n\n/start: Start the bot. \n/info: Check possible commands. \n/toggle_messages: toggles whether the bot sends notifications or not. \n/time: Set the time interval in which crypto prices / gas prices updates are sent (the default time is 5 minutes). \n/reset_bot: Reset bot data.  \n\n<strong>CRYPTO: <a id="emoji-html">&#128200;</a> </strong>\n\n/coin: See the price of a cryptocurrency. \n/coin_min_max: Set the minimum and maximum value of a cryptocurrency. \n/coin_min_max_remove: Delete a condition previously added.\n/my_portfolio: View saved conditions in /coin_min_max.\n/toggle_chart: Enable or disable the option to send charts together with the price (the default is enabled).\n/modify_chart: set the days in which the chart covers (the default time of the chart is 30 days).\n/convert: convert an amount of a crypto to usd. \n\n<strong>ETHEREUM GAS: <a id="emoji-html">&#9981;</a> </strong>  \n\n/gas: Check gas station. \n/gas_alert: Get alerts on gas prices according to priorities (safe, medium and fast) and a minimum gas price value.\n\n<strong>UNIVERSAL BASIC INCOME: <a id="emoji-html">&#128184;</a> </strong>\n\n/ubi_price: Check ubi price in usd. \n/ubi_monthly: Check ubi "streaming" price right now (ubi_price*720).\n/ubi_monthly_alert: Set desired minimum monthly price of ubi "streaming" (ubi_price * 720).\n\n<strong>OUR COMMUNITY: <a id="emoji-html">&#128080;</a> </strong>\n\n/donations: You can donate a tip and thus help the community, more information at the command. \n/bot_code: Here you will find the link of the bot code, since it is open source\n/contact_us: If you have any questions or want to make a recommendation you can contact us '
    print(datos)
    telegram_ids = [persona[0] for persona in gente.values()]
    print(telegram_ids)
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=text, parse_mode=telegram.ParseMode.HTML)
    if len(gente) < 1 or update.effective_chat.id not in telegram_ids:
        # INSERT GENTE
        try:
            nyap = update.message.from_user.first_name + \
                " " + update.message.from_user.last_name
        except:
            nyap = update.message.from_user.first_name

        # INSERT GENTE
        c.execute(f'''INSERT INTO gente (
            telegram_id, nyap)VALUES({update.effective_chat.id},\"{nyap}\")''')
        conn.commit()

    if update.effective_chat.id not in datos.keys():
        print("ASHEEEEE")
        # INSERT DATOS
        c.execute(f'''INSERT INTO datos (
            "FK_gente", 
            "gas_requerido", 
            "tiempo_noti", 
            "confirmation_reset",
            "allow_graphic",
            "info_state",
            "tipo_gas",
            "cant_dias_grafico")
            VALUES (
                (SELECT gente.ID FROM gente WHERE telegram_id = {update.effective_chat.id}),
                NULL,
                5,
                0,
                1,
                1,
                'medium',
                30
            )''')

        # INSERT CONTADOR
        c.execute(f'''INSERT INTO contador(
            FK_gente,
            contador,
            cant_cripto)
            VALUES(
                (SELECT gente.ID FROM gente WHERE gente.telegram_id = {update.effective_chat.id}),
                0,
                0)''')
        conn.commit()
    confirmacion_reset(update, context)


def toggle_chart(update, context):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    datos = convertirTablaADiccionario(c, 'datos')

    is_chart_allowed = datos[update.effective_chat.id][5]
    print(is_chart_allowed)
    if is_chart_allowed == 1:
        new_chart_user = 0
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='The charts function has been disabled successfully\n\nIf you have any question please see /info ', parse_mode=telegram.ParseMode.HTML)

    elif is_chart_allowed == 0:
        new_chart_user = 1
        context.bot.send_message(chat_id=update.effective_chat.id,
                                text='The charts function has been enabled successfully\n\nIf you have any question please see /info ', parse_mode=telegram.ParseMode.HTML)
    else:
        new_chart_user = 1
        context.bot.send_message(chat_id=update.effective_chat.id,
                                text='The charts function has been enabled successfully\n\nIf you have any question please see /info ', parse_mode=telegram.ParseMode.HTML)

    # UPDATE GRAPHIC
    c.execute(f'''UPDATE datos
            SET allow_graphic = {new_chart_user}
            WHERE FK_gente = (SELECT ID FROM GENTE WHERE telegram_id = {update.effective_chat.id})''')
    conn.commit()

    confirmacion_reset(update, context)


def reset_bot(update, context):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute(f'''UPDATE datos
            SET confirmation_reset = 1
            WHERE FK_gente = (SELECT ID FROM GENTE WHERE telegram_id = {update.effective_chat.id})''')
    conn.commit()
    context.bot.send_message(chat_id=update.effective_chat.id,
                            text='Are you sure that you want to reset the bot?\n\nThe possible answers are: "<b> yes</b>" or  "<b>no</b>"\n\nIf you have any question please see /info ', parse_mode=telegram.ParseMode.HTML)


def confirmacion_reset_finish(update, context):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    datos = convertirTablaADiccionario(c, 'datos')

    mensaje = str(update.message.text).lower()

    if datos[update.effective_chat.id][4] == 1 and mensaje == 'yes':
        print("entro al if")
        c.execute(f'''UPDATE datos
                  SET gas_requerido = NULL, 
                  ubi_mensual = NULL,
                  tiempo_noti = 5,
                  confirmation_reset = 0,
                  allow_graphic = 1,
                  info_state = 1,
                  tipo_gas = "medium",
                  cant_dias_grafico = 30
                  WHERE FK_gente = (SELECT ID FROM GENTE WHERE telegram_id = {update.effective_chat.id})''')

        c.execute(f'''UPDATE contador
                  SET contador = 0, 
                  cant_cripto = 0
                  WHERE FK_gente = (SELECT ID FROM GENTE WHERE telegram_id = {update.effective_chat.id})''')

        c.execute(f'''DELETE FROM datos_cripto 
                  WHERE FK_gente = (SELECT ID FROM GENTE WHERE telegram_id = {update.effective_chat.id})''')

        conn.commit()

        context.bot.send_message(
            chat_id=update.effective_chat.id, text='The bot has been reseted')
    else:
        if datos[update.effective_chat.id][4] == 1:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text='The bot has not been reseted')

        c.execute(f'''UPDATE datos
                    SET confirmation_reset = 0 
                    WHERE FK_gente = (SELECT ID FROM GENTE WHERE telegram_id = {update.effective_chat.id})''')
        conn.commit()


def toggle_messages(update, context):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    datos = convertirTablaADiccionario(c, 'datos')
    if datos[update.effective_chat.id][6] == 1:
        new_message_state = 0
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='The bot has been stopped <a> &#128277;</a>', parse_mode=telegram.ParseMode.HTML)

    elif datos[update.effective_chat.id][6] == 0:
        new_message_state = 1
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='The bot has been reactivated <a id="emoji-html">&#128276;</a>', parse_mode=telegram.ParseMode.HTML)

    c.execute(f'''UPDATE datos
                  SET info_state = {new_message_state}
                  WHERE FK_gente = (SELECT ID FROM GENTE WHERE telegram_id = {update.effective_chat.id})''')
    conn.commit()

    confirmacion_reset(update, context)


def gasTracker_handle(update, context):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    gas_db = convertirTablaADiccionario(c, 'gas')
    gas = list(gas_db.values())[0]
    print(gas)
    text_gas = "The safe gas is: " + str(gas[0]) + "\n\nThe medium gas is: " + str(
        gas[1]) + "\n\nThe fast gas is: " + str(gas[2]) + "\n\nIf you have any question please see /info"
    try:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=text_gas)
    except:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text='Please try again')
    confirmacion_reset(update, context)


def gas_alert(update, context):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    datos = convertirTablaADiccionario(c, 'datos')

    if len(context.args) != 2:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Argument must only two words.\n\nThe syntax must be /gas_alert + typeOfGas +  number.\nThe possible type of gas are: "safe" , "medium" and "fast". \n\nExample: /gas_alert fast 124. ')

    else:
        if type(context.args[0]) == str and context.args[1].isnumeric():

            tipo_gas = context.args[0].strip().lower()
            if not (tipo_gas == 'safe' or tipo_gas == 'medium' or tipo_gas == 'fast'):
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text='Argument must only two words.\n\nThe syntax must be /gas_alert + typeOfGas +  number.\nThe possible type of gas are: "safe" , "medium" and "fast". \n\nExample: /gas_alert fast 124. ')
                return 0

            c.execute(f'''UPDATE datos
                      SET gas_requerido = {context.args[1]}  
                      WHERE FK_gente = (SELECT ID FROM GENTE WHERE telegram_id = {update.effective_chat.id})''')
            conn.commit()
            c.execute(f'''UPDATE datos
                      SET tipo_gas = \"{tipo_gas}\"  
                      WHERE FK_gente = (SELECT ID FROM GENTE WHERE telegram_id = {update.effective_chat.id})''')
            conn.commit()

            gas_db = convertirTablaADiccionario(c, 'gas')
            gas = list(gas_db.values())[0]
            if(tipo_gas == 'safe'):
                gas_medio = str(gas[0])
            elif(tipo_gas == 'medium'):
                gas_medio = str(gas[1])
            else:
                gas_medio = str(gas[2])

            context.bot.send_message(chat_id=update.effective_chat.id, text='You will be notified when the ' + tipo_gas + ' gas price falls below : ' +
                                     context.args[1] + " gwei. \n\nYou can change time alert interval with /time where interval is in minutes.\n\n" + str(tipo_gas).capitalize() + "  gas now is " + gas_medio + " gwei. \n\nIf you have any question please see /info.")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='Argument must only two words.\n\nThe syntax must be /gas_alert + typeOfGas +  number.\nThe possible type of gas are: "safe" , "medium" and "fast". \n\nExample: /gas_alert fast 124. ')
    confirmacion_reset(update, context)


def ubi(update, context):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    ubiPrice = convertirTablaADiccionario(c, 'ubi_price')

    try:
        context.bot.send_message(chat_id=update.effective_chat.id, text="The ubi price is: " + str(
            list(ubiPrice.values())[0][0]) + " usd" + "\n\nIf you have any question please see /info")
    except:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text='Please try again')
    confirmacion_reset(update, context)


def ubi_monthly(update, context):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    ubiPrice = convertirTablaADiccionario(c, 'ubi_price')
    mensual = list(ubiPrice.values())[0][0]*720
    try:
        context.bot.send_message(chat_id=update.effective_chat.id, text='The ubi streaming price right now ' +
                                 str(mensual) + ' usd. \n\nIf you have any question please see /info')
    except:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text='Please try again')
    confirmacion_reset(update, context)


def ubi_monthly_alert(update, context):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # try:
    if not len(context.args) == 1 or not context.args[0].isnumeric():
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Argument must only one number.\n\nThe syntax must be /ubi_monthly_alert + number. \n\nExample: /ubi_monthly_alert 255. ')
        return 0
    else:
        c.execute(f'''UPDATE datos
                    SET ubi_mensual = {context.args[0]}
                    WHERE FK_gente = (SELECT ID FROM GENTE WHERE telegram_id = {update.effective_chat.id})''')
        conn.commit()
        ubiPrice = convertirTablaADiccionario(c, 'ubi_price')
        ingresoMensualFloat = float(list(ubiPrice.values())[0][0])*720
        ingresoMensual = int(ingresoMensualFloat)
        context.bot.send_message(chat_id=update.effective_chat.id, text='You will be notified when the monthly UBI income exceeds : ' +
                                 context.args[0] + " usd. \n\nYou can change time alert interval with /time where interval is in minutes.\n\nThe monthly UBI income now is " + str(ingresoMensual) + " usd.\n\nIf you have any question please see /info")
    # except:
    #     context.bot.send_message(chat_id=update.effective_chat.id, text='Please try again')
    confirmacion_reset(update, context)


def time(update, context):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    datos = convertirTablaADiccionario(c, 'datos')

    if not len(context.args) == 1 or not context.args[0].isnumeric():
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Argument must only one number.\n\nThe syntax must be /time + number. \n\nExample: /time 6.\n\nThe number will set the interval time. ')
    else:
        minutos = int(context.args[0])
        c.execute(f'''UPDATE datos
                    SET tiempo_noti = {minutos}
                    WHERE FK_gente = (SELECT ID FROM GENTE WHERE telegram_id = {update.effective_chat.id})''')
        conn.commit()
        context.bot.send_message(chat_id=update.effective_chat.id, text='Time was set to: ' + str(
            context.args[0]) + ' minutes<a id="emoji-html">&#9203;</a>\n\nIf you have any question please see /info ', parse_mode=telegram.ParseMode.HTML)
    confirmacion_reset(update, context)


def coin(update, context):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    datos = convertirTablaADiccionario(c, 'datos')

    if len(context.args) != 1:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Argument must only one word.\n\nThe syntax must be /coin + coinName. \n\nExample: /coin ethereum.')
    else:
        moneda = context.args[0].lower()
        moneda = apiCoingecko.getCoinId(moneda)
        enviado = buscarCrypto.investigarYmandarPrecio(
            update.effective_chat.id, moneda, datos[update.effective_chat.id][5], datos[update.effective_chat.id][8])
        if enviado == False:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='Crypto not found, try again later\n\nThe syntax must be /coin + coinName. \n\nExample: /coin ethereum. ')
    confirmacion_reset(update, context)


def coin_min_max(update, context):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if len(context.args) != 3 or not context.args[1].isnumeric() or not context.args[2].isnumeric():
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Argument must three words.\n\nThe syntax must be /coin_min_max + coinName + minimumRequiredPrice + maximumRequiredPrice. \n\nExample: /coin_min_max ethereum 1000 2500.')
        return 0

    moneda = context.args[0].lower()
    moneda = apiCoingecko.getCoinId(moneda)
    precioRequeridoMinimo = int(context.args[1])
    precioRequeridoMaximo = int(context.args[2])
    enviado = buscarCrypto.investigarPrecio(moneda)
    if enviado == True:
        datos = convertirTablaADiccionario(c, 'todas_cripto')

        if not moneda in datos:
            print('ahseee')
            print(moneda)
            c.execute(
                f'''INSERT INTO todas_cripto(nombre) VALUES(\'{moneda}\')''')
            conn.commit()

        c.execute(f'''INSERT INTO datos_cripto (FK_gente, FK_todas_cripto, min, max)
                    VALUES (
                        (SELECT ID FROM GENTE WHERE telegram_id = {update.effective_chat.id}),
                        (SELECT ID FROM todas_cripto WHERE nombre = \'{moneda}\'),
                        {precioRequeridoMinimo},
                        {precioRequeridoMaximo})''')
        conn.commit()
        datosCrypto = convertirTablaADiccionario(c, 'datos_cripto')
        persona = datosCrypto[update.effective_chat.id]
        if moneda in persona.keys():
            c.execute(f'''UPDATE datos_cripto
                      SET min = {precioRequeridoMinimo},
                      max = {precioRequeridoMaximo}
                      WHERE 
                      FK_todas_cripto = (SELECT ID FROM todas_cripto WHERE nombre = \'{moneda}\')
                      AND
                      FK_gente = (SELECT ID FROM GENTE WHERE telegram_id = {update.effective_chat.id})''')
            conn.commit()

        datosCrypto = convertirTablaADiccionario(c, 'datos_cripto')
        cant_cripto_new = len(datosCrypto[update.effective_chat.id].keys())
        # sumo 1 al contador
        contador = convertirTablaADiccionario(c, 'contador')
        c.execute(f'''UPDATE contador
                  SET cant_cripto = {cant_cripto_new}
                  WHERE FK_gente = (SELECT ID FROM GENTE WHERE telegram_id = {update.effective_chat.id})''')
        conn.commit()

        precioCryptoAhora = buscarCrypto.investigarPrecioParaNewCryto(moneda)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='You will be notified when the ' + str(moneda).capitalize() + '  exceeds : ' + str(precioRequeridoMaximo) + " or falls bellow " + str(precioRequeridoMinimo) + " usd. \n\nYou can change time alert interval with /time where interval is in minutes.\n\nThe price of " + str(moneda).capitalize() + " now is: " + str(precioCryptoAhora) + " usd\n\nIf you have any question please see /info")
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text='Crypto not found, try again later')

    confirmacion_reset(update, context)


def coin_min_max_remove(update, context):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if not len(context.args) == 1:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Argument must only one words.\n\nThe syntax must be /coin_min_max_remove + coinName . \n\nExample: /coin_min_max_remove ethereum .')
        return 0

    moneda = context.args[0].lower()
    moneda = apiCoingecko.getCoinId(moneda)
    datosCrypto = convertirTablaADiccionario(c, 'datos_cripto')

    if moneda not in datosCrypto[update.effective_chat.id].keys():
        extra = cryptos2(update, context)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Crypto not found, try again later\n\n ' + extra)
        return 0

    c.execute(f'''DELETE FROM datos_cripto
                WHERE FK_todas_cripto = (SELECT ID FROM todas_cripto WHERE nombre = \'{moneda}\')
                AND
                FK_gente = (SELECT ID FROM GENTE WHERE telegram_id = {update.effective_chat.id})''')
    conn.commit()

    c.execute(f'''UPDATE contador
              SET cant_cripto = cant_cripto - 1
              WHERE FK_gente = (SELECT ID FROM GENTE WHERE telegram_id = {update.effective_chat.id})''')
    conn.commit()
    extra = cryptos2(update, context)
    context.bot.send_message(chat_id=update.effective_chat.id, text=str(moneda).capitalize(
    ) + ' has been successfully removed!\n\n' + extra + '\n\nIf you have any question please see /info')

    confirmacion_reset(update, context)


def setDaysGraph(update, context):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if not len(context.args) == 1 or not context.args[0].isnumeric():
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Argument must be a number. The sintax is modify_chart + days, example: /modify_chart 30. ')
        return 0
    dias = int(context.args[0])
    c.execute(f'''UPDATE datos
              SET cant_dias_grafico = {dias}
              WHERE FK_gente = (SELECT ID FROM GENTE WHERE telegram_id = {update.effective_chat.id})''')
    conn.commit()
    context.bot.send_message(
        chat_id=update.effective_chat.id, text='Modify chart successfully. ')
    confirmacion_reset(update, context)


def cryptos(update, context):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    datosCrypto = convertirTablaADiccionario(c, 'datos_cripto')
    persona = datosCrypto[update.effective_chat.id]

    text = 'Your cryptos are:\n '

    cryptoPersona = list(persona.keys())
    valoresPersona = list(persona.values())

    if len(persona) == 0:
        text = 'You do not have saved cryptocurrency yet.'
        return text
    for i in range(len(persona)):
        text += "\n" + str(cryptoPersona[i]).capitalize() + " " + str(
            valoresPersona[i][0]) + " " + str(valoresPersona[i][1])
    return text


def cryptos2(update, context):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    datosCrypto = convertirTablaADiccionario(c, 'datos_cripto')
    persona = datosCrypto[update.effective_chat.id]
    text = 'Your cryptos are: '
    for i in persona.keys():
        text += str(i).capitalize() + " "
    return text


def my_portfolio(update, context):
    text = cryptos(update, context) + \
        '\n\nIf you have any question please see /info'
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    confirmacion_reset(update, context)

def convert(update, context):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    datos = convertirTablaADiccionario(c, 'datos')
    if not len(context.args) == 2 or not context.args[0].isnumeric():
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Argument must only two words.\n\nThe syntax must be /convert + amount + coinName. \n\nExample: /convert 5 cardano .')
        return 0

    moneda = str(context.args[1].lower())
    moneda = apiCoingecko.getCoinId(moneda)
    cantidad = float(context.args[0])
    print(moneda, cantidad)
    enviado = buscarCrypto.investigarYmandarPrecioConCantidad(
        update.effective_chat.id, moneda, cantidad, datos[update.effective_chat.id][5], datos[update.effective_chat.id][8])
    if enviado == False:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text='Crypto not found, try again later')
    confirmacion_reset(update, context)




    if update.effective_chat.id == 805954751:
        try:
            id = context.args[0]
            message = ''
            for i in range(len(context.args)):

                if i == 0:
                    continue
                message = message + str(context.args[i]) + " "

            context.bot.send_message(chat_id=id, text=message)
            context.bot.send_message(
                chat_id=update.effective_chat.id, text='Mensaje enviado con exito!')
        except:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text='No se pudo enviar el mensaje')
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text='No such command')
    confirmacion_reset(update, context)


def bot_code(update, context):
    text = "This is the link to the bot's code: 'aca iria el codigo' \nUse it responsibly, hope you enjoy it.\n\nIf you have any question please see /info"
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=text, parse_mode=telegram.ParseMode.HTML)
    confirmacion_reset(update, context)

def donations(update, context):
    text = "<b> This are the possible addresses to help me out:</b>\n\n<b>Ethereum</b>: 0xb82771a516095658D0975ae97626D131F124b567 \n\n<b>Bitcoin</b>: bc1q0s2tmmhgtneak6mpfkl89d7ywn9vv5qyx968qv \n\n<b>BNB</b> bnb1x4nmn9ccutgu324rdz3vep5lurzsplpf838jmw \n\n<b>Cardano</b>: addr1qy77f2rpc2t36eungfecgzcv56ajlnshfpzs262yu4jy0ffauj5xrs5hr4nexsnnss9sef4m9l8pwjz9q455fetyg7jsauv3vd \n\n<b>DogeCoin</b>: D5e62D8HQvLqAdzSqUMLJcGzJkGzsrBnhB\<b>Litecoin</b>: LTz7PLvuyvonDdALcGcLasWPVPwh15MetP \n\n<b>Bitcoin-Cash</b>: qzkmavmmm2k3qgq6jzrky3pdqskkxldszg54lrrhs4 \n\n<b>Tezos</b>: tz1VtV1stSAwHLFsAocSddKXqEHAYjzLuC1R \n\n<b>Polkadot</b>: 149YS966VfP7NqexXSAuysS6k8RwRcXFKrjdu3DA4XmhezgE \n\n<b>XRP</b>: rQNfyddCyKkBBboo663JQEBjAiGfhiedG1 "
    text2 = '<b> Thank you for helping this community prosper day after day ! </b>'
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text2, parse_mode=telegram.ParseMode.HTML)
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=text, parse_mode=telegram.ParseMode.HTML)
    confirmacion_reset(update, context)

def contact_us(update, context):
    try:
        id = ""
        message = ''
        for i in range(len(context.args)):
            message = message + str(context.args[i]) + " "
        if message == '':
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=' <a id="emoji-html">&#128557;</a> The message could not be sent <a id="emoji-html">&#128557;</a>', parse_mode=telegram.ParseMode.HTML)
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='The sintax must be /contact_us + message, example: /contact_us hello ', parse_mode=telegram.ParseMode.HTML)
            return 0
        try:
            message = str(update.effective_chat.id) + " " + str(update.message.from_user.first_name +
                                                                " " + update.message.from_user.last_name) + " " + message
        except:
            message = str(update.effective_chat.id) + " " + \
                str(update.message.from_user.first_name + message)

        context.bot.send_message(chat_id=id, text=message)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='<a id="emoji-html">&#128515;</a> Message has been sent successfully! <a id="emoji-html">&#128515;</a>', parse_mode=telegram.ParseMode.HTML)
    except:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=' <a id="emoji-html">&#128557;</a> The message could not be sent <a id="emoji-html">&#128557;</a>', parse_mode=telegram.ParseMode.HTML)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='The sintax must be /contact_us + message, example: /contact_us hello ', parse_mode=telegram.ParseMode.HTML)

    confirmacion_reset(update, context)

def info(update, context):
    text = '<b> These are the possible commands:</b> \n\n<strong>ACCOUNT: <a id="emoji-html">&#128188;</a> </strong>\n\n/start: Start the bot. \n/info: Check possible commands. \n/toggle_messages: toggles whether the bot sends notifications or not. \n/time: Set the time interval in which crypto prices / gas prices updates are sent (the default time is 5 minutes). \n/reset_bot: Reset bot data.  \n\n<strong>CRYPTO: <a id="emoji-html">&#128200;</a> </strong>\n\n/coin: See the price of a cryptocurrency. \n/coin_min_max: Set the minimum and maximum value of a cryptocurrency. \n/coin_min_max_remove: Delete a condition previously added.\n/my_portfolio: View saved conditions in /coin_min_max.\n/toggle_chart: Enable or disable the option to send charts together with the price (the default is enabled).\n/modify_chart: set the days in which the chart covers (the default time of the chart is 30 days).\n/convert: convert an amount of a crypto to usd. \n\n<strong>ETHEREUM GAS: <a id="emoji-html">&#9981;</a> </strong>  \n\n/gas: Check gas station. \n/gas_alert: Get alerts on gas prices according to priorities (safe, medium and fast) and a minimum gas price value.\n\n<strong>UNIVERSAL BASIC INCOME: <a id="emoji-html">&#128184;</a> </strong>\n\n/ubi_price: Check ubi price in usd. \n/ubi_monthly: Check ubi "streaming" price right now (ubi_price*720).\n/ubi_monthly_alert: Set desired minimum monthly price of ubi "streaming" (ubi_price * 720).\n\n<strong>OUR COMMUNITY: <a id="emoji-html">&#128080;</a> </strong>\n\n/donations: You can donate a tip and thus help the community, more information at the command. \n/bot_code: Here you will find the link of the bot code, since it is open source\n/contact_us: If you have any questions or want to make a recommendation you can contact us '

    context.bot.send_message(
        chat_id=update.effective_chat.id, text=text, parse_mode=telegram.ParseMode.HTML)
    confirmacion_reset(update, context)

def confirmacion_reset(update, context):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    datos = convertirTablaADiccionario(c, 'datos')
    # print(datos)
    if datos[update.effective_chat.id][4] == 1:
        c.execute(f'''UPDATE datos
              SET confirmation_reset = 0
              WHERE FK_gente = (SELECT ID FROM GENTE WHERE telegram_id = {update.effective_chat.id})''')
        conn.commit()
        context.bot.send_message(
            chat_id=update.effective_chat.id, text='The bot has not been reseted')

def noSuchCommand(update, context):

    text = '<b> These are the possible commands:</b> \n\n<strong>ACCOUNT: <a id="emoji-html">&#128188;</a> </strong>\n\n/start: Start the bot. \n/info: Check possible commands. \n/notification_on: Activate notifications.  \n/notification_off: Deactivate notifications. \n/time: Set the time interval in which crypto prices / gas prices updates are sent (the default time is 5 minutes). \n/reset_bot: Reset bot data.  \n\n<strong>CRYPTO: <a id="emoji-html">&#128200;</a> </strong>\n\n/coin: See the price of a cryptocurrency. \n/coin_min_max: Set the minimum and maximum value of a cryptocurrency. \n/coin_min_max_remove: Delete a condition previously added.\n/my_portfolio: View saved conditions in /coin_min_max.\n/toggle_chart: Enable or disable the option to send charts together with the price (the default is enabled).\n/modify_chart: set the. \n/convert: convert an amount of a crypto to usd. \n\n<strong>ETHEREUM GAS: <a id="emoji-html">&#9981;</a> </strong>  \n\n/gas: Check gas station. \n/gas_alert: Get alerts on gas prices according to priorities (safe, medium and fast) and a minimum gas price value.\n\n<strong>UNIVERSAL BASIC INCOME: <a id="emoji-html">&#128184;</a> </strong>\n\n/ubi_price: Check ubi price in usd. \n/ubi_monthly: Check ubi "streaming" price right now (ubi_price*720).\n/ubi_monthly_alert: Set desired minimum monthly price of ubi "streaming" (ubi_price * 720).\n\n<strong>OUR COMMUNITY: <a id="emoji-html">&#128080;</a> </strong>\n\n/donations: You can donate a tip and thus help the community, more information at the command. \n/bot_code: Here you will find the link of the bot code, since it is open source\n/contact_us: If you have any questions or want to make a recommendation you can contact us '

    context.bot.send_message(
        chat_id=update.effective_chat.id, text='No such command')
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=text, parse_mode=telegram.ParseMode.HTML)
    confirmacion_reset(update, context)
# ------------------------------------------------------------------------------------------------------------


def main():
    try:
        updater = Updater(token=token, use_context=True)
        dispatcher = updater.dispatcher

        start_handler = CommandHandler('start', start)
        resetArgs_handler = CommandHandler('reset_bot', reset_bot)
        toggle_messages_handler = CommandHandler(
            'toggle_messages', toggle_messages)
        gasTracker_handler = CommandHandler('gas', gasTracker_handle)
        level_handler = CommandHandler('gas_alert', gas_alert)
        ubi_handler = CommandHandler('ubi_price', ubi)
        ubi_monthly_handler = CommandHandler('ubi_monthly', ubi_monthly)
        ubi_monthly_alert_handler = CommandHandler(
            'ubi_monthly_alert', ubi_monthly_alert)
        convert_handler = CommandHandler('convert', convert)
        time_handler = CommandHandler('time', time)
        coin_handler = CommandHandler('coin', coin)
        setDaysGraph_handler = CommandHandler('modify_chart', setDaysGraph)
        coin_min_max_handler = CommandHandler('coin_min_max', coin_min_max)
        coin_minMax_remove_handler = CommandHandler(
            'coin_min_max_remove', coin_min_max_remove)
        my_portfolio_handler = CommandHandler('my_portfolio', my_portfolio)
        toggle_chart_handler = CommandHandler('toggle_chart', toggle_chart)
        info_handler = CommandHandler('info', info)
        donations_handler = CommandHandler('donations', donations)
        contact_us_handler = CommandHandler('contact_us', contact_us)
        bot_code_handler = CommandHandler('bot_code', bot_code)
        confirmation_handler = MessageHandler(Filters.regex(
            "^(yes|yeS|yEs|Yes|yES|YeS|YEs|YES|no|nO|NO|No)$"), confirmacion_reset_finish)  # arranque con yes or no y termine ahi
        noCommand_handler = MessageHandler(Filters.command, noSuchCommand)

        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(resetArgs_handler)
        dispatcher.add_handler(gasTracker_handler)
        dispatcher.add_handler(level_handler)
        dispatcher.add_handler(toggle_messages_handler)
        dispatcher.add_handler(ubi_handler)
        dispatcher.add_handler(convert_handler)
        dispatcher.add_handler(ubi_monthly_handler)
        dispatcher.add_handler(ubi_monthly_alert_handler)
        dispatcher.add_handler(time_handler)
        dispatcher.add_handler(coin_handler)
        dispatcher.add_handler(contact_us_handler)
        dispatcher.add_handler(coin_min_max_handler)
        dispatcher.add_handler(coin_minMax_remove_handler)
        dispatcher.add_handler(setDaysGraph_handler)
        dispatcher.add_handler(my_portfolio_handler)
        dispatcher.add_handler(toggle_chart_handler)
        dispatcher.add_handler(info_handler)
        dispatcher.add_handler(confirmation_handler)
        dispatcher.add_handler(bot_code_handler)
        dispatcher.add_handler(donations_handler)
        dispatcher.add_handler(noCommand_handler)

        updater.start_polling()
        updater.idle()
    except:
        pass

main()
