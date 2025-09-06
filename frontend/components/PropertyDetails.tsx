'use client'

import { format } from 'date-fns'
import { InfoCard, InfoRow, DocumentItem, TimelineItem } from './InfoCard'
import { MapPin, Calendar, Clock, User, Building, Home, TreePine, Mountain } from 'lucide-react'

interface PropertyDetailsProps {
  publication: any
  auction: any
  auctionObject: any
}

export default function PropertyDetails({ publication, auction, auctionObject }: PropertyDetailsProps) {
  const formatDate = (dateString: string) => {
    return format(new Date(dateString), 'MMM dd, yyyy')
  }

  const formatTime = (timeString: string) => {
    return format(new Date(`2000-01-01T${timeString}`), 'h:mm a')
  }

  return (
    <div className="space-y-6">
      {/* Property Description */}
      <div className="card">
        <h3 className="section-title">Property Description</h3>
        <div 
          className="prose prose-sm max-w-none text-gray-700"
          dangerouslySetInnerHTML={{ __html: auctionObject.description }}
        />
      </div>

      {/* Property Details */}
      <InfoCard title="Property Details" isLocked={true}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <InfoRow label="Property Type" value="Single-family house" icon={<Home className="w-4 h-4" />} />
          <InfoRow label="Built Year" value="2000" icon={<Building className="w-4 h-4" />} />
          <InfoRow label="Garages" value="2" icon={<Building className="w-4 h-4" />} />
          <InfoRow label="Property Area" value="1,469 m²" icon={<MapPin className="w-4 h-4" />} />
          <InfoRow label="Building Area" value="69 m²" icon={<Home className="w-4 h-4" />} />
          <InfoRow label="Forest Area" value="177 m²" icon={<TreePine className="w-4 h-4" />} />
          <InfoRow label="Field Area" value="1,223 m²" icon={<Mountain className="w-4 h-4" />} />
        </div>
      </InfoCard>

      {/* Change History */}
      <InfoCard title="Change History" isLocked={true}>
        <div className="space-y-3">
          <div className="flex items-center justify-between py-2 border-b border-gray-100">
            <div>
              <p className="font-medium text-gray-900">Mountain ranges</p>
              <p className="text-sm text-gray-500">September 5, 2025</p>
            </div>
            <button className="btn-secondary text-sm">Unlock</button>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-gray-100">
            <div>
              <p className="font-medium text-gray-900">Documents have been updated</p>
              <p className="text-sm text-gray-500">September 3, 2025</p>
            </div>
            <button className="btn-secondary text-sm">Unlock</button>
          </div>
        </div>
      </InfoCard>

      {/* Land */}
      <InfoCard title="Land" isLocked={true}>
        <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center">
          <div className="text-center">
            <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-2" />
            <p className="text-gray-500">Cadastral Map</p>
          </div>
        </div>
      </InfoCard>

      {/* Values */}
      <InfoCard title="Values" isLocked={true}>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-gray-700">Market Value</span>
            <div className="flex items-center space-x-2">
              <div className="w-32 h-2 bg-gray-200 rounded-full">
                <div className="w-3/4 h-full bg-blue-500 rounded-full"></div>
              </div>
              <span className="text-sm text-gray-600">75%</span>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-700">Auction Value</span>
            <div className="flex items-center space-x-2">
              <div className="w-32 h-2 bg-gray-200 rounded-full">
                <div className="w-1/2 h-full bg-green-500 rounded-full"></div>
              </div>
              <span className="text-sm text-gray-600">50%</span>
            </div>
          </div>
        </div>
      </InfoCard>

      {/* Remarks */}
      <InfoCard title="Remarks" isLocked={true}>
        <div className="bg-gray-50 p-4 rounded-lg">
          <p className="text-gray-600 text-sm">
            Additional legal information and conditions for this property auction...
          </p>
        </div>
      </InfoCard>

      {/* Neighborhood */}
      <InfoCard title="Neighborhood" isLocked={true}>
        <div className="flex items-center space-x-4">
          <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center">
            <Mountain className="w-8 h-8 text-gray-400" />
          </div>
          <div className="flex-1">
            <h4 className="font-medium text-gray-900">Anniviers (Region)</h4>
            <p className="text-sm text-gray-500">24,337 km²</p>
          </div>
          <button className="btn-secondary text-sm">Unlock</button>
        </div>
      </InfoCard>

      {/* Documents */}
      <InfoCard title="Documents">
        <div className="space-y-0">
          <DocumentItem name="Auction conditions" type="PDF Document" isLocked={true} />
          <DocumentItem name="Land Register extract" type="PDF Document" isLocked={true} />
          <DocumentItem name="SPA Policy" type="PDF Document" isLocked={true} />
          <DocumentItem name="Official valuation" type="PDF Document" isLocked={true} />
        </div>
      </InfoCard>

      {/* Property Description from Publication */}
      <InfoCard title="Property description from publication" isLocked={true}>
        <div className="bg-gray-50 p-4 rounded-lg">
          <textarea
            className="w-full h-24 bg-transparent border-none resize-none text-gray-600"
            placeholder="Additional property description..."
            disabled
          />
        </div>
      </InfoCard>

      {/* Learn More Section */}
      <div className="card">
        <h3 className="section-title">Learn more about foreclosures</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors cursor-pointer">
            <div className="aspect-video bg-gray-200 rounded mb-3"></div>
            <h4 className="font-medium text-gray-900 mb-2">
              Foreclosure auctions in Graubünden: chalet, cabin or holiday apartment?
            </h4>
            <p className="text-sm text-gray-500">July 28, 2025</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors cursor-pointer">
            <div className="aspect-video bg-gray-200 rounded mb-3"></div>
            <h4 className="font-medium text-gray-900 mb-2">
              The most important laws and regulations on foreclosure sales in Switzerland
            </h4>
            <p className="text-sm text-gray-500">December 11, 2024</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors cursor-pointer">
            <div className="aspect-video bg-gray-200 rounded mb-3"></div>
            <h4 className="font-medium text-gray-900 mb-2">
              You need these documents for your first real estate auction
            </h4>
            <p className="text-sm text-gray-500">August 18, 2025</p>
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="text-xs text-gray-500 bg-gray-50 p-4 rounded-lg">
        <p>
          The information provided on this page is for general information purposes only. 
          While we endeavor to keep the information up to date and correct, we make no representations 
          or warranties of any kind, express or implied, about the completeness, accuracy, reliability, 
          suitability or availability with respect to the website or the information, products, services, 
          or related graphics contained on the website for any purpose. Any reliance you place on such 
          information is therefore strictly at your own risk. We recommend consulting with a professional 
          advisor before making any decisions.
        </p>
      </div>
    </div>
  )
}
