'use client'

import { Globe, HelpCircle, MapPin, BookOpen, Bell, MessageCircle } from 'lucide-react'

export default function Header() {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <h1 className="text-xl font-bold text-primary-600">Swiss Auction Property</h1>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex space-x-8">
            <a href="/auctions" className="text-gray-700 hover:text-primary-600 transition-colors">
              View Objects
            </a>
            <a href="#" className="text-gray-700 hover:text-primary-600 transition-colors flex items-center">
              <MapPin className="w-4 h-4 mr-1" />
              View Map
            </a>
            <a href="#" className="text-gray-700 hover:text-primary-600 transition-colors flex items-center">
              <BookOpen className="w-4 h-4 mr-1" />
              Magazine
            </a>
            <a href="#" className="text-gray-700 hover:text-primary-600 transition-colors flex items-center">
              <Bell className="w-4 h-4 mr-1" />
              Subscription
            </a>
            <a href="#" className="text-gray-700 hover:text-primary-600 transition-colors flex items-center">
              <MessageCircle className="w-4 h-4 mr-1" />
              Questions
            </a>
          </nav>

          {/* Right side actions */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-gray-700">
              <Globe className="w-4 h-4" />
              <span className="text-sm">English</span>
            </div>
            <button className="text-gray-700 hover:text-primary-600 transition-colors">
              <HelpCircle className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}
