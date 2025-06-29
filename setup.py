#!/usr/bin/env python3
"""
Setup script for AI Email Agent
This script helps users set up their environment and install dependencies.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_env_file():
    """Create a .env file with proper encoding"""
    env_content = """# AI Email Agent Environment Variables
# Add your API keys here

# OpenAI API Key (for AI content generation)
OPENAI_API_KEY=your_openai_api_key_here

# Cohere API Key (alternative AI provider)
COHERE_API_KEY=your_cohere_api_key_here

# Note: Replace the placeholder values with your actual API keys
# You can get these from:
# - OpenAI: https://platform.openai.com/api-keys
# - Cohere: https://dashboard.cohere.ai/api-keys
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ .env file created successfully with UTF-8 encoding")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def main():
    print("🚀 AI Email Agent Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install Python dependencies")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        print("❌ Failed to create .env file")
        sys.exit(1)
    
    # Check if frontend directory exists
    if os.path.exists("frontend"):
        print("🔄 Installing frontend dependencies...")
        if not run_command("cd frontend && npm install", "Installing frontend dependencies"):
            print("❌ Failed to install frontend dependencies")
            sys.exit(1)
    else:
        print("⚠️  Frontend directory not found")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit the .env file and add your API keys")
    print("2. Start the backend: python main.py")
    print("3. Start the frontend: cd frontend && npm run dev")
    print("4. Open http://localhost:5173 in your browser")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main() 