"""
Narrative Generator for Grant Applications
Uses OpenAI API to convert structured data into complete narrative prose.
"""

import openai
import logging
import time
import re
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class NarrativeGenerator:
    """Generates complete narratives from structured grant data using OpenAI API."""
    
    # Complete templates for each narrative type
    PROJECT_DESCRIPTION_TEMPLATE = """
You are writing a comprehensive project description for a grant application to {grant_name}.

ORGANIZATION CONTEXT:
- Organization Name: {organization_name}
- Mission: {organization_mission}
- Tax Status: {tax_status}
- Founded: {founded_year}
- Annual Budget: ${annual_budget:,.2f}
- Target Audience: {target_audience}

PROJECT DATA TO INCLUDE:
- Project Title: {project_title}
- Project Description: {project_description}
- Project Goals: {project_goals}
- Target Audience: {target_audience}
- Geographic Scope: {geographic_scope}
- Timeline: {timeline}
- Expected Participants: {expected_participants}

GRANT CONTEXT:
- Grant Name: {grant_name}
- Grant Deadline: {deadline}
- Grant Focus Areas: {grant_focus}
- Grant Amount Requested: ${budget_total:,.2f}

REQUIREMENTS FOR COMPLETE NARRATIVE:
1. Must include organization's mission and how project aligns
2. Must describe the specific problem or need being addressed
3. Must explain the project's approach and methodology
4. Must detail the target population and their needs
5. Must describe expected outcomes and impact
6. Must explain how this project is unique to your organization
7. Must connect project to grant's focus areas
8. Must include specific metrics and measurable goals
9. Must describe sustainability and long-term impact
10. Must explain community partnerships and collaboration

STYLE REQUIREMENTS:
- Write in professional grant writing style
- Use complete sentences and paragraphs (NO bullet points)
- Write in third person about the organization
- Use active voice where appropriate
- Include specific details, numbers, and concrete examples
- Length: 500-1000 words for comprehensive description
- Flow naturally from problem to solution to impact

UNIQUENESS REQUIREMENTS:
- Incorporate specific details about {organization_name}
- Reference specific programs, partnerships, or achievements
- Include organization-specific metrics and outcomes
- Connect to organization's unique mission and approach
- Reference specific community needs and context
- Include unique aspects of this project that differentiate it

Generate a complete, unique project description that incorporates ALL of the above information in a flowing narrative format with NO bullet points.
"""

    GOALS_NARRATIVE_TEMPLATE = """
You are writing project goals for a grant application to {grant_name}.

ORGANIZATION CONTEXT:
- Organization: {organization_name}
- Mission: {organization_mission}

PROJECT CONTEXT:
- Project Title: {project_title}
- Project Description: {project_description}
- Grant Amount: ${budget_total:,.2f}

GOALS DATA TO INCLUDE:
{goals_list}

Each goal should be expanded into a complete narrative that includes:
- The specific objective
- Why this goal is important
- How it will be achieved
- Who will benefit
- How success will be measured
- Timeline for achievement

REQUIREMENTS FOR COMPLETE NARRATIVE:
1. Convert each goal into a complete paragraph (not a list)
2. Explain the rationale and importance of each goal
3. Connect goals to organization's mission
4. Show how goals align with grant objectives
5. Include measurable outcomes for each goal
6. Explain how goals build upon each other
7. Describe the target population for each goal
8. Include specific metrics and success indicators
9. Explain long-term impact of achieving goals
10. Show how goals address community needs

STYLE REQUIREMENTS:
- Write in flowing prose (NO bullet points, NO numbered lists)
- Use complete sentences and paragraphs
- Each goal should be 2-4 sentences explaining the objective
- Connect goals with transitional phrases
- Use professional grant writing language
- Total length: 300-600 words depending on number of goals

UNIQUENESS REQUIREMENTS:
- Reference {organization_name}'s specific approach
- Include organization-specific metrics and targets
- Connect to organization's unique programs
- Reference specific community context
- Include unique aspects of how goals will be achieved

Generate a complete narrative that incorporates ALL goals into flowing prose with NO bullet points or lists.
"""

    IMPACT_NARRATIVE_TEMPLATE = """
You are writing about project impact for a grant application to {grant_name}.

ORGANIZATION CONTEXT:
- Organization: {organization_name}
- Years of Operation: {years_operating}
- Current Reach: {current_reach}
- Previous Impact: {previous_impact}

PROJECT CONTEXT:
- Project Title: {project_title}
- Target Population: {target_audience}
- Geographic Scope: {geographic_scope}

IMPACT DATA TO INCLUDE:
- Expected Outcomes: {expected_outcomes}
- Metrics: {impact_metrics}
- Target Numbers: {target_numbers}
- Previous Results: {previous_results}
- Community Impact: {community_impact}

REQUIREMENTS FOR COMPLETE NARRATIVE:
1. Describe both quantitative and qualitative impact
2. Include specific metrics and numbers
3. Explain impact on target population
4. Describe community-wide effects
5. Include short-term and long-term impact
6. Explain how impact will be measured
7. Reference previous successful outcomes
8. Describe transformative potential
9. Include impact on underserved populations
10. Explain sustainability of impact

STYLE REQUIREMENTS:
- Write in professional narrative style (NO bullet points)
- Use complete sentences and paragraphs
- Incorporate metrics naturally into prose
- Use specific numbers and percentages
- Write in third person
- Length: 400-700 words
- Flow from immediate to long-term impact

UNIQUENESS REQUIREMENTS:
- Reference {organization_name}'s track record
- Include organization-specific impact metrics
- Connect to organization's unique mission
- Reference specific community needs addressed
- Include unique aspects of impact measurement

Generate a complete impact narrative incorporating ALL metrics and outcomes in flowing prose with NO bullet points.
"""

    ACTIVITIES_NARRATIVE_TEMPLATE = """
You are writing about project activities for a grant application to {grant_name}.

ORGANIZATION CONTEXT:
- Organization: {organization_name}
- Expertise Areas: {expertise_areas}
- Program Experience: {program_experience}

PROJECT CONTEXT:
- Project Title: {project_title}
- Project Duration: {project_duration}
- Target Participants: {target_participants}

ACTIVITIES DATA TO INCLUDE:
{activities_list}

Each activity should be described as a complete narrative including:
- What will be done
- Who will participate
- When and where it occurs
- How it will be implemented
- Resources needed
- Expected outcomes from activity

REQUIREMENTS FOR COMPLETE NARRATIVE:
1. Convert each activity into complete paragraph(s)
2. Describe the activity in detail
3. Explain who will participate and why
4. Describe the methodology or approach
5. Include timeline and frequency
6. Explain resources and materials needed
7. Connect activity to project goals
8. Describe expected outcomes from activity
9. Explain how activities build upon each other
10. Include staff/volunteer roles

STYLE REQUIREMENTS:
- Write in flowing narrative style (NO bullet points, NO lists)
- Use complete sentences and paragraphs
- Describe activities as ongoing processes
- Use active voice
- Include specific details and examples
- Length: 500-800 words depending on number of activities
- Flow chronologically or thematically

UNIQUENESS REQUIREMENTS:
- Reference {organization_name}'s specific methods
- Include organization-specific program elements
- Connect to organization's expertise
- Reference unique partnerships or approaches
- Include specific community context

Generate a complete activities narrative incorporating ALL activities in flowing prose with NO bullet points or lists.
"""

    BUDGET_NARRATIVE_TEMPLATE = """
You are writing a budget narrative for a grant application to {grant_name}.

ORGANIZATION CONTEXT:
- Organization: {organization_name}
- Annual Budget: ${annual_budget:,.2f}
- Financial Stability: {financial_stability}

PROJECT CONTEXT:
- Project Title: {project_title}
- Total Requested: ${budget_total:,.2f}
- Project Duration: {project_duration}
- Matching Funds: {matching_funds}

BUDGET DATA TO INCLUDE:
- Total Request: ${budget_total:,.2f}
- Line Items: {budget_line_items}
- Budget Breakdown: {budget_breakdown}
- Matching Funds: {matching_funds_percentage}%
- In-Kind Contributions: {in_kind_contributions}

REQUIREMENTS FOR COMPLETE NARRATIVE:
1. Explain the total budget request and its justification
2. Describe each major budget category in detail
3. Explain costs for personnel, equipment, materials, etc.
4. Justify each expense as necessary for project success
5. Explain cost-effectiveness and value
6. Describe matching funds and their sources
7. Explain in-kind contributions
8. Show budget aligns with project activities
9. Explain sustainability and long-term funding
10. Include budget timeline and spending plan

STYLE REQUIREMENTS:
- Write in professional narrative style (NO bullet points, NO tables)
- Use complete sentences and paragraphs
- Incorporate dollar amounts naturally into prose
- Explain costs in context of project goals
- Use third person
- Length: 400-600 words
- Flow from total to categories to justification

UNIQUENESS REQUIREMENTS:
- Reference {organization_name}'s financial practices
- Include organization-specific cost structures
- Reference unique partnerships that reduce costs
- Include specific vendor or service details
- Connect to organization's efficiency

Generate a complete budget narrative incorporating ALL budget information in flowing prose with NO bullet points or tables.
"""

    TECHNICAL_NARRATIVE_TEMPLATE = """
You are writing technical specifications for a grant application to {grant_name}.

ORGANIZATION CONTEXT:
- Organization: {organization_name}
- Technical Expertise: {technical_expertise}
- Current Infrastructure: {current_infrastructure}

PROJECT CONTEXT:
- Project Title: {project_title}
- Technical Requirements: {technical_requirements}
- Equipment Needs: {equipment_needs}

TECHNICAL DATA TO INCLUDE:
- Specifications: {technical_specifications}
- Equipment List: {equipment_list}
- Infrastructure Needs: {infrastructure_needs}
- Technical Requirements: {technical_requirements}
- Integration Needs: {integration_needs}

REQUIREMENTS FOR COMPLETE NARRATIVE:
1. Describe technical infrastructure comprehensively
2. Explain equipment specifications and rationale
3. Describe how technology supports project goals
4. Explain technical requirements and standards
5. Describe integration with existing systems
6. Explain technical support and maintenance
7. Include capacity and scalability considerations
8. Describe security and data privacy measures
9. Explain technical training needs
10. Include technical timeline and implementation

STYLE REQUIREMENTS:
- Write in professional technical narrative style (NO bullet points)
- Use complete sentences and paragraphs
- Explain technical terms in context
- Describe equipment and systems naturally
- Use third person
- Length: 500-700 words
- Flow from overview to specifics to implementation

UNIQUENESS REQUIREMENTS:
- Reference {organization_name}'s technical capabilities
- Include organization-specific technical needs
- Connect to organization's existing systems
- Reference unique technical partnerships
- Include specific technical context

Generate a complete technical narrative incorporating ALL technical information in flowing prose with NO bullet points or lists.
"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4", 
                 temperature: float = 0.7, max_tokens: int = 2000):
        """
        Initialize the narrative generator.
        
        Args:
            api_key: OpenAI API key (uses environment variable if not provided)
            model: OpenAI model to use
            temperature: Temperature for generation (0.7 recommended)
            max_tokens: Maximum tokens per generation
        """
        self.api_key = api_key or self._get_api_key()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = None
        
        if not self.api_key:
            logger.warning("OpenAI API key not found. Narrative generation will be disabled.")
    
    def _get_api_key(self) -> Optional[str]:
        """Get OpenAI API key from environment or config."""
        import os
        try:
            # Try environment variable first
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                return api_key
            
            # Try importing from config
            try:
                from api import config
                return config.OPENAI_API_KEY
            except (ImportError, AttributeError):
                pass
            
            return None
        except Exception as e:
            logger.warning(f"Error getting API key: {e}")
            return None
    
    @property
    def client(self):
        """Lazy initialization of OpenAI client."""
        if self._client is None and self.api_key:
            try:
                self._client = openai.OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Error initializing OpenAI client: {e}")
                return None
        return self._client
    
    def _collect_organization_context(self, grant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect all organization context data."""
        org = grant_data.get('organization', {})
        return {
            'organization_name': org.get('name', 'Not specified'),
            'organization_mission': org.get('mission', 'Not specified'),
            'tax_status': org.get('tax_status', 'Not specified'),
            'founded_year': org.get('founded', 'Not specified'),
            'annual_budget': org.get('budget', 0),
            'target_audience': grant_data.get('project', {}).get('target_audience', 'Not specified'),
            'years_operating': 2024 - org.get('founded', 2024) if org.get('founded') else 'Not specified',
            'current_reach': 'Not specified',  # Could be extracted from project data
            'previous_impact': org.get('history', 'Not specified'),
            'expertise_areas': 'Not specified',  # Could be extracted
            'program_experience': org.get('structure', 'Not specified'),
            'technical_expertise': 'Not specified',
            'current_infrastructure': grant_data.get('technical', {}).get('infrastructure', 'Not specified'),
            'financial_stability': 'Not specified'
        }
    
    def _collect_project_context(self, grant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect all project context data."""
        project = grant_data.get('project', {})
        budget = grant_data.get('budget', {})
        timeline = grant_data.get('timeline', {})
        
        return {
            'project_title': project.get('title', 'Not specified'),
            'project_description': project.get('description', 'Not specified'),
            'project_goals': self._format_list(project.get('goals', [])),
            'target_audience': project.get('target_audience', 'Not specified'),
            'geographic_scope': 'Not specified',  # Could be extracted
            'timeline': timeline.get('duration', 'Not specified'),
            'expected_participants': 'Not specified',  # Could be extracted
            'project_duration': timeline.get('duration', 'Not specified'),
            'target_participants': project.get('target_audience', 'Not specified'),
            'budget_total': budget.get('total_requested', 0),
            'deadline': timeline.get('deadline', 'Not specified'),
            'grant_focus': 'Not specified'  # Could be from grant name or config
        }
    
    def _collect_grant_context(self, grant_name: str, grant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect grant-specific context."""
        budget = grant_data.get('budget', {})
        timeline = grant_data.get('timeline', {})
        
        return {
            'grant_name': grant_name,
            'deadline': timeline.get('deadline', 'Not specified'),
            'grant_focus': 'Not specified',  # Could be extracted from grant name
            'budget_total': budget.get('total_requested', 0),
            'matching_funds': budget.get('matching_funds', {}),
            'matching_funds_percentage': budget.get('matching_funds', {}).get('percentage', 0) if isinstance(budget.get('matching_funds'), dict) else 0
        }
    
    def _format_list(self, items: List[str]) -> str:
        """Format a list of items for inclusion in template."""
        if not items:
            return "Not specified"
        return "\n".join(f"- {item}" for item in items)
    
    def _build_narrative_prompt(self, template: str, data: Dict[str, Any]) -> str:
        """
        Build a complete narrative prompt from template and data.
        
        Args:
            template: Template string with placeholders
            data: Dictionary of data to fill template
            
        Returns:
            Complete prompt string
        """
        try:
            # Fill template with data, handling missing values
            prompt = template.format(**data)
            return prompt
        except KeyError as e:
            logger.warning(f"Missing template variable: {e}. Using 'Not specified'")
            # Fill missing keys with "Not specified"
            for key in template.split('{'):
                if '}' in key:
                    var_name = key.split('}')[0]
                    if var_name not in data:
                        data[var_name] = "Not specified"
            return template.format(**data)
    
    def _call_openai_api(self, prompt: str, system_message: Optional[str] = None, max_retries: int = 3) -> Optional[str]:
        """
        Call OpenAI API to generate narrative with retry logic.
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            max_retries: Maximum number of retry attempts
            
        Returns:
            Generated narrative or None if error
        """
        if not self.client:
            logger.error("OpenAI client not available")
            return None
        
        if not system_message:
            system_message = "You are an expert grant writer specializing in creating comprehensive, professional grant applications. You write clear, detailed, and compelling content that meets foundation requirements. Always write in complete prose with NO bullet points, NO lists, and NO tables."
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    timeout=60  # 60 second timeout
                )
                
                generated_text = response.choices[0].message.content
                elapsed_time = time.time() - start_time
                
                logger.info(f"Narrative generated in {elapsed_time:.2f}s using {response.usage.total_tokens if response.usage else 'unknown'} tokens")
                
                # Post-process to ensure no bullet points
                generated_text = self._remove_bullet_points(generated_text)
                
                # Validate output quality
                if self._validate_narrative_quality(generated_text):
                    return generated_text
                else:
                    logger.warning("Generated narrative failed quality check, retrying...")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        logger.warning("Using narrative despite quality concerns")
                        return generated_text
                
            except openai.RateLimitError as e:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"OpenAI API rate limit exceeded, waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error("Max retries reached for rate limit")
                    return None
            except openai.APITimeoutError:
                logger.warning(f"OpenAI API timeout, retrying {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    logger.error("Max retries reached for timeout")
                    return None
            except openai.APIError as e:
                error_str = str(e).lower()
                # Don't retry on authentication errors (invalid API key)
                if 'invalid' in error_str and 'api key' in error_str:
                    logger.error(f"Invalid OpenAI API key. Please check your API key.")
                    return None
                logger.error(f"OpenAI API error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    return None
            except Exception as e:
                logger.error(f"Error calling OpenAI API: {e}")
                return None
        
        return None
    
    def _validate_narrative_quality(self, text: str) -> bool:
        """
        Validate that generated narrative meets quality requirements.
        
        Args:
            text: Generated narrative text
            
        Returns:
            True if quality is acceptable, False otherwise
        """
        if not text or len(text.strip()) < 50:
            return False
        
        # Check for bullet points (should be removed but double-check)
        if re.search(r'^[\s]*[-*•]\s+', text, re.MULTILINE):
            logger.warning("Narrative contains bullet points")
            return False
        
        # Check for numbered lists
        if re.search(r'^\d+\.\s+', text, re.MULTILINE):
            logger.warning("Narrative contains numbered lists")
            return False
        
        # Check for complete sentences (should have periods)
        sentences = re.split(r'[.!?]', text)
        if len([s for s in sentences if len(s.strip()) > 10]) < 3:
            logger.warning("Narrative may not have enough complete sentences")
            return False
        
        return True
    
    def _remove_bullet_points(self, text: str) -> str:
        """Remove any bullet points or list formatting from text."""
        # Remove bullet points
        text = re.sub(r'^[\s]*[-*•]\s+', '', text, flags=re.MULTILINE)
        # Remove numbered lists
        text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
        # Remove multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
    
    def generate_project_description(self, grant_name: str, grant_data: Dict[str, Any]) -> Optional[str]:
        """
        Generate complete project description narrative.
        
        Args:
            grant_name: Name of the grant
            grant_data: Extracted grant data dictionary
            
        Returns:
            Generated narrative or None if error
        """
        org_context = self._collect_organization_context(grant_data)
        project_context = self._collect_project_context(grant_data)
        grant_context = self._collect_grant_context(grant_name, grant_data)
        
        data = {**org_context, **project_context, **grant_context}
        
        prompt = self._build_narrative_prompt(self.PROJECT_DESCRIPTION_TEMPLATE, data)
        return self._call_openai_api(prompt)
    
    def generate_goals_narrative(self, grant_name: str, grant_data: Dict[str, Any]) -> Optional[str]:
        """Generate complete goals narrative."""
        org_context = self._collect_organization_context(grant_data)
        project_context = self._collect_project_context(grant_data)
        grant_context = self._collect_grant_context(grant_name, grant_data)
        
        # Format goals list
        goals = grant_data.get('project', {}).get('goals', [])
        goals_list = self._format_list(goals)
        
        data = {
            **org_context,
            **project_context,
            **grant_context,
            'goals_list': goals_list
        }
        
        prompt = self._build_narrative_prompt(self.GOALS_NARRATIVE_TEMPLATE, data)
        return self._call_openai_api(prompt)
    
    def generate_impact_narrative(self, grant_name: str, grant_data: Dict[str, Any]) -> Optional[str]:
        """Generate complete impact narrative."""
        org_context = self._collect_organization_context(grant_data)
        project_context = self._collect_project_context(grant_data)
        grant_context = self._collect_grant_context(grant_name, grant_data)
        
        project = grant_data.get('project', {})
        impact_data = {
            'expected_outcomes': self._format_list(project.get('outcomes', [])),
            'impact_metrics': project.get('impact', 'Not specified'),
            'target_numbers': 'Not specified',  # Could be extracted
            'previous_results': org_context.get('previous_impact', 'Not specified'),
            'community_impact': 'Not specified'  # Could be extracted
        }
        
        data = {**org_context, **project_context, **grant_context, **impact_data}
        
        prompt = self._build_narrative_prompt(self.IMPACT_NARRATIVE_TEMPLATE, data)
        return self._call_openai_api(prompt)
    
    def generate_activities_narrative(self, grant_name: str, grant_data: Dict[str, Any]) -> Optional[str]:
        """Generate complete activities narrative."""
        org_context = self._collect_organization_context(grant_data)
        project_context = self._collect_project_context(grant_data)
        grant_context = self._collect_grant_context(grant_name, grant_data)
        
        # Format activities list
        activities = grant_data.get('project', {}).get('activities', [])
        activities_list = self._format_list(activities)
        
        data = {
            **org_context,
            **project_context,
            **grant_context,
            'activities_list': activities_list
        }
        
        prompt = self._build_narrative_prompt(self.ACTIVITIES_NARRATIVE_TEMPLATE, data)
        return self._call_openai_api(prompt)
    
    def generate_budget_narrative(self, grant_name: str, grant_data: Dict[str, Any]) -> Optional[str]:
        """Generate complete budget narrative."""
        org_context = self._collect_organization_context(grant_data)
        project_context = self._collect_project_context(grant_data)
        grant_context = self._collect_grant_context(grant_name, grant_data)
        
        budget = grant_data.get('budget', {})
        budget_data = {
            'budget_line_items': self._format_budget_items(budget.get('line_items', [])),
            'budget_breakdown': self._format_budget_breakdown(budget.get('breakdown', {})),
            'in_kind_contributions': 'Not specified'  # Could be extracted
        }
        
        data = {**org_context, **project_context, **grant_context, **budget_data}
        
        prompt = self._build_narrative_prompt(self.BUDGET_NARRATIVE_TEMPLATE, data)
        return self._call_openai_api(prompt)
    
    def generate_technical_narrative(self, grant_name: str, grant_data: Dict[str, Any]) -> Optional[str]:
        """Generate complete technical narrative."""
        org_context = self._collect_organization_context(grant_data)
        project_context = self._collect_project_context(grant_data)
        grant_context = self._collect_grant_context(grant_name, grant_data)
        
        technical = grant_data.get('technical', {})
        technical_data = {
            'technical_specifications': technical.get('specifications', 'Not specified'),
            'equipment_list': self._format_list(technical.get('equipment', [])),
            'infrastructure_needs': technical.get('infrastructure', 'Not specified'),
            'technical_requirements': self._format_list(technical.get('requirements', [])),
            'integration_needs': 'Not specified',  # Could be extracted
            'equipment_needs': self._format_list(technical.get('equipment', []))
        }
        
        data = {**org_context, **project_context, **grant_context, **technical_data}
        
        prompt = self._build_narrative_prompt(self.TECHNICAL_NARRATIVE_TEMPLATE, data)
        return self._call_openai_api(prompt)
    
    def _format_budget_items(self, line_items: List[Dict[str, Any]]) -> str:
        """Format budget line items for template."""
        if not line_items:
            return "Not specified"
        formatted = []
        for item in line_items:
            item_name = item.get('item', 'Unknown')
            amount = item.get('amount', 0)
            formatted.append(f"- {item_name}: ${amount:,.2f}")
        return "\n".join(formatted)
    
    def _format_budget_breakdown(self, breakdown: Dict[str, float]) -> str:
        """Format budget breakdown for template."""
        if not breakdown:
            return "Not specified"
        formatted = []
        for category, amount in breakdown.items():
            formatted.append(f"- {category}: ${amount:,.2f}")
        return "\n".join(formatted)
    
    def generate_narrative(self, narrative_type: str, grant_name: str, grant_data: Dict[str, Any]) -> Optional[str]:
        """
        Generate narrative for a specific narrative type.
        
        Args:
            narrative_type: Type of narrative to generate (project_description, goals, impact, etc.)
            grant_name: Name of the grant
            grant_data: Extracted grant data
            
        Returns:
            Generated narrative or None if error
        """
        narrative_method_map = {
            'project_description': self.generate_project_description,
            'goals': self.generate_goals_narrative,
            'project_goals': self.generate_goals_narrative,
            'impact': self.generate_impact_narrative,
            'project_impact': self.generate_impact_narrative,
            'activities': self.generate_activities_narrative,
            'project_activities': self.generate_activities_narrative,
            'budget': self.generate_budget_narrative,
            'budget_breakdown': self.generate_budget_narrative,
            'technical': self.generate_technical_narrative,
            'technical_specifications': self.generate_technical_narrative,
        }
        
        method = narrative_method_map.get(narrative_type)
        if method:
            return method(grant_name, grant_data)
        else:
            logger.warning(f"No narrative generator for type: {narrative_type}")
            return None

