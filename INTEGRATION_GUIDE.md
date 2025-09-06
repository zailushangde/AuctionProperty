# Frontend-Backend Integration Guide

This guide explains how to run the complete Swiss Auction Property application with real backend data.

## 🚀 Quick Start

### **Option 1: Use the Development Script (Recommended)**

```bash
# From the project root directory
./start-dev.sh
```

This script will:
- ✅ Start the backend API server on `http://localhost:8000`
- ✅ Start the frontend development server on `http://localhost:3000`
- ✅ Handle cleanup when you stop the servers

### **Option 2: Manual Setup**

#### **1. Start Backend**
```bash
cd backend
source ../.venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### **2. Start Frontend** (in a new terminal)
```bash
cd frontend
npm run dev
```

## 🔧 Configuration

### **Backend Configuration**
- **Port**: 8000
- **API Base URL**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`

### **Frontend Configuration**
- **Port**: 3000
- **API URL**: `http://localhost:8000` (configured in `lib/api.ts`)
- **Development URL**: `http://localhost:3000`

## 📊 API Integration Status

### ✅ **Completed Integration**

1. **Auctions List Endpoint**
   - **URL**: `GET /api/v1/auctions/`
   - **Frontend**: `app/auctions/page.tsx`
   - **Status**: ✅ Connected to real backend data

2. **Auction Detail Endpoint**
   - **URL**: `GET /api/v1/auctions/{id}`
   - **Frontend**: `app/auctions/[id]/page.tsx`
   - **Status**: ✅ Connected to real backend data

3. **Filtering & Pagination**
   - **Parameters**: canton, date_from, date_to, location, order_by, order_direction, page, size
   - **Frontend**: Filter panel in auctions page
   - **Status**: ✅ Fully integrated

### 📋 **API Endpoints Used**

| Endpoint | Method | Purpose | Frontend Usage |
|----------|--------|---------|----------------|
| `/api/v1/auctions/` | GET | List auctions with filters | Main auctions page |
| `/api/v1/auctions/{id}` | GET | Get auction details | Auction detail page |

## 🗄️ Database Integration

### **Current Database Status**
- ✅ **Supabase PostgreSQL** connected
- ✅ **8 auctions** loaded from real SHAB data
- ✅ **PostGIS extension** enabled for spatial data
- ✅ **All tables** created and populated

### **Data Flow**
```
SHAB XML → Parser → Database → API → Frontend
```

1. **SHAB XML** data fetched from official sources
2. **Parser** extracts structured data (auctions, debtors, contacts)
3. **Database** stores normalized data in PostgreSQL
4. **API** serves data via FastAPI endpoints
5. **Frontend** displays data with filtering and pagination

## 🎯 Features Working with Real Data

### **Auctions Listing Page** (`/auctions`)
- ✅ **Real auction data** from database
- ✅ **Property type filtering** (automatically detected from descriptions)
- ✅ **Canton filtering** (all 26 Swiss cantons)
- ✅ **Date range filtering** (auction dates)
- ✅ **Location search** (text search in location field)
- ✅ **Sorting** (date, location, newest first)
- ✅ **Pagination** (handles large datasets)

### **Auction Detail Page** (`/auctions/[id]`)
- ✅ **Full auction information** from database
- ✅ **Property descriptions** with HTML rendering
- ✅ **Important dates** (circulation/registration deadlines)
- ✅ **Property type badges** (auto-detected)
- ✅ **Action buttons** (ready for future features)

## 🔍 Testing the Integration

### **1. Test Backend API**
```bash
# Test auctions endpoint
curl http://localhost:8000/api/v1/auctions/

# Test with filters
curl "http://localhost:8000/api/v1/auctions/?canton=BE&page=1&size=5"
```

### **2. Test Frontend**
1. **Open browser**: `http://localhost:3000`
2. **Should redirect** to `/auctions` automatically
3. **Verify data**: Should see 8 real auctions from database
4. **Test filters**: Try canton, date, and location filters
5. **Test sorting**: Try different sort options
6. **Test detail page**: Click on any auction

