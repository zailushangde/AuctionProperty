"""Test API endpoints for SHAB parser without database storage."""

import httpx
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.parsers import SHABParser

router = APIRouter(prefix="/test-parser", tags=["test-parser"])


@router.get("/parse-url")
async def parse_shab_url(
    url: str = Query(..., description="SHAB XML URL to parse"),
    include_raw: bool = Query(False, description="Include raw XML content in response")
):
    """
    Parse SHAB XML from a URL and return structured JSON data.
    
    This endpoint fetches XML data from the provided URL, parses it using the SHAB parser,
    and returns the structured data without storing it in the database.
    
    Example usage:
    - /test-parser/parse-url?url=https://www.shab.ch/api/v1/publications/c42e67af-486d-44f4-8c6e-0ad03538770d/xml
    """
    
    try:
        # Fetch XML content from URL
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            xml_content = response.text
        
        # Parse XML using SHAB parser
        parser = SHABParser()
        # Convert XML URL to HTML URL for contact extraction
        html_url = url.replace('/xml', '').replace('/api/v1/publications/', '/#!/search/publications/detail/')
        publications_data = parser.parse_xml(xml_content, html_url)
        
        # Prepare response
        result = {
            "success": True,
            "url": url,
            "publications_count": len(publications_data),
            "publications": publications_data
        }
        
        # Include raw XML if requested
        if include_raw:
            result["raw_xml"] = xml_content
        
        return result
        
    except httpx.HTTPError as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse XML: {str(e)}")


@router.get("/parse-sample")
async def parse_sample_data():
    """
    Parse a sample SHAB publication and return structured JSON data.
    
    This endpoint uses the same sample data we tested earlier to demonstrate
    the parser functionality without requiring an external URL.
    """
    
    # Sample XML content based on the real SHAB data
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<sb:publication xmlns:sb="http://www.ech.ch/xmlns/eCH-0090/1">
    <sb:id>c42e67af-486d-44f4-8c6e-0ad03538770d</sb:id>
    <sb:publicationDate>2025-04-30</sb:publicationDate>
    <sb:title>Vente aux enchères d'immeubles dans le cadre de la poursuite Foncière Immobilière Nord Bernoise SA</sb:title>
    <sb:language>fr</sb:language>
    <sb:canton>BE</sb:canton>
    <sb:registrationOffice>Office des poursuites du Jura bernois - Département poursuites</sb:registrationOffice>
    <sb:content>Une attention particulière doit être portée à la loi fédérale sur l'acquisition d'immeubles par des personnes à l'étranger (LFAIE) et à l'ordonnance sur l'acquisition d'immeubles par des personnes à l'étranger (OAIE). <br />Pour autant qu'elles ne soient pas constatées par les registres publics, les prétentions non annoncées dans le délai imparti sont exclues de la participation au produit de la vente. De même, les créanciers nantis de titres de gage doivent annoncer leurs créances garanties par nantissement. <br />Référence est par ailleurs faite aux conditions de mise aux enchères. <br />Publication selon les art. 133, 134, 135, 138 LP; art. 29 de l'ORFI du 23 avril 1920.</sb:content>
    
    <sb:debtor>
        <sb:name>Foncière Immobilière Nord Bernoise SA</sb:name>
        <sb:legalForm>company</sb:legalForm>
        <sb:uid>CHE-175.482.480</sb:uid>
    </sb:debtor>
    
    <sb:contact>
        <sb:name>Berney Associés Fribourg SA</sb:name>
        <sb:address>Boulevard de Pérolles 37, 1700 Fribourg</sb:address>
    </sb:contact>
    
    <sb:auction>
        <sb:auctionDate>2025-09-04</sb:auctionDate>
        <sb:auctionTime>14:30</sb:auctionTime>
        <sb:auctionLocation>Salle de Conférence de l'Office des poursuites et des faillites du Jura bernois, Rue Centrale 33, 2740 Moutier</sb:auctionLocation>
        <sb:court>Office des poursuites du Jura bernois - Département poursuites</sb:court>
    </sb:auction>
    
    <sb:auctionObjects>
        <sb:auctionObject>
            <p><b>Ban de Saint-Imier - Feuillet no 812</b></p>
            <p><b>Bâtiment, habitation 182 m<sup>2</sup>, Rue du Midi 57, 2610 Saint-Imier, Jardin 161 m<sup>2</sup>, Autre revêtement dur, 108 m<sup>2</sup>, Surface totale 451 m<sup>2</sup>.</b></p>
            <p><b>Valeur officielle : CHF 489'000.00</b></p>
            <p><b>Valeur vénale : CHF 650'000.00 (estimation de l'expert du 20 décembre 2023)</b></p>
        </sb:auctionObject>
    </sb:auctionObjects>
