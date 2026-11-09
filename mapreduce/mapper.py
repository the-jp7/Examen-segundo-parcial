#!/usr/bin/env python3
import sys

# Combinación local: acumulamos en un diccionario y emitimos al final.
# Así el mapper manda ~120 líneas en vez de millones.
# Se guarda en centavos (enteros) para evitar errores de punto flotante.
totales = {}

for linea in sys.stdin:
    try:
        campos = linea.strip().split(",")
        if len(campos) != 8 or campos[0] == "id":   # línea mal formada o encabezado
            continue
        mes = campos[1][:7]                          # "YYYY-MM"
        categoria = campos[3]
        cantidad = int(campos[5])
        centavos = int(round(float(campos[6]) * 100))
        if len(mes) != 7 or mes[4] != "-":
            continue
        clave = f"{categoria}|{mes}"
        totales[clave] = totales.get(clave, 0) + cantidad * centavos
    except (ValueError, IndexError):
        continue                                     # no truncar el job por una línea mala

for clave, total in sorted(totales.items()):
    print(f"{clave}\t{total}")