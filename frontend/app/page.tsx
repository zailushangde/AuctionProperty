'use client'

import Header from '@/components/Header'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'


export default function HomePage() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to auctions page
    router.push('/auctions')
  }, [router])

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Redirecting to auctions...</p>
        </div>
      </div>
    </div>
  )
}
