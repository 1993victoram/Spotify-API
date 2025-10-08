import sqlite3
import pandas as pd  # si tienes instalado pandas (opcional, para ver como tabla bonita)

# Conectar a la base
conn = sqlite3.connect("spotifyAPI.db")  # reemplaza con el nombre real de tu archivo
cursor = conn.cursor()

# Leer la tabla historial
cursor.execute("SELECT * FROM historial")
registros = cursor.fetchall()

# Mostrar los registros
for fila in registros:
    print(fila)

# OPCIONAL: mostrar con pandas en forma de tabla
try:
    df = pd.read_sql_query("SELECT * FROM historial", conn)
    print(df)
except:
    pass

conn.close()
