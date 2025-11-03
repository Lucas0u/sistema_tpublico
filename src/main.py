import webbrowser
import os
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def executar_sistema():
    """Executa todo o sistema"""
    print("=" * 60)
    print("🚇 SISTEMA INTELIGENTE DE TRANSPORTE PÚBLICO")
    print("🤖 IA + Machine Learning + Dashboard Interativo")
    print("=" * 60)
    
    try:
        # Executar coleta - IMPORT DIRETO
        print("\n1️⃣  COLETANDO DADOS...")
        from coleta_sptrans import main as coleta_main
        coleta_main()
        
        # Executar ML
        print("\n2️⃣  TREINANDO MODELO DE IA...")
        from ml_simples import main as ml_main
        ml_main()
        
        # Executar dashboard
        print("\n3️⃣  INICIANDO DASHBOARD INTERATIVO...")
        print("🌐 Abrindo navegador em: http://127.0.0.1:8050")
        print("⏳ Aguarde alguns segundos...")
        
        # Abrir navegador
        webbrowser.open("http://127.0.0.1:8050")
        
        # Importar e executar dashboard
        from dashboard import app
        app.run(debug=False, port=8050)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    executar_sistema()