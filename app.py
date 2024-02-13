import mysql.connector
import pandas as pd
import streamlit as st
import datetime
# Establish a connection to MySQL Server

#conexion remota
mydb = mysql.connector.connect(
    host="viaduct.proxy.rlwy.net",
    user="root",
    port=43998,
    password="Bg1-CcfDfDcG6e3GeFa4hBAaDc5B3CgC",
    database="railway")

#conexion local
# mydb = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="Soler839",
#     database="crud_rabbia")


mycursor=mydb.cursor()
print("Connection Established")

# Create Streamlit Appcrud_streamlit

def main():
    
    st.title("Gestor de clientes Ruben Rabbia seguros");

    # Display Options for CRUD Operations
    option = st.sidebar.selectbox("Seleccionar operacion", ("Crear", "Buscar", "Modificar", "Eliminar"))
    
    if option == "Crear":
        st.subheader("Agregar usuario")
        name = st.text_input("Nombre")
        contacto = st.text_input("Contacto")
        poliza = st.text_input("Poliza")
        compañia = st.selectbox("Compañia", ["RUS", "RIVADAVIA", "COOP"])
        tipo_de_plan = st.selectbox("Tipo de plan", ["Trimestral", "Cuatrimestral", "Semestral"])
        fecha_de_inicio = st.date_input("Fecha de Inicio")
        fecha_de_fin = st.date_input("Fecha de fin")

        if st.button("Crear usuario"):  # Clave única para el botón Crear usuario
            if name and contacto and poliza:
                try:
                    sql = "INSERT INTO customers (name, contacto, poliza, compañia, tipo_de_plan, fecha_de_inicio, fecha_de_fin) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    val = (name, contacto, poliza, compañia, tipo_de_plan, fecha_de_inicio, fecha_de_fin)
                    mycursor.execute(sql, val)
                    mydb.commit()
                    st.success("Creado exitosamente!")
                except Exception as e:
                    st.error(f"Error al crear el usuario: {e}")
            else:
                st.warning("Por favor completa todos los campos antes de continuar.")



    elif option == "Buscar":
        # Compañia seleccionada
        st.subheader("Vencimientos de pólizas")
        
        compañia = st.selectbox("Seleccionar compañia", ["RUS", "RIVADAVIA", "COOP"])

        # Obtener la fecha actual
        today = datetime.date.today()

        # Calcular las fechas de referencia para los tres rangos
        range_0_15_days = today + datetime.timedelta(days=15)
        range_15_30_days = today + datetime.timedelta(days=30)

        # Consulta SQL para los registros con fecha_de_fin dentro del rango actual a 15 días
        sql_0_15_days = "SELECT * FROM customers WHERE compañia = %s AND fecha_de_fin BETWEEN %s AND %s ORDER BY fecha_de_fin ASC"
        val_0_15_days = (compañia, today, range_0_15_days)
        mycursor.execute(sql_0_15_days, val_0_15_days)
        result_0_15_days = mycursor.fetchall()

        # Consulta SQL para los registros con fecha_de_fin dentro del rango 15 a 30 días
        sql_15_30_days = "SELECT * FROM customers WHERE compañia = %s AND fecha_de_fin BETWEEN %s AND %s ORDER BY fecha_de_fin ASC"
        val_15_30_days = (compañia, range_0_15_days, range_15_30_days)
        mycursor.execute(sql_15_30_days, val_15_30_days)
        result_15_30_days = mycursor.fetchall()

        # Consulta SQL para los registros con fecha_de_fin vencida
        sql_expired = "SELECT * FROM customers WHERE compañia = %s AND fecha_de_fin < %s ORDER BY fecha_de_fin ASC"
        val_expired = (compañia, today)
        mycursor.execute(sql_expired, val_expired)
        result_expired = mycursor.fetchall()

        # Mostrar los resultados en Streamlit como tablas
        st.subheader("Vencimiento en los próximos 15 días")
        st.table(pd.DataFrame(result_0_15_days, columns=mycursor.column_names))

        st.subheader("Vencimiento desde los 15 a los 30 dias")
        st.table(pd.DataFrame(result_15_30_days, columns=mycursor.column_names))

        st.subheader("Pólizas vencidas")
        st.table(pd.DataFrame(result_expired, columns=mycursor.column_names))



    elif option == "Modificar":
        st.subheader("Buscar usuario")        
        # Campo para ingresar el valor de la póliza a filtrar
        poliza_value = st.text_input("Ingrese el valor de la póliza a filtrar")

        # Consulta SQL para buscar el registro con el valor de la póliza ingresado
        sql = "SELECT * FROM customers WHERE poliza = %s"
        val = (poliza_value,)
        mycursor.execute(sql, val)
        result = mycursor.fetchone()  # Obtener el primer registro que coincida (debería ser único)

        # Si se encuentra un registro coincidente, mostrar los datos actuales
        if result:
            st.text(f"Nombre actual: {result[1]}")
            st.text(f"Contacto actual: {result[2]}")
            st.text(f"Póliza actual: {result[3]}")
            st.text(f"Compañia actual: {result[4]}")
            st.text(f"Tipo de plan actual: {result[5]}")
            st.text(f"Fecha de Inicio actual: {result[6]}")
            st.text(f"Fecha de fin actual: {result[7]}")
            
            st.subheader("Modificar usuario")
            # Campos para ingresar los nuevos valores
            name = st.text_input("Nombre", value=result[1])
            contacto = st.text_input("Contacto", value=result[2])
            poliza = st.text_input("Poliza", value=result[3])
            compañia = st.selectbox("Compañia", ["RUS", "RIVADAVIA", "COOP"], index=["RUS", "RIVADAVIA", "COOP"].index(result[4]))
            tipo_de_plan = st.selectbox("Tipo de plan", ["Trimestral", "Cuatrimestral", "Semestral"], index=["Trimestral", "Cuatrimestral", "Semestral"].index(result[5]))
            fecha_de_inicio = st.date_input("Fecha de Inicio", value=result[6])
            fecha_de_fin = st.date_input("New Fecha de fin", value=result[7])

            if st.button("Modificar"):
                # Actualizar el registro en la base de datos
                sql_update = "UPDATE customers SET name=%s, contacto=%s, poliza=%s, compañia=%s, tipo_de_plan=%s, fecha_de_inicio=%s, fecha_de_fin=%s WHERE poliza = %s"
                val_update = (name, contacto, poliza, compañia, tipo_de_plan, fecha_de_inicio, fecha_de_fin, poliza_value)
                mycursor.execute(sql_update, val_update)
                mydb.commit()
                st.success("¡Registro actualizado correctamente!")




    elif option == "Eliminar":
        st.subheader("Eliminar un registro")
        
        # Campo para ingresar el valor de la póliza a borrar
        poliza_value = st.text_input("Ingrese el valor de la póliza a borrar")
        
        # Consulta SQL para buscar el registro con el valor de la póliza ingresado
        sql = "SELECT * FROM customers WHERE poliza = %s"
        val = (poliza_value,)
        mycursor.execute(sql, val)
        result = mycursor.fetchone()  # Obtener el primer registro que coincida (debería ser único)

        # Si se encuentra un registro coincidente, mostrar los detalles
        if result:
            st.text(f"Nombre: {result[1]}")
            st.text(f"Contacto: {result[2]}")
            st.text(f"Póliza: {result[3]}")
            st.text(f"Compañía: {result[4]}")
            st.text(f"Tipo de plan: {result[5]}")
            st.text(f"Fecha de Inicio: {result[6]}")
            st.text(f"Fecha de fin: {result[7]}")
            
            # Botón para confirmar el borrado
            if st.button("Borrar"):
                # Consulta SQL para eliminar el registro con el valor de la póliza ingresado
                sql_delete = "DELETE FROM customers WHERE poliza = %s"
                val_delete = (poliza_value,)
                mycursor.execute(sql_delete, val_delete)
                mydb.commit()
                st.success("¡Registro eliminado correctamente!")




if __name__ == "__main__":
    main()









