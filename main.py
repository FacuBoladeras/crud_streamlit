import streamlit as st
from dateutil.relativedelta import relativedelta
import mysql.connector
import pandas as pd
import streamlit as st
import datetime
from appClientes.app import crear_clientes, vencimientos_clientes,modificar_clientes, renovar_clientes, eliminar_clientes,buscar_clientes, logica_de_pago
from appSiniestros.Siniestros import main_siniestros,buscar_por_patente,modificar_registro
from streamlit_option_menu import option_menu


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
    option = st.sidebar.selectbox("  ", ("Crear 📝", "Vencimientos ⚠️", "Logica de pago 💵", "Buscar 🔎", "Modificar ✏️", "Renovar ♻️",
                                         "Eliminar ❌"))

    if option == "Crear 📝":
        crear_clientes()
    elif option == "Vencimientos ⚠️":
        vencimientos_clientes()
    elif option == "Logica de pago 💵":
        logica_de_pago()
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
        main_siniestros()
    elif option == "Buscar por patente 🔎":
        buscar_por_patente()
    elif option == "Modificar ✏️":
        modificar_registro()

    
    




if __name__ == "__main__":
    main()