import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, request

app = Flask(__name__)


def get_conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=os.environ.get("DB_PORT", "5432"),
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.environ["POSTGRES_DB"],
    )


def ejecutar(sql, params=(), fetch=False):
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            filas = cur.fetchall() if fetch else cur.rowcount
        conn.commit()
        return filas
    finally:
        conn.close()


def init_db():
    for _ in range(15):
        try:
            ejecutar("""CREATE TABLE IF NOT EXISTS resultados (
                categoria TEXT NOT NULL,
                mes TEXT NOT NULL,
                ingreso_total NUMERIC(14,2) NOT NULL,
                PRIMARY KEY (categoria, mes))""")
            return
        except psycopg2.OperationalError:
            time.sleep(2)


SELECT = "SELECT categoria, mes, ingreso_total::float AS ingreso_total FROM resultados"


@app.get("/")
def home():
    return {"status": "ok"}


@app.get("/resultados")
def listar():
    return jsonify(ejecutar(SELECT + " ORDER BY categoria, mes", fetch=True))


@app.get("/resultados/<categoria>")
def por_categoria(categoria):
    filas = ejecutar(SELECT + " WHERE LOWER(categoria) = LOWER(%s) ORDER BY mes",
                     (categoria,), fetch=True)
    if not filas:
        return {"error": "categoria no encontrada"}, 404
    return jsonify(filas)


@app.post("/resultados")
def crear():
    d = request.get_json(silent=True) or {}
    if not all(k in d for k in ("categoria", "mes", "ingreso_total")):
        return {"error": "faltan campos: categoria, mes, ingreso_total"}, 400
    try:
        ejecutar("INSERT INTO resultados VALUES (%s, %s, %s)",
                 (d["categoria"], d["mes"], d["ingreso_total"]))
    except psycopg2.errors.UniqueViolation:
        return {"error": "ya existe ese registro"}, 409
    return d, 201


@app.put("/resultados/<categoria>/<mes>")
def actualizar(categoria, mes):
    d = request.get_json(silent=True) or {}
    if "ingreso_total" not in d:
        return {"error": "falta ingreso_total"}, 400
    n = ejecutar("UPDATE resultados SET ingreso_total = %s WHERE categoria = %s AND mes = %s",
                 (d["ingreso_total"], categoria, mes))
    if n == 0:
        return {"error": "no encontrado"}, 404
    return {"categoria": categoria, "mes": mes, "ingreso_total": d["ingreso_total"]}


@app.delete("/resultados/<categoria>/<mes>")
def borrar(categoria, mes):
    n = ejecutar("DELETE FROM resultados WHERE categoria = %s AND mes = %s", (categoria, mes))
    if n == 0:
        return {"error": "no encontrado"}, 404
    return {"eliminado": f"{categoria}/{mes}"}


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)