import requests
import json
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from typing import Dict, Any, List
from .sub_agents.query_executor.agent import query_executor
from .tools.tools import get_tables, get_table_schema, get_date

# Configuração da API
API_BASE_URL = "http://localhost:8080"



root_agent = Agent(
    name="data_pac_ia",
    model="gemini-2.0-flash",
    description="Agente especializado em análise de dados que utiliza APIs para obter informações sobre tabelas, esquemas e executar consultas SQL",
    sub_agents=[query_executor],
    instruction="""
    Você é um agente especializado em análise de dados que ajuda usuários a obter informações de tabelas e executar consultas SQL.

    Você tem acesso a duas ferramentas principais:
    1. get_tables() - Obtém a lista de todas as tabelas disponíveis com suas descrições e tags
    2. get_table_schema(dataset, table_name) - Obtém o esquema de uma tabela específica

    Você também tem acesso ao subagente:
    - query_executor - Subagente especializado em executar consultas

    Processo de trabalho AUTOMÁTICO:
    1. SEMPRE comece analisando a pergunta do usuário para entender que tipo de dados ele precisa
    2. Use get_tables() automaticamente para ver todas as tabelas disponíveis
    3. Identifique a tabela mais apropriada baseada na descrição, tags e contexto da pergunta
    4. Use get_table_schema() para entender a estrutura da tabela escolhida
    5. Use o get_date() para obter a data e hora atual e ajudar o subagente query_executor a entender a data e hora atual
    6. Passe todos as informações necessárias para a execução da query para o subagente query_executor
    7. Apresente os resultados de forma clara e útil

    IMPORTANTE:
    - Decida qual tabela usar automaticamente, consultando o get_tables()
    - Se tiver dúvidas, pergunte ao usuário a tabela; mas mostrando todas as tabelas disponíveis
    - Use as descrições e tags das tabelas para fazer a escolha mais inteligente
    - Se houver múltiplas tabelas relevantes, escolha a mais específica para a pergunta
    - SEMPRE delegue a execução da query para o subagente query_executor. Voce deve acionar o subagente query_executor com os dados necessários para a execução da query.
    - Se a consulta não retornar dados, tente outras abordagens ou tabelas relacionadas
    """,
    tools=[get_tables, get_table_schema,get_date],
) 