#!/usr/bin/env python3
"""Script to run database migrations."""

import asyncio
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from alembic.config import Config
from alembic import command
from app.database import engine
from app.config import settings


async def run_migrations():
    """Run Alembic migrations."""
    
    # Create Alembic config
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
    
    # Run migrations
    print("Running database migrations...")
    command.upgrade(alembic_cfg, "head")
    print("Migrations completed successfully!")


if __name__ == "__main__":
    asyncio.run(run_migrations())
