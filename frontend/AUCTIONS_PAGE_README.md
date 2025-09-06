# Auctions Page - Frontend Implementation

This document describes the implementation of the auctions listing page and auction detail pages in the frontend.

## 📁 File Structure

```
frontend/
├── app/
│   ├── auctions/
│   │   ├── page.tsx              # Main auctions listing page
│   │   └── [id]/
│   │       └── page.tsx          # Individual auction detail page
├── components/
│   └── Header.tsx                # Updated with auctions link
├── lib/
│   ├── api.ts                    # Updated with auction API methods
│   └── utils.ts                  # Utility functions for data processing
└── types/
    └── auction.ts                # Updated with auction list types
```

## 🎯 Features Implemented

### **Auctions Listing Page (`/auctions`)**

#### **Core Functionality**
- ✅ **List all auctions** from the database
- ✅ **Real-time filtering** by multiple criteria
- ✅ **Sorting options** (date, location, newest first)
- ✅ **Pagination** support
- ✅ **Property type filtering** with visual badges
- ✅ **Responsive design** for mobile and desktop

#### **Filter Options**
1. **Canton Filter** - Filter by Swiss canton
2. **Date Range** - Filter by auction date range
3. **Location Search** - Text search in location field
4. **Property Type** - Filter by property type:
   - 🏠 Residential
   - 🏢 Commercial
   - 🌲 Land
   - 🏗️ Mixed Use
   - 🏛️ Other

#### **Sorting Options**
- **Date** (Earliest/Latest)
- **Location** (A-Z/Z-A)
- **Newest First** (by publication date)

#### **Visual Features**
- **Property type badges** with icons
- **Auction date and time** display
- **Location information** with map pin icon
- **Deadline information** (circulation/registration)
- **Property description** preview
- **Loading states** and error handling

### **Auction Detail Page (`/auctions/[id]`)**

#### **Core Functionality**
- ✅ **Detailed auction information** display
- ✅ **Property descriptions** with full HTML rendering
- ✅ **Important dates** and deadlines
- ✅ **Action buttons** for user interactions
- ✅ **Property type badges** and categorization
- ✅ **Responsive layout** with sidebar

#### **Information Displayed**
1. **Auction Details**
   - Date and time
   - Location
   - Property type badges

2. **Property Information**
   - Full property descriptions
   - Multiple properties per auction

3. **Important Dates**
   - Circulation deadlines
   - Registration deadlines
   - Additional comments

4. **Action Buttons**
   - Register for Auction
   - Download Documents
   - Contact Office

## 🔧 Technical Implementation

### **API Integration**

#### **Mock API (Development)**
```typescript
// Mock data for development
const mockAuctions: AuctionListResponse = {
  items: [...], // Array of auction items
  total: 3,
  page: 1,
  size: 20,
  pages: 1
}
```

#### **Real API (Production)**
```typescript
// Real API endpoints
GET /api/v1/auctions/                    // List auctions with filters
GET /api/v1/auctions/{id}                // Get single auction
```

### **Data Types**

#### **AuctionListItem**
```typescript
interface AuctionListItem {
  id: string
  date: string
  time?: string
  location: string
  circulation_entry_deadline?: string
  circulation_comment_deadline?: string
  registration_entry_deadline?: string
  registration_comment_deadline?: string
  created_at: string
  updated_at: string
  auction_objects: AuctionObject[]
}
```

#### **AuctionFilters**
```typescript
interface AuctionFilters {
  canton?: string
  date_from?: string
  date_to?: string
  location?: string
  property_type?: string
  order_by?: 'date' | 'location' | 'created_at'
  order_direction?: 'asc' | 'desc'
  page?: number
  size?: number
}
```

### **Utility Functions**

#### **Property Type Detection**
```typescript
function getPropertyType(description: string): PropertyType {
  // Analyzes property description to determine type
  // Returns: 'residential' | 'commercial' | 'land' | 'mixed' | 'other'
}
```

