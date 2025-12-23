"""
Data Extractor for Grant Applications
Identifies relevant documents and extracts grant-specific data.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from .document_parser import DocumentParser

logger = logging.getLogger(__name__)


class DataExtractor:
    """Extracts structured grant data from documents."""
    
    def __init__(self, docs_folder: str):
        """
        Initialize the data extractor.
        
        Args:
            docs_folder: Path to the docs folder containing markdown files
        """
        self.docs_folder = Path(docs_folder)
        self.parser = DocumentParser(str(self.docs_folder))
        self.parsed_documents: Dict[str, Dict] = {}
    
    def identify_relevant_documents(self, grant_name: str, organization_name: Optional[str] = None) -> List[str]:
        """
        Identify relevant documents for a specific grant application.
        
        Args:
            grant_name: Name of the grant being applied for
            organization_name: Optional organization name to filter documents
            
        Returns:
            List of relevant document file paths
        """
        relevant_docs = []
        
        # Search for markdown files in docs folder
        markdown_files = list(self.docs_folder.glob("*.md"))
        
        for md_file in markdown_files:
            # Skip certain files
            if any(skip in md_file.name.lower() for skip in ['readme', 'test', 'guide', 'master']):
                continue
            
            # Check if file is relevant
            try:
                parsed = self.parser.parse_markdown_file(str(md_file))
                
                # Check if organization matches
                if organization_name:
                    org_name = parsed.get('organization', {}).get('name', '')
                    if organization_name.lower() not in org_name.lower() and org_name.lower() not in organization_name.lower():
                        continue
                
                # Check if grant-related content exists
                if self._is_grant_relevant(parsed, grant_name):
                    relevant_docs.append(str(md_file))
                    self.parsed_documents[str(md_file)] = parsed
                    
            except Exception as e:
                logger.warning(f"Error parsing {md_file}: {e}")
                continue
        
        return relevant_docs
    
    def _is_grant_relevant(self, parsed_data: Dict, grant_name: str) -> bool:
        """Check if document is relevant to the grant."""
        # Check if grant name appears in content
        content = parsed_data.get('raw_content', '').lower()
        grant_keywords = grant_name.lower().split()
        
        # Check if any keywords match
        for keyword in grant_keywords:
            if len(keyword) > 3 and keyword in content:
                return True
        
        return False
    
    def extract_grant_data(self, grant_name: str, document_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Extract grant application data from relevant documents.
        
        Args:
            grant_name: Name of the grant being applied for
            document_paths: Optional list of specific document paths to use
            
        Returns:
            Dictionary containing structured grant application data
        """
        if document_paths is None:
            document_paths = self.identify_relevant_documents(grant_name)
        
        if not document_paths:
            raise ValueError(f"No relevant documents found for grant: {grant_name}")
        
        # Parse all documents if not already parsed
        for doc_path in document_paths:
            if doc_path not in self.parsed_documents:
                try:
                    self.parsed_documents[doc_path] = self.parser.parse_markdown_file(doc_path)
                except Exception as e:
                    logger.error(f"Error parsing {doc_path}: {e}")
                    continue
        
        # Merge data from all relevant documents
        merged_data = self._merge_document_data(document_paths, grant_name)
        
        return merged_data
    
    def _merge_document_data(self, document_paths: List[str], grant_name: str) -> Dict[str, Any]:
        """Merge data from multiple documents."""
        merged = {
            'grant_name': grant_name,
            'organization': {},
            'project': {},
            'budget': {},
            'contact': {},
            'timeline': {},
            'technical': {},
            'source_documents': document_paths
        }
        
        # Merge data from all documents
        for doc_path in document_paths:
            parsed = self.parsed_documents.get(doc_path, {})
            
            # Merge organization info (take first non-empty value)
            org_data = parsed.get('organization', {})
            for key, value in org_data.items():
                if value and not merged['organization'].get(key):
                    merged['organization'][key] = value
            
            # Merge project info
            project_data = parsed.get('project', {})
            for key, value in project_data.items():
                if value:
                    if key not in merged['project']:
                        merged['project'][key] = []
                    if isinstance(value, list):
                        merged['project'][key].extend(value)
                    else:
                        merged['project'][key] = value
            
            # Merge budget (sum amounts, combine line items)
            budget_data = parsed.get('budget', {})
            if budget_data.get('total_requested'):
                if not merged['budget'].get('total_requested'):
                    merged['budget']['total_requested'] = 0
                merged['budget']['total_requested'] += budget_data['total_requested']
            
            if budget_data.get('line_items'):
                if 'line_items' not in merged['budget']:
                    merged['budget']['line_items'] = []
                merged['budget']['line_items'].extend(budget_data['line_items'])
            
            # Merge contact (take first non-empty)
            contact_data = parsed.get('contact', {})
            for key, value in contact_data.items():
                if value and not merged['contact'].get(key):
                    merged['contact'][key] = value
            
            # Merge timeline
            timeline_data = parsed.get('timeline', {})
            for key, value in timeline_data.items():
                if value and not merged['timeline'].get(key):
                    merged['timeline'][key] = value
            
            # Merge technical
            technical_data = parsed.get('technical', {})
            for key, value in technical_data.items():
                if value:
                    if key not in merged['technical']:
                        merged['technical'][key] = []
                    if isinstance(value, list):
                        merged['technical'][key].extend(value)
                    else:
                        merged['technical'][key] = value
        
        return merged
    
    def validate_extracted_data(self, grant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted data and identify missing fields.
        
        Args:
            grant_data: Extracted grant data dictionary
            
        Returns:
            Validation result with missing fields and warnings
        """
        validation_result = {
            'valid': True,
            'missing_required': [],
            'missing_optional': [],
            'warnings': []
        }
        
        # Required fields
        required_fields = {
            'organization': ['name'],
            'project': ['description'],
            'contact': ['email'],
        }
        
        # Check required fields
        for section, fields in required_fields.items():
            section_data = grant_data.get(section, {})
            for field in fields:
                if not section_data.get(field):
                    validation_result['missing_required'].append(f"{section}.{field}")
                    validation_result['valid'] = False
        
        # Optional but recommended fields
        optional_fields = {
            'organization': ['mission', 'structure', 'tax_status'],
            'project': ['goals', 'impact', 'target_audience'],
            'budget': ['total_requested', 'line_items'],
            'contact': ['name', 'phone', 'address'],
            'timeline': ['start_date', 'end_date'],
        }
        
        # Check optional fields
        for section, fields in optional_fields.items():
            section_data = grant_data.get(section, {})
            for field in fields:
                if not section_data.get(field):
                    validation_result['missing_optional'].append(f"{section}.{field}")
        
        # Warnings
        if not grant_data.get('budget', {}).get('total_requested'):
            validation_result['warnings'].append("No budget amount found")
        
        if not grant_data.get('organization', {}).get('tax_status'):
            validation_result['warnings'].append("Tax status (501(c)(3)) not found")
        
        return validation_result
    
    def get_standardized_data(self, grant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert extracted data to standardized format for form filling.
        
        Args:
            grant_data: Extracted grant data dictionary
            
        Returns:
            Standardized data dictionary ready for form mapping
        """
        standardized = {
            # Organization fields
            'organization_name': grant_data.get('organization', {}).get('name', ''),
            'organization_mission': grant_data.get('organization', {}).get('mission', ''),
            'organization_structure': grant_data.get('organization', {}).get('structure', ''),
            'organization_tax_status': grant_data.get('organization', {}).get('tax_status', ''),
            'organization_budget': grant_data.get('organization', {}).get('budget', ''),
            'organization_founded': grant_data.get('organization', {}).get('founded', ''),
            
            # Project fields
            'project_title': grant_data.get('project', {}).get('title', ''),
            'project_description': grant_data.get('project', {}).get('description', ''),
            'project_goals': '\n'.join(grant_data.get('project', {}).get('goals', [])),
            'project_impact': grant_data.get('project', {}).get('impact', ''),
            'project_target_audience': grant_data.get('project', {}).get('target_audience', ''),
            'project_activities': '\n'.join(grant_data.get('project', {}).get('activities', [])),
            'project_outcomes': '\n'.join(grant_data.get('project', {}).get('outcomes', [])),
            
            # Budget fields
            'budget_total': grant_data.get('budget', {}).get('total_requested', 0),
            'budget_line_items': grant_data.get('budget', {}).get('line_items', []),
            'budget_matching_funds': grant_data.get('budget', {}).get('matching_funds', {}),
            'budget_breakdown': grant_data.get('budget', {}).get('breakdown', {}),
            
            # Contact fields
            'contact_name': grant_data.get('contact', {}).get('name', ''),
            'contact_email': grant_data.get('contact', {}).get('email', ''),
            'contact_phone': grant_data.get('contact', {}).get('phone', ''),
            'contact_address': grant_data.get('contact', {}).get('address', ''),
            'contact_website': grant_data.get('contact', {}).get('website', ''),
            
            # Timeline fields
            'timeline_start_date': grant_data.get('timeline', {}).get('start_date', ''),
            'timeline_end_date': grant_data.get('timeline', {}).get('end_date', ''),
            'timeline_deadline': grant_data.get('timeline', {}).get('deadline', ''),
            'timeline_milestones': grant_data.get('timeline', {}).get('milestones', []),
            'timeline_duration': grant_data.get('timeline', {}).get('duration', ''),
            
            # Technical fields
            'technical_specifications': grant_data.get('technical', {}).get('specifications', ''),
            'technical_equipment': '\n'.join(grant_data.get('technical', {}).get('equipment', [])),
            'technical_infrastructure': grant_data.get('technical', {}).get('infrastructure', ''),
            'technical_requirements': '\n'.join(grant_data.get('technical', {}).get('requirements', [])),
        }
        
        return standardized

