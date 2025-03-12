"""
RFP Generation Agent - Responsible for creating RFP documents from request information.
"""
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from typing import Dict, Any
import uuid

from config.settings import OPENAI_API_KEY, MODEL_NAME, RFP_GENERATION_SYSTEM_MESSAGE, RFP_TEMPLATES
from models.request import ProcurementRequest, ClassificationResult
from models.rfp import RFP, RFPStatus

class RFPGenerationAgent:
    """Agent for generating RFP documents based on procurement requests."""
    
    def __init__(self):
        """Initialize the RFP generation agent with the OpenAI model."""
        self.llm = ChatOpenAI(api_key=OPENAI_API_KEY, model=MODEL_NAME, temperature=0.2)
        self.parser = JsonOutputParser()
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", RFP_GENERATION_SYSTEM_MESSAGE),
            ("user", self._create_prompt_template())
        ])
        
        # Create the chain
        self.chain = self.prompt | self.llm | self.parser
    
    def _create_prompt_template(self) -> str:
        """Create the prompt template for RFP generation."""
        return """
        Generate a Request for Proposal (RFP) based on the following procurement request information:
        
        REQUEST TITLE: {title}
        REQUEST DESCRIPTION: {description}
        ESTIMATED BUDGET: {budget}
        TIMELINE: {timeline}
        DEPARTMENT: {department}
        REQUESTER: {requester}
        REQUIRED BY DATE: {required_by_date}
        ADDITIONAL NOTES: {additional_notes}
        
        CATEGORY: {category}
        
        Based on this information, extract all relevant details and structure them into an RFP document.
        The RFP should follow the standard template for {category} categories.
        
        Provide your response in JSON format with the following fields:
        - project_overview: A brief overview of the procurement need
        - requirements: Detailed specifications or requirements
        - timeline: Expected timeline for delivery
        - budget: Budget constraints or expectations
        - evaluation_criteria: Criteria for evaluating proposals
        - submission_instructions: Instructions for suppliers to submit proposals
        - quantity: (if applicable) Quantity of items needed
        - warranty: (if applicable) Warranty requirements
        - sla: (if applicable) Service level requirements
        - quality: (if applicable) Quality standards
        
        JSON RESPONSE:
        """
    
    async def generate_rfp(self, request: ProcurementRequest, classification: ClassificationResult) -> RFP:
        """
        Generate an RFP document based on a classified procurement request.
        
        Args:
            request: The procurement request
            classification: The classification result
            
        Returns:
            RFP: The generated RFP document
        """
        try:
            # Create input data with flattened properties
            input_data = {
                "title": request.title,
                "description": request.description,
                "budget": request.estimated_budget or "Not specified",
                "timeline": request.timeline or "Not specified",
                "department": request.department or "Not specified",
                "requester": request.requester or "Not specified",
                "required_by_date": request.required_by_date or "Not specified",
                "additional_notes": request.additional_notes or "Not specified",
                "category": classification.category
            }
            
            # Run the RFP generation chain
            rfp_content_json = await self.chain.ainvoke(input_data)
            
            # Get the appropriate template for the category
            template = RFP_TEMPLATES.get(classification.category, RFP_TEMPLATES["Services"])
            
            # Format the template with the extracted information
            # Add empty string defaults for any missing keys
            for key in [
                "project_overview", "requirements", "timeline", "budget", 
                "evaluation_criteria", "submission_instructions", "quantity", 
                "warranty", "sla", "quality"
            ]:
                if key not in rfp_content_json:
                    rfp_content_json[key] = ""
            
            formatted_content = template.format(**rfp_content_json)
            
            # Create and return the RFP
            return RFP(
                id=str(uuid.uuid4()),
                request_id=request.id,
                title=f"RFP for {request.title}",
                category=classification.category,
                content=formatted_content,
                status=RFPStatus.PENDING_APPROVAL
            )
        except Exception as e:
            print(f"Error in generate_rfp: {str(e)}")
            import traceback
            traceback.print_exc()
            raise