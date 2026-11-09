#!/usr/bin/env python3
import sys

ruta = sys.argv[1]
totales = {}

with open(ruta, "r", encoding="utf-8") as f:
    for linea in f:
        try:
            campos = linea.strip().split(",")
            if len(campos) != 8 or campos[0] == "id":
                continue
            mes = campos[1][:7]
            clave = f"{campos[3]}|{mes}"
            centavos = int(round(float(campos[6]) * 100))
            totales[clave] = totales.get(clave, 0) + int(campos[5]) * centavos
        except (ValueError, IndexError):
            continue

for clave, total in sorted(totales.items()):
    print(f"{clave}\t{total / 100:.2f}")