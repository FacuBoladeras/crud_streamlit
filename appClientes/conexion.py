
import mysql.connector
import streamlit as st


# Función para establecer la conexión con la base de datos
def establecer_conexion():
    try:
        mydb = mysql.connector.connect(
            host="rabbia-db.c1o28sciaahh.us-east-1.rds.amazonaws.com",
            user="admin",
            port=3306,
            password="Soler839",
            database="rabbia"
        )
        mycursor = mydb.cursor(buffered=True)
        return mydb, mycursor
    except mysql.connector.Error as e:
        st.error(f"Error al conectar a la base de datos: {e}")
        return None, None
    
    
# Función para cerrar la conexión con la base de datos
def cerrar_conexion(mydb, mycursor):
    try:
        if mycursor:
            mycursor.close()
        if mydb:
            mydb.close()
    except mysql.connector.Error as e:
        st.error(f"Error al cerrar la conexión: {e}")
