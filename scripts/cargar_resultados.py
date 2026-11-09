#!/usr/bin/env python3
import os
import sys
import psycopg2

RUTA = sys.argv[1] if len(sys.argv) > 1 else "/data/output/resultado/part-00000"

conn = psycopg2.connect(
    host=os.environ.get("DB_HOST", "db"),
    port=os.environ.get("DB_PORT", "5432"),
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    dbname=os.environ["POSTGRES_DB"],
)
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS resultados (
        categoria TEXT NOT NULL,
        mes TEXT NOT NULL,
        ingreso_total NUMERIC(14,2) NOT NULL,
        PRIMARY KEY (categoria, mes)
    )
""")

cargados = 0
with open(RUTA, encoding="utf-8") as f:
    for linea in f:
        try:
            clave, valor = linea.rstrip("\n").split("\t")
            categoria, mes = clave.split("|")
            cur.execute(
                """INSERT INTO resultados (categoria, mes, ingreso_total)
                   VALUES (%s, %s, %s)
                   ON CONFLICT (categoria, mes)
                   DO UPDATE SET ingreso_total = EXCLUDED.ingreso_total""",
                (categoria, mes, valor),
            )
            cargados += 1
        except ValueError:
            print(f"Línea ignorada: {linea!r}")

conn.commit()
cur.close()
conn.close()
print(f"Registros cargados: {cargados}")