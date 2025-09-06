import { useEffect } from 'react'
import { useAuctionStore } from '@/store/auctionStore'
import { Publication, Auction, AuctionObject } from '@/types/auction'

interface UseAuctionOptions {
  publicationId?: string
  autoFetch?: boolean
}

export function useAuction({ publicationId, autoFetch = false }: UseAuctionOptions = {}) {
  const {
    currentPublication,
    currentAuction,
    currentAuctionObject,
    isLoading,
    error,
    favoriteAuctions,
    setCurrentAuction,
    setLoading,
    setError,
    addToFavorites,
    removeFromFavorites,
    isFavorite,
    clearCurrentAuction,
  } = useAuctionStore()

  // Fetch auction data (mock implementation)
  const fetchAuction = async (id: string) => {
    setLoading(true)
    setError(null)

    try {
      // Mock API call - replace with actual API
      const response = await fetch(`/api/auctions/${id}`)
      
      if (!response.ok) {
        throw new Error('Failed to fetch auction data')
      }

      const data = await response.json()
      
      if (data.success && data.publications.length > 0) {
        const publication = data.publications[0]
        const auction = publication.auctions[0]
        const auctionObject = auction.auction_objects[0]
        
        setCurrentAuction(publication, auction, auctionObject)
      } else {
        throw new Error('Auction not found')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  // Auto-fetch if publicationId is provided
  useEffect(() => {
    if (autoFetch && publicationId) {
      fetchAuction(publicationId)
    }
  }, [publicationId, autoFetch])

  // Toggle favorite status
  const toggleFavorite = (auctionId: string) => {
    if (isFavorite(auctionId)) {
      removeFromFavorites(auctionId)
    } else {
      addToFavorites(auctionId)
    }
  }

  return {
    // State
    publication: currentPublication,
    auction: currentAuction,
    auctionObject: currentAuctionObject,
    isLoading,
    error,
    favoriteAuctions,
    
    // Actions
    fetchAuction,
    toggleFavorite,
    isFavorite,
    clearCurrentAuction,
  }
}
