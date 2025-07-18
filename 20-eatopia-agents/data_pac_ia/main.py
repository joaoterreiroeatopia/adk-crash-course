#!/usr/bin/env python3
"""
Data Pac IA - Agente de Consultas de Dados

Este arquivo executa o agente de forma interativa.
"""

import os

# Tentar importar dotenv, mas não falhar se não estiver instalado
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv não instalado. Configure as variáveis de ambiente manualmente.")

from agent import root_agent

def main():
    """Função principal para executar o agente Data Pac IA."""
    
    print("🤖 Data Pac IA - Agente de Consultas de Dados")
    print("=" * 50)
    print("Este agente pode ajudar você a:")
    print("- Encontrar tabelas relevantes para suas consultas")
    print("- Entender a estrutura dos dados")
    print("- Executar consultas personalizadas")
    print("\nDigite 'sair' para encerrar.")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\n💬 Sua pergunta sobre dados: ").strip()
            
            if user_input.lower() in ['sair', 'exit', 'quit']:
                print("👋 Até logo!")
                break
            
            if not user_input:
                continue
            
            print("\n🔍 Processando sua pergunta...")
            response = root_agent.run(user_input)
            print(f"\n🤖 {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Encerrando...")
            break
        except Exception as e:
            print(f"\n❌ Erro: {str(e)}")

if __name__ == "__main__":
    main() 