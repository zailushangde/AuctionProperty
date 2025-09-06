# Database Bootstrap Scripts

This directory contains scripts to populate the database with SHAB publication data.

## 🚀 Quick Start

### 1. Prepare Your Publication IDs

Create a text file with publication IDs (one per line):

```bash
# Create a file with your publication IDs
echo "c42e67af-486d-44f4-8c6e-0ad03538770d" > my_publications.txt
echo "bb0b8622-803e-413e-8d71-bb6da17f5b0c" >> my_publications.txt
# Add more IDs as needed...
```

### 2. Run the Bootstrap Script

```bash
# From the backend directory
source /path/to/your/.venv/bin/activate
python scripts/bootstrap_database.py my_publications.txt
```

### 3. Verify the Data

```bash
# Test the API
python -c "
from app.main import app
from fastapi.testclient import TestClient
client = TestClient(app)
response = client.get('/api/v1/auctions/')
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Total auctions: {data[\"total\"]}')
"
```

## 📋 Script Details

### `bootstrap_database.py`

The main bootstrap script that:

1. **Reads publication IDs** from a file or uses the default list
2. **Constructs URLs** in the correct format:
   - XML: `https://www.shab.ch/api/v1/publications/{id}/xml`
   - HTML: `https://www.shab.ch/#!/search/publications/detail/{id}`
3. **Fetches and parses** XML data using the existing SHAB parser
4. **Stores data** in the database using the existing task functions
5. **Handles errors** gracefully and provides detailed logging
6. **Skips duplicates** if publications already exist

#### Usage Options

```bash
# Use default publication IDs (hardcoded in script)
python scripts/bootstrap_database.py

# Use publication IDs from a file
python scripts/bootstrap_database.py my_publications.txt

# Use the simple runner script
python scripts/run_bootstrap.py
```

#### Features

- ✅ **Batch processing** (configurable batch size)
- ✅ **Error handling** with detailed logging
- ✅ **Duplicate detection** (skips existing publications)
- ✅ **Progress tracking** with statistics
- ✅ **Respectful rate limiting** (1 second delay between batches)
- ✅ **Concurrent processing** within batches

### `run_bootstrap.py`

A simple wrapper script that demonstrates how to use the bootstrap functionality programmatically.

### `sample_publication_ids.txt`

Contains sample publication IDs for testing.

## 🔧 Configuration

### Batch Size

Modify the batch size in the script:

```python
# In bootstrap_database.py or run_bootstrap.py
stats = await bootstrap.bootstrap_database(publication_ids, batch_size=5)
```

### Rate Limiting

Adjust the delay between batches:

```python
# In bootstrap_database.py
await asyncio.sleep(1)  # 1 second delay
```

## 📊 Output

The script provides detailed logging and final statistics:

```
============================================================
🎉 DATABASE BOOTSTRAP COMPLETED!
============================================================
📊 Total publications: 10
✅ Successfully processed: 8
⏭️  Skipped (already exist): 1
❌ Errors: 1
============================================================
```

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Make sure you're in the backend directory
   cd /path/to/backend
   source .venv/bin/activate
   ```

2. **Database Connection Issues**
   ```bash
   # Check your .env file has the correct DATABASE_URL
   cat .env | grep DATABASE_URL
   ```

3. **XML Parsing Errors**
   - Check if the publication ID is valid
   - Verify the SHAB API is accessible
   - Check the XML structure hasn't changed

4. **Storage Errors**
   - Ensure the database schema is up to date
   - Run `alembic upgrade head` if needed
   - Check for missing required fields

### Debug Mode

For detailed debugging, modify the logging level:

```python
# In bootstrap_database.py
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

## 📈 Performance

### Typical Performance

- **Processing speed**: ~2-3 publications per second
- **Memory usage**: Low (processes one batch at a time)
- **Network usage**: Respectful (1 second delay between batches)

### Scaling

For large datasets:

1. **Increase batch size** (but not too much to avoid overwhelming the server)
2. **Run multiple instances** with different publication ID files
3. **Use Celery** for distributed processing (see `app/tasks/shab_tasks.py`)

## 🧹 Database Cleanup

After testing, clean up your database:

```bash
# Quick cleanup (removes test data only)
python scripts/quick_cleanup.py

# Full cleanup (removes all data)
python scripts/cleanup_database.py --mode all --confirm

# Check database status
python scripts/cleanup_database.py --mode stats
```

For detailed cleanup options, see [CLEANUP_GUIDE.md](CLEANUP_GUIDE.md).

## 🔄 Integration with Existing System

The bootstrap script integrates seamlessly with the existing system:

- ✅ Uses the same **SHAB parser** (`app/parsers/shab_parser.py`)
- ✅ Uses the same **storage functions** (`app/tasks/shab_tasks.py`)
- ✅ Uses the same **database models** (`app/models/`)
- ✅ Compatible with **Celery tasks** for background processing
- ✅ Works with the **existing API** endpoints

## 📝 Example Workflow

```bash
# 1. Get publication IDs from SHAB search
# (You'll need to extract these from the SHAB website)

# 2. Create your publication list
echo "publication-id-1" > publications.txt
echo "publication-id-2" >> publications.txt

# 3. Run bootstrap
python scripts/bootstrap_database.py publications.txt

# 4. Verify data
python -c "
import asyncio
from app.database import AsyncSessionLocal
from app.models import Publication
from sqlalchemy import select, func

async def check():
    async with AsyncSessionLocal() as db:
        count = await db.scalar(select(func.count(Publication.id)))
        print(f'Publications in database: {count}')

asyncio.run(check())
"

# 5. Test API
curl http://localhost:8000/api/v1/auctions/
```

## 🎯 Next Steps

After bootstrapping your database:

1. **Set up Celery** for automated daily fetching
2. **Configure the frontend** to consume the API
3. **Implement payment system** for premium content
4. **Add map visualization** using the spatial data
5. **Set up monitoring** and alerting

## 📞 Support

If you encounter issues:

1. Check the logs for detailed error messages
2. Verify your database connection and schema
3. Test with a small set of publication IDs first
4. Check the SHAB API accessibility
5. Review the existing parser and task implementations
