from datetime import datetime
from typing import Dict, Any
import requests
API_BASE_URL = "http://localhost:8080"

def get_date() -> dict:
    """
    Get the current time in the format YYYY-MM-DD
    """
    return {
        "current_time": datetime.now().strftime("%Y-%m-%d"),
    }

def get_tables() -> Dict[str, Any]:
    """
    Obtém a lista de tabelas disponíveis com suas descrições e tags
    """
    try:
        response = requests.get(f"{API_BASE_URL}/data_pac/tables")
        response.raise_for_status()
        return {
            "status": "success",
            "tables": response.json()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao obter tabelas: {str(e)}"
        }

def get_table_schema(dataset: str, table_name: str) -> Dict[str, Any]:
    """
    Obtém o esquema de uma tabela específica
    """
    try:
        response = requests.get(f"{API_BASE_URL}/bigquery/schema/{dataset}/{table_name}")
        response.raise_for_status()
        return {
            "status": "success",
            "schema": response.json()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao obter esquema da tabela {dataset}.{table_name}: {str(e)}"
        }
