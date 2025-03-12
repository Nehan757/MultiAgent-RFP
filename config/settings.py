import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4")



# Email Service Configuration
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")  # Your email username
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")  # Your email password or app password
EMAIL_FROM = os.getenv("EMAIL_FROM", "procurement@company.com")  # The "from" address

# Procurement Categories
PROCUREMENT_CATEGORIES = ["Software", "Hardware", "Services", "Raw Materials"]

# RFP Templates based on category
RFP_TEMPLATES = {
    "Software": """
# REQUEST FOR PROPOSAL: SOFTWARE PROCUREMENT
## Project Overview
{project_overview}

## Requirements
{requirements}

## Timeline
{timeline}

## Budget
{budget}

## Evaluation Criteria
{evaluation_criteria}

## Submission Instructions
{submission_instructions}
    """,
    
    "Hardware": """
# REQUEST FOR PROPOSAL: HARDWARE PROCUREMENT
## Project Overview
{project_overview}

## Technical Specifications
{requirements}

## Quantity
{quantity}

## Delivery Timeline
{timeline}

## Budget
{budget}

## Warranty Requirements
{warranty}

## Submission Instructions
{submission_instructions}
    """,
    
    "Services": """
# REQUEST FOR PROPOSAL: SERVICES PROCUREMENT
## Service Overview
{project_overview}

## Scope of Work
{requirements}

## Service Level Requirements
{sla}

## Timeline
{timeline}

## Budget
{budget}

## Evaluation Criteria
{evaluation_criteria}

## Submission Instructions
{submission_instructions}
    """,
    
    "Raw Materials": """
# REQUEST FOR PROPOSAL: RAW MATERIALS PROCUREMENT
## Material Overview
{project_overview}

## Material Specifications
{requirements}

## Quantity
{quantity}

## Quality Standards
{quality}

## Delivery Timeline
{timeline}

## Budget
{budget}

## Submission Instructions
{submission_instructions}
    """
}

# System messages for agents
CLASSIFICATION_SYSTEM_MESSAGE = """
You are an AI procurement classification agent. Your job is to classify procurement requests 
into one of the following categories: Software, Hardware, Services, or Raw Materials.
Analyze the request details and determine the most appropriate category.
"""

RFP_GENERATION_SYSTEM_MESSAGE = """
You are an AI RFP generation agent. Your job is to extract relevant details from a 
procurement request and generate a comprehensive Request for Proposal (RFP) document.
The RFP should include all necessary sections such as overview, requirements, timeline, 
budget, and evaluation criteria.
"""

APPROVAL_SYSTEM_MESSAGE = """
You are an AI approval agent for procurement requests. Your job is to validate RFP documents
before they are sent to suppliers. Check for completeness, clarity, compliance with standards,
and any potential issues or anomalies. Provide clear feedback if revisions are needed.
"""

# Guardrails
MAX_BUDGET = 1000000  # $1M budget cap for automatic approval
MIN_TIMELINE_DAYS = 7  # Minimum timeline of 7 days