import streamlit as st
from functools import wraps
from datetime import datetime, date, timedelta
from uuid import uuid4
from calendar import monthrange

from boto3.dynamodb.conditions import Key, Attr
from appClientes.conexion import get_table, cerrar_conexion

# ---------------------------
# Helpers de conexión
# ---------------------------
def manejar_conexion(func):
    """Obtiene la tabla DynamoDB antes de ejecutar la función."""
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

# ---------------------------
# Helpers de fechas / GSIs
# ---------------------------
MONTHS_BY_FACTURACION = {
    "Trimestral": 3,
    "Cuatrimestral": 4,
    "Semestral": 6,
    "Anual": 12,
}

def add_months_ymd(d: date, months: int) -> date:
    """Suma meses a una fecha (con control de fin de mes)."""
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    last_day = monthrange(y, m)[1]
    return date(y, m, min(d.day, last_day))

def ymd_int(d: date) -> int:
    return int(d.strftime("%Y%m%d"))

def ymd_month_str(d: date) -> str:
    return d.strftime("%Y-%m")

# ---------------------------
# Updates en Dynamo
# ---------------------------
def update_due_item(table, poliza: str, item_id: str, new_date: date, new_estado: str | None = None):
    """Actualiza vencimiento y campos derivados (mantiene item_id)."""
    venc_iso = new_date.isoformat()
    venc_yyyymmdd = ymd_int(new_date)
    venc_yyyymm = ymd_month_str(new_date)

    update_expr = "SET vencimiento_de_cuota=:v, venc_yyyymmdd=:d, venc_yyyymm=:m, updated_at=:u"
    expr_vals = {
        ":v": venc_iso,
        ":d": venc_yyyymmdd,
        ":m": venc_yyyymm,
        ":u": datetime.utcnow().isoformat(),
    }
    if new_estado:
        update_expr += ", estado=:s"
        expr_vals[":s"] = new_estado

    table.update_item(
        Key={"poliza": poliza, "item_id": item_id},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_vals,
        ReturnValues="UPDATED_NEW",
    )

def update_due_item_with_audit(table, poliza: str, item_id: str, new_date: date, new_estado: str | None = None):
    """Igual que arriba, pero incrementa renovación y setea last_renewed_at."""
    venc_iso = new_date.isoformat()
    venc_yyyymmdd = ymd_int(new_date)
    venc_yyyymm = ymd_month_str(new_date)

    update_expr = (
        "SET vencimiento_de_cuota=:v, venc_yyyymmdd=:d, venc_yyyymm=:m, "
        "updated_at=:u, last_renewed_at=:u, renewal_count = if_not_exists(renewal_count, :zero) + :one"
    )
    expr_vals = {
        ":v": venc_iso,
        ":d": venc_yyyymmdd,
        ":m": venc_yyyymm,
        ":u": datetime.utcnow().isoformat(),
        ":zero": 0, ":one": 1,
    }
    if new_estado:
        update_expr += ", estado=:s"
        expr_vals[":s"] = new_estado

    table.update_item(
        Key={"poliza": poliza, "item_id": item_id},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_vals,
        ReturnValues="UPDATED_NEW",
    )

# ---------------------------
# Crear
# ---------------------------
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

        item_id = str(uuid4())
        venc_iso = vencimiento_de_cuota.isoformat()
        item = {
            "poliza": poliza,
            "item_id": item_id,
            "vencimiento_de_cuota": venc_iso,
            "venc_yyyymmdd": ymd_int(vencimiento_de_cuota),
            "venc_yyyymm": ymd_month_str(vencimiento_de_cuota),
            "name": name,
            "contacto": contacto,
            "descripcion": descripcion or "",
            "compañia": compañia,
            "tipo_de_plan": tipo_de_plan,
            "tipo_de_facturacion": tipo_de_facturacion,
            "numero_de_cuota": int(numero_de_cuota),
            "estado": estado,
            "created_at": datetime.utcnow().isoformat(),
        }
        try:
            table.put_item(Item=item, ConditionExpression="attribute_not_exists(item_id)")
            st.success("Creado exitosamente ✅")
        except Exception as e:
            st.error(f"No se pudo crear: {e}")

