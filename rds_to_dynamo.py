import re
import csv
import io
import boto3
import uuid
from collections import defaultdict

TABLE_NAME = "customers"
EXPECTED_COLS = 12  # id + 11 columnas reales

def parse_sql_file(sql_file_path):
    data = []
    insert_re = re.compile(r"INSERT INTO `customers` VALUES (.*);", re.DOTALL)
    duplicates_counter = defaultdict(int)

    with open(sql_file_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    match = insert_re.search(sql_content)
    if match:
        rows_str = match.group(1)
        rows = re.findall(r"\((.*?)\)", rows_str, re.DOTALL)

        for idx, row in enumerate(rows, start=1):
            reader = csv.reader(io.StringIO(row), delimiter=",", quotechar="'", skipinitialspace=True)
            fields = next(reader)

            if len(fields) < EXPECTED_COLS:
                fields += ["Sin dato"] * (EXPECTED_COLS - len(fields))

            poliza = (fields[3] or "Sin dato").strip()
            vencimiento = (fields[9] or "1900-01-01").strip()

            # clave compuesta (poliza + vencimiento)
            key = (poliza, vencimiento)
            duplicates_counter[key] += 1

            # si es duplicado, agregamos sufijo
            if duplicates_counter[key] > 1:
                vencimiento = f"{vencimiento}#{duplicates_counter[key]}"
            item = {
                "poliza": poliza,                          # PartitionKey
                "id_sql": int(fields[0]) if fields[0].isdigit() else 0,  # SortKey
                "vencimiento_de_cuota": vencimiento,       # Para GSI
                "name": (fields[1] or "Sin dato").strip(),
                "contacto": (fields[2] or "Sin dato").strip(),
                "descripcion": (fields[4] or "Sin dato").strip(),
                "compañia": (fields[5] or "Sin dato").strip(),
                "tipo_de_plan": (fields[6] or "Sin dato").strip(),
                "tipo_de_facturacion": (fields[7] or "Sin dato").strip(),
                "numero_de_cuota": int(fields[8]) if fields[8].isdigit() else 0,
                "estado": (fields[10] or "Sin dato").strip(),
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
                print(f"❌ Error al insertar poliza={item.get('poliza')} id_sql={item.get('id_sql')}: {e}")



path_file = r"C:\Users\Facundo\Desktop\rabia-app.sql"
if __name__ == "__main__":
    migrate_to_dynamodb(path_file)
