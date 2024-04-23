import mysql.connector
import pandas as pd
from functools import wraps
import streamlit as st
import datetime
from appClientes.conexion import establecer_conexion, cerrar_conexion




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



#     #conexion remota railway
# mydb = mysql.connector.connect(
#     host="rabbia-db.c1o28sciaahh.us-east-1.rds.amazonaws.com",
#     user="admin",
#     port=3306,
#     password="Soler839",
#     database="rabbia"
# )
# mycursor=mydb.cursor(buffered=True)
# print("Connection Established")

@manejar_conexion
def crear_clientes(mydb, mycursor):    
        st.subheader("Agregar usuario ✅")
        name = st.text_input("Nombre")
        contacto = st.text_input("Contacto")
        poliza = st.text_input("Poliza")
        descripcion = st.text_input("Descripción")
        compañia = st.selectbox("Compañia", ["RIVADAVIA","RUS","COOP"])
        tipo_de_plan = st.selectbox("Duración del plan", ["Anual","Semestral"])
        tipo_de_facturacion = st.selectbox("Tipo de facturacion", ["Trimestral", "Cuatrimestral", "Semestral","Anual"])
        numero_de_cuota = st.selectbox("Numero de cuota", [0,1,2,3,4])
        vencimiento_de_cuota = st.date_input("Vencimiento de la cuota")
        estado = st.selectbox("Estado de la cuota", ["Sin pagar","Pagado"])
        

        if st.button("Crear", type="primary"):  # Clave única para el botón Crear usuario
            if name and contacto and poliza:
                # Consultar si la póliza ya existe en la base de datos
                sql_check_poliza = "SELECT * FROM customers WHERE poliza = %s"
                val_check_poliza = (poliza,)
                mycursor.execute(sql_check_poliza, val_check_poliza)
                existing_poliza = mycursor.fetchone()

                if existing_poliza:
                    st.warning("La póliza ingresada ya existe. Por favor, ingresa una póliza diferente.")
                else:
                    try:
                        sql = "INSERT INTO customers (name, contacto, poliza, descripcion, compañia, tipo_de_plan,tipo_de_facturacion,numero_de_cuota,vencimiento_de_cuota,estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"
                        val = (name, contacto, poliza, descripcion, compañia, tipo_de_plan,tipo_de_facturacion,numero_de_cuota,vencimiento_de_cuota,estado)
                        mycursor.execute(sql, val)
                        mydb.commit()
                        st.success("Creado exitosamente ✅")
                    except Exception as e:
                        st.error(f"Error al crear el usuario: {e}")
            else:
                st.warning("Por favor completa todos los campos antes de continuar.")

