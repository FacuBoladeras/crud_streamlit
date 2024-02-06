import mysql.connector
import pandas as pd
import streamlit as st

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
        name = st.text_input("Enter Name")
        contacto = st.text_input("Enter Contacto")
        poliza = st.text_input("Enter Poliza")
        compañia = st.selectbox("Compañia", ["RUS", "RIVADAVIA", "COOP"])
        tipo_de_plan = st.selectbox("Tipo de plan", ["Trimestral", "Cuatrimestral", "Semestral"])
        fecha_de_inicio = st.date_input("Enter Fecha de Inicio")
        fecha_de_fin = st.date_input("Enter Fecha de fin")

        if st.button("Crear"):
            sql = "INSERT INTO customers (name, contacto, poliza, compañia, tipo_de_plan, fecha_de_inicio, fecha_de_fin) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (name, contacto, poliza, compañia, tipo_de_plan, fecha_de_inicio, fecha_de_fin)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Record Created Successfully!!!")


    elif option == "Buscar":
        # Compañia seleccionada
        compañia = st.selectbox("Compañia", ["RUS", "RIVADAVIA", "COOP"])

        # Consulta SQL para obtener registros que coincidan con la compañia y ordenados por fecha_de_fin
        sql = "SELECT * FROM customers WHERE compañia = %s ORDER BY fecha_de_fin ASC"
        val = (compañia,)

        # Ejecutar la consulta
        mycursor.execute(sql, val)

        # Obtener los resultados y los nombres de las columnas
        result = mycursor.fetchall()
        column_names = [i[0] for i in mycursor.description]

        # Mostrar los resultados en Streamlit como una tabla
        st.table(pd.DataFrame(result, columns=column_names))



    elif option == "Crear":
        st.subheader("Agregar usuario")
        name = st.text_input("Enter Name")
        contacto = st.text_input("Enter Contacto")
        poliza = st.text_input("Enter Poliza")
        compañia = st.selectbox("Compañia", ["RUS", "RIVADAVIA", "COOP"])
        tipo_de_plan = st.selectbox("Tipo de plan", ["Trimestral", "Cuatrimestral", "Semestral"])
        fecha_de_inicio = st.date_input("Enter Fecha de Inicio")
        fecha_de_fin = st.date_input("Enter Fecha de fin")

        if st.button("Crear"):
            sql = "INSERT INTO customers (name, contacto, poliza, compañia, tipo_de_plan, fecha_de_inicio, fecha_de_fin) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (name, contacto, poliza, compañia, tipo_de_plan, fecha_de_inicio, fecha_de_fin)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Record Created Successfully!!!")




    elif option=="Borrar":
        st.subheader("Delete a Record")
        id=st.number_input("Enter ID",min_value=1)
        if st.button("Borrar"):
            sql="delete from users where id =%s"
            val=(id,)
            mycursor.execute(sql,val)
            mydb.commit()
            st.success("Record Deleted Successfully!!!")


if __name__ == "__main__":
    main()









