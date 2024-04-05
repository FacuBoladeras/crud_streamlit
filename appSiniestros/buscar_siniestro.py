import boto3
import uuid
import streamlit as st
import pandas as pd
from boto3.dynamodb.conditions import Key

# Función para obtener todos los registros de la tabla de DynamoDB ordenados por fecha de siniestro
def obtener_registros_por_patente(patente):
    dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
    table = dynamodb.Table('siniestros-rabbia')

    # Realizar una consulta utilizando la clave de partición (patente) y ordenando por fecha de siniestro
    response = table.query(
        KeyConditionExpression=Key('Patente').eq(patente),
        ScanIndexForward=True  # Orden ascendente por defecto
    )
    items = response['Items']
    return items


def buscar_por_patente():
    st.subheader("Buscar siniestro por patente 🔎")    

    patente = st.text_input("Ingrese la patente para ver los siniestros: ")

    if st.button("Buscar", type="primary"):
        if patente:        
            # Obtener registros por patente
            data = obtener_registros_por_patente(patente)
            st.subheader("Detalles del siniestro 🧾")
            for item in data:
                st.write(f"Patente: {item['Patente']}")
                st.write(f"Nombre: {item['Nombre']}")
                st.write(f"Contacto: {item['Contacto']}")
                st.write(f"Compañía: {item['Compañia']}")
                st.write(f"Descripción: {item['Descripcion']}")
                st.write(f"Fecha de siniestro: {item['FechaSiniestro']}")
                st.write(f"Fecha de denuncia: {item['FechaDenuncia']}")
                st.write("------------------")
        else:
            st.warning("Ingrese una patente para buscar siniestros.")