@manejar_conexion
def vencimientos_clientes(mydb, mycursor):
    # Compañia seleccionada
    st.subheader("Vencimientos de cuotas 📜")
    
    compañia = st.selectbox("Seleccionar compañia", ["RIVADAVIA", "RUS", "COOP"])

    # Obtener la fecha actual
    today = datetime.date.today()

    # Consulta SQL para los registros con vencimiento_de_cuota dentro del rango actual a 7 días y estado 'Sin pagar'
    sql_0_7_days = "SELECT * FROM customers WHERE compañia = %s AND vencimiento_de_cuota BETWEEN %s AND %s AND estado = 'Sin pagar' ORDER BY vencimiento_de_cuota ASC"
    val_0_7_days = (compañia, today, today + datetime.timedelta(days=7))
    mycursor.execute(sql_0_7_days, val_0_7_days)
    result_0_7_days = mycursor.fetchall()

    # Consulta SQL para los registros con vencimiento_de_cuota dentro del rango 8 a 15 días y estado 'Sin pagar'
    sql_8_15_days = "SELECT * FROM customers WHERE compañia = %s AND vencimiento_de_cuota BETWEEN %s AND %s AND estado = 'Sin pagar' ORDER BY vencimiento_de_cuota ASC"
    val_8_15_days = (compañia, today + datetime.timedelta(days=8), today + datetime.timedelta(days=15))
    mycursor.execute(sql_8_15_days, val_8_15_days)
    result_8_15_days = mycursor.fetchall()

    # Consulta SQL para los registros con vencimiento_de_cuota vencida y estado 'Sin pagar'
    sql_expired = "SELECT * FROM customers WHERE compañia = %s AND vencimiento_de_cuota < %s AND estado = 'Sin pagar' ORDER BY vencimiento_de_cuota ASC LIMIT 20"
    val_expired = (compañia, today)
    mycursor.execute(sql_expired, val_expired)
    result_expired = mycursor.fetchall()
    
    # Consulta SQL para obtener los últimos 20 registros ingresados y estado 'Sin pagar'
    sql_last_20_sin_pagar = "SELECT * FROM customers WHERE estado = 'Sin pagar' ORDER BY id DESC LIMIT 20"
    mycursor.execute(sql_last_20_sin_pagar)
    result_last_20_sin_pagar = mycursor.fetchall()

    # Consulta SQL para obtener los últimos 20 registros ingresados y estado 'Pagado'
    sql_last_20_pagado = "SELECT * FROM customers WHERE estado = 'Pagado' ORDER BY id DESC LIMIT 20"
    mycursor.execute(sql_last_20_pagado)
    result_last_20_pagado = mycursor.fetchall()

    # Definir las columnas para la tabla
    columnas = ["id", "Nombre", "Contacto", "Poliza", "Descripcion", "Compañia", "Tipo de plan", "Tipo de facturacion", "Numero de cuota", "Vencimiento de cuota", "Estado"]

    # Mostrar los resultados en Streamlit como tablas
    st.subheader("Vencimiento en los próximos 7 días")
    st.table(pd.DataFrame(result_0_7_days, columns=columnas))

    st.subheader("Vencimiento desde los 8 a los 15 días")
    st.table(pd.DataFrame(result_8_15_days, columns=columnas))

    st.subheader("Últimos 20 usuarios ingresados")
    st.table(pd.DataFrame(result_last_20_sin_pagar, columns=columnas))

    st.subheader("Cuotas vencidas")
    st.table(pd.DataFrame(result_expired, columns=columnas))

    st.subheader("Últimos 20 pagados")
    st.table(pd.DataFrame(result_last_20_pagado, columns=columnas))




@manejar_conexion
def logica_de_pago(mydb, mycursor):
    st.subheader("Buscar usuario por póliza 🔎")
       
    # Campo para ingresar el valor de la póliza a filtrar
    poliza_value = st.text_input("Ingrese el valor de la póliza a filtrar")

    # Consulta SQL para buscar los registros con el valor de la póliza ingresado
    sql = "SELECT * FROM customers WHERE poliza = %s"
    val = (poliza_value,)
    mycursor.execute(sql, val)
    results = mycursor.fetchall()

    if results:
        for result in results:
            st.text(f"ID: {result[0]}")
            st.text(f"Nombre actual: {result[1]}")
            st.text(f"Contacto actual: {result[2]}")
            st.text(f"Póliza actual: {result[3]}")
            st.text(f"Descripción actual: {result[4]}")
            st.text(f"Compañía actual: {result[5]}")
            st.text(f"Tipo de plan actual: {result[6]}")
            st.text(f"Tipo de facturación: {result[7]}")
            st.text(f"Número de cuota: {result[8]}")
            st.text(f"Vencimiento de cuota: {result[9]}")
            st.text(f"Estado de cuota: {result[10]}")

            # Botón para marcar como Pagado para el registro actual
            if st.button(f"Marcar como Pagado (Vencimiento: {result[9]})", key=f'marcar_pagado_{result[0]}', type="primary"):
                # Consulta SQL para actualizar el estado a "Pagado" solo para este registro
                update_sql = "UPDATE customers SET estado = 'Pagado' WHERE id = %s"
                mycursor.execute(update_sql, (result[0],))  # result[0] es el id del registro
                mydb.commit()  # Confirmar la transacción

                st.success(f"Estado actualizado con éxito para el vencimiento.")


