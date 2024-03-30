import streamlit as st
from dateutil.relativedelta import relativedelta
import mysql.connector
import pandas as pd
import streamlit as st
import datetime
from app import crear, vencimientos,modificar, renovar, eliminar,buscar






def main():    
        # Configurar el ancho y alto del lienzo
    st.set_page_config(layout="wide")  # Esto establece el lienzo en modo ancho   
    st.title("Gestor de clientes Ruben Rabbia seguros 🚗"); 
    # Display Options for CRUD Operations
    titulo = st.sidebar.markdown("# Seleccionar operación 💻")
    option = st.sidebar.selectbox("  ", ("Crear 📝", "Vencimientos ⚠️","Buscar 🔎" ,"Modificar ✏️", "Renovar ♻️", "Eliminar ❌"))
    
    
    if option == "Crear 📝": 
        crear()
    elif option == "Vencimientos ⚠️":
        vencimientos()
    elif option == "Buscar 🔎":
        buscar()
    elif option == "Modificar ✏️":
        modificar()
    elif option == "Renovar ♻️":
        renovar()
    elif option == "Eliminar ❌":
        eliminar()
    

if __name__ == "__main__":
    main()
