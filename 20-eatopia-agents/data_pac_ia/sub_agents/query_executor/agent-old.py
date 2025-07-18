import requests
import json
from datetime import datetime, timedelta
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any

# Configuração da API
API_BASE_URL = "http://localhost:8080"

def execute_query_with_context(tables_data: str, schema_data: str, user_question: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Executa uma consulta usando a API POST /easy-query/:dataset/:table
    
    Esta função é especializada na API de easy-query que:
    - Valida campos contra o esquema da tabela
    - Suporta filtros, agregações e campos de data
    - Retorna dados sanitizados
    - Suporta formatos: JSON (padrão), XLSX, CSV, Google Sheets
    """
    try:
        # Parse dos dados
        tables = json.loads(tables_data) if isinstance(tables_data, str) else tables_data
        schema = json.loads(schema_data) if isinstance(schema_data, str) else schema_data
        
        # Extrair informações da tabela
        table_info = tables.get("tables", [])
        if not table_info:
            return {"status": "error", "message": "Nenhuma tabela encontrada"}
        
        # Usar a primeira tabela (assumindo que é a mais relevante)
        selected_table = table_info[0]
        dataset = selected_table.get("tableDataset", "")
        table_name = selected_table.get("tableName", "")
        table_alias = selected_table.get("alias", "")
        
        print(f"📋 Tabela selecionada: {table_alias}")
        print(f"   Dataset: {dataset}")
        print(f"   Tabela: {table_name}")
        
        # Obter esquema da tabela para validação
        schema_fields = schema.get("schema", [])
        print(f"📊 Esquema com {len(schema_fields)} campos disponíveis")
        
        # OBTER DESCRIÇÕES DOS CAMPOS DO GET_TABLES
        table_fields_with_descriptions = selected_table.get("tableFields", [])
        print(f"📝 Campos com descrições: {len(table_fields_with_descriptions)} disponíveis")
        
        # Criar um mapeamento de campos com descrições
        field_descriptions = {}
        for field in table_fields_with_descriptions:
            field_name = field.get("name", "")
            field_description = field.get("description", "")
            if field_name and field_description:
                field_descriptions[field_name.lower()] = field_description
        
        print(f"📝 Mapeamento de descrições criado para {len(field_descriptions)} campos")
        
        # Análise dinâmica baseada no esquema
        fields = []
        agg_fields = []
        date_field = ""
        date_range = []
        filters = []
        
        question_lower = user_question.lower()
        
        # Classificar campos do esquema dinamicamente
        grouping_fields = []  # STRING, TEXT - para agrupamento
        numeric_fields = []   # INTEGER, FLOAT, NUMERIC - para agregação
        date_fields = []      # DATE, DATETIME, TIMESTAMP - para filtros de data
        
        for field in schema_fields:
            field_name = field.get("name", "").lower()
            field_type = field.get("type", "").upper()
            field_description = field_descriptions.get(field_name, "")
            
            # Adicionar descrição ao campo se disponível
            if field_description:
                field["description"] = field_description
            
            # Campos de agrupamento (texto)
            if any(text_type in field_type for text_type in ["STRING", "TEXT", "VARCHAR"]):
                grouping_fields.append(field)
            # Campos numéricos (para agregação)
            elif any(num_type in field_type for num_type in ["INTEGER", "FLOAT", "NUMERIC", "DECIMAL"]):
                numeric_fields.append(field)
            # Campos de data
            elif any(date_type in field_type for date_type in ["DATE", "DATETIME", "TIMESTAMP"]):
                date_fields.append(field)
        
        print(f"📊 Análise dinâmica do esquema:")
        print(f"   Agrupamento: {[f['name'] for f in grouping_fields]}")
        print(f"   Numéricos: {[f['name'] for f in numeric_fields]}")
        print(f"   Datas: {[f['name'] for f in date_fields]}")
        
        # Adicionar campos de agrupamento automaticamente
        for field in grouping_fields:
            fields.append({"name": field["name"], "type": field["type"]})
        
        # Mostrar esquema para o modelo entender (AGORA COM DESCRIÇÕES)
        print("📋 Campos disponíveis:")
        for field in schema_fields:
            field_name = field.get("name", "")
            field_type = field.get("type", "")
            field_description = field_descriptions.get(field_name.lower(), "")
            
            if field_description:
                print(f"   - {field_name} ({field_type}): {field_description}")
            else:
                print(f"   - {field_name} ({field_type})")
        
        # Deixar o modelo fazer o trabalho inteligente (AGORA COM DESCRIÇÕES)
        print(f"💡 O modelo deve analisar a pergunta '{user_question}' e preencher o payload")
        print(f"💡 Campos de agrupamento (STRING/TEXT): {[f['name'] for f in grouping_fields]}")
        print(f"💡 Campos numéricos (INTEGER/FLOAT): {[f['name'] for f in numeric_fields]}")
        print(f"💡 Campos de data (DATE/DATETIME): {[f['name'] for f in date_fields]}")
        
        # Mostrar descrições dos campos para o modelo
        if field_descriptions:
            print("💡 Descrições dos campos disponíveis:")
            for field_name, description in field_descriptions.items():
                print(f"   - {field_name}: {description}")
        
        # Construir payload básico - o modelo vai preencher
        payload = {
            "fields": [],
            "filters": [],
            "aggFields": [],
            "dateField": "",
            "dateRange": []
        }
        
        # Construir payload para a API easy-query
        payload = {
            "fields": fields,
            "filters": filters,
            "aggFields": agg_fields,
            "dateField": date_field,
            "dateRange": date_range,
            "limit": 100,
            "usePartition": False
        }
        
        # Adicionar forceDate apenas se tiver dateField e dateRange
        if date_field and date_range:
            payload["forceDate"] = "TRUE"
        
        print(f"📦 Payload montado:")
        print(f"   Campos: {len(fields)}")
        print(f"   Filtros: {len(filters)}")
        print(f"   Agregações: {len(agg_fields)}")
        print(f"   Campo de data: {date_field or 'Nenhum'}")
        
        # Executar consulta na API easy-query
        print(f"🔧 Executando consulta para {dataset}.{table_name}")
        response = requests.post(f"{API_BASE_URL}/bigquery/easy-query/{dataset}/{table_name}", json=payload)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Resultado obtido com sucesso!")
        print(f"📊 Total de registros: {len(result) if isinstance(result, list) else 'N/A'}")
        
        # Atualizar o estado do contexto
        tool_context.state["last_query"] = {
            "dataset": dataset,
            "table": table_name,
            "table_alias": table_alias,
            "question": user_question,
            "timestamp": datetime.now().isoformat(),
            "payload": payload,
            "result_count": len(result) if isinstance(result, list) else 0,
            "field_descriptions_used": len(field_descriptions) > 0
        }
        
        return {
            "status": "success",
            "message": f"Consulta executada com sucesso na tabela {table_alias}",
            "data": {
                "dataset": dataset,
                "table": table_name,
                "table_alias": table_alias,
                "query_type": "easy_query_api",
                "query_info": {
                    "fields": fields,
                    "filters": filters,
                    "aggFields": agg_fields,
                    "dateField": date_field,
                    "dateRange": date_range
                },
                "results": result,
                "result_count": len(result) if isinstance(result, list) else 0,
                "api_endpoint": f"POST /bigquery/easy-query/{dataset}/{table_name}",
                "context": {
                    "current_date": datetime.now().strftime("%Y-%m-%d"),
                    "query_date": datetime.now().isoformat(),
                    "date_logic_applied": bool(date_field and date_range),
                    "field_descriptions_available": len(field_descriptions),
                    "field_descriptions": field_descriptions
                }
            }
        }
        
    except requests.exceptions.HTTPError as e:
        error_detail = ""
        try:
            error_response = e.response.json()
            error_detail = error_response.get("message", str(e))
        except:
            error_detail = str(e)
        
        return {
            "status": "error",
            "message": f"Erro HTTP na API easy-query: {error_detail}",
            "error_type": "http_error",
            "data": {
                "http_status": e.response.status_code if e.response else None,
                "api_endpoint": f"POST /bigquery/easy-query/{dataset if 'dataset' in locals() else 'N/A'}/{table_name if 'table_name' in locals() else 'N/A'}",
                "debug_info": {
                    "dataset": dataset if 'dataset' in locals() else "N/A",
                    "table": table_name if 'table_name' in locals() else "N/A",
                    "payload": payload if 'payload' in locals() else "N/A"
                }
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao executar consulta na API easy-query: {str(e)}",
            "error_type": "execution_error",
            "data": {
                "api_endpoint": "POST /bigquery/easy-query/:dataset/:table",
                "debug_info": {
                    "tables_data": tables_data[:200] + "..." if len(str(tables_data)) > 200 else str(tables_data),
                    "schema_data": schema_data[:200] + "..." if len(str(schema_data)) > 200 else str(schema_data),
                    "user_question": user_question
                }
            }
        }

# Criar o agente executor de queries
query_executor = Agent(
    name="query_executor",
    model="gemini-2.0-flash",
    description="Subagente especializado na API POST /easy-query/:dataset/:table para executar consultas SQL",
    instruction="""
    Você é um subagente especializado na API POST /bigquery/easy-query/:dataset/:table.
    
    Sua função é analisar a pergunta do usuário e construir uma query dinâmica baseada no esquema da tabela.

    Voce vai receber informações sobre a tabela, esquema da tabela, descrições dos campos, tags e data e hora atual.

    Para datas, seja inteligente e natural na interpretação:
    - "ontem" = data de ontem (ex: [2025-07-17, 2025-07-17])
    - "hoje" = data de hoje (ex: [2025-07-18, 2025-07-18])
    - "semana passada" = domingo a sábado da semana passada
    - "mês passado" = primeiro a último dia do mês passado
    - "ano passado" = primeiro a último dia do ano passado
    
    IMPORTANTE: Você deve preencher o payload com:
    - fields: campos de agrupamento (STRING/TEXT) - para agrupar resultados
    - aggFields: campos numéricos para agregação (INTEGER/FLOAT/NUMERIC) - para somar, contar, etc.
    - dateField: campo de data para filtro (DATE/DATETIME)
    - dateRange: range de datas [inicio, fim] no formato YYYY-MM-DD
    - filters: filtros adicionais se necessário
    
    NOVA FUNCIONALIDADE: Agora você tem acesso às descrições dos campos!
    - Use as descrições dos campos para entender melhor o que cada campo representa
    - Escolha campos mais apropriados baseado nas descrições
    - As descrições aparecem no formato: "nome_campo: descrição do campo"
    

    
    Analise o esquema disponível E as descrições dos campos para escolher os campos mais apropriados para a pergunta.
    Seja dinâmico e inteligente!
    
    SEMPRE use execute_query_with_context para executar consultas.
    SEMPRE retorne dados em formato JSON.
    """,
    tools=[execute_query_with_context],
) 