# ---------------------------
# Buscar (por póliza → múltiples ítems)
# ---------------------------
@manejar_conexion
def buscar_clientes(table):
    st.subheader("Buscar cliente 🔎")
    poliza = st.text_input("Póliza")
    if st.button("Buscar", type="primary") and poliza:
        # Varios ítems por póliza → usamos query
        resp = table.query(
            KeyConditionExpression=Key("poliza").eq(poliza)
        )
        items = resp.get("Items", [])
        if not items:
            st.info("No se encontraron registros para esa póliza.")
            return
        st.markdown("**Resultados**")        

        st.markdown("**Detalles por registro**")
        for it in items:
            with st.expander(f"{it.get('name','(Sin nombre)')} • vence: {it.get('vencimiento_de_cuota','')}"):
                st.json(it)

# ---------------------------
# Modificar (elige item_id)
# ---------------------------
@manejar_conexion
def modificar_clientes(table):
    st.subheader("Modificar ✏️")
    poliza = st.text_input("Póliza")
    if not poliza:
        return

    # Traemos todos los ítems de la póliza
    resp = table.query(KeyConditionExpression=Key("poliza").eq(poliza))
    items = resp.get("Items", [])
    if not items:
        st.info("No hay registros para esa póliza.")
        return

    # Elegimos el registro a modificar
    options = {f"{it.get('name','(Sin nombre)')} | {it.get('vencimiento_de_cuota','')}": it for it in items}
    choice = st.selectbox("Elegí el registro", list(options.keys()))
    it = options[choice]
    item_id = it["item_id"]

    # Form
    name = st.text_input("Nombre", value=it.get("name", ""))
    contacto = st.text_input("Contacto", value=it.get("contacto", ""))
    descripcion = st.text_input("Descripción", value=it.get("descripcion", ""))
    compañia = st.selectbox("Compañia", ["RIVADAVIA", "RUS", "COOP"],
                            index=["RIVADAVIA","RUS","COOP"].index(it.get("compañia","RIVADAVIA")))
    tipo_de_plan = st.selectbox("Duración del plan", ["Anual","Semestral"],
                                index=["Anual","Semestral"].index(it.get("tipo_de_plan","Anual")))
    tipo_de_facturacion = st.selectbox("Tipo de facturacion", ["Trimestral","Cuatrimestral","Semestral","Anual"],
                                       index=["Trimestral","Cuatrimestral","Semestral","Anual"].index(it.get("tipo_de_facturacion","Anual")))
    numero_de_cuota = st.selectbox("Numero de cuota", [0,1,2,3,4],
                                   index=[0,1,2,3,4].index(int(it.get("numero_de_cuota",0))))
    # fecha
    try:
        default_date = datetime.strptime(it.get("vencimiento_de_cuota","1970-01-01"), "%Y-%m-%d").date()
    except Exception:
        default_date = date.today()
    vencimiento_de_cuota = st.date_input("Vencimiento de la cuota", value=default_date)
    estado = st.selectbox("Estado", ["Sin pagar","Pagado","Avisado","Vencido"],
                          index=["Sin pagar","Pagado","Avisado","Vencido"].index(it.get("estado","Sin pagar")))

    if st.button("Guardar cambios", type="primary"):
        # ojo: 'name' es palabra reservada → #n
                update_expr = (
                    "SET #n=:name, contacto=:contacto, descripcion=:descripcion, "
                    "#comp=:compania, tipo_de_plan=:tipo_de_plan, tipo_de_facturacion=:tipo_de_facturacion, "
                    "numero_de_cuota=:numero_de_cuota, estado=:estado, "
                    "vencimiento_de_cuota=:v, venc_yyyymmdd=:d, venc_yyyymm=:m, updated_at=:u"
                )
                values = {
                    ":name": name,
                    ":contacto": contacto,
                    ":descripcion": descripcion or "",
                    ":compania": compañia,  # 👈 acá uso "compania" en vez de "compañia"
                    ":tipo_de_plan": tipo_de_plan,
                    ":tipo_de_facturacion": tipo_de_facturacion,
                    ":numero_de_cuota": int(numero_de_cuota),
                    ":estado": estado,
                    ":v": vencimiento_de_cuota.isoformat(),
                    ":d": ymd_int(vencimiento_de_cuota),
                    ":m": ymd_month_str(vencimiento_de_cuota),
                    ":u": datetime.utcnow().isoformat(),
                }
                table.update_item(
                    Key={"poliza": poliza, "item_id": item_id},
                    UpdateExpression=update_expr,
                    ExpressionAttributeValues=values,
                    ExpressionAttributeNames={
                        "#n": "name",
                        "#comp": "compañia",  # 👈 acá sí mapeamos el campo real
                    },
                )
                st.success("Registro actualizado ✅")

