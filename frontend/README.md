# Swiss Auction Property Frontend

A modern Next.js frontend for the Swiss real estate auction platform that displays property auction listings from SHAB XML data.

## Features

- **Property Detail Pages**: Comprehensive auction property information display
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **State Management**: Zustand for efficient state management
- **TypeScript**: Full type safety throughout the application
- **Modern UI**: Clean, professional interface inspired by Swiss design principles

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Icons**: Lucide React
- **Date Handling**: date-fns

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Copy environment variables:
```bash
cp .env.local.example .env.local
```

3. Start the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── [id]/              # Dynamic auction detail pages
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   └── not-found.tsx      # 404 page
├── components/            # Reusable UI components
│   ├── Header.tsx         # Navigation header
│   ├── InfoCard.tsx       # Information display cards
│   ├── PropertyDetails.tsx # Main property information
│   ├── PropertyImage.tsx  # Property image gallery
│   └── Sidebar.tsx        # Right sidebar with timeline
├── hooks/                 # Custom React hooks
│   └── useAuction.ts      # Auction data management
├── lib/                   # Utility libraries
│   └── api.ts             # API client and mock data
├── store/                 # Zustand state stores
│   └── auctionStore.ts    # Auction state management
├── types/                 # TypeScript type definitions
│   └── auction.ts         # Auction data types
└── README.md
```

## Key Components

### Property Detail Page (`/[id]`)

The main auction detail page displays:

- **Property Images**: Gallery with main image and thumbnails
- **Property Information**: Detailed description and specifications
- **Auction Timeline**: Important dates and deadlines
- **Contact Information**: Office details and contact methods
- **Documents**: Available property documents (with unlock functionality)
- **Quick Actions**: Register, schedule inspection, save property

### Responsive Design

- **Mobile-first**: Optimized for mobile devices
- **Breakpoints**: sm (640px), md (768px), lg (1024px), xl (1280px)
- **Grid Layout**: 2/3 main content, 1/3 sidebar on desktop
- **Stacked Layout**: Single column on mobile

### State Management

Uses Zustand for:
- Current auction data
- Loading states
- Error handling
- Favorites management
- User preferences

## API Integration

The frontend is designed to work with the backend API:

- **Base URL**: Configurable via `NEXT_PUBLIC_API_URL`
- **Endpoints**: `/api/v1/publications/{id}`
- **Mock Data**: Available for development without backend

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Code Style

- **TypeScript**: Strict mode enabled
- **ESLint**: Next.js recommended configuration
- **Prettier**: Code formatting (recommended)
- **Tailwind**: Utility-first CSS approach

## Future Enhancements

- **Maps Integration**: Mapbox/Leaflet for property locations
- **Internationalization**: Multi-language support (DE, FR, IT)
- **Search & Filters**: Advanced property search
- **User Authentication**: Login and user accounts
- **Real-time Updates**: WebSocket integration for live auction data
- **PWA Support**: Progressive Web App capabilities

## Contributing

1. Follow the existing code style
2. Add TypeScript types for new features
3. Test responsive design on multiple devices
4. Update documentation for new components

## License

This project is part of the Swiss Auction Property platform.