### **3. Test API Connection**
```bash
# From frontend directory
node test-api-connection.js
```

## 🐛 Troubleshooting

### **Backend Issues**

#### **Port 8000 Already in Use**
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

#### **Database Connection Issues**
```bash
# Check database connection
cd backend
python -c "from app.database import AsyncSessionLocal; print('DB OK')"

# Check if tables exist
python scripts/check_database.py
```

#### **No Data in Database**
```bash
# Populate database with test data
cd backend
python scripts/enhanced_bootstrap.py
```

### **Frontend Issues**

#### **Port 3000 Already in Use**
```bash
# Frontend will automatically use next available port
# Or specify a different port
npm run dev -- -p 3001
```

#### **API Connection Failed**
- ✅ Check if backend is running on `http://localhost:8000`
- ✅ Verify API URL in `lib/api.ts`
- ✅ Check browser console for CORS errors
- ✅ Test API directly: `curl http://localhost:8000/api/v1/auctions/`

#### **No Data Displayed**
- ✅ Check if database has data: `python scripts/check_database.py`
- ✅ Check API response: `curl http://localhost:8000/api/v1/auctions/`
- ✅ Check browser network tab for API calls

## 📈 Performance Optimization

### **Backend Optimizations**
- ✅ **Async/await** for database operations
- ✅ **Connection pooling** with asyncpg
- ✅ **Indexed queries** for filtering and sorting
- ✅ **Pagination** to handle large datasets

### **Frontend Optimizations**
- ✅ **Client-side filtering** for property types
- ✅ **Debounced search** for location filtering
- ✅ **Loading states** for better UX
- ✅ **Error boundaries** for graceful error handling

## 🔄 Development Workflow

### **Making Changes**

1. **Backend Changes**
   - Edit files in `backend/`
   - Server auto-reloads with `--reload` flag
   - Test API endpoints: `http://localhost:8000/docs`

2. **Frontend Changes**
   - Edit files in `frontend/`
   - Server auto-reloads with `npm run dev`
   - Browser auto-refreshes on changes

3. **Database Changes**
   - Create migration: `alembic revision --autogenerate -m "description"`
   - Apply migration: `alembic upgrade head`
   - Update bootstrap script if needed

### **Adding New Features**

1. **New API Endpoint**
   - Add to `backend/app/api/v1/`
   - Update `frontend/lib/api.ts`
   - Add types to `frontend/types/auction.ts`

2. **New Filter**
   - Add to `AuctionFilters` type
   - Update API endpoint parameters
   - Add UI component in frontend

3. **New Page**
   - Create in `frontend/app/`
   - Add routing and navigation
   - Connect to API endpoints

## 📊 Current Data Status

### **Database Contents**
- **Publications**: 4 (from SHAB XML)
- **Auctions**: 8 (with real auction data)
- **Debtors**: 8 (with debtor information)
- **Contacts**: 4 (with contact details)
- **Auction Objects**: 8 (with property descriptions)

### **Data Quality**
- ✅ **Real Swiss locations** (Vex, Moutier, Sion, etc.)
- ✅ **Accurate dates** (auction dates, deadlines)
- ✅ **Property descriptions** in multiple languages
- ✅ **Estimated values** in CHF
- ✅ **Contact information** for auction offices

## 🎉 Success Indicators

### **✅ Integration is Working When:**
1. **Frontend loads** without errors
2. **Auctions display** with real data from database
3. **Filters work** and update results
4. **Sorting works** and changes order
5. **Detail pages** show full auction information
6. **Property types** are correctly detected and displayed
7. **No console errors** in browser developer tools

### **🚀 Ready for Production When:**
1. **All tests pass** (unit, integration, e2e)
2. **Performance is acceptable** (load times < 2s)
3. **Error handling** covers all edge cases
4. **Security measures** are in place
5. **Monitoring and logging** are configured

The integration is now complete and ready for development and testing! 🎯
