import boto3
import pandas as pd

# Leer el archivo CSV
file_path = r'C:\Users\Facundo\Downloads\2025-01-23T13-17_export.csv'  # Reemplázalo por la ruta correcta
df = pd.read_csv(file_path)

# Conectar con DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Nombre de la tabla en DynamoDB
table_name = 'siniestros-rabbia'  # Cambia por el nombre real de tu tabla
table = dynamodb.Table(table_name)

# Recorrer cada fila e insertarla en DynamoDB
for index, row in df.iterrows():
    item = {
        'Patente': str(row['Patente']),  # Clave primaria
        'Compañia': row['Compañia'],
        'Nombre': row['Nombre'],
        'Descripcion': row['Descripcion'],
        'FechaSiniestro': row['FechaSiniestro'],
        'FechaDenuncia': row['FechaDenuncia'],
        'Contacto': str(row['Contacto']) if pd.notna(row['Contacto']) else None
    }
    
    # Insertar en DynamoDB
    table.put_item(Item=item)
    print(f"Fila {index + 1} insertada con éxito")

print("¡Carga de datos completada!")
