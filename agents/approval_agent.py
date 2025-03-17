"""
Approval Agent - Responsible for validating RFPs before submission.
"""
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from typing import Dict, Any, List
from datetime import datetime
import re

from config.settings import OPENAI_API_KEY, MODEL_NAME, APPROVAL_SYSTEM_MESSAGE, MAX_BUDGET
from models.request import ProcurementRequest
from models.rfp import RFP, RFPStatus, ApprovalResult
from api.email_service import EmailService

class ApprovalAgent:
    """Agent for validating RFP documents before sending to suppliers."""
    
    def __init__(self):
        """Initialize the approval agent with the OpenAI model."""
        self.llm = ChatOpenAI(api_key=OPENAI_API_KEY, model=MODEL_NAME, temperature=0)
        self.parser = JsonOutputParser()
        self.email_service = EmailService()
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", APPROVAL_SYSTEM_MESSAGE),
            ("user", self._create_prompt_template())
        ])
        
        # Create the chain
        self.chain = self.prompt | self.llm | self.parser
    
    def _create_prompt_template(self) -> str:
        """Create the prompt template for RFP validation."""
        return """
        Please validate the following Request for Proposal (RFP) document:
        
        RFP TITLE: {title}
        RFP CATEGORY: {category}
        RFP CONTENT:
        {content}
        
        Check for the following aspects:
        1. Completeness: Does the RFP include all necessary sections?
        2. Clarity: Are the requirements clearly stated?
        3. Specificity: Are the specifications detailed enough for suppliers?
        4. Timeline: Is the timeline reasonable and clearly defined?
        5. Budget: Are budget expectations clear and reasonable?
        6. Compliance: Does the RFP comply with standard procurement practices?
        7. Anomalies: Are there any unusual requests or red flags?
        
        Provide your response in JSON format with the following fields:
        - approved: Boolean indicating whether the RFP is approved (true) or rejected (false)
        - feedback: Overall feedback on the RFP
        - issues: A list of specific issues that need to be addressed (if any)
        
        Note : Too restricitve guardrails may lead to rejection of valid RFPs. Please use your discretion. Dont be too restrictive. Allow majority of RFPs to pass through.
        
        JSON RESPONSE:
        """
    
    def _extract_budget(self, rfp_content: str) -> float:
        """
        Extract the budget amount from the RFP content.
        
        Args:
            rfp_content: The RFP content
            
        Returns:
            float: The extracted budget amount or 0 if not found
        """
        # Look for budget patterns like "$50,000" or "50,000 USD"
        budget_patterns = [
            r'\$\s*([\d,]+(?:\.\d+)?)',  # $50,000 or $ 50,000
            r'([\d,]+(?:\.\d+)?)\s*(?:USD|dollars)',  # 50,000 USD or 50,000 dollars
            r'budget.*?\$\s*([\d,]+(?:\.\d+)?)',  # Budget: $50,000
            r'budget.*?([\d,]+(?:\.\d+)?)\s*(?:USD|dollars)'  # Budget: 50,000 USD
        ]
        
        for pattern in budget_patterns:
            matches = re.findall(pattern, rfp_content, re.IGNORECASE)
            if matches:
                # Take the first match and remove commas
                budget_str = matches[0].replace(',', '')
                try:
                    return float(budget_str)
                except ValueError:
                    continue
        
        return 0.0
    
    def _apply_guardrails(self, rfp: RFP, approval_result: ApprovalResult) -> ApprovalResult:
        """
        Apply guardrails to the approval process.
        
        Args:
            rfp: The RFP to validate
            approval_result: The initial approval result
            
        Returns:
            ApprovalResult: The potentially modified approval result
        """
        issues = approval_result.issues.copy()
        
        # Check budget guardrail
        budget = self._extract_budget(rfp.content)
        if budget > MAX_BUDGET:
            approval_result.approved = False
            issues.append(f"Budget exceeds maximum allowed threshold of ${MAX_BUDGET:,.2f}")
        
        # Check for missing sections
        essential_sections = ["Overview", "Requirements", "Timeline", "Budget"]
        for section in essential_sections:
            if section.lower() not in rfp.content.lower():
                approval_result.approved = False
                issues.append(f"Missing essential section: {section}")
        
        # Apply any other business rules
        # ...
        
        # Update the issues list
        approval_result.issues = issues
        return approval_result
    
    async def validate_rfp(self, rfp: RFP) -> ApprovalResult:
        """
        Validate an RFP document using AI and guardrails.
        
        Args:
            rfp: The RFP to validate
            
        Returns:
            ApprovalResult: The result of the validation
        """
        try:
            print(f"Starting validation of RFP {rfp.id}...")
            
            # Create input data with flattened properties
            input_data = {
                "title": rfp.title,
                "category": rfp.category,
                "content": rfp.content
            }
            
            # Run the validation chain
            print("Invoking OpenAI for validation...")
            try:
                result = await self.chain.ainvoke(input_data)
                print(f"Validation result from OpenAI: {result}")
            except Exception as api_error:
                print(f"OpenAI API error: {str(api_error)}")
                import traceback
                traceback.print_exc()
                raise
            
            # Create the approval result
            approval_result = ApprovalResult(
                rfp_id=rfp.id,
                approved=result["approved"],
                feedback=result["feedback"],
                issues=result.get("issues", [])
            )
            
            # Apply guardrails
            print("Applying guardrails...")
            approval_result = self._apply_guardrails(rfp, approval_result)
            print(f"Final approval result after guardrails: {approval_result.approved}")
            
            # Update the RFP status based on the approval result
            if approval_result.approved:
                rfp.status = RFPStatus.APPROVED
                rfp.approval_date = datetime.now()
            else:
                rfp.status = RFPStatus.REJECTED
            
            rfp.approval_feedback = approval_result.feedback
            
            return approval_result
        except Exception as e:
            print(f"Error in validate_rfp: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    async def send_to_suppliers(self, rfp: RFP) -> bool:
        """
        Send the approved RFP to suppliers.
        
        Args:
            rfp: The approved RFP
            
        Returns:
            bool: Whether the email was sent successfully
        """
        if rfp.status != RFPStatus.APPROVED:
            return False
        
        success = await self.email_service.send_rfp(rfp)
        
        if success:
            rfp.status = RFPStatus.SENT
            rfp.sent_date = datetime.now()
        
        return success