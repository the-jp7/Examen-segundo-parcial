# Examen Segundo Parcial: Pipeline de datos contenerizado

**Alumno:** Carapia Rocha Juan Pedro
**Matrícula:** 125055450
**Materia:** Manejo Masivo de Datos (Big Data)

## Pregunta de negocio asignada
Mi matrícula termina en 0, por lo que me corresponde:
**Ingreso total (cantidad × precio_unitario) por categoría y mes.**

## Estructura del proyecto
(Aquí pegas el árbol de carpetas del examen)

## Requisitos
- Docker Desktop
- Python 3 (solo para generar el dataset)

## Cómo generar el dataset
```bash
python generar_dataset.py 125055450
```
Se genera `ventas_125055450.csv` (~400 MB, 5 millones de registros).
El CSV **no se sube al repositorio** (está en `.gitignore`); se monta como volumen de solo lectura en el contenedor.

## Cómo levantar el ambiente
(Pendiente: se completa cuando tengamos el docker-compose)

## Evidencias

### A1. Dockerfile de Hadoop


![hadoop version](evidencias/hadoop_version.png)

### B. SSH
(Pendiente)

### C. MapReduce y comparativa de tiempos
(Pendiente)

### D. API y persistencia
(Pendiente)

