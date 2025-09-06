"""SHAB XML parser for Swiss auction publications."""

import re
import uuid
from datetime import datetime, date, time as dt_time
from decimal import Decimal
from typing import List, Dict, Optional, Any
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup
from lxml import etree

from app.config import settings
from app.models import Publication, Auction, Debtor, AuctionObject, Contact


class SHABParser:
    """Parser for SHAB XML files containing auction information."""
    
    def __init__(self):
        self.namespaces = {
            'SB01': 'https://shab.ch/shab/SB01-export',
            'sb': 'https://shab.ch/shab/SB01-export',
            'ns': 'http://www.ech.ch/xmlns/eCH-0090/1',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }
    
    def fetch_xml_data(self, date_from: Optional[date] = None, date_to: Optional[date] = None) -> str:
        """Fetch XML data from SHAB API."""
        url = f"{settings.shab_base_url}/shab"
        params = {}
        
        if date_from:
            params['dateFrom'] = date_from.isoformat()
        if date_to:
            params['dateTo'] = date_to.isoformat()
        
        import httpx
        with httpx.Client() as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response.text
    
    def fetch_url_data(self, url: str) -> str:
        """Fetch data from a specific URL."""
        import httpx
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()
            return response.text
    
    def parse_xml(self, xml_content: str, html_url: str = None) -> List[Dict[str, Any]]:
        """Parse SHAB XML content and extract auction data."""
        try:
            # Parse XML with lxml for better namespace handling
            root = etree.fromstring(xml_content.encode('utf-8'))
            
            publications = []
            
            # Try different parsing approaches
            # Method 1: Look for SB01:publication or sb:publication elements
            for pub_elem in root.xpath('//SB01:publication | //sb:publication', namespaces=self.namespaces):
                publication_data = self._parse_publication(pub_elem)
                if publication_data:
                    # Parse contacts from HTML page if URL provided
                    if html_url:
                        contacts = self._parse_contacts_from_html_page(html_url)
                        publication_data['contacts'] = contacts
                    publications.append(publication_data)
            
            # Method 2: If no publication elements found, try to parse the root as a single publication
            if not publications:
                # Check if this is a single publication document
                if root.tag.endswith('publication') or 'publication' in root.tag.lower():
                    publication_data = self._parse_publication(root)
                    if publication_data:
                        # Parse contacts from HTML page if URL provided
                        if html_url:
                            contacts = self._parse_contacts_from_html_page(html_url)
                            publication_data['contacts'] = contacts
                        publications.append(publication_data)
            
            # Method 3: Try to parse as flat data structure (based on web search results)
            if not publications:
                publication_data = self._parse_flat_structure(xml_content)
                if publication_data:
                    # Parse contacts from HTML page if URL provided
                    if html_url:
                        contacts = self._parse_contacts_from_html_page(html_url)
                        publication_data['contacts'] = contacts
                    publications.append(publication_data)
            
            return publications
            
        except Exception as e:
            print(f"Error parsing XML: {e}")
            return []
    
    def _parse_publication(self, pub_elem: etree.Element) -> Optional[Dict[str, Any]]:
        """Parse a single publication element."""
        try:
            # Extract basic publication info - use unprefixed element names
            id_text = self._get_text(pub_elem.xpath('.//id/text()', namespaces=self.namespaces))
            pub_date_text = pub_elem.xpath('.//publicationDate/text()', namespaces=self.namespaces)
            expiration_date_text = pub_elem.xpath('.//expirationDate/text()', namespaces=self.namespaces)
            language_text = pub_elem.xpath('.//language/text()', namespaces=self.namespaces)
            canton_text = pub_elem.xpath('.//cantons/text()', namespaces=self.namespaces)
            
            # Parse registration office details
            registration_office = self._parse_registration_office(pub_elem)
            
            # Parse multilingual title
            title_data = self._parse_multilingual_title(pub_elem)
            
            publication_data = {
                'id': id_text or str(uuid.uuid4()),
                'publication_date': self._parse_date(pub_date_text),
                'expiration_date': self._parse_date(expiration_date_text),
                'title': title_data,
                'language': self._get_text(language_text, 'de'),
                'canton': self._get_text(canton_text),
                'registration_office': registration_office,
                'auctions': [],
                'debtors': [],
                'contacts': []
            }
            
            # Parse auction objects
            auction_objects = self._parse_auction_objects(pub_elem)
            
            # Parse auctions
            auctions = self._parse_auctions(pub_elem, auction_objects)
            publication_data['auctions'] = auctions
            
            # Parse debtors
            debtors = self._parse_debtors(pub_elem)
            publication_data['debtors'] = debtors
            
            return publication_data
            
        except Exception as e:
            print(f"Error parsing publication: {e}")
            return None
    
    def _parse_multilingual_title(self, pub_elem: etree.Element) -> Optional[Dict[str, str]]:
        """Parse multilingual title information."""
        try:
            title_elem = pub_elem.xpath('.//title', namespaces=self.namespaces)
            if not title_elem:
                return None
            
            title_elem = title_elem[0]
            
            # Extract all language versions
            title_data = {}
            for lang in ['de', 'en', 'it', 'fr']:
                lang_text = self._get_text(title_elem.xpath(f'.//{lang}/text()', namespaces=self.namespaces))
                if lang_text:
                    title_data[lang] = lang_text
            
            return title_data if title_data else None
            
        except Exception as e:
            print(f"Error parsing multilingual title: {e}")
            return None

    def _parse_registration_office(self, pub_elem: etree.Element) -> Optional[Dict[str, Any]]:
        """Parse registration office information with full details."""
        try:
            office_elem = pub_elem.xpath('.//registrationOffice', namespaces=self.namespaces)
            if not office_elem:
                return None
            
            office_elem = office_elem[0]
            
            office_data = {
                'id': self._get_text(office_elem.xpath('.//id/text()', namespaces=self.namespaces)),
                'display_name': self._get_text(office_elem.xpath('.//displayName/text()', namespaces=self.namespaces)),
                'street': self._get_text(office_elem.xpath('.//street/text()', namespaces=self.namespaces)),
                'street_number': self._get_text(office_elem.xpath('.//streetNumber/text()', namespaces=self.namespaces)),
                'swiss_zip_code': self._get_text(office_elem.xpath('.//swissZipCode/text()', namespaces=self.namespaces)),
                'town': self._get_text(office_elem.xpath('.//town/text()', namespaces=self.namespaces)),
                'contains_post_office_box': self._get_text(office_elem.xpath('.//containsPostOfficeBox/text()', namespaces=self.namespaces)) == 'true'
            }
            
            # Add post office box details if available
            post_office_box = office_elem.xpath('.//postOfficeBox', namespaces=self.namespaces)
            if post_office_box:
                post_office_box = post_office_box[0]
                office_data['post_office_box'] = {
                    'number': self._get_text(post_office_box.xpath('.//number/text()', namespaces=self.namespaces)),
                    'zip_code': self._get_text(post_office_box.xpath('.//zipCode/text()', namespaces=self.namespaces)),
                    'town': self._get_text(post_office_box.xpath('.//town/text()', namespaces=self.namespaces))
                }
            
            return office_data
            
        except Exception as e:
            print(f"Error parsing registration office: {e}")
            return None
    
    def _parse_auction_objects(self, pub_elem: etree.Element) -> List[Dict[str, Any]]:
        """Parse auction objects from publication."""
        objects = []
        
        # Parse auctionObjects as simple string elements
        for obj_elem in pub_elem.xpath('.//auctionObjects', namespaces=self.namespaces):
            try:
                # Extract text content from the element
                text_content = self._get_text(obj_elem.xpath('.//text()', namespaces=self.namespaces))
                if text_content:
                    obj_data = {
                        'description': text_content,
                    }
                    objects.append(obj_data)
                    
            except Exception as e:
                print(f"Error parsing auction object: {e}")
                continue
        
        return objects
    
    def _parse_html_content(self, html_content: str) -> Dict[str, Any]:
        """Parse HTML content within auction objects."""
        soup = BeautifulSoup(html_content, 'html.parser')
        result = {}
        
        # Extract parcel number (French and German patterns)
        parcel_patterns = [
            r'Feuillet\s*no\s*(\d+)',  # French: Feuillet no 812
            r'Grundstück\s*Nr\.?\s*(\d+)',  # German: Grundstück Nr. 123
            r'Parcelle\s*no\s*(\d+)',  # French: Parcelle no 123
        ]
        
        for pattern in parcel_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                result['parcel_number'] = match.group(1)
                break
        
        # Extract estimated value (French and German patterns)
        value_patterns = [
            r'Valeur\s*vénale\s*[:\s]*CHF\s*([\d\s\']+)',  # French: Valeur vénale : CHF 650'000.00
            r'Valeur\s*officielle\s*[:\s]*CHF\s*([\d\s\']+)',  # French: Valeur officielle : CHF 489'000.00
            r'Schätzwert[:\s]*([\d\s\']+)\s*CHF',  # German: Schätzwert: 500'000 CHF
            r'CHF\s*([\d\s\']+)',  # Generic: CHF 650'000.00
        ]
        
        for pattern in value_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace("'", "").replace(" ", "").replace(".", "")
                try:
                    result['estimated_value'] = Decimal(value_str)
                    break
                except:
                    continue
        
        # Extract surface area (French and German patterns)
        surface_patterns = [
            r'(\d+(?:\.\d+)?)\s*m²',  # Generic: 182 m²
            r'(\d+(?:\.\d+)?)\s*m2',  # Alternative: 182 m2
            r'(\d+(?:\.\d+)?)\s*m<sup>2</sup>',  # HTML: 182 m<sup>2</sup>
            r'Surface\s*totale\s*(\d+(?:\.\d+)?)\s*m²',  # French: Surface totale 451 m²
            r'Surface\s*totale\s*(\d+(?:\.\d+)?)\s*m<sup>2</sup>',  # French HTML: Surface totale 451 m<sup>2</sup>
        ]
        
        for pattern in surface_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                try:
                    result['surface_area'] = Decimal(match.group(1))
                    break
                except:
                    continue
        
        # Extract address information (French and German patterns)
        address_patterns = [
            r'Rue\s+([^,]+),\s*(\d+)\s+([^,]+)',  # French: Rue du Midi 57, 2610 Saint-Imier
            r'Adresse[:\s]*([^<>\n]+)',  # German: Adresse: ...
            r'Lage[:\s]*([^<>\n]+)',  # German: Lage: ...
            r'Standort[:\s]*([^<>\n]+)',  # German: Standort: ...
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                if 'Rue' in pattern:
                    # Extract full address for French pattern
                    full_match = re.search(r'Rue\s+([^,]+),\s*(\d+)\s+([^,]+)', html_content, re.IGNORECASE)
                    if full_match:
                        result['address'] = f"Rue {full_match.group(1)}, {full_match.group(2)} {full_match.group(3)}"
                        result['municipality'] = full_match.group(3)
                else:
                    result['address'] = match.group(1).strip()
                break
        
        # Extract municipality (French and German patterns)
        municipality_patterns = [
            r'(\d{4})\s+([A-Za-z\s]+)',  # French: 2610 Saint-Imier
            r'Gemeinde[:\s]*([^<>\n]+)',  # German: Gemeinde: ...
        ]
        
        for pattern in municipality_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                if 'Gemeinde' in pattern:
                    result['municipality'] = match.group(1).strip()
                else:
                    # Extract municipality from postal code pattern
                    postal_match = re.search(r'(\d{4})\s+([A-Za-z\s]+)', html_content, re.IGNORECASE)
                    if postal_match:
                        result['municipality'] = postal_match.group(2).strip()
                break
        
        # Extract property type (French and German patterns)
        type_patterns = [
            r'Bâtiment,\s*habitation',  # French: Bâtiment, habitation
            r'Einzelhaus',  # German: Einzelhaus
            r'Eigentumswohnung',  # German: Eigentumswohnung
            r'Gewerbeimmobilie',  # German: Gewerbeimmobilie
            r'Landwirtschaftsbetrieb',  # German: Landwirtschaftsbetrieb
            r'Grundstück',  # German: Grundstück
            r'Jardin',  # French: Jardin
        ]
        
        for prop_type in type_patterns:
            if re.search(prop_type, html_content, re.IGNORECASE):
                if 'Bâtiment' in prop_type:
                    result['property_type'] = 'Bâtiment habitation'
                elif 'Jardin' in prop_type:
                    result['property_type'] = 'Jardin'
                else:
                    result['property_type'] = prop_type
                break
        
        # Use the full HTML content as description
        result['description'] = html_content.strip()
        
        return result
    
    def _parse_auctions(self, pub_elem: etree.Element, auction_objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse auction information."""
        auctions = []
        
        # Extract auction date and time
        auction_date = self._parse_date(
            pub_elem.xpath('.//auction/date/text()', namespaces=self.namespaces)
        )
        auction_time = self._parse_time(
            pub_elem.xpath('.//auction/time/text()', namespaces=self.namespaces)
        )
        location = self._get_text(pub_elem.xpath('.//auction/location/text()', namespaces=self.namespaces))
        
        if auction_date:
            # Parse circulation and registration information
            circulation = self._parse_circulation(pub_elem)
            registration = self._parse_registration(pub_elem)
            
            auction_data = {
                'id': str(uuid.uuid4()),
                'date': auction_date,
                'time': auction_time,
                'location': location or 'Nicht angegeben',
                'circulation': circulation,
                'registration': registration,
                'auction_objects': auction_objects
            }
            auctions.append(auction_data)
        
        return auctions
    
    def _parse_circulation(self, pub_elem: etree.Element) -> Optional[Dict[str, Any]]:
        """Parse circulation information."""
        try:
            circulation_elem = pub_elem.xpath('.//circulation', namespaces=self.namespaces)
            if not circulation_elem:
                return None
            
            circulation_elem = circulation_elem[0]
            
            return {
                'entry_deadline': self._parse_date(circulation_elem.xpath('.//entryDeadline/text()', namespaces=self.namespaces)),
                'comment_entry_deadline': self._get_text(circulation_elem.xpath('.//commentEntryDeadline/text()', namespaces=self.namespaces))
            }
            
        except Exception as e:
            print(f"Error parsing circulation: {e}")
            return None
    
    def _parse_registration(self, pub_elem: etree.Element) -> Optional[Dict[str, Any]]:
        """Parse registration information."""
        try:
            registration_elem = pub_elem.xpath('.//registration', namespaces=self.namespaces)
            if not registration_elem:
                return None
            
            registration_elem = registration_elem[0]
            
            return {
                'entry_deadline': self._parse_date(registration_elem.xpath('.//entryDeadline/text()', namespaces=self.namespaces)),
                'comment_entry_deadline': self._get_text(registration_elem.xpath('.//commentEntryDeadline/text()', namespaces=self.namespaces))
            }
            
        except Exception as e:
            print(f"Error parsing registration: {e}")
            return None
    
    def _parse_debtors(self, pub_elem: etree.Element) -> List[Dict[str, Any]]:
        """Parse debtor information with complete company and person details."""
        debtors = []
        
        for debtor_elem in pub_elem.xpath('.//debtor', namespaces=self.namespaces):
            try:
                # Get the first selectType (debtor type), not the residence selectType
                debtor_type_elements = debtor_elem.xpath('.//selectType', namespaces=self.namespaces)
                debtor_type = self._get_text(debtor_type_elements[0].xpath('.//text()', namespaces=self.namespaces)) if debtor_type_elements else None
                
                if debtor_type == 'company':
                    debtor_data = self._parse_company_debtor(debtor_elem)
                elif debtor_type == 'person':
                    debtor_data = self._parse_person_debtor(debtor_elem)
                else:
                    # Fallback to basic parsing
                    debtor_data = self._parse_basic_debtor(debtor_elem)
                
                
                if debtor_data and debtor_data.get('name'):  # Only add if we have a name
                    debtors.append(debtor_data)
                    
            except Exception as e:
                print(f"Error parsing debtor: {e}")
                continue
                
        return debtors
    
    def _parse_company_debtor(self, debtor_elem: etree.Element) -> Optional[Dict[str, Any]]:
        """Parse company debtor with complete details."""
        try:
            company_elem = debtor_elem.xpath('.//company', namespaces=self.namespaces)
            if not company_elem:
                return None
                
            company_elem = company_elem[0]
            
            # Parse address if present
            address_data = None
            address_elem = company_elem.xpath('.//address', namespaces=self.namespaces)
            if address_elem:
                address_elem = address_elem[0]
                address_data = {
                    'address_line1': self._get_text(address_elem.xpath('.//addressLine1/text()', namespaces=self.namespaces)),
                    'street': self._get_text(address_elem.xpath('.//street/text()', namespaces=self.namespaces)),
                    'house_number': self._get_text(address_elem.xpath('.//houseNumber/text()', namespaces=self.namespaces)),
                    'swiss_zip_code': self._get_text(address_elem.xpath('.//swissZipCode/text()', namespaces=self.namespaces)),
                    'town': self._get_text(address_elem.xpath('.//town/text()', namespaces=self.namespaces))
                }
            
            return {
                'id': str(uuid.uuid4()),
                'debtor_type': 'company',
                'name': self._get_text(company_elem.xpath('.//name/text()', namespaces=self.namespaces)),
                'uid': self._get_text(company_elem.xpath('.//uid/text()', namespaces=self.namespaces)),
                'uid_organisation_id': self._get_text(company_elem.xpath('.//uidOrganisationId/text()', namespaces=self.namespaces)),
                'uid_organisation_id_categorie': self._get_text(company_elem.xpath('.//uidOrganisationIdCategorie/text()', namespaces=self.namespaces)),
                'legal_form': self._get_text(company_elem.xpath('.//legalForm/text()', namespaces=self.namespaces)),
                'canton': self._get_text(company_elem.xpath('.//canton/text()', namespaces=self.namespaces)),
                'address': address_data,
                # Legacy fields for compatibility
                'prename': None,
                'date_of_birth': None,
                'city': address_data['town'] if address_data else None,
                'postal_code': address_data['swiss_zip_code'] if address_data else None
            }
        except Exception as e:
            print(f"Error parsing company debtor: {e}")
            return None
    
    def _parse_person_debtor(self, debtor_elem: etree.Element) -> Optional[Dict[str, Any]]:
        """Parse person debtor with complete details."""
        try:
            person_elem = debtor_elem.xpath('.//person', namespaces=self.namespaces)
            if not person_elem:
                return None
                
            person_elem = person_elem[0]
            
            # Parse country of origin
            country_data = None
            country_elem = person_elem.xpath('.//countryOfOrigin', namespaces=self.namespaces)
            if country_elem:
                country_elem = country_elem[0]
                country_data = {
                    'name': {
                        'de': self._get_text(country_elem.xpath('.//name/de/text()', namespaces=self.namespaces)),
                        'fr': self._get_text(country_elem.xpath('.//name/fr/text()', namespaces=self.namespaces)),
                        'it': self._get_text(country_elem.xpath('.//name/it/text()', namespaces=self.namespaces)),
                        'en': self._get_text(country_elem.xpath('.//name/en/text()', namespaces=self.namespaces))
                    },
                    'iso_code': self._get_text(country_elem.xpath('.//isoCode/text()', namespaces=self.namespaces))
                }
            
            # Parse residence
            residence_data = None
            residence_elem = person_elem.xpath('.//residence', namespaces=self.namespaces)
            if residence_elem:
                residence_elem = residence_elem[0]
                residence_data = {
                    'select_type': self._get_text(residence_elem.xpath('.//selectType/text()', namespaces=self.namespaces))
                }
            
            # Parse Swiss address
            address_data = None
            address_elem = person_elem.xpath('.//addressSwitzerland', namespaces=self.namespaces)
            if address_elem:
                address_elem = address_elem[0]
                address_data = {
                    'street': self._get_text(address_elem.xpath('.//street/text()', namespaces=self.namespaces)),
                    'house_number': self._get_text(address_elem.xpath('.//houseNumber/text()', namespaces=self.namespaces)),
                    'swiss_zip_code': self._get_text(address_elem.xpath('.//swissZipCode/text()', namespaces=self.namespaces)),
                    'town': self._get_text(address_elem.xpath('.//town/text()', namespaces=self.namespaces))
                }
            
            return {
                'id': str(uuid.uuid4()),
                'debtor_type': 'person',
                'name': self._get_text(person_elem.xpath('.//name/text()', namespaces=self.namespaces)),
                'prename': self._get_text(person_elem.xpath('.//prename/text()', namespaces=self.namespaces)),
                'date_of_birth': self._parse_date(person_elem.xpath('.//dateOfBirth/text()', namespaces=self.namespaces)),
                'country_of_origin': country_data,
                'residence': residence_data,
                'address_switzerland': address_data,
                # Legacy fields for compatibility
                'address': f"{address_data['street']} {address_data['house_number']}" if address_data else None,
                'city': address_data['town'] if address_data else None,
                'postal_code': address_data['swiss_zip_code'] if address_data else None,
                'legal_form': None
            }
        except Exception as e:
            print(f"Error parsing person debtor: {e}")
            return None
    
    def _parse_basic_debtor(self, debtor_elem: etree.Element) -> Optional[Dict[str, Any]]:
        """Parse basic debtor information (fallback)."""
        try:
            return {
                'id': str(uuid.uuid4()),
                'name': self._get_text(debtor_elem.xpath('.//name/text()', namespaces=self.namespaces)),
                'prename': self._get_text(debtor_elem.xpath('.//prename/text()', namespaces=self.namespaces)),
                'date_of_birth': self._parse_date(
                    debtor_elem.xpath('.//dateOfBirth/text()', namespaces=self.namespaces)
                ),
                'address': self._get_text(debtor_elem.xpath('.//address/text()', namespaces=self.namespaces)),
                'city': self._get_text(debtor_elem.xpath('.//city/text()', namespaces=self.namespaces)),
                'postal_code': self._get_text(debtor_elem.xpath('.//postalCode/text()', namespaces=self.namespaces)),
                'legal_form': self._get_text(debtor_elem.xpath('.//legalForm/text()', namespaces=self.namespaces)),
                'debtor_type': self._get_text(debtor_elem.xpath('.//selectType/text()', namespaces=self.namespaces))
            }
        except Exception as e:
            print(f"Error parsing basic debtor: {e}")
            return None
    
    def _parse_contacts(self, pub_elem: etree.Element) -> List[Dict[str, Any]]:
        """Parse contact information."""
        contacts = []
        
        for contact_elem in pub_elem.xpath('.//sb:contact', namespaces=self.namespaces):
            try:
                contact_data = {
                    'id': str(uuid.uuid4()),
                    'name': self._get_text(contact_elem.xpath('.//sb:name/text()', namespaces=self.namespaces)),
                    'title': self._get_text(contact_elem.xpath('.//sb:title/text()', namespaces=self.namespaces)),
                    'phone': self._get_text(contact_elem.xpath('.//sb:phone/text()', namespaces=self.namespaces)),
                    'email': self._get_text(contact_elem.xpath('.//sb:email/text()', namespaces=self.namespaces)),
                    'fax': self._get_text(contact_elem.xpath('.//sb:fax/text()', namespaces=self.namespaces)),
                    'organization': self._get_text(contact_elem.xpath('.//sb:organization/text()', namespaces=self.namespaces)),
                    'department': self._get_text(contact_elem.xpath('.//sb:department/text()', namespaces=self.namespaces)),
                    'address': self._get_text(contact_elem.xpath('.//sb:address/text()', namespaces=self.namespaces)),
                    'city': self._get_text(contact_elem.xpath('.//sb:city/text()', namespaces=self.namespaces)),
                    'postal_code': self._get_text(contact_elem.xpath('.//sb:postalCode/text()', namespaces=self.namespaces)),
                    'contact_type': self._get_text(contact_elem.xpath('.//sb:contactType/text()', namespaces=self.namespaces))
                }
                
                if contact_data['name']:  # Only add if we have a name
                    contacts.append(contact_data)
                    
            except Exception as e:
                print(f"Error parsing contact: {e}")
                continue
        
        return contacts
    
    def _parse_contacts_from_html_page(self, html_url: str) -> List[Dict[str, Any]]:
        """Parse contact information from the JSON API endpoint."""
        contacts = []
        
        try:
            # Convert XML URL to JSON API URL
            # Example: https://www.shab.ch/api/v1/publications/xxx/xml -> https://www.shab.ch/api/v1/publications/xxx
            if '/xml' in html_url:
                json_url = html_url.replace('/xml', '')
            else:
                # Extract the publication ID from the URL
                import re
                # Handle both formats: /publications/xxx and /publications/detail/xxx
                match = re.search(r'/publications/(?:detail/)?([^/]+)', html_url)
                if match:
                    pub_id = match.group(1)
                    json_url = f"https://www.shab.ch/api/v1/publications/{pub_id}"
                else:
                    return contacts
            
            # Fetch JSON content
            json_content = self.fetch_url_data(json_url)
            
            # Parse contact information from JSON
            contacts = self._extract_contacts_from_json(json_content)
            
        except Exception as e:
            print(f"Error parsing contacts from JSON API: {e}")
        
        return contacts
    
    def _extract_contacts_from_json(self, json_content: str) -> List[Dict[str, Any]]:
        """Extract contact information from JSON content."""
        contacts = []
        
        try:
            import json
            
            data = json.loads(json_content)
            
            # Extract registration office information as contact
            if 'meta' in data and 'registrationOffice' in data['meta']:
                office = data['meta']['registrationOffice']
                
                contact_data = {
                    'id': str(uuid.uuid4()),
                    'name': office.get('displayName', ''),
                    'address': f"{office.get('street', '')} {office.get('streetNumber', '')}".strip(),
                    'postal_code': office.get('swissZipCode', ''),
                    'city': office.get('town', ''),
                    'phone': None,
                    'email': None,
                    'contact_type': 'office',
                    'office_id': office.get('id', ''),
                    'contains_post_office_box': office.get('containsPostOfficeBox', False)
                }
                
                # Add post office box information if available
                if office.get('postOfficeBox'):
                    pob = office['postOfficeBox']
                    contact_data['post_office_box'] = {
                        'number': pob.get('number', ''),
                        'zip_code': pob.get('zipCode', ''),
                        'town': pob.get('town', '')
                    }
                
                contacts.append(contact_data)
            
        except Exception as e:
            print(f"Error extracting contacts from JSON: {e}")
        
        return contacts
    
    def _extract_contacts_from_html(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract contact information from HTML content."""
        contacts = []
        
        try:
            import re
            
            # Pattern to match contact information
            # Example: "Point of contact\nOffice des poursuites des districts de Sion, Hérens et Conthey\nRue de la Piscine 10\n1950 Sion"
            contact_pattern = r'Point of contact\s*\n([^\n]+)\s*\n([^\n]+)\s*\n(\d{4}\s+[^\n]+)'
            
            matches = re.findall(contact_pattern, html_content, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                contact_data = {
                    'id': str(uuid.uuid4()),
                    'name': match[0].strip(),  # Office name
                    'address': match[1].strip(),  # Street address
                    'postal_code': match[2].strip().split()[0],  # Postal code
                    'city': ' '.join(match[2].strip().split()[1:]),  # City
                    'phone': None,
                    'email': None,
                    'contact_type': 'office'
                }
                contacts.append(contact_data)
            
            # Alternative pattern for different formats
            if not contacts:
                # Try a more flexible pattern
                flexible_pattern = r'(?:Point of contact|Contact|Kontakt)\s*:?\s*\n([^\n]+(?:\n[^\n]+)*?)(?=\n\n|\n[A-Z]|\Z)'
                flexible_matches = re.findall(flexible_pattern, html_content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                
                for match in flexible_matches:
                    lines = [line.strip() for line in match.strip().split('\n') if line.strip()]
                    if len(lines) >= 3:
                        contact_data = {
                            'id': str(uuid.uuid4()),
                            'name': lines[0],
                            'address': lines[1] if len(lines) > 1 else None,
                            'postal_code': lines[2].split()[0] if len(lines) > 2 and lines[2].split() else None,
                            'city': ' '.join(lines[2].split()[1:]) if len(lines) > 2 and len(lines[2].split()) > 1 else lines[2] if len(lines) > 2 else None,
                            'phone': None,
                            'email': None,
                            'contact_type': 'office'
                        }
                        contacts.append(contact_data)
            
        except Exception as e:
            print(f"Error extracting contacts from HTML: {e}")
        
        return contacts
    
    def _get_text(self, text_list: List[str], default: str = None) -> Optional[str]:
        """Get first non-empty text from list."""
        for text in text_list:
            if text and text.strip():
                return text.strip()
        return default
    
    def _parse_date(self, date_list: List[str]) -> Optional[date]:
        """Parse date from string list."""
        date_str = self._get_text(date_list)
        if not date_str:
            return None
        
        try:
            # Try different date formats
            formats = ['%Y-%m-%d', '%d.%m.%Y', '%Y%m%d']
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
        except:
            pass
        
        return None
    
    def _parse_time(self, time_list: List[str]) -> Optional[dt_time]:
        """Parse time from string list."""
        time_str = self._get_text(time_list)
        if not time_str:
            return None
        
        try:
            # Try different time formats
            formats = ['%H:%M', '%H:%M:%S', '%H.%M']
            for fmt in formats:
                try:
                    return datetime.strptime(time_str, fmt).time()
                except ValueError:
                    continue
        except:
            pass
        
        return None
    
    def _parse_flat_structure(self, xml_content: str) -> Optional[Dict[str, Any]]:
        """Parse SHAB data in flat/tabular format (based on actual SHAB structure)."""
        try:
            # Based on the web search results, the data appears to be in a flat format
            # Let's try to extract information using regex patterns
            
            # Extract basic information using regex
            import re
            
            # Extract ID
            id_match = re.search(r'([a-f0-9-]{36})', xml_content)
            publication_id = id_match.group(1) if id_match else str(uuid.uuid4())
            
            # Extract title (look for French title)
            title_match = re.search(r'<fr>(.*?)</fr>', xml_content, re.DOTALL)
            title = title_match.group(1).strip() if title_match else "Unknown Title"
            
            # Extract date
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', xml_content)
            publication_date = self._parse_date([date_match.group(1)]) if date_match else None
            
            # Extract canton
            canton_match = re.search(r'\b([A-Z]{2})\b', xml_content)
            canton = canton_match.group(1) if canton_match else None
            
            # Extract language
            language_match = re.search(r'\b(fr|de|it|en)\b', xml_content)
            language = language_match.group(1) if language_match else "fr"
            
            # Extract registration office
            office_match = re.search(r'Office des poursuites[^<]*', xml_content)
            registration_office = office_match.group(0).strip() if office_match else None
            
            # Extract debtor information
            debtor_match = re.search(r'([A-Za-z\s]+SA)\s+([A-Z0-9-]+)', xml_content)
            debtor_name = debtor_match.group(1).strip() if debtor_match else None
            debtor_uid = debtor_match.group(2) if debtor_match else None
            
            # Extract auction date and time
            auction_date_match = re.search(r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})', xml_content)
            auction_date = self._parse_date([auction_date_match.group(1)]) if auction_date_match else None
            auction_time = self._parse_time([auction_date_match.group(2)]) if auction_date_match else None
            
            # Extract location
            location_match = re.search(r'Salle de[^<]*', xml_content)
            location = location_match.group(0).strip() if location_match else None
            
            # Extract HTML content for auction objects
            html_match = re.search(r'<p><b>(.*?)</b></p>', xml_content, re.DOTALL)
            html_content = html_match.group(0) if html_match else ""
            
            # Parse auction objects from HTML
            auction_objects = []
            if html_content:
                parsed_content = self._parse_html_content(html_content)
                auction_objects.append({
                    'id': str(uuid.uuid4()),
                    'parcel_number': parsed_content.get('parcel_number'),
                    'property_number': parsed_content.get('property_number'),
                    'surface_area': parsed_content.get('surface_area'),
                    'estimated_value': parsed_content.get('estimated_value'),
                    'description': parsed_content.get('description'),
                    'property_type': parsed_content.get('property_type'),
                    'address': parsed_content.get('address'),
                    'municipality': parsed_content.get('municipality'),
                    'canton': parsed_content.get('canton'),
                    'remarks': parsed_content.get('remarks')
                })
            
            # Create publication data
            publication_data = {
                'id': publication_id,
                'publication_date': publication_date,
                'title': title,
                'language': language,
                'canton': canton,
                'registration_office': registration_office,
                'content': xml_content[:500] + "..." if len(xml_content) > 500 else xml_content,
                'auctions': [],
                'debtors': [],
                'contacts': []
            }
            
            # Add auction if we have auction data
            if auction_date:
                auction_data = {
                    'id': str(uuid.uuid4()),
                    'date': auction_date,
                    'time': auction_time,
                    'location': location or 'Nicht angegeben',
                    'court': registration_office,
                    'auction_type': 'Zwangsversteigerung',
                    'auction_objects': auction_objects
                }
                publication_data['auctions'].append(auction_data)
            
            # Add debtor if we have debtor data
            if debtor_name:
                debtor_data = {
                    'id': str(uuid.uuid4()),
                    'name': debtor_name,
                    'prename': None,
                    'date_of_birth': None,
                    'address': None,
                    'city': None,
                    'postal_code': None,
                    'legal_form': 'company' if 'SA' in debtor_name else None
                }
                publication_data['debtors'].append(debtor_data)
            
            # Extract contact information
            contact_match = re.search(r'([A-Za-z\s]+SA)\s+([^<]+)', xml_content)
            if contact_match and contact_match.group(1) != debtor_name:
                contact_data = {
                    'id': str(uuid.uuid4()),
                    'name': contact_match.group(1).strip(),
                    'title': None,
                    'phone': None,
                    'email': None,
                    'fax': None,
                    'organization': None,
                    'department': None,
                    'address': contact_match.group(2).strip(),
                    'city': None,
                    'postal_code': None,
                    'contact_type': None
                }
                publication_data['contacts'].append(contact_data)
            
            return publication_data
            
        except Exception as e:
            print(f"Error parsing flat structure: {e}")
            return None
