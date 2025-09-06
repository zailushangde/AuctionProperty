'use client'

import { Share2, Heart } from 'lucide-react'
import PropertyImage from './PropertyImage'
import PropertyDetails from './PropertyDetails'
import Sidebar from './Sidebar'
import { Publication, Auction, AuctionObject } from '@/types/auction'

interface AuctionDetailClientProps {
  publication: Publication
  auction: Auction
  auctionObject: AuctionObject
}

export default function AuctionDetailClient({ 
  publication, 
  auction, 
  auctionObject 
}: AuctionDetailClientProps) {
  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: 'Historic village house in Albinen',
        text: publication.title.en,
        url: window.location.href,
      })
    } else {
      // Fallback to clipboard
      navigator.clipboard.writeText(window.location.href)
      alert('Link copied to clipboard!')
    }
  }

  const handleSave = () => {
    // In a real app, this would save to user's favorites
    alert('Property saved to favorites!')
  }

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Property Title and Actions */}
      <div className="mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Historic village house in Albinen
            </h1>
            <p className="text-lg text-gray-600">
              {publication.title.en}
            </p>
          </div>
          <div className="flex items-center space-x-3 mt-4 sm:mt-0">
            <button 
              onClick={handleShare}
              className="flex items-center space-x-2 text-gray-600 hover:text-primary-600 transition-colors"
            >
              <Share2 className="w-5 h-5" />
              <span>Share</span>
            </button>
            <button 
              onClick={handleSave}
              className="flex items-center space-x-2 text-gray-600 hover:text-primary-600 transition-colors"
            >
              <Heart className="w-5 h-5" />
              <span>Save</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content - 2/3 width */}
        <div className="lg:col-span-2 space-y-8">
          {/* Property Images */}
          <PropertyImage 
            estimatedValue="342'000 CHF"
            auctionDate={auction.date}
          />

          {/* Property Details */}
          <PropertyDetails 
            publication={publication}
            auction={auction}
            auctionObject={auctionObject}
          />
        </div>

        {/* Sidebar - 1/3 width */}
        <div className="lg:col-span-1">
          <Sidebar 
            publication={publication}
            auction={auction}
            contacts={publication.contacts}
          />
        </div>
      </div>
    </main>
  )
}
