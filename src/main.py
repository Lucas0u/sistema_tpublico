import webbrowser
import os

def executar_sistema():
    """Executa todo o sistema"""
    print("=" * 60)
    print("🚇 SISTEMA INTELIGENTE DE TRANSPORTE PÚBLICO")
    print("🤖 IA + Machine Learning + Dashboard Interativo")
    print("=" * 60)
    
    try:
        
        print("\n1️⃣  COLETANDO DADOS...")
        import coleta_sptrans
        coleta_sptrans.main()
        
        
        print("\n2️⃣  TREINANDO MODELO DE IA...")
        import ml_simples
        ml_simples.main()
        
        
        print("\n3️⃣  INICIANDO DASHBOARD INTERATIVO...")
        print("🌐 Abrindo navegador em: http://127.0.0.1:8050")
        print("⏳ Aguarde alguns segundos...")
        
        
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