import mysql.connector
import pandas as pd
from functools import wraps
import streamlit as st
import datetime
from appClientes.conexion import establecer_conexion, cerrar_conexion
from urllib.parse import quote
                        # Añadir tipo_estado al key para hacerlos únicos
import time



def manejar_conexion(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Establecer conexión
        mydb, mycursor = establecer_conexion()
        
        # Ejecutar la función con la conexión
        result = func(mydb, mycursor, *args, **kwargs)
        
        # Cerrar conexión
        cerrar_conexion(mydb, mycursor)
        
        return result
    return wrapper


@manejar_conexion
def crear_clientes(mydb, mycursor):    
    st.subheader("Agregar usuario ✅")
    name = st.text_input("Nombre")
    contacto = st.text_input("Contacto")
    poliza = st.text_input("Poliza")
    descripcion = st.text_input("Descripción")
    compañia = st.selectbox("Compañia", ["RIVADAVIA", "RUS", "COOP"])
    tipo_de_plan = st.selectbox("Duración del plan", ["Anual", "Semestral"])
    tipo_de_facturacion = st.selectbox("Tipo de facturacion", ["Trimestral", "Cuatrimestral", "Semestral", "Anual"])
    numero_de_cuota = st.selectbox("Numero de cuota", [0, 1, 2, 3, 4])
    vencimiento_de_cuota = st.date_input("Vencimiento de la cuota")
    estado = st.selectbox("Estado de la cuota", ["Sin pagar", "Pagado", "Avisado"])

    if st.button("Crear", type="primary"):
        if name and contacto and poliza:
            sql_check_poliza = "SELECT * FROM customers WHERE poliza = %s"
            val_check_poliza = (poliza,)
            mycursor.execute(sql_check_poliza, val_check_poliza)
            existing_poliza = mycursor.fetchone()

            if existing_poliza:
                st.warning("La póliza ingresada ya existe. Por favor, ingresa una póliza diferente.")
            else:
                try:
                    sql = "INSERT INTO customers (name, contacto, poliza, descripcion, compañia, tipo_de_plan, tipo_de_facturacion, numero_de_cuota, vencimiento_de_cuota, estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    val = (name, contacto, poliza, descripcion, compañia, tipo_de_plan, tipo_de_facturacion, numero_de_cuota, vencimiento_de_cuota, estado)
                    mycursor.execute(sql, val)
                    mydb.commit()
                    st.success("Creado exitosamente ✅")
                except Exception as e:
                    st.error(f"Error al crear el usuario: {e}")
        else:
            st.warning("Por favor completa todos los campos antes de continuar.")

@manejar_conexion
def vencimientos_clientes(mydb, mycursor):
    st.subheader("Vencimientos de cuotas 📜")
    compañia = st.selectbox("Seleccionar compañia", ["RIVADAVIA", "RUS", "COOP"])

    today = datetime.date.today()

    sql_0_7_days = "SELECT * FROM customers WHERE compañia = %s AND vencimiento_de_cuota BETWEEN %s AND %s AND estado IN ('Sin pagar', 'Avisado') ORDER BY vencimiento_de_cuota ASC"
    val_0_7_days = (compañia, today, today + datetime.timedelta(days=7))
    mycursor.execute(sql_0_7_days, val_0_7_days)
    result_0_7_days = mycursor.fetchall()

    sql_8_15_days = "SELECT * FROM customers WHERE compañia = %s AND vencimiento_de_cuota BETWEEN %s AND %s AND estado IN ('Sin pagar', 'Avisado') ORDER BY vencimiento_de_cuota ASC"
    val_8_15_days = (compañia, today + datetime.timedelta(days=8), today + datetime.timedelta(days=15))
    mycursor.execute(sql_8_15_days, val_8_15_days)
    result_8_15_days = mycursor.fetchall()

    sql_expired = "SELECT * FROM customers WHERE compañia = %s AND vencimiento_de_cuota < %s AND estado = 'Sin pagar' ORDER BY vencimiento_de_cuota ASC LIMIT 20"
    val_expired = (compañia, today)
    mycursor.execute(sql_expired, val_expired)
    result_expired = mycursor.fetchall()

    def mostrar_tabla(resultados, titulo, mostrar_checkbox=False, tipo_estado=""):
        st.subheader(titulo)
        for row in resultados:
            nombre_cliente = row[1].strip().upper()  # Eliminar espacios en blanco y convertir a mayúsculas
            poliza_cliente = row[3].strip()  # Eliminar espacios en blanco
            
            with st.expander(f"**{nombre_cliente}** - Póliza: **{poliza_cliente}**", expanded=False):
                st.markdown(
                    f"""
                    <div style="font-size: 16px; line-height: 1.5; color: #333;">
                        <p><strong>Nombre:</strong> <span style="font-weight:bold; color:#3C559A;">{row[1]}</span></p>
                        <p><strong>Contacto:</strong> {row[2]}</p>
                        <p><strong>Póliza:</strong> {row[3]}</p>
                        <p><strong>Descripción:</strong> {row[4]}</p>
                        <p><strong>Compañía:</strong> {row[5]}</p>
                        <p><strong>Tipo de plan:</strong> {row[6]}</p>
                        <p><strong>Tipo de facturación:</strong> {row[7]}</p>
                        <p><strong>Número de cuota:</strong> {row[8]}</p>
                        <p><strong>Vencimiento de cuota:</strong> {row[9]}</p>
                        <p><strong>Estado:</strong> {row[10]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


                if mostrar_checkbox:
                    if row[10] == 'Sin pagar':
                        avisado = st.checkbox("Marcar como Avisado", key=f"avisado_{row[0]}")
                        pagado = st.checkbox("Marcar como Pagado", key=f"pagado_{row[0]}")

                        if avisado:
                            try:
                                sql_update = "UPDATE customers SET estado = 'Avisado' WHERE id = %s"
                                mycursor.execute(sql_update, (row[0],))
                                mydb.commit()
                                st.success("Estado actualizado a Avisado")
                            except Exception as e:
                                st.error(f"Error al actualizar el estado: {e}")

                        elif pagado:
                            try:
                                sql_update = "UPDATE customers SET estado = 'Pagado' WHERE id = %s"
                                mycursor.execute(sql_update, (row[0],))
                                mydb.commit()
                                st.success("Estado actualizado a Pagado")
                            except Exception as e:
                                st.error(f"Error al actualizar el estado: {e}")

                    elif row[10] == 'Avisado':
                        pagado = st.checkbox("Marcar como Pagado", key=f"{tipo_estado}_pagado_{row[0]}")
                        if pagado:
                            try:
                                sql_update = "UPDATE customers SET estado = 'Pagado' WHERE id = %s"
                                mycursor.execute(sql_update, (row[0],))
                                mydb.commit()
                                st.success("Estado actualizado a Pagado")
                            except Exception as e:
                                st.error(f"Error al actualizar el estado: {e}")


    mostrar_tabla(result_0_7_days, "Vencimiento en los próximos 7 días", mostrar_checkbox=True, tipo_estado="sin_pagar")
    mostrar_tabla(result_8_15_days, "Vencimiento desde los 8 a los 15 días", mostrar_checkbox=True, tipo_estado="sin_pagar")
    mostrar_tabla(result_expired, "Cuotas vencidas", mostrar_checkbox=True, tipo_estado="sin_pagar")

@manejar_conexion
def avisados(mydb, mycursor):
    

    # Consulta SQL para obtener los últimos 20 clientes con estado "Avisado"
    sql_avisado = """
        SELECT id, name, contacto, poliza, descripcion, compañia, tipo_de_plan, tipo_de_facturacion, 
               numero_de_cuota, vencimiento_de_cuota, estado 
        FROM customers 
        WHERE estado = 'Avisado' 
        ORDER BY id DESC 
        LIMIT 20
    """
    mycursor.execute(sql_avisado)
    resultados_avisado = mycursor.fetchall()

    # Consulta SQL para obtener los últimos 20 clientes con estado "Pagado"
    sql_pagado = """
        SELECT id, name, contacto, poliza, descripcion, compañia, tipo_de_plan, tipo_de_facturacion, 
               numero_de_cuota, vencimiento_de_cuota, estado 
        FROM customers 
        WHERE estado = 'Pagado' 
        ORDER BY id DESC 
        LIMIT 20
    """
    mycursor.execute(sql_pagado)
    resultados_pagado = mycursor.fetchall()

    # Definir nombres de columnas
    columnas = [
        "ID", "Nombre", "Contacto", "Póliza", "Descripción", 
        "Compañía", "Tipo de Plan", "Tipo de Facturación", 
        "Número de Cuota", "Vencimiento de Cuota", "Estado"
    ]

    # Mostrar los clientes "Avisado"
    st.subheader("Avisados")
    if resultados_avisado:
        df_avisado = pd.DataFrame(resultados_avisado, columns=columnas)
        st.dataframe(df_avisado, hide_index=True, use_container_width=True)
    else:
        st.info("No hay clientes con estado 'Avisado' en este momento.")

    # Espacio entre los DataFrames
    st.markdown("---")

    # Mostrar los clientes "Pagado"
    st.subheader("Pagados")
    if resultados_pagado:
        df_pagado = pd.DataFrame(resultados_pagado, columns=columnas)
        st.dataframe(df_pagado, hide_index=True, use_container_width=True)
    else:
        st.info("No hay clientes con estado 'Pagado' en este momento.")



@manejar_conexion
def buscar_clientes(mydb, mycursor):
    st.subheader("Buscar usuario 🔎")
    option = st.selectbox(" ", ("Por poliza 📝", "Por nombre 🧑"))
    
    if option == "Por poliza 📝":
        poliza_value = st.text_input("Ingrese el valor de la póliza a filtrar").strip()
        
        sql = "SELECT * FROM customers WHERE poliza = %s ORDER BY id DESC LIMIT 1"
        val = (poliza_value,)
        mycursor.execute(sql, val)
        result = mycursor.fetchone()
        
        if result:
            st.text(f"Nombre actual: {result[1]}")
            st.text(f"Contacto actual: {result[2]}")
            st.text(f"Póliza actual: {result[3]}")
            st.text(f"Descripcion actual: {result[4]}")
            st.text(f"Compañia actual: {result[5]}")
            st.text(f"Tipo de plan actual: {result[6]}")
            st.text(f"Tipo de facturacion actual: {result[7]}")
            st.text(f"Numero de cuota: {result[8]}")
            st.text(f"Vencimiento de cuota: {result[9]}")
            st.text(f"Estado de cuota: {result[10]}")

            
    elif option == "Por nombre 🧑":
        nombre_value = st.text_input("Ingrese el nombre a filtrar").strip()
        
        sql = "SELECT * FROM customers WHERE name = %s ORDER BY id DESC LIMIT 1"
        val = (nombre_value,)
        mycursor.execute(sql, val)
        result = mycursor.fetchone()
        
        if result:
            st.text(f"Nombre actual: {result[1]}")
            st.text(f"Contacto actual: {result[2]}")
            st.text(f"Póliza actual: {result[3]}")
            st.text(f"Descripcion actual: {result[4]}")
            st.text(f"Compañia actual: {result[5]}")
            st.text(f"Tipo de plan actual: {result[6]}")
            st.text(f"Tipo de facturacion actual: {result[7]}")
            st.text(f"Numero de cuota: {result[8]}")
            st.text(f"Vencimiento de cuota: {result[9]}")
            st.text(f"Estado de cuota: {result[10]}")


            
@manejar_conexion
def modificar_clientes(mydb, mycursor):    
    st.subheader("Buscar y modificar usuario 🔎")

    # Seleccionar el criterio de búsqueda
    option = st.selectbox("Buscar por:", ["Por poliza 📝", "Por nombre 🧑"])
    
    if option == "Por poliza 📝":
        poliza_value = st.text_input("Ingrese el valor de la póliza a filtrar").strip()

        sql = "SELECT * FROM customers WHERE poliza = %s"
        val = (poliza_value,)
        mycursor.execute(sql, val)
        result = mycursor.fetchone()                 
                    
        if result:
            st.text(f"Nombre actual: {result[1]}")
            st.text(f"Contacto actual: {result[2]}")
            st.text(f"Póliza actual: {result[3]}")
            st.text(f"Descripcion actual: {result[4]}")
            st.text(f"Compañia actual: {result[5]}")
            st.text(f"Tipo de plan actual: {result[6]}")
            st.text(f"Tipo de facturacion actual: {result[7]}")
            st.text(f"Numero de cuota: {result[8]}")
            st.text(f"Vencimiento de cuota: {result[9]}")
            st.text(f"Estado de cuota: {result[10]}")
            
            st.subheader("Modificar usuario ✏️")
            name = st.text_input("Nombre", value=result[1])
            contacto = st.text_input("Contacto", value=result[2])
            poliza = st.text_input("Poliza", value=result[3])
            descripcion = st.text_input("Descripción", value=result[4])
            compañia = st.selectbox("Compañia", ["RIVADAVIA", "RUS", "COOP"], index=["RIVADAVIA", "RUS", "COOP"].index(result[5]))
            tipo_de_plan = st.selectbox("Tipo de plan", ["Anual", "Semestral"], index=["Anual", "Semestral"].index(result[6]))
            tipo_de_facturacion = st.selectbox("Tipo de facturacion", ["Trimestral", "Cuatrimestral", "Semestral", "Anual"], index=["Trimestral", "Cuatrimestral", "Semestral", "Anual"].index(result[7]))
            numero_de_cuota = st.selectbox("Numero de cuota", [0, 1, 2, 3, 4], index=[0, 1, 2, 3, 4].index(result[8]))
            vencimiento_de_cuota = st.date_input("Vencimiento de cuota", value=result[9])

            if st.button("Modificar", type="primary"):
                sql_update = "UPDATE customers SET name=%s, contacto=%s, poliza=%s, descripcion=%s, compañia=%s, tipo_de_plan=%s, tipo_de_facturacion=%s, numero_de_cuota=%s, vencimiento_de_cuota=%s WHERE poliza = %s"
                val_update = (name, contacto, poliza, descripcion, compañia, tipo_de_plan, tipo_de_facturacion, numero_de_cuota, vencimiento_de_cuota, poliza_value)
                try:
                    mycursor.execute(sql_update, val_update)
                    mydb.commit()
                    st.success("Registro actualizado correctamente ✅")
                except Exception as e:
                    st.error(f"Error al actualizar el registro: {e}")

    elif option == "Por nombre 🧑":
        nombre_value = st.text_input("Ingrese el nombre a filtrar").strip()
        
        sql = "SELECT * FROM customers WHERE name = %s"
        val = (nombre_value,)
        mycursor.execute(sql, val)
        result = mycursor.fetchone()
        
        if result:
            st.text(f"Nombre actual: {result[1]}")
            st.text(f"Contacto actual: {result[2]}")
            st.text(f"Póliza actual: {result[3]}")
            st.text(f"Descripción actual: {result[4]}")
            st.text(f"Compañia actual: {result[5]}")
            st.text(f"Tipo de plan actual: {result[6]}")
            st.text(f"Tipo de facturacion actual: {result[7]}")
            st.text(f"Numero de cuota: {result[8]}")
            st.text(f"Vencimiento de cuota: {result[9]}")
            st.text(f"Estado de cuota: {result[10]}")
            
            st.subheader("Modificar usuario ✏️")
            name = st.text_input("Nombre", value=result[1])
            contacto = st.text_input("Contacto", value=result[2])
            poliza = st.text_input("Poliza", value=result[3])
            descripcion = st.text_input("Descripción", value=result[4])
            compañia = st.selectbox("Compañia", ["RIVADAVIA", "RUS", "COOP"], index=["RIVADAVIA", "RUS", "COOP"].index(result[5]))
            tipo_de_plan = st.selectbox("Tipo de plan", ["Anual", "Semestral"], index=["Anual", "Semestral"].index(result[6]))
            tipo_de_facturacion = st.selectbox("Tipo de facturacion", ["Trimestral", "Cuatrimestral", "Semestral", "Anual"], index=["Trimestral", "Cuatrimestral", "Semestral", "Anual"].index(result[7]))
            numero_de_cuota = st.selectbox("Numero de cuota", [0, 1, 2, 3, 4], index=[0, 1, 2, 3, 4].index(result[8]))
            vencimiento_de_cuota = st.date_input("Vencimiento de cuota", value=result[9])

            if st.button("Modificar", type="primary"):
                sql_update = "UPDATE customers SET name=%s, contacto=%s, poliza=%s, descripcion=%s, compañia=%s, tipo_de_plan=%s, tipo_de_facturacion=%s, numero_de_cuota=%s, vencimiento_de_cuota=%s WHERE name = %s"
                val_update = (name, contacto, poliza, descripcion, compañia, tipo_de_plan, tipo_de_facturacion, numero_de_cuota, vencimiento_de_cuota, nombre_value)
                try:
                    mycursor.execute(sql_update, val_update)
                    mydb.commit()
                    st.success("Registro actualizado correctamente ✅")
                except Exception as e:
                    st.error(f"Error al actualizar el registro: {e}")



@manejar_conexion
def renovar_clientes(mydb, mycursor):
        st.subheader("Renovar cuota ♻️")        
        # Campo para ingresar el valor de la póliza a filtrar
        poliza_value = st.text_input("Ingrese el valor de la póliza a filtrar").strip()

        # Consulta SQL para buscar el último registro con el valor de la póliza ingresado
        sql = "SELECT * FROM customers WHERE poliza = %s ORDER BY id DESC LIMIT 1"
        val = (poliza_value,)
        mycursor.execute(sql, val)
        result = mycursor.fetchone()  # Obtener el último registro que coincida (debería ser único)


        # Si se encuentra un registro coincidente, mostrar los datos actuales
        if result:
            st.text("ULTIMA CUOTA INGRESADA:")
            st.text(f"Nombre actual: {result[1]}")
            st.text(f"Contacto actual: {result[2]}")
            st.text(f"Póliza actual: {result[3]}")
            st.text(f"Descripcion actual: {result[4]}")
            st.text(f"Compañia actual: {result[5]}")
            st.text(f"Tipo de plan actual: {result[6]}")
            st.text(f"Tipo de facturacion: {result[7]}")
            st.text(f"Numero de cuota: {result[8]}")
            st.text(f"Vencimiento de cuota: {result[9]}")
            st.text(f"Estado de cuota: {result[10]}")
            
            
            st.subheader("Modificar usuario ✏️")
            # Campos para ingresar los nuevos valores  
            numero_de_cuota = st.selectbox("Número de cuota", [0, 1, 2, 3, 4], index=[0, 1, 2, 3, 4].index(result[8]))
            vencimiento_de_cuota = st.date_input("Vencimiento de cuota", value=result[9])

            if st.button("Renovar", type="primary"):
                # Crear una lista con los valores modificados
                modified_values = list(result)
                modified_values[8] = numero_de_cuota  # Índice de la columna 'numero_de_cuota'
                modified_values[9] = vencimiento_de_cuota  # Índice de la columna 'vencimiento_de_cuota'

                # Insertar un nuevo registro con los valores modificados
                sql_insert = "INSERT INTO customers (name, contacto, poliza, descripcion, compañia, tipo_de_plan, tipo_de_facturacion, numero_de_cuota, vencimiento_de_cuota,estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s)"
                val_insert = tuple(modified_values[1:])  # Ignorar el ID al insertar
                mycursor.execute(sql_insert, val_insert)
                mydb.commit()
                
                st.success("Datos modificados correctamente ✅")


@manejar_conexion
def eliminar_clientes(mydb, mycursor):
    st.subheader("Eliminar un registro ❌")
    
    # Campo para ingresar el valor de la póliza a borrar
    poliza_value = st.text_input("Ingrese el valor de la póliza a borrar").strip()
    
    # Consulta SQL para buscar los registros con el valor de la póliza ingresado
    sql = "SELECT * FROM customers WHERE poliza = %s"
    val = (poliza_value,)
    mycursor.execute(sql, val)
    results = mycursor.fetchall()  # Obtener todos los registros que coincidan

    # Si se encuentran registros coincidentes, mostrar los detalles y botones para eliminar
    if results:
        for result in results:
            st.text(f"Nombre: {result[1]}")
            st.text(f"Contacto: {result[2]}")
            st.text(f"Póliza: {result[3]}")
            st.text(f"Descripcion: {result[4]}")
            st.text(f"Compañía: {result[5]}")
            st.text(f"Tipo de plan: {result[6]}")
            st.text(f"Tipo de facturacion: {result[7]}")
            st.text(f"Numero de cuota: {result[8]}")
            st.text(f"Vencimiento de cuota: {result[9]}")

            # Botón para confirmar el borrado
            if st.button(f"Borrar cuota {result[8]}", key=result[0],type="primary"):
                # Consulta SQL para eliminar el registro actual
                sql_delete = "DELETE FROM customers WHERE id = %s"
                val_delete = (result[0],)  # El ID del registro actual
                mycursor.execute(sql_delete, val_delete)
                mydb.commit()
                st.success("Registro eliminado correctamente ✅")