# ---------------------------
# Eliminar (por item)
# ---------------------------
@manejar_conexion
def eliminar_clientes(table):
    st.subheader("Eliminar un registro ❌")
    poliza = st.text_input("Póliza")
    if not poliza:
        return

    resp = table.query(KeyConditionExpression=Key("poliza").eq(poliza))
    items = resp.get("Items", [])
    if not items:
        st.info("No hay registros para esa póliza.")
        return

    options = {f"{it.get('name','(Sin nombre)')} | {it.get('vencimiento_de_cuota','')} | {it['item_id']}": it for it in items}
    choice = st.selectbox("Elegí el registro a borrar", list(options.keys()))
    it = options[choice]
    item_id = it["item_id"]

    if st.button("Borrar", type="primary"):
        try:
            table.delete_item(Key={"poliza": poliza, "item_id": item_id})
            st.success("Registro eliminado correctamente ✅")
        except Exception as e:
            st.error(f"No se pudo eliminar: {e}")

# ---------------------------
# Últimos 20 ingresados (scan)
# ---------------------------
@manejar_conexion
def ultimos_20_clientes_ingresados(table):
    st.subheader("📄 Últimos 20 clientes ingresados")

    # Traer todos los registros (puede ser costoso si hay muchos; se puede optimizar con GSI si hace falta)
    resp = table.scan()
    items = resp.get("Items", [])
    
    if not items:
        st.info("No hay clientes cargados todavía.")
        return

    # Ordenar por fecha de creación (descendente)
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    # Limitar a los últimos 20
    items = items[:20]

    # Renombrar campos para la vista
    rows = []
    for it in items:
        rows.append({
            "Nombre": it.get("name", ""),
            "Contacto": it.get("contacto", ""),
            "Póliza": it.get("poliza", ""),
            "Tipo de facturación": it.get("tipo_de_facturacion", ""),
            "Descripción": it.get("descripcion", ""),
            "Fecha de vencimiento": it.get("vencimiento_de_cuota", ""),
            "Compaia": it.get("compañia", ""),
        })

    # Mostrar en tabla
    st.dataframe(rows, use_container_width=True, hide_index=True)


# ---------------------------
# Ventana por meses (GSI ByMonth)
# ---------------------------
def _query_by_month_window(table, start_d: date, end_d: date) -> list[dict]:
    """Consulta por ventana de días cruzando meses con GSI ByMonth y agrupa resultados."""
    meses = {start_d.strftime("%Y-%m"), end_d.strftime("%Y-%m")}
    y1, y2 = ymd_int(start_d), ymd_int(end_d)
    items = []
    for mes in meses:
        resp = table.query(
            IndexName="ByMonth",
            KeyConditionExpression=Key("venc_yyyymm").eq(mes) & Key("venc_yyyymmdd").between(y1, y2),
        )
        items.extend(resp.get("Items", []))
    return items

def _dedupe_and_sort(items: list[dict]) -> list[dict]:
    """Elimina duplicados por (poliza,item_id) y ordena por venc_yyyymmdd ascendente."""
    seen = set()
    out = []
    for it in items:
        key = (it.get("poliza"), it.get("item_id"))
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    out.sort(key=lambda x: x.get("venc_yyyymmdd", 99999999))
    return out

def _filter_company_and_range(items: list[dict], compania: str, start_d: date, end_d: date) -> list[dict]:
    """Filtra por compañía y por rango real de fechas (seguridad extra)."""
    y1, y2 = ymd_int(start_d), ymd_int(end_d)
    out = []
    for it in items:
        if it.get("compañia") != compania:
            continue
        d = it.get("venc_yyyymmdd")
        if isinstance(d, int) and y1 <= d <= y2:
            out.append(it)
    return _dedupe_and_sort(out)

