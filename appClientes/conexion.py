import boto3
import streamlit as st


TABLE_NAME = "customers"

def _ensure_table_exists(dynamodb):
    client = dynamodb.meta.client
    try:
        client.describe_table(TableName=TABLE_NAME)
    except client.exceptions.ResourceNotFoundException:
        client.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {"AttributeName": "poliza", "KeyType": "HASH"},   # PK
                {"AttributeName": "id_sql", "KeyType": "RANGE"}   # SK
            ],
            AttributeDefinitions=[
                {"AttributeName": "poliza", "AttributeType": "S"},
                {"AttributeName": "id_sql", "AttributeType": "N"},
                {"AttributeName": "vencimiento_de_cuota", "AttributeType": "S"},  # Para GSI
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "VencimientoIndex",
                    "KeySchema": [
                        {"AttributeName": "vencimiento_de_cuota", "KeyType": "HASH"},
                        {"AttributeName": "poliza", "KeyType": "RANGE"}
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
                }
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )


def get_table():
    """Return a DynamoDB table resource for the customers table."""
    try:
        dynamodb = boto3.resource("dynamodb")
        _ensure_table_exists(dynamodb)
        return dynamodb.Table(TABLE_NAME)
    except Exception as e:
        st.error(f"Error al conectar a DynamoDB: {e}")
        return None



def cerrar_conexion(_table: object) -> None:
    """DynamoDB no requiere cerrar conexiones explícitamente."""
    return None

