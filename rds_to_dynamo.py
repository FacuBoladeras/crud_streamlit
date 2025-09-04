import re
import csv
import io
import uuid
import boto3

TABLE_NAME = "customers"  # usa el mismo nombre que en conexion.py
EXPECTED_COLS = 12  # id_sql + 11 columnas

def _parse_iso_date(s: str):
    """Devuelve (iso, yyyymmdd:int, yyyymm:str) si es YYYY-MM-DD válido; si no, (None, None, None)."""
    if not s or s == "Sin dato":
        return None, None, None
    s = s.strip()
    # formato muy simple: 'YYYY-MM-DD'
    if len(s) == 10 and s[4] == '-' and s[7] == '-' and s[:4].isdigit() and s[5:7].isdigit() and s[8:10].isdigit():
        yyyymmdd = int(s.replace("-", ""))
        yyyymm = s[:7]
        return s, yyyymmdd, yyyymm
    return None, None, None

def parse_sql_file(sql_file_path):
    data = []
    insert_re = re.compile(r"INSERT INTO `customers` VALUES (.*);", re.DOTALL)

    with open(sql_file_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    match = insert_re.search(sql_content)
    if not match:
        print("No se encontraron INSERTs en el SQL.")
        return data

    rows_str = match.group(1)
    rows = re.findall(r"\((.*?)\)", rows_str, re.DOTALL)

    for idx, row in enumerate(rows, start=1):
        reader = csv.reader(io.StringIO(row), delimiter=",", quotechar="'", skipinitialspace=True)
        fields = next(reader)

        if len(fields) < EXPECTED_COLS:
            fields += ["Sin dato"] * (EXPECTED_COLS - len(fields))

        id_sql_raw = fields[0]
        poliza = (fields[3] or "Sin dato").strip()
        venc_raw = (fields[9] or "Sin dato").strip()

        iso, yyyymmdd, yyyymm = _parse_iso_date(venc_raw)

        item = {
            # Claves
            "poliza": poliza,
            "item_id": str(uuid.uuid4()),

            # Fecha (atributos para GSI)
            "vencimiento_de_cuota": iso if iso else "Sin dato",
            # Solo agregamos los atributos de índice si son válidos
            **({"venc_yyyymmdd": yyyymmdd} if yyyymmdd is not None else {}),
            **({"venc_yyyymm": yyyymm} if yyyymm is not None else {}),

            # Resto
            "name": (fields[1] or "Sin dato").strip(),
            "contacto": (fields[2] or "Sin dato").strip(),
            "descripcion": (fields[4] or "Sin dato").strip(),
            "compañia": (fields[5] or "Sin dato").strip(),
            "tipo_de_plan": (fields[6] or "Sin dato").strip(),
            "tipo_de_facturacion": (fields[7] or "Sin dato").strip(),
            "numero_de_cuota": int(fields[8]) if (fields[8] and fields[8].isdigit()) else 0,
            "estado": (fields[10] or "Sin dato").strip(),
            # Traza del SQL original (opcional)
            "id_sql": int(id_sql_raw) if id_sql_raw.isdigit() else id_sql_raw,
        }
        data.append(item)

    return data

def migrate_to_dynamodb(sql_file_path):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)

    items = parse_sql_file(sql_file_path)
    print(f"✅ Total registros a migrar: {len(items)}")

    with table.batch_writer() as batch:
        for item in items:
            try:
                batch.put_item(Item=item)
            except Exception as e:
                print(f"❌ Error al insertar poliza={item.get('poliza')} item_id={item.get('item_id')}: {e}")

if __name__ == "__main__":
    path_file = r"C:\Users\Facu\Downloads\rabia-app.sql"
    migrate_to_dynamodb(path_file)


