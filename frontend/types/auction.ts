export interface AddressSwitzerland {
  street: string;
  house_number: string;
  swiss_zip_code: string;
  town: string;
}

export interface Residence {
  select_type: 'switzerland' | 'foreign';
}

export interface Debtor {
  id: string;
  debtor_type: 'person' | 'company';
  name: string;
  prename?: string;
  date_of_birth?: string;
  country_of_origin?: string | null;
  residence: Residence;
  address_switzerland?: AddressSwitzerland;
  address: string;
  city: string;
  postal_code: string;
  legal_form?: string | null;
}

export interface RegistrationOffice {
  id: string;
  display_name: string;
  street: string;
  street_number: string;
  swiss_zip_code: string;
  town: string;
  contains_post_office_box: boolean;
}

export interface Contact {
  id: string;
  name: string;
  address: string;
  postal_code: string;
  city: string;
  phone?: string;
  email?: string;
  contact_type: 'office' | 'person';
  office_id?: string;
  contains_post_office_box: boolean;
}

export interface AuctionObject {
  description: string;
}

export interface Circulation {
  entry_deadline: string;
  comment_entry_deadline?: string | null;
}

export interface Registration {
  entry_deadline: string;
  comment_entry_deadline?: string | null;
}

export interface Auction {
  id: string;
  date: string;
  time: string;
  location: string;
  circulation: Circulation;
  registration: Registration;
  auction_objects: AuctionObject[];
}

export interface Title {
  de: string;
  en: string;
  it: string;
  fr: string;
}

export interface Publication {
  id: string;
  publication_date: string;
  expiration_date: string;
  title: Title;
  language: string;
  canton: string;
  registration_office: RegistrationOffice;
  auctions: Auction[];
  debtors: Debtor[];
  contacts: Contact[];
}

export interface ApiResponse {
  success: boolean;
  url: string;
  publications_count: number;
  publications: Publication[];
}

export interface AuctionDetailPageProps {
  publication: Publication;
  auction: Auction;
  auctionObject: AuctionObject;
}

// Auction list types
export interface AuctionListItem {
  id: string;
  date: string;
  time?: string;
  location: string;
  circulation_entry_deadline?: string;
  circulation_comment_deadline?: string | null;
  registration_entry_deadline?: string;
  registration_comment_deadline?: string | null;
  created_at: string;
  updated_at: string;
  auction_objects: AuctionObject[];
}

export interface AuctionListResponse {
  items: AuctionListItem[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Filter types
export interface AuctionFilters {
  canton?: string;
  date_from?: string;
  date_to?: string;
  location?: string;
  property_type?: string;
  order_by?: 'date' | 'location' | 'created_at';
  order_direction?: 'asc' | 'desc';
  page?: number;
  size?: number;
}

// Property type enum
export type PropertyType = 
  | 'all'
  | 'residential'
  | 'commercial'
  | 'land'
  | 'mixed'
  | 'other';
