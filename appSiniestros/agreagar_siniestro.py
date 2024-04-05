import streamlit as st
import boto3

def agregarSiniestro_st():
    st.subheader("Agregar datos de siniestro 📝")

    # Formulario para ingresar los datos
    nombre = st.text_input("Nombre")
    contacto = st.text_input("Contacto")
    compañia = st.selectbox("Compañía", ["RUS", "RIVADAVIA", "COOP"])
    patente = st.text_input("Patente")
    descripcion = st.text_area("Descripción")
    fecha_de_siniestro = st.date_input("Fecha de siniestro")
    fecha_de_denuncia = st.date_input("Fecha de denuncia")

    # Botón para insertar los datos en DynamoDB
    if st.button("Insertar Datos en DynamoDB", type="primary"):
        insertar_siniestro(nombre, contacto, compañia, patente, descripcion, fecha_de_siniestro, fecha_de_denuncia)


def insertar_siniestro(nombre, contacto, compañia, patente, descripcion, fecha_de_siniestro, fecha_de_denuncia):
    try:
        # Aquí debes implementar la lógica para insertar los datos en DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # Ajusta la región según tu configuración
        table = dynamodb.Table('siniestros-rabbia')  # Reemplaza con el nombre de tu tabla en DynamoDB

        # Insertar los datos en la tabla de DynamoDB
        table.put_item(
            Item={
                'Patente': patente,
                'Nombre': nombre,
                'Contacto': contacto,
                'Compañia': compañia,
                'Descripcion': descripcion,
                'FechaSiniestro': str(fecha_de_siniestro),
                'FechaDenuncia': str(fecha_de_denuncia),
            }
        )

        st.success("Datos insertados correctamente en DynamoDB.")
    except Exception as e:
        st.error(f"Error al insertar datos en DynamoDB: {e}")