# ---------------------------
# Expansores por ítem (preview + renovar)
# ---------------------------
def _show_due_item_expanders(table, items: list[dict]):
    """Expansores por ítem con acciones de renovación, modificación (colapsable) y eliminación."""
    for it in items:
        nombre = it.get("name", "Sin nombre")
        poliza = it["poliza"]
        item_id = it["item_id"]
        vence = it.get("vencimiento_de_cuota", "")

        with st.expander(f"**{nombre}**  ·  póliza {poliza}  ·  vence: {vence}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**Compañía:**", it.get("compañia",""))
                st.write("**Plan:**", it.get("tipo_de_plan",""))
                st.write("**Facturación:**", it.get("tipo_de_facturacion",""))
            with col2:
                st.write("**Cuota #:**", it.get("numero_de_cuota",""))
                st.write("**Poliza:**", it.get("poliza",""))
                st.write("**Contacto:**", it.get("contacto",""))
            with col3:
                st.write("**Descripción:**")
                st.write(it.get("descripcion",""))

            st.divider()
            st.markdown("#### 🔄 Renovar")

            auto_col, manual_col = st.columns(2)

            # --- Renovación automática ---
            with auto_col:
                st.caption("Automática (según tipo de facturación)")
                meses = MONTHS_BY_FACTURACION.get(it.get("tipo_de_facturacion",""), 0)
                try:
                    current_date = datetime.strptime(vence, "%Y-%m-%d").date()
                except Exception:
                    current_date = None
                if meses > 0 and current_date:
                    new_auto = add_months_ymd(current_date, meses)
                    st.write(f"→ Nueva fecha propuesta: **{new_auto.isoformat()}**")
                    if st.button(f"Renovar automáticamente (+{meses} meses)", key=f"auto_{item_id}", type="primary"):
                        try:
                            update_due_item_with_audit(table, poliza, item_id, new_auto, new_estado="Sin pagar")
                            st.success("Renovado automáticamente ✅")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"No se pudo renovar: {e}")
                else:
                    st.info("Tipo de facturación o fecha inválida; usa renovación manual.")

            # --- Renovación manual ---
            with manual_col:
                st.caption("Manual")
                try:
                    default_date = datetime.strptime(vence, "%Y-%m-%d").date()
                except Exception:
                    default_date = date.today()
                new_manual_date = st.date_input(
                    "Nueva fecha de vencimiento", value=default_date, key=f"manual_date_{item_id}"
                )

                if st.button("Aplicar renovación manual", key=f"manual_btn_{item_id}",type="primary"):
                    try:
                        update_due_item_with_audit(table, poliza, item_id, new_manual_date)
                        st.success("Fecha actualizada ✅")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"No se pudo actualizar: {e}")

            st.divider()
            st.markdown("#### Modificar o Eliminar")

            # --- Botones para mostrar opciones ---
            action_col1, action_col2 = st.columns(2)
            if action_col1.button("✏️ Modificar", key=f"mod_btn_{item_id}",type="primary"):
                st.session_state[f"show_mod_{item_id}"] = not st.session_state.get(f"show_mod_{item_id}", False)
            if action_col2.button("❌ Eliminar", key=f"del_btn_{item_id}",type="primary"):
                try:
                    table.delete_item(Key={"poliza": poliza, "item_id": item_id})
                    st.warning("Registro eliminado correctamente ❌")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"No se pudo eliminar: {e}")

            # --- Formulario de modificación (solo si se clickeó Modificar) ---
            if st.session_state.get(f"show_mod_{item_id}", False):
                with st.form(key=f"form_mod_{item_id}"):
                    n_name = st.text_input("Nombre", value=it.get("name", ""))
                    n_contacto = st.text_input("Contacto", value=it.get("contacto", ""))
                    n_desc = st.text_input("Descripción", value=it.get("descripcion", ""))
                    n_estado = st.selectbox(
                        "Estado", ["Sin pagar","Pagado","Avisado","Vencido"],
                        index=["Sin pagar","Pagado","Avisado","Vencido"].index(it.get("estado","Sin pagar")),
                    )
                    save_btn = st.form_submit_button("Guardar cambios ✏️")
                    if save_btn:
                        try:
                            update_expr = (
                                "SET #n=:name, contacto=:c, descripcion=:d, estado=:s, updated_at=:u"
                            )
                            expr_vals = {
                                ":name": n_name,
                                ":c": n_contacto,
                                ":d": n_desc,
                                ":s": n_estado,
                                ":u": datetime.utcnow().isoformat(),
                            }
                            table.update_item(
                                Key={"poliza": poliza, "item_id": item_id},
                                UpdateExpression=update_expr,
                                ExpressionAttributeValues=expr_vals,
                                ExpressionAttributeNames={"#n": "name"},
                            )
                            st.success("Registro actualizado ✅")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"No se pudo modificar: {e}")


