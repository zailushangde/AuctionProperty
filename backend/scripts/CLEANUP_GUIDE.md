# Database Cleanup Guide

This guide shows you how to clean your database after testing or when you need to reset it.

## 🚀 Quick Cleanup Options

### 1. **Quick Test Data Cleanup** (Recommended for testing)

```bash
# Clean only the test publications we used
python scripts/quick_cleanup.py

# Or use the full cleanup script
python scripts/cleanup_database.py --mode test
```

**What it does:**
- ✅ Removes only test publications (`c42e67af-486d-44f4-8c6e-0ad03538770d`, `bb0b8622-803e-413e-8d71-bb6da17f5b0c`)
- ✅ Removes all related data (auctions, debtors, contacts, etc.)
- ✅ Keeps system tables intact
- ✅ Safe for development/testing

### 2. **Complete Database Reset** (Use with caution)

```bash
# Clean ALL data in the database
python scripts/cleanup_database.py --mode all --confirm

# Or without confirmation (dangerous!)
python scripts/cleanup_database.py --mode all
```

**What it does:**
- ⚠️ Removes ALL application data
- ⚠️ Keeps system tables (spatial_ref_sys, etc.)
- ⚠️ Resets sequences if any exist
- ⚠️ **Use only when you want to start completely fresh**

### 3. **Check Database Status**

```bash
# Show current database statistics
python scripts/cleanup_database.py --mode stats

# Or use the quick version
python scripts/quick_cleanup.py stats
```

## 📋 Available Cleanup Scripts

### `cleanup_database.py` - Full Featured Cleanup

**Features:**
- ✅ Multiple cleanup modes
- ✅ Detailed logging and statistics
- ✅ Error handling and rollback
- ✅ Confirmation prompts for safety
- ✅ Dependency-aware deletion order

**Usage:**
```bash
# Show help
python scripts/cleanup_database.py --help

# Clean test data only
python scripts/cleanup_database.py --mode test

# Clean all data (with confirmation)
python scripts/cleanup_database.py --mode all

# Clean all data (skip confirmation)
python scripts/cleanup_database.py --mode all --confirm

# Show statistics
python scripts/cleanup_database.py --mode stats
```

### `quick_cleanup.py` - Simple Cleanup

**Features:**
- ✅ Fast and simple
- ✅ Removes only test data
- ✅ Minimal dependencies
- ✅ Good for development workflow

**Usage:**
```bash
# Clean test data
python scripts/quick_cleanup.py

# Show statistics
python scripts/quick_cleanup.py stats
```

## 🔄 Common Workflows

### Development Testing Workflow

```bash
# 1. Run your tests
python scripts/bootstrap_database.py scripts/sample_publication_ids.txt

# 2. Test your application
curl http://localhost:8000/api/v1/auctions/

# 3. Clean up when done
python scripts/quick_cleanup.py

# 4. Verify cleanup
python scripts/quick_cleanup.py stats
```

### Production Reset Workflow

```bash
# 1. Backup your data first (if needed)
# pg_dump your_database > backup.sql

# 2. Clean all data
python scripts/cleanup_database.py --mode all --confirm

# 3. Verify cleanup
python scripts/cleanup_database.py --mode stats

# 4. Restore from backup or re-populate
# psql your_database < backup.sql
```

### CI/CD Pipeline Workflow

```bash
# In your CI/CD pipeline
python scripts/cleanup_database.py --mode all --confirm
python scripts/bootstrap_database.py test_publications.txt
# Run your tests
python scripts/cleanup_database.py --mode all --confirm
```

## 🛠️ Manual Cleanup Options

### Using SQL Directly

```sql
-- Connect to your database and run:

-- Clean all application data
DELETE FROM auction_views;
DELETE FROM user_subscriptions;
DELETE FROM contacts;
DELETE FROM debtors;
DELETE FROM auction_objects;
DELETE FROM auctions;
DELETE FROM publications;

-- Reset sequences (if any)
-- Note: PostgreSQL with UUIDs doesn't use sequences
```

### Using Alembic (Nuclear Option)

```bash
# Drop all tables and recreate schema
alembic downgrade base
alembic upgrade head
```

**⚠️ Warning:** This will drop ALL tables including system tables. Only use if you want to completely reset the database schema.

## 📊 Understanding the Cleanup Process

### Data Dependencies

The cleanup scripts handle data dependencies in the correct order:

```
auction_views → user_subscriptions → contacts → debtors → auction_objects → auctions → publications
```

### What Gets Cleaned

**Test Data Cleanup:**
- ✅ Publications with test IDs
- ✅ Related auctions, debtors, contacts
- ✅ Related auction objects
- ✅ Related user subscriptions and views

**Full Cleanup:**
- ✅ All publications
- ✅ All auctions and related data
- ✅ All user subscriptions
- ✅ All analytics data
- ✅ System tables (spatial_ref_sys) are preserved

### What's Preserved

- ✅ **System tables**: `spatial_ref_sys`, `information_schema`, etc.
- ✅ **Database schema**: Tables, indexes, constraints
- ✅ **Extensions**: PostGIS, UUID extensions
- ✅ **User permissions**: Database users and roles

## 🔍 Troubleshooting

### Common Issues

1. **Permission Errors**
   ```bash
   # Make sure you have the right database permissions
   # Check your .env file has the correct DATABASE_URL
   ```

2. **Connection Errors**
   ```bash
   # Verify database is running and accessible
   python -c "from app.database import AsyncSessionLocal; print('DB OK')"
   ```

3. **Partial Cleanup**
   ```bash
   # If cleanup fails partway through, run it again
   # The scripts are idempotent and safe to re-run
   ```

4. **Foreign Key Constraints**
   ```bash
   # The scripts handle dependencies automatically
   # If you get constraint errors, use the full cleanup script
   ```

### Verification

After cleanup, verify the database is clean:

```bash
# Check statistics
python scripts/cleanup_database.py --mode stats

# Test API (should return empty results)
curl http://localhost:8000/api/v1/auctions/

# Check database directly
python -c "
import asyncio
from app.database import AsyncSessionLocal
from sqlalchemy import text

async def check():
    async with AsyncSessionLocal() as db:
        count = await db.scalar(text('SELECT COUNT(*) FROM publications'))
        print(f'Publications: {count}')

asyncio.run(check())
"
```

## 🎯 Best Practices

### For Development
- ✅ Use `quick_cleanup.py` for daily testing
- ✅ Use `--mode test` for targeted cleanup
- ✅ Always verify cleanup with `--mode stats`

### For Production
- ✅ **Always backup before full cleanup**
- ✅ Use `--mode all --confirm` for complete reset
- ✅ Test cleanup scripts in staging first
- ✅ Monitor database performance during cleanup

### For CI/CD
- ✅ Use `--mode all --confirm` for clean builds
- ✅ Include cleanup in your test pipeline
- ✅ Verify cleanup success in your tests

## 📞 Support

If you encounter issues:

1. **Check the logs** for detailed error messages
2. **Verify database connection** and permissions
3. **Try the quick cleanup** first before full cleanup
4. **Check for running transactions** that might block cleanup
5. **Use manual SQL** as a last resort

## 🔄 Integration with Other Scripts

The cleanup scripts work well with other database scripts:

```bash
# Complete workflow
python scripts/cleanup_database.py --mode all --confirm
python scripts/bootstrap_database.py my_publications.txt
python scripts/check_database.py
```

This gives you a complete database management toolkit for your auction platform!