</sb:publication>'''
    
    try:
        # Parse XML using SHAB parser
        parser = SHABParser()
        publications_data = parser.parse_xml(xml_content)
        
        return {
            "success": True,
            "description": "Sample SHAB publication parsed successfully",
            "publications_count": len(publications_data),
            "publications": publications_data,
            "sample_data": {
                "source": "Sample SHAB publication from Jura bernois",
                "property": "Ban de Saint-Imier - Feuillet no 812",
                "estimated_value": "CHF 650'000.00",
                "surface_area": "182 m²",
                "auction_date": "2025-09-04 14:30"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse sample XML: {str(e)}")


@router.get("/parse-html")
async def parse_html_content(
    html_content: str = Query(..., description="HTML content to parse for property details")
):
    """
    Parse HTML content to extract property details.
    
    This endpoint demonstrates the HTML parsing functionality by extracting
    property information from HTML content.
    """
    
    try:
        parser = SHABParser()
        parsed_content = parser._parse_html_content(html_content)
        
        return {
            "success": True,
            "description": "HTML content parsed successfully",
            "extracted_data": parsed_content,
            "summary": {
                "parcel_number": parsed_content.get('parcel_number'),
                "estimated_value": parsed_content.get('estimated_value'),
                "surface_area": parsed_content.get('surface_area'),
                "address": parsed_content.get('address'),
                "municipality": parsed_content.get('municipality'),
                "property_type": parsed_content.get('property_type')
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse HTML content: {str(e)}")


@router.get("/debug-xml")
async def debug_xml_structure(
    url: str = Query(..., description="SHAB XML URL to debug")
):
    """
    Debug endpoint to see the actual XML structure from SHAB URL.
    """
    
    try:
        # Fetch XML content from URL
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            xml_content = response.text
        
        # Try to parse with different approaches
        from lxml import etree
        
        # Parse the XML
        root = etree.fromstring(xml_content.encode('utf-8'))
        
        # Get all namespaces
        namespaces = root.nsmap if hasattr(root, 'nsmap') else {}
        
        # Try to find publication elements with different approaches
        publication_elements = []
        
        # Method 1: Look for elements with 'publication' in the tag name
        for elem in root.iter():
            if 'publication' in elem.tag.lower():
                publication_elements.append({
                    'tag': elem.tag,
                    'text': elem.text[:100] if elem.text else None,
                    'children': [child.tag for child in elem]
                })
        
        # Method 2: Look for common SHAB elements
        common_elements = []
        for elem in root.iter():
            tag_lower = elem.tag.lower()
            if any(keyword in tag_lower for keyword in ['title', 'date', 'canton', 'auction', 'debtor', 'object']):
                common_elements.append({
                    'tag': elem.tag,
                    'text': elem.text[:100] if elem.text else None,
                    'parent': elem.getparent().tag if elem.getparent() is not None else None
                })
        
        return {
            "success": True,
            "url": url,
            "xml_length": len(xml_content),
            "root_tag": root.tag,
            "namespaces": namespaces,
            "publication_elements": publication_elements[:10],  # Limit to first 10
            "common_elements": common_elements[:20],  # Limit to first 20
            "raw_xml_preview": xml_content[:1000] + "..." if len(xml_content) > 1000 else xml_content
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": url
        }


@router.get("/parser-info")
async def get_parser_info():
    """
    Get information about the SHAB parser capabilities.
    """
    
    return {
        "parser_name": "SHAB XML Parser",
        "version": "1.0.0",
        "description": "Parser for Swiss Official Gazette (SHAB) XML publications",
        "capabilities": {
            "languages": ["French", "German", "Italian", "English"],
            "extracted_fields": [
                "Publication metadata (title, date, canton, language)",
                "Auction details (date, time, location, court)",
                "Property information (parcel number, estimated value, surface area)",
                "Debtor information (name, legal form, address)",
                "Contact details (name, phone, email, address)"
            ],
            "supported_formats": [
                "SHAB XML with sb: namespace",
                "HTML content within auction objects",
                "Multilingual property descriptions"
            ]
        },
        "example_urls": [
            "https://www.shab.ch/api/v1/publications/{publication-id}/xml"
        ],
        "endpoints": {
            "parse_url": "/test-parser/parse-url?url={shab_xml_url}",
            "parse_sample": "/test-parser/parse-sample",
            "parse_html": "/test-parser/parse-html?html_content={html_content}",
            "parser_info": "/test-parser/parser-info"
        }
    }
