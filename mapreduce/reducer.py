#!/usr/bin/env python3
import sys

clave_actual = None
suma = 0

def emitir(clave, centavos):
    print(f"{clave}\t{centavos / 100:.2f}")

for linea in sys.stdin:
    try:
        clave, valor = linea.rstrip("\n").split("\t")
        valor = int(valor)
    except ValueError:
        continue
    if clave == clave_actual:
        suma += valor
    else:
        if clave_actual is not None:
            emitir(clave_actual, suma)
        clave_actual, suma = clave, valor

if clave_actual is not None:
    emitir(clave_actual, suma)