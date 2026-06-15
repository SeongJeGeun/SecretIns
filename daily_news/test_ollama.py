import sys
import ollama

def test_ollama():
    print("=" * 60)
    print("Testing Local Ollama & Models...")
    print("=" * 60)
    
    try:
        # 1. List models
        print("1. Listing local models...")
        models_response = ollama.list()
        models = [m.model for m in models_response.models]
        print(f"   Available models: {models}")
        
        has_gemma = any('gemma4:12b' in m for m in models)
        has_bge = any('bge-m3' in m for m in models)
        
        print(f"   gemma4:12b present: {has_gemma}")
        print(f"   bge-m3 present: {has_bge}")
        
        if not has_gemma:
            print("   ✗ ERROR: gemma4:12b is not pulled.")
        if not has_bge:
            print("   ✗ ERROR: bge-m3 is not pulled.")
            
        # 2. Test Gemma 4 Inference
        print("\n2. Testing gemma4:12b chat completion...")
        response = ollama.chat(
            model='gemma4:12b',
            messages=[
                {'role': 'user', 'content': '안녕하세요! 짧게 한 문장으로 대답해주세요.'}
            ],
            options={
                'temperature': 0.7
            }
        )
        print(f"   Response: {response['message']['content'].strip()}")
        
        # 3. Test bge-m3 Embeddings
        print("\n3. Testing bge-m3 embeddings...")
        embedding_response = ollama.embeddings(
            model='bge-m3',
            prompt='로컬 AI 오케스트라 RAG 테스트'
        )
        vector = embedding_response.get('embedding', [])
        print(f"   Embedding vector generated. Dimension: {len(vector)}")
        print("   ✓ All Ollama connection tests passed successfully!")
        
    except Exception as e:
        print(f"   ✗ Connection test failed: {e}")
        sys.exit(1)
        
    print("=" * 60)

if __name__ == '__main__':
    test_ollama()