#### **Date/Time Formatting**
```typescript
function formatDate(dateString: string): string
function formatTime(timeString?: string): string
```

#### **Text Processing**
```typescript
function stripHtml(html: string): string
function truncateText(text: string, maxLength: number): string
```

## 🎨 UI/UX Features

### **Design System**
- **Consistent styling** with Tailwind CSS
- **Primary color scheme** with blue accents
- **Responsive grid layouts**
- **Card-based design** for auction items
- **Icon integration** with Lucide React

### **User Experience**
- **Intuitive filtering** with collapsible filter panel
- **Visual feedback** for active filters
- **Loading states** with spinners
- **Error handling** with retry options
- **Breadcrumb navigation** on detail pages
- **Hover effects** and transitions

### **Accessibility**
- **Semantic HTML** structure
- **Keyboard navigation** support
- **Screen reader** friendly
- **Color contrast** compliance
- **Focus indicators** for interactive elements

## 🚀 Usage

### **Navigation**
1. **From Homepage** - Click "View Objects" in header
2. **Direct URL** - Navigate to `/auctions`
3. **From Detail Page** - Use back button or breadcrumb

### **Filtering**
1. **Click "Filters"** button to expand filter panel
2. **Select options** from dropdowns and inputs
3. **Filters apply automatically** as you type/select
4. **Clear filters** by selecting "All" options

### **Sorting**
1. **Use sort dropdown** in the top bar
2. **Choose sort field** (date, location, newest)
3. **Direction changes** automatically based on current selection

### **Viewing Details**
1. **Click any auction card** to view details
2. **Use back button** to return to list
3. **Action buttons** for registration and documents

## 🔄 Integration with Backend

### **API Endpoints Used**
- `GET /api/v1/auctions/` - List auctions with filters
- `GET /api/v1/auctions/{id}` - Get auction details

### **Filter Parameters**
- `canton` - Swiss canton code
- `date_from` - Start date (YYYY-MM-DD)
- `date_to` - End date (YYYY-MM-DD)
- `location` - Location search term
- `order_by` - Sort field
- `order_direction` - Sort direction
- `page` - Page number
- `size` - Items per page

### **Response Format**
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 20,
  "pages": 5
}
```

## 🧪 Testing

### **Mock Data**
- **3 sample auctions** with different property types
- **Realistic Swiss locations** and dates
- **Varied property descriptions** in multiple languages
- **Different deadline scenarios**

### **Test Scenarios**
1. **Load auctions list** - Verify data displays correctly
2. **Apply filters** - Test each filter type
3. **Sort functionality** - Test all sort options
4. **Pagination** - Test page navigation
5. **Property type detection** - Verify correct categorization
6. **Detail page navigation** - Test routing and data display
7. **Error handling** - Test network errors and missing data
8. **Responsive design** - Test on different screen sizes

## 🎯 Future Enhancements

### **Planned Features**
- **Map integration** for location visualization
- **Advanced search** with full-text search
- **Favorites system** for saved auctions
- **Email notifications** for new auctions
- **Export functionality** for auction lists
- **User authentication** for premium features

### **Performance Optimizations**
- **Virtual scrolling** for large lists
- **Image lazy loading** for property photos
- **Caching strategies** for API responses
- **Progressive loading** for better UX

## 📱 Mobile Responsiveness

### **Breakpoints**
- **Mobile** (< 768px) - Single column layout
- **Tablet** (768px - 1024px) - Two column layout
- **Desktop** (> 1024px) - Full three column layout

### **Mobile Features**
- **Collapsible filters** to save space
- **Touch-friendly** buttons and inputs
- **Swipe gestures** for navigation
- **Optimized typography** for small screens

## 🔧 Development Setup

### **Prerequisites**
- Node.js 18+
- Next.js 14+
- TypeScript
- Tailwind CSS

### **Installation**
```bash
cd frontend
npm install
npm run dev
```

### **Environment Variables**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

The auctions page is now fully functional and ready for integration with the real backend API! 🎉
