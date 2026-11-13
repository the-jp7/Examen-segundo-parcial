import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, request, Response

app = Flask(__name__)
app.json.compact = False
app.json.sort_keys = False

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

PAGINA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DataMart · Ingreso por categoría y mes</title>
<style>
  :root { --bg:#f6f7f9; --card:#ffffff; --txt:#1f2430; --muted:#6b7280; --line:#e5e7eb; --acc:37,99,235; }
  @media (prefers-color-scheme: dark) {
    :root { --bg:#0f1218; --card:#171b24; --txt:#e6e8ee; --muted:#9aa3b2; --line:#2a3040; --acc:96,165,250; }
  }
  * { box-sizing:border-box; }
  body { margin:0; padding:24px; background:var(--bg); color:var(--txt);
         font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; }
  .wrap { max-width:1200px; margin:0 auto; }
  h1 { font-size:22px; margin:0 0 4px; }
  p.sub { margin:0 0 18px; color:var(--muted); font-size:14px; }
  .card { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:16px; }
  .barra { display:flex; gap:12px; align-items:center; flex-wrap:wrap; margin-bottom:12px; }
  input { padding:8px 10px; border:1px solid var(--line); border-radius:8px;
          background:var(--bg); color:var(--txt); min-width:220px; }
  .tabla { overflow-x:auto; }
  table { border-collapse:collapse; width:100%; font-size:13px; }
  th, td { padding:8px 10px; text-align:right; white-space:nowrap; border-bottom:1px solid var(--line); }
  th:first-child, td:first-child { text-align:left; font-weight:600; }
  th { color:var(--muted); font-weight:600; }
  td.total { font-weight:600; }
  .nota { margin-top:12px; color:var(--muted); font-size:12px; }
  code { background:var(--bg); padding:1px 5px; border-radius:4px; }
</style>
</head>
<body>
<div class="wrap">
  <h1>Ingreso total por categoría y mes</h1>
  <p class="sub">DataMart · 2025 · cifras en millones. Cuanto más intenso el color, mayor el ingreso.</p>
  <div class="card">
    <div class="barra">
      <input id="filtro" placeholder="Filtrar categoría (ej. Ropa)">
      <span id="resumen" class="sub" style="margin:0"></span>
    </div>
    <div class="tabla"><table id="tabla"></table></div>
    <p class="nota">Datos de <code>GET /resultados</code>. Filtro por categoría: <code>GET /resultados/Ropa</code>.</p>
  </div>
</div>
<script>
const MESES = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"];
const esc = s => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const millones = n => (n / 1e6).toFixed(1);
let datos = [];

function dibujar() {
  const q = document.getElementById("filtro").value.trim().toLowerCase();
  const cats = [...new Set(datos.map(d => d.categoria))].sort().filter(c => c.toLowerCase().includes(q));
  const meses = [...new Set(datos.map(d => d.mes))].sort();
  const mapa = {};
  datos.forEach(d => { mapa[d.categoria + "|" + d.mes] = d.ingreso_total; });
  const vals = datos.map(d => d.ingreso_total);
  const min = Math.min(...vals), max = Math.max(...vals);
  let html = "<tr><th>Categoría</th>" +
    meses.map(m => "<th>" + MESES[parseInt(m.slice(5), 10) - 1] + "</th>").join("") +
    "<th>Total año</th></tr>";
  cats.forEach(c => {
    let total = 0;
    const celdas = meses.map(m => {
      const v = mapa[c + "|" + m];
      if (v === undefined) return "<td>–</td>";
      total += v;
      const a = max === min ? 0.4 : 0.12 + 0.7 * (v - min) / (max - min);
      return '<td style="background:rgba(var(--acc),' + a.toFixed(2) + ')" title="' +
             v.toLocaleString("es-MX", {minimumFractionDigits: 2}) + '">' + millones(v) + "</td>";
    }).join("");
    html += "<tr><td>" + esc(c) + "</td>" + celdas + '<td class="total">' + millones(total) + "</td></tr>";
  });
  document.getElementById("tabla").innerHTML = html;
  document.getElementById("resumen").textContent = cats.length + " categorías · " + datos.length + " registros";
}

fetch("/resultados").then(r => r.json()).then(d => { datos = d; dibujar(); });
document.getElementById("filtro").addEventListener("input", dibujar);
</script>
</body>
</html>"""


@app.get("/ui")
def interfaz():
    return Response(PAGINA, mimetype="text/html")

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