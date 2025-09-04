import streamlit as st
from functools import wraps
from datetime import datetime, date, timedelta
from boto3.dynamodb.conditions import Attr

from appClientes.conexion import get_table, cerrar_conexion


def manejar_conexion(func):
    """Decorator that obtains a DynamoDB table before running the function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        table = get_table()
        if table is None:
            return None
        try:
            return func(table, *args, **kwargs)
        finally:
            cerrar_conexion(table)

    return wrapper


@manejar_conexion
def crear_clientes(table):
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
    estado = st.selectbox("Estado de la cuota", ["Sin pagar", "Pagado", "Avisado", "Vencido"])

    if st.button("Crear", type="primary"):
        if not (name and contacto and poliza):
            st.warning("Completa los campos obligatorios")
            return

        item = {
            "poliza": poliza,
            "name": name,
            "contacto": contacto,
            "descripcion": descripcion,
            "compañia": compañia,
            "tipo_de_plan": tipo_de_plan,
            "tipo_de_facturacion": tipo_de_facturacion,
            "numero_de_cuota": int(numero_de_cuota),
            "vencimiento_de_cuota": vencimiento_de_cuota.isoformat(),
            "estado": estado,
            "created_at": datetime.utcnow().isoformat(),
        }
        try:
            table.put_item(Item=item, ConditionExpression="attribute_not_exists(poliza)")
            st.success("Creado exitosamente ✅")
        except Exception as e:
            st.error(f"No se pudo crear: {e}")


@manejar_conexion
def buscar_clientes(table):
    st.subheader("Buscar cliente 🔎")
    poliza = st.text_input("Póliza")
    if st.button("Buscar", type="primary") and poliza:
        response = table.get_item(Key={"poliza": poliza})
        item = response.get("Item")
        if item:
            st.json(item)
        else:
            st.info("No se encontró ningún cliente con esa póliza")


@manejar_conexion
def modificar_clientes(table):
    st.subheader("Modificar ✏️")
    poliza = st.text_input("Póliza a modificar")
    if poliza:
        response = table.get_item(Key={"poliza": poliza})
        item = response.get("Item")
        if item:
            name = st.text_input("Nombre", value=item.get("name", ""))
            contacto = st.text_input("Contacto", value=item.get("contacto", ""))
            descripcion = st.text_input("Descripción", value=item.get("descripcion", ""))
            compañia = st.selectbox(
                "Compañia", ["RIVADAVIA", "RUS", "COOP"],
                index=["RIVADAVIA", "RUS", "COOP"].index(item.get("compañia", "RIVADAVIA")),
            )
            tipo_de_plan = st.selectbox(
                "Duración del plan", ["Anual", "Semestral"],
                index=["Anual", "Semestral"].index(item.get("tipo_de_plan", "Anual")),
            )
            tipo_de_facturacion = st.selectbox(
                "Tipo de facturacion", ["Trimestral", "Cuatrimestral", "Semestral", "Anual"],
                index=["Trimestral", "Cuatrimestral", "Semestral", "Anual"].index(item.get("tipo_de_facturacion", "Anual")),
            )
            numero_de_cuota = st.selectbox(
                "Numero de cuota", [0, 1, 2, 3, 4],
                index=[0, 1, 2, 3, 4].index(int(item.get("numero_de_cuota", 0))),
            )
            vencimiento_de_cuota = st.date_input(
                "Vencimiento de la cuota",
                value=datetime.fromisoformat(item.get("vencimiento_de_cuota")).date(),
            )
            estado = st.selectbox(
                "Estado", ["Sin pagar", "Pagado", "Avisado", "Vencido"],
                index=["Sin pagar", "Pagado", "Avisado", "Vencido"].index(item.get("estado", "Sin pagar")),
            )

            if st.button("Guardar", type="primary"):
                update_expr = (
                    "SET name=:name, contacto=:contacto, descripcion=:descripcion, "
                    "compañia=:compañia, tipo_de_plan=:tipo_de_plan, tipo_de_facturacion=:tipo_de_facturacion, "
                    "numero_de_cuota=:numero_de_cuota, vencimiento_de_cuota=:vencimiento_de_cuota, estado=:estado"
                )
                values = {
                    ":name": name,
                    ":contacto": contacto,
                    ":descripcion": descripcion,
                    ":compañia": compañia,
                    ":tipo_de_plan": tipo_de_plan,
                    ":tipo_de_facturacion": tipo_de_facturacion,
                    ":numero_de_cuota": int(numero_de_cuota),
                    ":vencimiento_de_cuota": vencimiento_de_cuota.isoformat(),
                    ":estado": estado,
                }
                table.update_item(
                    Key={"poliza": poliza},
                    UpdateExpression=update_expr,
                    ExpressionAttributeValues=values,
                )
                st.success("Cliente actualizado ✅")
        else:
            st.info("No encontrado")


@manejar_conexion
def eliminar_clientes(table):
    st.subheader("Eliminar un registro ❌")
    poliza = st.text_input("Póliza a borrar")
    if st.button("Borrar", type="primary") and poliza:
        try:
            table.delete_item(Key={"poliza": poliza})
            st.success("Registro eliminado correctamente ✅")
        except Exception as e:
            st.error(f"No se pudo eliminar: {e}")


@manejar_conexion
def ultimos_20_clientes_ingresados(table):
    st.subheader("Últimos ingresados 📄")
    response = table.scan()
    items = response.get("Items", [])
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    st.table(items[:20])


@manejar_conexion
def avisados(table):
    st.subheader("Avisados - Pagados 🗣️")
    response = table.scan(FilterExpression=Attr("estado").is_in(["Avisado", "Pagado"]))
    items = response.get("Items", [])
    st.table(items)


@manejar_conexion
def vencimientos_clientes(table):
    st.subheader("Vencimientos de cuotas 📜")
    compañia = st.selectbox("Seleccionar compañia", ["RIVADAVIA", "RUS", "COOP"])
    today = date.today()
    response = table.scan(FilterExpression=Attr("compañia").eq(compañia))
    items = response.get("Items", [])
    for item in items:
        if isinstance(item.get("vencimiento_de_cuota"), str):
            item["vencimiento_de_cuota"] = date.fromisoformat(item["vencimiento_de_cuota"])

    proximos = [i for i in items if today <= i["vencimiento_de_cuota"] <= today + timedelta(days=7)]
    vencidos = [i for i in items if i["vencimiento_de_cuota"] < today]

    st.write("Próximas a vencer (7 días)")
    st.table(proximos)
    st.write("Ya vencidas")
    st.table(vencidos)


@manejar_conexion
def renovar_clientes(table):
    st.subheader("Renovar ♻️")
    poliza = st.text_input("Póliza a renovar")
    if poliza:
        response = table.get_item(Key={"poliza": poliza})
        item = response.get("Item")
        if item:
            nueva_fecha = st.date_input("Nuevo vencimiento")
            if st.button("Renovar", type="primary"):
                update_expr = "SET vencimiento_de_cuota=:vencimiento, numero_de_cuota=:cuota"
                values = {
                    ":vencimiento": nueva_fecha.isoformat(),
                    ":cuota": int(item.get("numero_de_cuota", 0)) + 1,
                }
                table.update_item(
                    Key={"poliza": poliza},
                    UpdateExpression=update_expr,
                    ExpressionAttributeValues=values,
                )
                st.success("Póliza renovada ✅")
        else:
            st.info("No encontrado")

