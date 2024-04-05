import streamlit as st
from PIL import Image
import io
import boto3
import uuid
import os

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
    imagenes = st.file_uploader("Cargar imágenes (máx. 4)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    
    imagen_urls = []

    if imagenes is not None:
        for idx, imagen in enumerate(imagenes):
            try:
                # Abrir la imagen utilizando PIL (Pillow)
                img = Image.open(imagen)

                # Redimensionar la imagen si es necesario
                img = img.resize((400, 300))  # Tamaño personalizado (400x300 píxeles)

                # Convertir la imagen en bytes utilizando BytesIO
                image_bytes = io.BytesIO()
                img.save(image_bytes, format="JPEG")  # Guardar la imagen como bytes en formato JPEG

                # Mostrar la imagen en Streamlit
                st.image(img, caption=f"Imagen {idx+1} cargada")

                # Almacenar los bytes de la imagen en una lista
                imagen_urls.append(image_bytes)

            except Exception as e:
                st.error(f"Error al procesar imagen {idx+1}: {e}")

    # Botón para cargar las imágenes en S3 y obtener las URLs públicas
    if st.button("Cargar Imágenes en S3", type="primary") and len(imagen_urls) > 0:
        imagen_s3_urls = []
        s3 = boto3.client('s3', region_name='us-east-1')  # Ajusta la región según tu configuración
        bucket_name = 'siniestros-rabbia'  # Reemplaza con el nombre de tu bucket S3

        for idx, image_bytes in enumerate(imagen_urls):
            try:
                image_filename = f"imagen_{uuid.uuid4().hex[:8]}.jpg"  # Nombre único para la imagen en S3
                s3.upload_fileobj(image_bytes, bucket_name, image_filename)
                imagen_s3_url = f"https://{bucket_name}.s3.amazonaws.com/{image_filename}"
                imagen_s3_urls.append(imagen_s3_url)
            except Exception as e:
                st.error(f"Error al cargar imagen {idx+1} en S3: {e}")

        st.success("Imágenes cargadas en S3 correctamente.")

        # Botón para insertar los datos en DynamoDB
        if st.button("Insertar Datos en DynamoDB", type="primary") and len(imagen_s3_urls) > 0:
            insertar_siniestro(nombre, contacto, compañia, patente, descripcion, fecha_de_siniestro, fecha_de_denuncia, imagen_s3_urls)

def insertar_siniestro(nombre, contacto, compañia, patente, descripcion, fecha_de_siniestro, fecha_de_denuncia, imagen_s3_urls):
    try:
        # Aquí debes implementar la lógica para insertar los datos en DynamoDB
        # junto con las URLs de las imágenes en S3
        dynamodb = boto3.resource('siniestros-rabbia', region_name='us-east-1')  # Ajusta la región según tu configuración
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
                'ImagenesS3': imagen_s3_urls
            }
        )

        st.success("Datos insertados correctamente en DynamoDB.")
    except Exception as e:
        st.error(f"Error al insertar datos en DynamoDB: {e}")