# ---------------------------
# Vencimientos próximos (0–7 días y 8–15 días)
# ---------------------------
from boto3.dynamodb.conditions import Key, Attr

def _query_by_month_window(table, start_d: date, end_d: date) -> list[dict]:
    """Consulta por ventana de días con GSI ByMonth (si existe y los datos están backfilleados)."""
    meses = {start_d.strftime("%Y-%m"), end_d.strftime("%Y-%m")}
    y1, y2 = ymd_int(start_d), ymd_int(end_d)
    items = []
    for mes in meses:
        resp = table.query(
            IndexName="ByMonth",
            KeyConditionExpression=Key("venc_yyyymm").eq(mes) & Key("venc_yyyymmdd").between(y1, y2),
        )
        items.extend(resp.get("Items", []))
    return items

def _scan_fallback_window(table, compania: str, start_d: date, end_d: date) -> list[dict]:
    """Fallback: si el GSI no devuelve nada, usamos scan + FilterExpression sobre strings ISO."""
    start_iso, end_iso = start_d.isoformat(), end_d.isoformat()
    items, last_key = [], None
    fe = Attr("compañia").eq(compania) & Attr("vencimiento_de_cuota").between(start_iso, end_iso)
    while True:
        kwargs = {"FilterExpression": fe}
        if last_key:
            kwargs["ExclusiveStartKey"] = last_key
        resp = table.scan(**kwargs)
        items.extend(resp.get("Items", []))
        last_key = resp.get("LastEvaluatedKey")
        if not last_key:
            break
    return items

def _dedupe_and_sort(items: list[dict]) -> list[dict]:
    seen, out = set(), []
    for it in items:
        key = (it.get("poliza"), it.get("item_id"))
        if key in seen: 
            continue
        seen.add(key); out.append(it)
    out.sort(key=lambda x: x.get("venc_yyyymmdd") or int(x.get("vencimiento_de_cuota","9999-12-31").replace("-","")))
    return out

def _filter_company_and_range(items: list[dict], compania: str, start_d: date, end_d: date) -> list[dict]:
    y1, y2 = ymd_int(start_d), ymd_int(end_d)
    out = []
    for it in items:
        if it.get("compañia") != compania:
            continue
        d = it.get("venc_yyyymmdd")
        if isinstance(d, int):
            if y1 <= d <= y2: out.append(it)
        else:
            # fallback si no tiene los derivados pero sí la ISO
            v = it.get("vencimiento_de_cuota")
            if isinstance(v, str) and (start_d.isoformat() <= v <= end_d.isoformat()):
                out.append(it)
    return _dedupe_and_sort(out)

@manejar_conexion
def vencimientos_clientes(table):
    compañia = st.selectbox("Seleccionar compañia", ["RIVADAVIA", "RUS", "COOP"])

    hoy = date.today()
    fin_7 = hoy + timedelta(days=7)
    ini_8 = hoy + timedelta(days=8)
    fin_15 = hoy + timedelta(days=15)

    # Primero intentamos por GSI
    gsi_0_7 = _query_by_month_window(table, hoy, fin_7)
    gsi_8_15 = _query_by_month_window(table, ini_8, fin_15)

    items_0_7 = _filter_company_and_range(gsi_0_7, compañia, hoy, fin_7)
    items_8_15 = _filter_company_and_range(gsi_8_15, compañia, ini_8, fin_15)

    # Si no hay nada (o muy poco) y sabés que debería haber, caemos a scan
    if not items_0_7:
        scan_0_7 = _scan_fallback_window(table, compañia, hoy, fin_7)
        items_0_7 = _dedupe_and_sort(scan_0_7)
    if not items_8_15:
        scan_8_15 = _scan_fallback_window(table, compañia, ini_8, fin_15)
        items_8_15 = _dedupe_and_sort(scan_8_15)

    st.markdown("### **Próximas a vencer en 7 días**")
    if items_0_7:
        _show_due_item_expanders(table, items_0_7)
    else:
        st.info("No hay vencimientos en los próximos 7 días.")

    st.markdown("### **Entre 8 y 15 días**")
    if items_8_15:
        _show_due_item_expanders(table, items_8_15)
    else:
        st.info("No hay vencimientos entre 8 y 15 días.")
