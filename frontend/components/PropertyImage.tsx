'use client'

import { useState } from 'react'
import { ChevronLeft, ChevronRight, Lock } from 'lucide-react'

interface PropertyImageProps {
  images?: string[]
  estimatedValue?: string
  auctionDate?: string
}

export default function PropertyImage({ 
  images = [], 
  estimatedValue = "342'000 CHF",
  auctionDate = "2025-10-23"
}: PropertyImageProps) {
  const [currentImageIndex, setCurrentImageIndex] = useState(0)
  
  // Mock images for now - in real app these would come from the API
  const mockImages = [
    '/api/placeholder/800/600',
    '/api/placeholder/400/300',
    '/api/placeholder/400/300',
    '/api/placeholder/400/300',
  ]

  const displayImages = images.length > 0 ? images : mockImages

  const nextImage = () => {
    setCurrentImageIndex((prev) => (prev + 1) % displayImages.length)
  }

  const prevImage = () => {
    setCurrentImageIndex((prev) => (prev - 1 + displayImages.length) % displayImages.length)
  }

  return (
    <div className="space-y-4">
      {/* Main Image */}
      <div className="relative">
        <div className="aspect-video bg-gray-200 rounded-lg overflow-hidden relative">
          <img
            src={displayImages[currentImageIndex]}
            alt="Property"
            className="w-full h-full object-cover"
            onError={(e) => {
              // Fallback to placeholder
              e.currentTarget.src = `https://via.placeholder.com/800x600/f3f4f6/6b7280?text=Property+Image+${currentImageIndex + 1}`
            }}
          />
          
          {/* Auction Banner */}
          <div className="absolute top-4 left-4 bg-red-600 text-white px-3 py-1 rounded-full text-sm font-medium">
            Auction in {Math.ceil((new Date(auctionDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))} days
          </div>

          {/* Navigation arrows */}
          {displayImages.length > 1 && (
            <>
              <button
                onClick={prevImage}
                className="absolute left-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 transition-opacity"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <button
                onClick={nextImage}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 transition-opacity"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </>
          )}
        </div>

        {/* Estimated Value */}
        <div className="mt-4">
          <p className="text-2xl font-bold text-gray-900">
            {estimatedValue} Estimated Value
          </p>
        </div>
      </div>

      {/* Thumbnail Grid */}
      <div className="grid grid-cols-3 gap-2">
        {displayImages.slice(0, 3).map((image, index) => (
          <div
            key={index}
            className={`aspect-video bg-gray-200 rounded-lg overflow-hidden cursor-pointer relative ${
              index === currentImageIndex ? 'ring-2 ring-primary-500' : ''
            }`}
            onClick={() => setCurrentImageIndex(index)}
          >
            <img
              src={image}
              alt={`Property ${index + 1}`}
              className="w-full h-full object-cover"
              onError={(e) => {
                e.currentTarget.src = `https://via.placeholder.com/400x300/f3f4f6/6b7280?text=Image+${index + 1}`
              }}
            />
            {index === 2 && displayImages.length > 3 && (
              <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                <div className="text-white text-center">
                  <Lock className="w-6 h-6 mx-auto mb-1" />
                  <span className="text-xs">Unlock</span>
                  <div className="text-xs mt-1">{displayImages.length}/36</div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
