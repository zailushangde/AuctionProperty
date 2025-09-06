'use client'

import { Lock, Download, MapPin, Calendar, Clock, User, Building } from 'lucide-react'

interface InfoCardProps {
  title: string
  children: React.ReactNode
  isLocked?: boolean
  unlockText?: string
}

export function InfoCard({ title, children, isLocked = false, unlockText = "Unlock" }: InfoCardProps) {
  return (
    <div className="card relative">
      <h3 className="section-title">{title}</h3>
      <div className={`${isLocked ? 'blur-sm pointer-events-none' : ''}`}>
        {children}
      </div>
      {isLocked && (
        <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-80 rounded-lg">
          <button className="btn-primary flex items-center space-x-2">
            <Lock className="w-4 h-4" />
            <span>{unlockText}</span>
          </button>
        </div>
      )}
    </div>
  )
}

interface InfoRowProps {
  label: string
  value: string | React.ReactNode
  icon?: React.ReactNode
}

export function InfoRow({ label, value, icon }: InfoRowProps) {
  return (
    <div className="flex items-start space-x-3 py-2">
      {icon && <div className="text-gray-400 mt-0.5">{icon}</div>}
      <div className="flex-1 min-w-0">
        <p className="info-label">{label}</p>
        <div className="info-value">{value}</div>
      </div>
    </div>
  )
}

interface DocumentItemProps {
  name: string
  type: string
  isLocked?: boolean
}

export function DocumentItem({ name, type, isLocked = true }: DocumentItemProps) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0">
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 bg-gray-100 rounded flex items-center justify-center">
          <Download className="w-4 h-4 text-gray-600" />
        </div>
        <div>
          <p className="font-medium text-gray-900">{name}</p>
          <p className="text-sm text-gray-500">{type}</p>
        </div>
      </div>
      {isLocked && (
        <button className="btn-secondary text-sm flex items-center space-x-1">
          <Lock className="w-3 h-3" />
          <span>Unlock</span>
        </button>
      )}
    </div>
  )
}

interface TimelineItemProps {
  date: string
  time?: string
  title: string
  description?: string
  isLocked?: boolean
}

export function TimelineItem({ date, time, title, description, isLocked = false }: TimelineItemProps) {
  return (
    <div className="flex items-start space-x-4 py-3">
      <div className="flex-shrink-0">
        <div className="w-3 h-3 bg-primary-500 rounded-full mt-2"></div>
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium text-gray-900">{title}</p>
            <p className="text-sm text-gray-500">{date} {time && `at ${time}`}</p>
            {description && <p className="text-sm text-gray-600 mt-1">{description}</p>}
          </div>
          {isLocked && (
            <button className="btn-secondary text-sm flex items-center space-x-1">
              <Lock className="w-3 h-3" />
              <span>Unlock</span>
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
