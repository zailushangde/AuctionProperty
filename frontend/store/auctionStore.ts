import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { Publication, Auction, AuctionObject } from '@/types/auction'

interface AuctionState {
  // Current auction data
  currentPublication: Publication | null
  currentAuction: Auction | null
  currentAuctionObject: AuctionObject | null
  
  // Loading states
  isLoading: boolean
  error: string | null
  
  // Favorites
  favoriteAuctions: string[]
  
  // Actions
  setCurrentAuction: (publication: Publication, auction: Auction, auctionObject: AuctionObject) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  addToFavorites: (auctionId: string) => void
  removeFromFavorites: (auctionId: string) => void
  isFavorite: (auctionId: string) => boolean
  clearCurrentAuction: () => void
}

export const useAuctionStore = create<AuctionState>()(
  devtools(
    (set, get) => ({
      // Initial state
      currentPublication: null,
      currentAuction: null,
      currentAuctionObject: null,
      isLoading: false,
      error: null,
      favoriteAuctions: [],

      // Actions
      setCurrentAuction: (publication, auction, auctionObject) => {
        set({
          currentPublication: publication,
          currentAuction: auction,
          currentAuctionObject: auctionObject,
          error: null,
        })
      },

      setLoading: (loading) => {
        set({ isLoading: loading })
      },

      setError: (error) => {
        set({ error, isLoading: false })
      },

      addToFavorites: (auctionId) => {
        const { favoriteAuctions } = get()
        if (!favoriteAuctions.includes(auctionId)) {
          set({ favoriteAuctions: [...favoriteAuctions, auctionId] })
        }
      },

      removeFromFavorites: (auctionId) => {
        const { favoriteAuctions } = get()
        set({ 
          favoriteAuctions: favoriteAuctions.filter(id => id !== auctionId) 
        })
      },

      isFavorite: (auctionId) => {
        const { favoriteAuctions } = get()
        return favoriteAuctions.includes(auctionId)
      },

      clearCurrentAuction: () => {
        set({
          currentPublication: null,
          currentAuction: null,
          currentAuctionObject: null,
          error: null,
        })
      },
    }),
    {
      name: 'auction-store',
    }
  )
)
