import sqlite3
conn = sqlite3.connect('database.db')
c = conn.cursor()


def iniciarTabla(c):
    c.execute('''CREATE TABLE IF NOT EXISTS "contador" 
            ("ID"	INTEGER NOT NULL,
                "FK_gente"	INTEGER NOT NULL,
                "contador"	INTEGER,
                "cant_cripto"	INTEGER,
                PRIMARY KEY("ID" AUTOINCREMENT),
                FOREIGN KEY("FK_gente") REFERENCES "gente"("ID")
            );''')
    conn.commit()

    c.execute('''CREATE TABLE IF NOT EXISTS "datos" 
                ("ID"	INTEGER NOT NULL,
        	        "FK_gente"	INTEGER NOT NULL,
        	        "gas_requerido"	INTEGER,
        	        "ubi_mensual"	INTEGER,
        	        "tiempo_noti"	INTEGER,
        	        "confirmation_reset"	INTEGER CHECK("confirmation_reset" == 0 OR "confirmation_reset" == 1),
        	        "allow_graphic"	INTEGER CHECK("allow_graphic" == 0 OR "allow_graphic" == 1),
        	        "info_state"	INTEGER CHECK("info_state" == 0 OR "info_state" == 1),
        	        "tipo_gas"	TEXT CHECK ("tipo_gas" == "safe" OR "tipo_gas" == "medium" OR "tipo_gas" == "fast"),
        	        "cant_dias_grafico"	INTEGER,
        	        FOREIGN KEY("FK_gente") REFERENCES "gente"("ID"),
        	        PRIMARY KEY("ID" AUTOINCREMENT)
                );''')
    conn.commit()

    c.execute('''CREATE TABLE IF NOT EXISTS "datos_cripto" (
	                "FK_gente"	INTEGER NOT NULL,
	                "FK_todas_cripto"	INTEGER NOT NULL,
	                "min"	INTEGER,
	                "max"	INTEGER,
	                PRIMARY KEY("FK_gente","FK_todas_crypto")
                    );''')
    conn.commit()

    c.execute('''CREATE TABLE IF NOT EXISTS "gas" 
                ("ID"	INTEGER NOT NULL,
        	        "bajo"	REAL,
        	        "medio"	REAL,
        	        "alto"	REAL,
        	        PRIMARY KEY("ID" AUTOINCREMENT)
                );''')
    conn.commit()

    c.execute('''CREATE TABLE IF NOT EXISTS "todas_cripto" 
                ("ID"	INTEGER NOT NULL,
                "nombre"	TEXT,
                PRIMARY KEY("ID" AUTOINCREMENT)
                );''')
    conn.commit()

    c.execute('''CREATE TABLE IF NOT EXISTS "ubi_price" 
                ("ID"	INTEGER NOT NULL,
        	        "price"	REAL,
        	        PRIMARY KEY("ID" AUTOINCREMENT)
                );''')
    conn.commit()

    c.execute('''CREATE TABLE IF NOT EXISTS "gente" 
                ("ID"	INTEGER NOT NULL,
        	        "telegram_id"	INTEGER NOT NULL,
        	        "nyap"	TEXT,
        	        PRIMARY KEY("ID")
                );''')

    if len(convertirTablaADiccionario(c, 'gas')) <= 0:
        c.execute(f'''INSERT INTO gas(bajo,medio,alto) VALUES(NULL,NULL,NULL)''')

    if len(convertirTablaADiccionario(c, 'ubi_price')) <= 0:
        c.execute(f'''INSERT INTO ubi_price(price) VALUES (NULL)''')

    conn.commit()


def convertirTablaADiccionario(cursor, tabla, relevant=1):
    cursor = cursor.execute(f"SELECT * from {tabla}")
    names = [description[0] for description in cursor.description]
    # print(names)
    diccionario = {}

    for columna in names:
        if "FK" not in columna:
            continue
        if "FK" in columna:
            tabla_fk = columna.split("_", 1)[1]
            cursorTabla2 = cursor.execute(f'''SELECT * from {tabla_fk}''')
            names = [description[0]
                     for description in cursorTabla2.description] # for description in cursorTabla2.description : names.append(descripcion[0])
            relevant_tabla2 = names[relevant]
            id_tabla2 = names[0]
            # print(id_tabla2)
            cursor = cursor.execute(f'''SELECT {tabla_fk}.{relevant_tabla2}, {tabla}.* FROM {tabla}
                                    INNER JOIN {tabla_fk} ON {tabla}.{columna} = {tabla_fk}.{id_tabla2}
                                    ''')

            if tabla == 'datos_cripto':
                cursor_crypto = cursor.execute(
                    f'''SELECT * FROM todas_cripto''')
                dict_cripto = dict()
                for row in cursor_crypto:
                    dict_cripto[row[0]] = row[1]
                # print(dict_cripto)
                cursor = cursor.execute(f'''SELECT {tabla_fk}.{relevant_tabla2}, {tabla}.* FROM {tabla}
                                    INNER JOIN {tabla_fk} ON {tabla}.{columna} = {tabla_fk}.{id_tabla2}
                                    ''')
                for row in cursor:
                    # print('asge')
                    if row[0] not in diccionario.keys():
                        diccionario[row[0]] = dict()
                    diccionario[row[0]][dict_cripto[row[2]]] = [row[3], row[4]]

                return(diccionario)

            for row in cursor:
                diccionario[row[0]] = list()
                for i in range(len(row)):
                    if i == 0 or i == 1:
                        continue
                    diccionario[row[0]].append(row[i])
            return(diccionario)
            break

    for row in cursor:
        diccionario[row[0]] = list()
        for i in range(len(row)):
            if i == 0:
                continue
            diccionario[row[0]].append(row[i])

    if tabla == 'todas_cripto':
        diccionario = [array[0] for (key, array) in diccionario.items()]

    return(diccionario)


print("Opened database successfully")
iniciarTabla(c)
# print(convertirTablaADiccionario(c,"datos"))
