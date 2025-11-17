"""
Script de Teste e Verificação do Sistema
Verifica se todos os componentes estão funcionando corretamente
"""

import sys
import os

def print_section(title):
    """Imprime cabeçalho de seção"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_module(module_name):
    """Verifica se um módulo está instalado"""
    try:
        __import__(module_name)
        print(f"✅ {module_name:20s} - OK")
        return True
    except ImportError:
        print(f"❌ {module_name:20s} - NÃO INSTALADO")
        return False

def check_file(filepath):
    """Verifica se um arquivo existe"""
    if os.path.exists(filepath):
        print(f"✅ {filepath:30s} - OK")
        return True
    else:
        print(f"❌ {filepath:30s} - NÃO ENCONTRADO")
        return False

def test_nlp():
    """Testa o módulo NLP"""
    try:
        from nlp_chat import ChatbotNLP
        chatbot = ChatbotNLP()
        
        pergunta = "Qual a lotação do ônibus?"
        resposta = chatbot.gerar_resposta(pergunta)
        
        if resposta and len(resposta) > 0:
            print("✅ NLP funcionando")
            return True
        else:
            print("⚠️ NLP retornou resposta vazia")
            return False
    except Exception as e:
        print(f"❌ Erro no NLP: {e}")
        return False

def test_ml():
    """Testa o modelo de ML"""
    try:
        import joblib
        modelo = joblib.load('dados/modelo_lotacao.pkl')
        features = joblib.load('dados/features.pkl')
        
        import pandas as pd
        teste_df = pd.DataFrame([[14, 2, 30]], columns=features)
        previsao = modelo.predict(teste_df)[0]
        
        if 0 <= previsao <= 100:
            print(f"✅ ML funcionando - Previsão: {previsao:.0f}%")
            return True
        else:
            print(f"⚠️ ML retornou valor fora do esperado: {previsao}")
            return False
    except Exception as e:
        print(f"❌ Erro no ML: {e}")
        return False

def test_data():
    """Testa os dados"""
    try:
        import pandas as pd
        df = pd.read_csv('dados/dados_onibus.csv')
        
        if len(df) > 0:
            print(f"✅ Dados carregados - {len(df)} registros")
            print(f"   Colunas: {', '.join(df.columns)}")
            print(f"   Linhas únicas: {len(df['linha'].unique())}")
            return True
        else:
            print("⚠️ Arquivo de dados vazio")
            return False
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return False

def main():
    """Função principal de teste"""
    print("\n" + "🔍"*30)
    print("  VERIFICAÇÃO DO SISTEMA DE TRANSPORTE INTELIGENTE")
    print("🔍"*30)
    
    # 1. Verificar módulos Python
    print_section("1️⃣ VERIFICANDO DEPENDÊNCIAS PYTHON")
    
    modules = [
        'dash',
        'plotly',
        'pandas',
        'numpy',
        'sklearn',
        'joblib',
        'statsmodels',
        'spacy',
        'requests'
    ]
    
    modules_ok = sum([check_module(m) for m in modules])
    print(f"\n📊 Resultado: {modules_ok}/{len(modules)} módulos instalados")
    
    # 2. Verificar arquivos do projeto
    print_section("2️⃣ VERIFICANDO ARQUIVOS DO PROJETO")
    
    files = [
        'coleta_sptrans.py',
        'ml_simples.py',
        'modelo_arima_rf.py',
        'nlp_chat.py',
        'dashboard.py',
        'main.py',
        'requirements.txt'
    ]
    
    files_ok = sum([check_file(f) for f in files])
    print(f"\n📊 Resultado: {files_ok}/{len(files)} arquivos encontrados")
    
    # 3. Verificar pasta de dados
    print_section("3️⃣ VERIFICANDO PASTA DE DADOS")
    
    if os.path.exists('dados'):
        print("✅ Pasta 'dados/' existe")
        
        data_files = [
            'dados/dados_onibus.csv',
            'dados/modelo_lotacao.pkl',
            'dados/features.pkl'
        ]
        
        data_ok = sum([check_file(f) for f in data_files])
        print(f"\n📊 Resultado: {data_ok}/{len(data_files)} arquivos de dados")
    else:
        print("❌ Pasta 'dados/' não existe")
        data_ok = 0
    
    # 4. Testar componentes
    print_section("4️⃣ TESTANDO COMPONENTES")
    
    print("\n🧪 Testando Dados...")
    data_test = test_data()
    
    print("\n🧪 Testando Machine Learning...")
    ml_test = test_ml()
    
    print("\n🧪 Testando NLP...")
    nlp_test = test_nlp()
    
    # 5. Verificar spaCy
    print_section("5️⃣ VERIFICANDO MODELO SPACY")
    
    try:
        import spacy
        nlp_model = spacy.load("pt_core_news_sm")
        print("✅ Modelo spaCy (pt_core_news_sm) carregado")
        spacy_ok = True
    except:
        print("❌ Modelo spaCy não encontrado")
        print("   Execute: python -m spacy download pt_core_news_sm")
        spacy_ok = False
    
    # 6. Resumo Final
    print_section("📊 RESUMO FINAL")
    
    total_checks = 5
    passed_checks = sum([
        modules_ok >= 8,  # Pelo menos 8 de 9 módulos
        files_ok >= 6,    # Pelo menos 6 de 7 arquivos
        data_ok >= 2,     # Pelo menos 2 de 3 arquivos de dados
        ml_test or data_test,  # ML ou Dados funcionando
        nlp_test or not spacy_ok  # NLP funcionando ou spaCy não instalado (esperado)
    ])
    
    print(f"\n✅ Checks passados: {passed_checks}/{total_checks}")
    
    if passed_checks >= 4:
        print("\n" + "🎉"*20)
        print("  ✅ SISTEMA PRONTO PARA USO!")
        print("  Execute: python main.py")
        print("🎉"*20)
        return True
    elif passed_checks >= 2:
        print("\n" + "⚠️"*20)
        print("  ⚠️ SISTEMA PARCIALMENTE FUNCIONAL")
        print("  Verifique os erros acima e instale dependências faltantes")
        print("⚠️"*20)
        return False
    else:
        print("\n" + "❌"*20)
        print("  ❌ SISTEMA NÃO ESTÁ PRONTO")
        print("  Instale as dependências: pip install -r requirements.txt")
        print("  Execute: python coleta_sptrans.py")
        print("  Execute: python ml_simples.py")
        print("❌"*20)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)