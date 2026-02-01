import os
from dotenv import load_dotenv

load_dotenv()

def test_openai():
    """Test OpenAI API key"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        client.models.list()
        print("✅ OpenAI: Working")
        return True
    except Exception as e:
        print(f"❌ OpenAI: {e}")
        return False

def test_pinecone():
    """Test Pinecone API key and host"""
    try:
        from pinecone import Pinecone
        api_key = os.getenv("PINECONE_API_KEY")
        host = os.getenv("PINECONE_HOST")
        
        if not api_key:
            print("❌ Pinecone: API key missing")
            return False
        
        if not host:
            print("❌ Pinecone: Host URL missing (required for Pinecone 3.0+)")
            print("   Get it from: https://app.pinecone.io -> Your Index -> Host URL")
            return False
        
        if not host.startswith("https://"):
            print("❌ Pinecone: Host URL should start with 'https://'")
            return False
        
        pc = Pinecone(api_key=api_key)
        indexes = pc.list_indexes()
        print(f"✅ Pinecone: Working (API key + host configured)")
        
        # Check if workspace-memory index exists
        index_names = [idx.name for idx in indexes]
        if "workspace-memory" in index_names:
            print("   ✓ Index 'workspace-memory' found")
        else:
            print("   ⚠️  Index 'workspace-memory' not found - will be created on first run")
        
        return True
    except Exception as e:
        print(f"❌ Pinecone: {e}")
        return False

def test_langsmith():
    """Test LangSmith API key"""
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if api_key and len(api_key) > 10:
        print("✅ LangSmith: Key present (will verify on first workflow run)")
        return True
    else:
        print("❌ LangSmith: Key missing or invalid")
        return False

def test_secret_key():
    """Test SECRET_KEY"""
    secret = os.getenv("SECRET_KEY")
    if secret and len(secret) >= 32:
        print("✅ SECRET_KEY: Valid")
        return True
    else:
        print("❌ SECRET_KEY: Too short or missing (minimum 32 characters)")
        return False

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🔑 Testing API Keys and Configuration")
    print("="*50 + "\n")
    
    all_good = True
    all_good &= test_openai()
    all_good &= test_pinecone()
    all_good &= test_langsmith()
    all_good &= test_secret_key()
    
    print("\n" + "="*50)
    if all_good:
        print("✅ ALL CHECKS PASSED!")
        print("\nYou're ready to run the application:")
        print("  1. python main.py      (start backend)")
        print("  2. cd ../frontend && npm run dev    (start frontend)")
        print("  3. Open http://localhost:5173")
    else:
        print("❌ SOME CHECKS FAILED")
        print("\nPlease fix the errors above.")
        print("See API_KEYS.md for detailed instructions.")
    print("="*50 + "\n")
