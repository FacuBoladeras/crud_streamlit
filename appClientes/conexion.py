import boto3
import streamlit as st

TABLE_NAME = "customers"  # cambia a "customers_v2" si ya tenés una tabla creada con otro esquema

def _ensure_table_exists(dynamodb):
    client = dynamodb.meta.client
    try:
        client.describe_table(TableName=TABLE_NAME)
    except client.exceptions.ResourceNotFoundException:
        client.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {"AttributeName": "poliza", "KeyType": "HASH"},    # PK
                {"AttributeName": "item_id", "KeyType": "RANGE"},  # SK (uuid)
            ],
            AttributeDefinitions=[
                {"AttributeName": "poliza", "AttributeType": "S"},
                {"AttributeName": "item_id", "AttributeType": "S"},
                {"AttributeName": "venc_yyyymmdd", "AttributeType": "N"},
                {"AttributeName": "venc_yyyymm", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "ByPolizaVenc",
                    "KeySchema": [
                        {"AttributeName": "poliza", "KeyType": "HASH"},
                        {"AttributeName": "venc_yyyymmdd", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                },
                {
                    "IndexName": "ByMonth",
                    "KeySchema": [
                        {"AttributeName": "venc_yyyymm", "KeyType": "HASH"},
                        {"AttributeName": "venc_yyyymmdd", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                },
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        client.get_waiter("table_exists").wait(TableName=TABLE_NAME)

def get_table():
    try:
        dynamodb = boto3.resource("dynamodb")
        _ensure_table_exists(dynamodb)
        return dynamodb.Table(TABLE_NAME)
    except Exception as e:
        st.error(f"Error al conectar a DynamoDB: {e}")
        return None

def cerrar_conexion(_table: object) -> None:
    return None


