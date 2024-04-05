import streamlit as st
from dateutil.relativedelta import relativedelta
import mysql.connector
import pandas as pd
import datetime
import boto3
import uuid
from boto3.dynamodb.conditions import Key
from appClientes.app import crear_clientes, vencimientos_clientes,modificar_clientes, renovar_clientes, eliminar_clientes,buscar_clientes
from streamlit_option_menu import option_menu
from appSiniestros.agreagar_siniestro import agregarSiniestro_st
from appSiniestros.buscar_siniestro import  buscar_por_patente
from appSiniestros.modificar_siniestro import modificar_registro



def main():
    st.set_page_config(layout="wide")  # Configurar el ancho y alto del lienzo

    # Menú horizontal para seleccionar entre las dos aplicaciones
    selected = option_menu(
        menu_title=None,
        options=["Clientes", "Siniestros"],
        icons=["card-list", "car-front-fill"],
        default_index=0,
        orientation="horizontal",
    )

    # Según la opción seleccionada, ejecuta la función correspondiente
    if selected == "Clientes":
        main_clientes()
    elif selected == "Siniestros":
        main_siniestros2()
        

def main_clientes():
    st.title("Gestor de clientes Ruben Rabbia seguros 📚")
    # Display Options for CRUD Operations
    titulo = st.sidebar.markdown("# Seleccionar operación 💻")
    option = st.sidebar.selectbox("  ", ("Crear 📝", "Vencimientos ⚠️", "Buscar 🔎", "Modificar ✏️", "Renovar ♻️",
                                         "Eliminar ❌"))

    if option == "Crear 📝":
        crear_clientes()
    elif option == "Vencimientos ⚠️":
        vencimientos_clientes()
    elif option == "Buscar 🔎":
        buscar_clientes()
    elif option == "Modificar ✏️":
        modificar_clientes()
    elif option == "Renovar ♻️":
        renovar_clientes()
    elif option == "Eliminar ❌":
        eliminar_clientes()


def main_siniestros2():
    st.title("Gestor de siniestros Ruben Rabbia seguros 🚗")
    titulo = st.sidebar.markdown("# Seleccionar operación 💻")
    option = st.sidebar.selectbox("  ", ("Crear 📝", "Buscar por patente 🔎", "Modificar ✏️"))
    if option == "Crear 📝":
        agregarSiniestro_st()
    elif option == "Buscar por patente 🔎":
        buscar_por_patente()
    elif option == "Modificar ✏️":
        modificar_registro()
    
    




if __name__ == "__main__":
    main()