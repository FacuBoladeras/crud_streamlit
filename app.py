import streamlit as st
from streamlit_option_menu import option_menu

# Importar funciones de clientes
from appClientes.clientes import (
    crear_clientes,
    vencimientos_clientes,    
    ultimos_20_clientes_ingresados,
    modificar_clientes,   
    eliminar_clientes,
    buscar_clientes,
    ultimos_20_vencidos
)

# Importar funciones de siniestros
from appSiniestros.Siniestros import (
    main_siniestros,
    buscar_por_patente,
    modificar_registro,
    mostrar_ultimos_20_registros
)

def main():
    st.set_page_config(layout="wide")  # Configurar el ancho y alto del lienzo
    
    # Cuadro para "Seleccionar app"
    st.markdown(
        """
        <div style="
            border: 3px solid #3C559A; 
            padding: 4px; 
            border-radius: 8px; 
            font-size: 24px;  
            background-color: #EEF3F7;
            color: #000000;
            box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.1);
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;">
            ⬇︎ Seleccionar sección ⬇︎
        </div>
        """,
        unsafe_allow_html=True
    )
    # Menú horizontal para seleccionar entre las dos aplicaciones
    selected = option_menu(
        menu_title=None,
        options=["Clientes", "Siniestros"],
        icons=["card-list", "car-front-fill"],
        default_index=0,
        orientation="horizontal",
    )

    # Selección de módulo
    if selected == "Clientes":
        main_clientes()
    elif selected == "Siniestros":
        main_siniestros2()

def main_clientes():
    st.title("Gestor de clientes Ruben Rabbia seguros 📚")

    # Caja con borde de color personalizado
    st.sidebar.markdown(
        """
        <div style="
            border: 3px solid #3C559A; 
            padding: 10px; 
            border-radius: 8px; 
            font-size: 22px; 
            background-color: #EEF3F7;
            color: #000000;
            box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.1);
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;">
            Seleccionar operación 💻
        </div>
        """,
        unsafe_allow_html=True
    )
    # Inicializar la variable de sesión para la selección predeterminada
    if "selected_option" not in st.session_state:
        st.session_state.selected_option = "Crear 📝"

    # Opciones CRUD para clientes
    options = {
        "Crear 📝": crear_clientes,
        "Vencimientos ⚠️": vencimientos_clientes,    
        "Últimos ingresados 📄": ultimos_20_clientes_ingresados,
        "Buscar 🔎": buscar_clientes,
        "Modificar ✏️": modificar_clientes,        
        "Eliminar ❌": eliminar_clientes,
        "Vencidos 📄": ultimos_20_vencidos
    }

    # Crear botones y actualizar el estado de la opción seleccionada con claves únicas
    for key, function in options.items():
        if st.sidebar.button(key, key=f"btn_{key}", type="primary", use_container_width=True):
            st.session_state.selected_option = key

    # Ejecutar la función correspondiente a la opción seleccionada
    options[st.session_state.selected_option]()


def main_siniestros2():
    st.title("Gestor de siniestros Ruben Rabbia seguros 🚗")

    st.sidebar.markdown(
        """
        <div style="
            border: 3px solid #3C559A; 
            padding: 10px; 
            border-radius: 8px; 
            font-size: 22px; 
            background-color: #EEF3F7;
            color: #000000;
            box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.1);
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;">
            Seleccionar operación 💻
        </div>
        """,
        unsafe_allow_html=True
    )

    # Inicializar la variable de sesión para la selección predeterminada
    if "selected_option_siniestros" not in st.session_state:
        st.session_state.selected_option_siniestros = "Crear 📝"

    # Opciones CRUD para siniestros
    options = {
        "Crear 📝": main_siniestros,
        "Buscar por patente 🔎": buscar_por_patente,
        "Ultimos ingresados 📅": mostrar_ultimos_20_registros,
        "Modificar ✏️": modificar_registro,
    }

    # Crear botones y actualizar el estado de la opción seleccionada con claves únicas
    for key, function in options.items():
        if st.sidebar.button(key, key=f"btn_siniestros_{key}", type="primary", use_container_width=True):
            st.session_state.selected_option_siniestros = key

    # Ejecutar la función correspondiente a la opción seleccionada
    options[st.session_state.selected_option_siniestros]()

if __name__ == "__main__":
    main()
