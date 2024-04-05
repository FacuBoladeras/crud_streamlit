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


# Función para actualizar un registro
def actualizar_registro(patente, nuevo_nombre, nuevo_contacto, nueva_compania, nueva_descripcion, nueva_fecha_siniestro, nueva_fecha_denuncia):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('siniestros-rabbia')

    # Obtener el registro existente
    registro = obtener_registros_por_patente(patente)
    if not registro:
        st.warning("No se encontraron registros para la patente proporcionada.")
        return

    # Actualizar los campos necesarios
    registro_actualizado = registro[0].copy()  # Tomamos el primer registro de la lista
    if nuevo_nombre:
        registro_actualizado['Nombre'] = nuevo_nombre
    if nuevo_contacto:
        registro_actualizado['Contacto'] = nuevo_contacto
    if nueva_compania:
        registro_actualizado['Compañia'] = nueva_compania
    if nueva_descripcion:
        registro_actualizado['Descripcion'] = nueva_descripcion
    if nueva_fecha_siniestro:
        registro_actualizado['FechaSiniestro'] = nueva_fecha_siniestro.strftime("%Y-%m-%d")
    if nueva_fecha_denuncia:
        registro_actualizado['FechaDenuncia'] = nueva_fecha_denuncia.strftime("%Y-%m-%d")

    # Actualizar el registro en DynamoDB
    table.put_item(Item=registro_actualizado)
    st.success("Registro actualizado correctamente.")

# Función para modificar un registro filtrado por patente
def modificar_registro():
    st.subheader("Modificar registro por patente")

    patente = st.text_input("Ingrese la patente del registro que desea modificar:")
    
    if patente:
            # Obtener el registro por patente
            registro = obtener_registros_por_patente(patente)
            if not registro:
                st.warning("No se encontraron registros para la patente proporcionada.")
                return

            # Mostrar los detalles del registro en un formulario de Streamlit
            st.subheader("Detalles del registro:")
            st.write("Nombre:", registro[0]['Nombre'])
            st.write("Contacto:", registro[0]['Contacto'])
            st.write("Compañia:", registro[0]['Compañia'])
            st.write("Descripción:", registro[0]['Descripcion'])
            st.write("Fecha de siniestro:", registro[0]['FechaSiniestro'])
            st.write("Fecha de denuncia:", registro[0]['FechaDenuncia'])

            st.subheader("Modificar registro:")
            nuevo_nombre = st.text_input("Nuevo nombre:")
            nuevo_contacto = st.text_input("Nuevo contacto:")
            nueva_compania = st.selectbox("Nueva compañía", ["RUS", "RIVADAVIA", "COOP"])
            nueva_descripcion = st.text_area("Nueva descripción:")
            nueva_fecha_siniestro = st.date_input("Nueva fecha de siniestro")
            nueva_fecha_denuncia = st.date_input("Nueva fecha de denuncia")

            # Botón para actualizar el registro
            if st.button("Actualizar registro", type="primary"):
                actualizar_registro(patente, nuevo_nombre, nuevo_contacto, nueva_compania, nueva_descripcion, nueva_fecha_siniestro, nueva_fecha_denuncia)