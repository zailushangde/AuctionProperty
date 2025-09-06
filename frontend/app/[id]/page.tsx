'use client'

import Header from '@/components/Header'
import AuctionDetailClient from '@/components/AuctionDetailClient'
import { useEffect, useState } from 'react'
import { Publication, Auction, AuctionObject } from '@/types/auction'
import { useParams } from 'next/navigation'

// This would be replaced with actual API calls
function getAuctionData(id: string) {
  // Mock data - in real app this would be an API call
  const mockData = {
    "success": true,
    "url": "https://www.shab.ch/api/v1/publications/bb0b8622-803e-413e-8d71-bb6da17f5b0c/xml",
    "publications_count": 1,
    "publications": [
      {
        "id": "bb0b8622-803e-413e-8d71-bb6da17f5b0c",
        "publication_date": "2025-09-05",
        "expiration_date": "2026-09-05",
        "title": {
          "de": "Betreibungsamtliche Grundstücksteigerung Blaise Blein",
          "en": "Property auction initiated by the debt enforcement office Blaise Blein",
          "it": "Incanto immobiliare Blaise Blein",
          "fr": "Vente aux enchères d'immeubles dans le cadre de la poursuite Blaise Blein"
        },
        "language": "fr",
        "canton": "VS",
        "registration_office": {
          "id": "4095950d-a5d2-11e8-99a2-0050569d3c43",
          "display_name": "Office des poursuites des districts de Sion, Hérens et Conthey",
          "street": "Rue de la Piscine",
          "street_number": "10",
          "swiss_zip_code": "1950",
          "town": "Sion",
          "contains_post_office_box": false
        },
        "auctions": [
          {
            "id": "6c8521f9-55c9-4bca-99cf-f65fb72a9143",
            "date": "2025-10-23",
            "time": "11:00:00",
            "location": "au Café de la Place, Place du Cotterd 1, 1981 Vex",
            "circulation": {
              "entry_deadline": "2025-09-25",
              "comment_entry_deadline": null
            },
            "registration": {
              "entry_deadline": "2025-10-03",
              "comment_entry_deadline": null
            },
            "auction_objects": [
              {
                "description": "<p>Commune de Vex :</p><p>Parcelle No 4687, plan No 9, nom local &#34;Mayens des Plans&#34;, surface totale de 1'469 m2, soit un bâtiment de 69 m2, une forêt dense / forêt de 177m2 et un pré, champ de 1'223 m2</p><p>Estimation officielle : Fr. 342'000.00</p>"
              }
            ]
          }
        ],
        "debtors": [
          {
            "id": "88d1d485-4859-4265-b75e-4338f51bc4cd",
            "debtor_type": "person" as const,
            "name": "Blein",
            "prename": "Blaise",
            "date_of_birth": "1964-10-15",
            "country_of_origin": null,
            "residence": {
              "select_type": "switzerland" as const
            },
            "address_switzerland": {
              "street": "Rue du Port",
              "house_number": "25",
              "swiss_zip_code": "1815",
              "town": "Clarens"
            },
            "address": "Rue du Port 25",
            "city": "Clarens",
            "postal_code": "1815",
            "legal_form": null
          }
        ],
        "contacts": [
          {
            "id": "f7ab5c82-86bb-4329-b345-3ec3934f04f5",
            "name": "Office des poursuites des districts de Sion, Hérens et Conthey",
            "address": "Rue de la Piscine 10",
            "postal_code": "1950",
            "city": "Sion",
            "phone": "+41 27 606 40 00",
            "email": "info@office-poursuites-sion.ch",
            "contact_type": "office" as const,
            "office_id": "4095950d-a5d2-11e8-99a2-0050569d3c43",
            "contains_post_office_box": false
          }
        ]
      }
    ]
  }

  // In real app, check if publication exists
  if (id !== mockData.publications[0].id) {
    return null
  }
  
  return mockData
}

export default function AuctionDetailPage() {
  const params = useParams()
  const [publication, setPublication] = useState<Publication | null>(null)
  const [auction, setAuction] = useState<Auction | null>(null)
  const [auctionObject, setAuctionObject] = useState<AuctionObject | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 100))
        
        const data = getAuctionData(params.id as string)
        
        if (!data) {
          setError('Auction not found')
          return
        }

        const pub = data.publications[0]
        setPublication(pub)
        setAuction(pub.auctions[0])
        setAuctionObject(pub.auctions[0].auction_objects[0])
      } catch (err) {
        setError('Failed to load auction data')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [params.id])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading auction data...</p>
        </div>
      </div>
    )
  }

  if (error || !publication || !auction || !auctionObject) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Auction Not Found</h1>
          <p className="text-gray-600 mb-8">
            The auction you're looking for doesn't exist or has been removed.
          </p>
          <a
            href="/"
            className="btn-primary"
          >
            Go Home
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <AuctionDetailClient 
        publication={publication}
        auction={auction}
        auctionObject={auctionObject}
      />
    </div>
  )
}
