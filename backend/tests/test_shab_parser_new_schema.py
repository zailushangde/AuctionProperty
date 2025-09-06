"""Tests for SHAB parser with new schema integration."""

import pytest
import uuid
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import patch, MagicMock

from app.parsers.shab_parser import SHABParser


class TestSHABParserNewSchema:
    """Test SHAB parser with new schema format."""
    
    def test_parse_multilingual_title(self):
        """Test parsing multilingual titles."""
        parser = SHABParser()
        
        # Mock XML with multilingual title
        xml_content = """
        <publication>
            <title>
                <de>Betreibungsamtliche Grundstücksteigerung</de>
                <fr>Vente aux enchères d'immeubles</fr>
                <it>Incanto immobiliare</it>
                <en>Property auction</en>
            </title>
        </publication>
        """
        
        # Test the parsing method
        from lxml import etree
        root = etree.fromstring(xml_content)
        
        title = parser._parse_multilingual_title(root)
        
        assert title["de"] == "Betreibungsamtliche Grundstücksteigerung"
        assert title["fr"] == "Vente aux enchères d'immeubles"
        assert title["it"] == "Incanto immobiliare"
        assert title["en"] == "Property auction"
    
    def test_parse_expiration_date(self):
        """Test parsing expiration date."""
        parser = SHABParser()
        
        xml_content = """
        <publication>
            <expirationDate>2026-04-30</expirationDate>
        </publication>
        """
        
        from lxml import etree
        root = etree.fromstring(xml_content)
        
        expiration_date = parser._parse_date(root.xpath('.//expirationDate/text()'))
        
        assert expiration_date == date(2026, 4, 30)
    
    def test_parse_person_debtor(self):
        """Test parsing person debtor with new schema."""
        parser = SHABParser()
        
        xml_content = """
        <publication>
            <debtor>
                <person>
                    <prename>Jan Henrik</prename>
                    <name>JEBSEN</name>
                    <countryOfOrigin>
                        <name>
                            <de>Norwegen</de>
                            <fr>Norvège</fr>
                            <it>Norvegia</it>
                            <en>Norway</en>
                        </name>
                        <isoCode>NO</isoCode>
                    </countryOfOrigin>
                    <dateOfBirth>1961-02-09</dateOfBirth>
                    <residence>
                        <selectType>switzerland</selectType>
                    </residence>
                    <addressSwitzerland>
                        <street>Chemin des Chanoz</street>
                        <houseNumber>5</houseNumber>
                        <swissZipCode>1299</swissZipCode>
                        <town>Crans VD</town>
                    </addressSwitzerland>
                </person>
            </debtor>
        </publication>
        """
        
        from lxml import etree
        root = etree.fromstring(xml_content)
        
        debtor = parser._parse_person_debtor(root.xpath('.//debtor')[0])
        
        assert debtor["debtor_type"] == "person"
        assert debtor["name"] == "JEBSEN"
        assert debtor["prename"] == "Jan Henrik"
        assert debtor["date_of_birth"] == date(1961, 2, 9)
        assert debtor["country_of_origin"]["isoCode"] == "NO"
        assert debtor["country_of_origin"]["name"]["en"] == "Norway"
        assert debtor["residence_type"] == "switzerland"
        assert debtor["address"] == "Chemin des Chanoz 5"
        assert debtor["city"] == "Crans VD"
        assert debtor["postal_code"] == "1299"
    
    def test_parse_company_debtor(self):
        """Test parsing company debtor with new schema."""
        parser = SHABParser()
        
        xml_content = """
        <publication>
            <debtor>
                <company>
                    <name>Foncière Immobilière Nord Bernoise SA</name>
                    <uid>CHE-175.482.480</uid>
                    <uidOrganisationId>175482480</uidOrganisationId>
                    <uidOrganisationIdCategorie>CHE</uidOrganisationIdCategorie>
                    <legalForm>0106</legalForm>
                    <address>
                        <addressLine1>Berney Associés Fribourg SA</addressLine1>
                        <street>Boulevard de Pérolles</street>
                        <houseNumber>37</houseNumber>
                        <swissZipCode>1700</swissZipCode>
                        <town>Fribourg</town>
                    </address>
                    <canton>FR</canton>
                </company>
            </debtor>
        </publication>
        """
        
        from lxml import etree
        root = etree.fromstring(xml_content)
        
        debtor = parser._parse_company_debtor(root.xpath('.//debtor')[0])
        
        assert debtor["debtor_type"] == "company"
        assert debtor["name"] == "Foncière Immobilière Nord Bernoise SA"
        assert debtor["legal_form"] == "0106"
        assert debtor["address"] == "Boulevard de Pérolles 37"
        assert debtor["city"] == "Fribourg"
        assert debtor["postal_code"] == "1700"
    
    def test_parse_circulation_and_registration(self):
        """Test parsing circulation and registration deadlines."""
        parser = SHABParser()
        
        xml_content = """
        <publication>
            <auctions>
                <auction>
                    <circulation>
                        <entryDeadline>2025-05-20</entryDeadline>
                        <commentEntryDeadline>(Valeur dates des enchères)</commentEntryDeadline>
                    </circulation>
                    <registration>
                        <entryDeadline>2025-06-16</entryDeadline>
                        <commentEntryDeadline>jusqu'au 26.06.2025. L'état des charges, les conditions de vente, le rapport d'expertise pourront être consultés du 16.06.2025 au 26.06.2025.</commentEntryDeadline>
                    </registration>
                </auction>
            </auctions>
        </publication>
        """
        
        from lxml import etree
        root = etree.fromstring(xml_content)
        
        circulation = parser._parse_circulation(root)
        registration = parser._parse_registration(root)
        
        assert circulation["entry_deadline"] == date(2025, 5, 20)
        assert circulation["comment_entry_deadline"] == "(Valeur dates des enchères)"
        
        assert registration["entry_deadline"] == date(2025, 6, 16)
        assert "jusqu'au 26.06.2025" in registration["comment_entry_deadline"]
    
    def test_parse_auction_objects_as_string(self):
        """Test parsing auction objects as string (not structured)."""
        parser = SHABParser()
        
        xml_content = """
        <publication>
            <auctions>
                <auction>
                    <auctionObjects>
                        <p>Commune de Vex :</p>
                        <p>Parcelle No 4687, plan No 9, nom local "Mayens des Plans", surface totale de 1'469 m2, soit un bâtiment de 69 m2, une forêt dense / forêt de 177m2 et un pré, champ de 1'223 m2</p>
                        <p>Estimation officielle : Fr. 342'000.00</p>
                    </auctionObjects>
                </auction>
            </auctions>
        </publication>
        """
        
        from lxml import etree
        root = etree.fromstring(xml_content)
        
        auction_objects = parser._parse_auction_objects(root)
        
        assert len(auction_objects) == 1
        obj = auction_objects[0]
        
        # Should be treated as string description
        assert "Parcelle No 4687" in obj["description"]
        assert "Estimation officielle : Fr. 342'000.00" in obj["description"]
        
        # Other fields should be None since we're treating it as string
        assert obj["parcel_number"] is None
        assert obj["estimated_value"] is None
        assert obj["surface_area"] is None
    
    def test_parse_contacts_from_json_api(self):
        """Test parsing contacts from JSON API."""
        parser = SHABParser()
        
        # Mock JSON response
        json_content = """
        {
            "meta": {
                "registrationOffice": {
                    "id": "4095950d-a5d2-11e8-99a2-0050569d3c43",
                    "displayName": "Office des poursuites des districts de Sion, Hérens et Conthey",
                    "street": "Rue de la Piscine",
                    "streetNumber": "10",
                    "swissZipCode": "1950",
                    "town": "Sion",
                    "containsPostOfficeBox": false
                }
            }
        }
        """
        
        contacts = parser._extract_contacts_from_json(json_content)
        
        assert len(contacts) == 1
        contact = contacts[0]
        
        assert contact["name"] == "Office des poursuites des districts de Sion, Hérens et Conthey"
        assert contact["address"] == "Rue de la Piscine 10"
        assert contact["postal_code"] == "1950"
        assert contact["city"] == "Sion"
        assert contact["contact_type"] == "office"
        assert contact["office_id"] == "4095950d-a5d2-11e8-99a2-0050569d3c43"
        assert contact["contains_post_office_box"] is False
    
    def test_parse_contacts_with_post_office_box(self):
        """Test parsing contacts with post office box."""
        parser = SHABParser()
        
        json_content = """
        {
            "meta": {
                "registrationOffice": {
                    "id": "office-123",
                    "displayName": "Test Office",
                    "street": "Test Street",
                    "streetNumber": "1",
                    "swissZipCode": "8001",
                    "town": "Zurich",
                    "containsPostOfficeBox": true,
                    "postOfficeBox": {
                        "number": "123",
                        "zipCode": "8001",
                        "town": "Zurich"
                    }
                }
            }
        }
        """
        
        contacts = parser._extract_contacts_from_json(json_content)
        
        assert len(contacts) == 1
        contact = contacts[0]
        
        assert contact["contains_post_office_box"] is True
        assert contact["post_office_box"]["number"] == "123"
        assert contact["post_office_box"]["zipCode"] == "8001"
        assert contact["post_office_box"]["town"] == "Zurich"
    
    @patch('app.parsers.shab_parser.httpx.Client')
    def test_fetch_url_data(self, mock_client):
        """Test fetching data from URL."""
        parser = SHABParser()
        
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.text = "Test content"
        mock_response.raise_for_status.return_value = None
        
        mock_client_instance = MagicMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        result = parser.fetch_url_data("https://test.com")
        
        assert result == "Test content"
        mock_client_instance.get.assert_called_once_with("https://test.com")
    
    def test_parse_complete_publication(self):
        """Test parsing a complete publication with all new fields."""
        parser = SHABParser()
        
        # Mock complete XML
        xml_content = """
        <publication>
            <id>bb0b8622-803e-413e-8d71-bb6da17f5b0c</id>
            <publicationDate>2025-09-05</publicationDate>
            <expirationDate>2026-09-05</expirationDate>
            <title>
                <de>Betreibungsamtliche Grundstücksteigerung Blaise Blein</de>
                <en>Property auction initiated by the debt enforcement office Blaise Blein</en>
                <it>Incanto immobiliare Blaise Blein</it>
                <fr>Vente aux enchères d'immeubles dans le cadre de la poursuite Blaise Blein</fr>
            </title>
            <language>fr</language>
            <canton>VS</canton>
            <registrationOffice>
                <id>4095950d-a5d2-11e8-99a2-0050569d3c43</id>
                <displayName>Office des poursuites des districts de Sion, Hérens et Conthey</displayName>
                <street>Rue de la Piscine</street>
                <streetNumber>10</streetNumber>
                <swissZipCode>1950</swissZipCode>
                <town>Sion</town>
                <containsPostOfficeBox>false</containsPostOfficeBox>
            </registrationOffice>
            <auctions>
                <auction>
                    <id>6c8521f9-55c9-4bca-99cf-f65fb72a9143</id>
                    <date>2025-10-23</date>
                    <time>11:00:00</time>
                    <location>au Café de la Place, Place du Cotterd 1, 1981 Vex</location>
                    <circulation>
                        <entryDeadline>2025-09-25</entryDeadline>
                        <commentEntryDeadline>(Valeur dates des enchères)</commentEntryDeadline>
                    </circulation>
                    <registration>
                        <entryDeadline>2025-10-03</entryDeadline>
                        <commentEntryDeadline>jusqu'au 26.06.2025</commentEntryDeadline>
                    </registration>
                    <auctionObjects>
                        <p>Commune de Vex :</p>
                        <p>Parcelle No 4687, plan No 9, nom local "Mayens des Plans", surface totale de 1'469 m2, soit un bâtiment de 69 m2, une forêt dense / forêt de 177m2 et un pré, champ de 1'223 m2</p>
                        <p>Estimation officielle : Fr. 342'000.00</p>
                    </auctionObjects>
                </auction>
            </auctions>
            <debtors>
                <debtor>
                    <person>
                        <prename>Blaise</prename>
                        <name>Blein</name>
                        <dateOfBirth>1964-10-15</dateOfBirth>
                        <residence>
                            <selectType>switzerland</selectType>
                        </residence>
                        <addressSwitzerland>
                            <street>Rue du Port</street>
                            <houseNumber>25</houseNumber>
                            <swissZipCode>1815</swissZipCode>
                            <town>Clarens</town>
                        </addressSwitzerland>
                    </person>
                </debtor>
            </debtors>
        </publication>
        """
        
        # Mock JSON API response for contacts
        json_content = """
        {
            "meta": {
                "registrationOffice": {
                    "id": "4095950d-a5d2-11e8-99a2-0050569d3c43",
                    "displayName": "Office des poursuites des districts de Sion, Hérens et Conthey",
                    "street": "Rue de la Piscine",
                    "streetNumber": "10",
                    "swissZipCode": "1950",
                    "town": "Sion",
                    "containsPostOfficeBox": false
                }
            }
        }
        """
        
        with patch.object(parser, 'fetch_url_data', return_value=json_content):
            publications = parser.parse_xml(xml_content, "https://test.com")
        
        assert len(publications) == 1
        pub = publications[0]
        
        # Test publication fields
        assert pub["id"] == "bb0b8622-803e-413e-8d71-bb6da17f5b0c"
        assert pub["publication_date"] == date(2025, 9, 5)
        assert pub["expiration_date"] == date(2026, 9, 5)
        assert pub["title"]["de"] == "Betreibungsamtliche Grundstücksteigerung Blaise Blein"
        assert pub["title"]["fr"] == "Vente aux enchères d'immeubles dans le cadre de la poursuite Blaise Blein"
        assert pub["language"] == "fr"
        assert pub["canton"] == "VS"
        
        # Test auction fields
        assert len(pub["auctions"]) == 1
        auction = pub["auctions"][0]
        assert auction["id"] == "6c8521f9-55c9-4bca-99cf-f65fb72a9143"
        assert auction["date"] == date(2025, 10, 23)
        assert auction["time"] == "11:00:00"
        assert auction["location"] == "au Café de la Place, Place du Cotterd 1, 1981 Vex"
        assert auction["circulation"]["entry_deadline"] == date(2025, 9, 25)
        assert auction["registration"]["entry_deadline"] == date(2025, 10, 3)
        
        # Test auction objects
        assert len(auction["auction_objects"]) == 1
        obj = auction["auction_objects"][0]
        assert "Parcelle No 4687" in obj["description"]
        assert "Estimation officielle : Fr. 342'000.00" in obj["description"]
        
        # Test debtor
        assert len(pub["debtors"]) == 1
        debtor = pub["debtors"][0]
        assert debtor["debtor_type"] == "person"
        assert debtor["name"] == "Blein"
        assert debtor["prename"] == "Blaise"
        assert debtor["date_of_birth"] == date(1964, 10, 15)
        assert debtor["residence_type"] == "switzerland"
        assert debtor["address"] == "Rue du Port 25"
        assert debtor["city"] == "Clarens"
        assert debtor["postal_code"] == "1815"
        
        # Test contacts
        assert len(pub["contacts"]) == 1
        contact = pub["contacts"][0]
        assert contact["name"] == "Office des poursuites des districts de Sion, Hérens et Conthey"
        assert contact["address"] == "Rue de la Piscine 10"
        assert contact["postal_code"] == "1950"
        assert contact["city"] == "Sion"
        assert contact["contact_type"] == "office"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
