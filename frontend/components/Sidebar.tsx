'use client'

import { format } from 'date-fns'
import { TimelineItem } from './InfoCard'
import { Calendar, Clock, MapPin, User, Building, Phone, Mail } from 'lucide-react'

interface SidebarProps {
  publication: any
  auction: any
  contacts: any[]
}

export default function Sidebar({ publication, auction, contacts }: SidebarProps) {
  const formatDate = (dateString: string) => {
    return format(new Date(dateString), 'MMM dd, yyyy')
  }

  const formatTime = (timeString: string) => {
    return format(new Date(`2000-01-01T${timeString}`), 'h:mm a')
  }

  return (
    <div className="space-y-6">
      {/* Auction Timeline */}
      <div className="card">
        <h3 className="section-title">Termine (Appointments)</h3>
        <div className="space-y-0">
          <TimelineItem
            date={formatDate(auction.date)}
            time={formatTime(auction.time)}
            title="Versteigerung (Auction)"
            description={auction.location}
            isLocked={true}
          />
          <TimelineItem
            date={formatDate(auction.circulation.entry_deadline)}
            title="Besichtigung (Inspection)"
            description="Property inspection deadline"
            isLocked={true}
          />
          <TimelineItem
            date={formatDate(auction.registration.entry_deadline)}
            title="Bedingungen (Conditions)"
            description="Registration deadline"
            isLocked={true}
          />
          <TimelineItem
            date={formatDate(publication.publication_date)}
            title="Veröffentlichung (Publication)"
            description="Publication date"
            isLocked={true}
          />
        </div>
      </div>

      {/* Contact Information */}
      <div className="card">
        <h3 className="section-title">Kontakt (Contact)</h3>
        {contacts.map((contact) => (
          <div key={contact.id} className="space-y-4">
            <div className="flex items-start space-x-3">
              <Building className="w-5 h-5 text-gray-400 mt-0.5" />
              <div>
                <h4 className="font-medium text-gray-900">{contact.name}</h4>
                <p className="text-sm text-gray-600">{contact.address}</p>
                <p className="text-sm text-gray-600">
                  {contact.postal_code} {contact.city}
                </p>
              </div>
            </div>
            
            {contact.phone && (
              <div className="flex items-center space-x-3">
                <Phone className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-600">{contact.phone}</span>
              </div>
            )}
            
            {contact.email && (
              <div className="flex items-center space-x-3">
                <Mail className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-600">{contact.email}</span>
              </div>
            )}
            
            <div className="pt-4 border-t border-gray-200">
              <button className="btn-primary w-full">
                Contact Office
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3 className="section-title">Quick Actions</h3>
        <div className="space-y-3">
          <button className="btn-primary w-full">
            Register for Auction
          </button>
          <button className="btn-secondary w-full">
            Schedule Inspection
          </button>
          <button className="btn-secondary w-full">
            Download Documents
          </button>
          <button className="btn-secondary w-full">
            Save Property
          </button>
        </div>
      </div>

      {/* Important Dates */}
      <div className="card bg-red-50 border-red-200">
        <h3 className="text-lg font-semibold text-red-900 mb-4">Important Dates</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-red-900">Inspection Deadline</p>
              <p className="text-sm text-red-700">{formatDate(auction.circulation.entry_deadline)}</p>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-red-900">
                {Math.ceil((new Date(auction.circulation.entry_deadline).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))} days left
              </p>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-red-900">Registration Deadline</p>
              <p className="text-sm text-red-700">{formatDate(auction.registration.entry_deadline)}</p>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-red-900">
                {Math.ceil((new Date(auction.registration.entry_deadline).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))} days left
              </p>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-red-900">Auction Date</p>
              <p className="text-sm text-red-700">{formatDate(auction.date)} at {formatTime(auction.time)}</p>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-red-900">
                {Math.ceil((new Date(auction.date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))} days left
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
