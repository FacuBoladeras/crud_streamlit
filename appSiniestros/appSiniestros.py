import streamlit as st
import boto3
from datetime import datetime

# Configuración de la conexión con DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # Cambia la región según tu configuración
table = dynamodb.Table('siniestros-rabbia')  # Reemplaza 'Nombre_de_tu_tabla' por el nombre de tu tabla en DynamoDB

# Función para insertar datos en la tabla de DynamoDB
def insert(id, nombre, contacto, compañia, descripcion, fecha_inicio, fecha_cobro):
    try:
        # Convertir las fechas a strings
        fecha_inicio_str = fecha_inicio.strftime("%Y-%m-%d")
        fecha_cobro_str = fecha_cobro.strftime("%Y-%m-%d")

        # Insertar los datos en la tabla de DynamoDB
        table.put_item(
            Item={
                'id': id,
                'Nombre': nombre,
                'Contacto': contacto,
                'Compañia': compañia,
                'Descripcion': descripcion,
                'FechaInicio': fecha_inicio_str,
                'FechaCobro': fecha_cobro_str
            }
        )

        # Mostrar mensaje de éxito
        st.success("Datos insertados correctamente en DynamoDB.")
    except Exception as e:
        # Mostrar mensaje de error en caso de que ocurra una excepción
        st.error(f"Error al insertar datos en DynamoDB: {e}")

# Interfaz de usuario para ingresar datos y llamar a la función insert
def main():
    st.title("Inserción de Datos en DynamoDB")

    # Formulario para ingresar los datos
    id =st.text_input("user")
    nombre = st.text_input("Nombre")
    contacto = st.text_input("Contacto")
    compañia = st.selectbox("Compañía", ["RUS", "RIVADAVIA", "COOP"])
    descripcion = st.text_area("Descripción")
    fecha_inicio = st.date_input("Fecha de inicio")
    fecha_cobro = st.date_input("Fecha de cobro")

    # Botón para insertar los datos
    if st.button("Insertar Datos"):
        # Llamar a la función insert con los datos ingresados por el usuario
        insert(id,nombre, contacto, compañia, descripcion, fecha_inicio, fecha_cobro)




import pandas as pd
import streamlit as st

# Función para obtener todos los registros de la tabla de DynamoDB
def scan_dynamodb_table():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('siniestros-rabbia')
    response = table.scan()
    items = response['Items']
    return items

# Obtener todos los registros de la tabla DynamoDB
data = scan_dynamodb_table()

# Convertir los datos en un DataFrame de Pandas
df = pd.DataFrame(data)

# Ordenar el DataFrame por la columna "Fecha de cobro"
df_sorted = df.sort_values(by='FechaCobro', ascending=False)

# Mostrar el DataFrame ordenado en Streamlit como una tabla
st.write(df_sorted)


# Función para consultar datos por campo de fecha
main()
