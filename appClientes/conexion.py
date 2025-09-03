import boto3
import streamlit as st


TABLE_NAME = "customers"


def get_table():
    """Return a DynamoDB table resource for the customers table."""
    try:
        dynamodb = boto3.resource("dynamodb")
        return dynamodb.Table(TABLE_NAME)
    except Exception as e:
        st.error(f"Error al conectar a DynamoDB: {e}")
        return None


def cerrar_conexion(_table: object) -> None:
    """DynamoDB no requiere cerrar conexiones explícitamente."""
    return None

