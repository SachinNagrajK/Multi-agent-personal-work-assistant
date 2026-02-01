"""Quick setup check and guide for Google APIs."""
import os
from pathlib import Path

def check_setup():
    """Check if Google API setup is complete."""
    backend_dir = Path(__file__).parent
    credentials_file = backend_dir / 'credentials.json'
    token_file = backend_dir / 'token.pickle'
    
    print("=" * 70)
    print("Google API Setup Status")
    print("=" * 70)
    
    # Check credentials.json
    if credentials_file.exists():
        print("✅ credentials.json found")
    else:
        print("❌ credentials.json NOT found")
        print("\n📋 TO DO:")
        print("   1. Follow the guide in GOOGLE_SETUP_GUIDE.md")
        print("   2. Download credentials.json from Google Cloud Console")
        print("   3. Place it in: backend/credentials.json")
        print("\n" + "=" * 70)
        return False
    
    # Check token.pickle
    if token_file.exists():
        print("✅ token.pickle found (already authenticated)")
    else:
        print("⚠️  token.pickle not found (need to authenticate)")
        print("   → Will create on first run")
    
    print("\n" + "=" * 70)
    print("✅ Setup looks good!")
    print("=" * 70)
    print("\n🚀 Next steps:")
    print("   1. Run: python google_auth.py")
    print("   2. Authorize in browser")
    print("   3. Test connections")
    print("\n" + "=" * 70)
    return True

if __name__ == "__main__":
    if check_setup():
        print("\nRun 'python google_auth.py' to test connections")
    else:
        print("\nComplete setup first, then run this script again")