@manejar_conexion
def buscar_clientes(mydb, mycursor):
    
    st.subheader("Buscar usuario 🔎")
    option = st.selectbox(" ",("Por poliza 📝", "Por nombre 🧑"))
    if option == "Por poliza 📝":
    # Campo para ingresar el valor de la póliza a filtrar
        poliza_value = st.text_input("Ingrese el valor de la póliza a filtrar")

        # Consulta SQL para buscar el registro con el valor de la póliza ingresado
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
            st.text(f"Tipo de facturacion: {result[7]}")
            st.text(f"Numero de cuota: {result[8]}")
            st.text(f"Vencimiento de cuota: {result[9]}")
            st.text(f"Estado de cuota: {result[10]}")
            
    elif option == "Por nombre 🧑":
        
        nombre_value = st.text_input("Ingrese el nombre a filtrar")

        # Consulta SQL para buscar el registro con el valor de la póliza ingresado
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
            st.text(f"Tipo de facturacion: {result[7]}")
            st.text(f"Numero de cuota: {result[8]}")
            st.text(f"Vencimiento de cuota: {result[9]}")
            st.text(f"Estado de cuota: {result[10]}")
            
@manejar_conexion           
def modificar_clientes(mydb, mycursor):    
    st.subheader("Buscar usuario 🔎")        
    # Campo para ingresar el valor de la póliza a filtrar
    poliza_value = st.text_input("Ingrese el valor de la póliza a filtrar")

    # Consulta SQL para buscar el registro con el valor de la póliza ingresado
    sql = "SELECT * FROM customers WHERE poliza = %s"
    val = (poliza_value,)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()                 
                    
    # Si se encuentra un registro coincidente, mostrar los datos actuales
    if result:
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
        name = st.text_input("Nombre", value=result[1])
        contacto = st.text_input("Contacto", value=result[2])
        poliza = st.text_input("Poliza", value=result[3])
        descripcion = st.text_input("Descripción", value=result[4])
        compañia = st.selectbox("Compañia", ["RIVADAVIA", "RUS", "COOP"], index=[ "RIVADAVIA", "RUS", "COOP"].index(result[5]))
        tipo_de_plan = st.selectbox("Tipo de plan", [ "Anual","Semestral" ], index=["Anual","Semestral"].index(result[6]))
        tipo_de_facturacion = st.selectbox("Tipo de facturacion", ["Trimestral", "Cuatrimestral", "Semestral","Anual"],index=["Trimestral", "Cuatrimestral", "Semestral", "Anual"].index(result[7]))
        numero_de_cuota = st.selectbox("Numero de cuota", [0,1,2,3,4],index=[0,1,2,3,4].index(result[8]))
        vencimiento_de_cuota = st.date_input("Vencimeinto de cuota", value=result[9])

        if st.button("Modificar", type="primary"):
            # Actualizar el registro en la base de datos
            sql_update = "UPDATE customers SET name=%s, contacto=%s, poliza=%s,descripcion=%s, compañia=%s, tipo_de_plan=%s,tipo_de_facturacion=%s,numero_de_cuota=%s,vencimiento_de_cuota=%s WHERE poliza = %s"
            val_update = (name, contacto, poliza,descripcion, compañia, tipo_de_plan,tipo_de_facturacion,numero_de_cuota,vencimiento_de_cuota,poliza_value)
            mycursor.execute(sql_update, val_update)
            mydb.commit()
            st.success("Registro actualizado correctamente ✅")

@manejar_conexion
def renovar_clientes(mydb, mycursor):
        st.subheader("Renovar cuota ♻️")        
        # Campo para ingresar el valor de la póliza a filtrar
        poliza_value = st.text_input("Ingrese el valor de la póliza a filtrar")

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

            if st.button("Modificar", type="primary"):
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
    poliza_value = st.text_input("Ingrese el valor de la póliza a borrar")
    
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




