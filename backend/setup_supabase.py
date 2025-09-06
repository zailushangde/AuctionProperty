#!/usr/bin/env python3
"""
Setup script for Supabase database configuration.
This script helps you configure the database connection for the Swiss Auction Platform.
"""

import os
import sys
from pathlib import Path

def setup_supabase_config():
    """Setup Supabase database configuration."""
    
    print("🏠 Swiss Real Estate Auction Platform - Supabase Setup")
    print("=" * 60)
    
    # Get password from user
    password = input("Enter your Supabase database password: ").strip()
    
    if not password:
        print("❌ Password cannot be empty!")
        sys.exit(1)
    
    # Database URL template
    db_url = f"postgresql://postgres:{password}@db.hwyuvjamgcawjcpsitrj.supabase.co:5432/postgres"
    
    print(f"\n✅ Database URL configured:")
    print(f"   {db_url}")
    
    # Update .env file
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_example.exists():
        # Read env.example
        with open(env_example, 'r') as f:
            content = f.read()
        
        # Replace the database URL
        content = content.replace(
            "DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.hwyuvjamgcawjcpsitrj.supabase.co:5432/postgres",
            f"DATABASE_URL={db_url}"
        )
        
        # Write to .env
        with open(env_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Created .env file with Supabase configuration")
    else:
        # Create basic .env file
        env_content = f"""# Database Configuration
DATABASE_URL={db_url}

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# SHAB API Configuration
SHAB_BASE_URL=https://amtsblattportal.ch/api/v1

# Application Configuration
APP_NAME=Swiss Auction Platform
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-change-in-production

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Scheduler Configuration
FETCH_INTERVAL_HOURS=24
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Created .env file with Supabase configuration")
    
    print(f"\n📋 Next steps:")
    print(f"   1. Run database migrations: alembic upgrade head")
    print(f"   2. Start the application: uvicorn app.main:app --reload")
    print(f"   3. Or use Docker: docker-compose up -d")
    
    print(f"\n🔗 Supabase Dashboard:")
    print(f"   https://supabase.com/dashboard/project/hwyuvjamgcawjcpsitrj")

if __name__ == "__main__":
    setup_supabase_config()
