"""
Classification Agent - Responsible for categorizing procurement requests.
"""
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from typing import Dict, Any
import uuid

from config.settings import OPENAI_API_KEY, MODEL_NAME, CLASSIFICATION_SYSTEM_MESSAGE, PROCUREMENT_CATEGORIES
from models.request import ProcurementRequest, ClassificationResult

class ClassificationAgent:
    """Agent for classifying procurement requests into categories."""
    
    def __init__(self):
        """Initialize the classification agent with the OpenAI model."""
        print("Initializing ClassificationAgent...")
        try:
            self.llm = ChatOpenAI(api_key=OPENAI_API_KEY, model=MODEL_NAME, temperature=0)
            print(f"Successfully created LLM using model: {MODEL_NAME}")
            self.parser = JsonOutputParser()
            
            # Create prompt template
            self.prompt = ChatPromptTemplate.from_messages([
                ("system", CLASSIFICATION_SYSTEM_MESSAGE),
                ("user", self._create_prompt_template())
            ])
            
            # Create the chain
            self.chain = self.prompt | self.llm | self.parser
            print("Classification agent initialized successfully")
        except Exception as e:
            print(f"Error initializing ClassificationAgent: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def _create_prompt_template(self) -> str:
        """Create the prompt template for classification."""
        categories_str = ", ".join(PROCUREMENT_CATEGORIES)
        return f"""
        Please analyze the following procurement request and classify it into one of these categories: {categories_str}.
        
        REQUEST TITLE: {{title}}
        REQUEST DESCRIPTION: {{description}}
        ADDITIONAL NOTES: {{additional_notes}}
        
        Provide your response in JSON format with the following fields:
        - category: The selected category
        - confidence: A numerical score between 0 and 1 indicating your confidence in the classification
        - reasoning: A brief explanation of why you selected this category
        
        Note : if the request does not fit any of the above categories, please assign a new categorty to the request based on the contents.
        
        JSON RESPONSE:
        """
    
    async def classify(self, request: ProcurementRequest) -> ClassificationResult:
        """
        Classify a procurement request into a specific category.
        
        Args:
            request: The procurement request to classify
            
        Returns:
            ClassificationResult: The classification result
        """
        try:
            print(f"Starting classification for request: {request.title}")
            
            # Ensure request has an ID
            if not request.id:
                request.id = str(uuid.uuid4())
                print(f"Generated new ID for request: {request.id}")
            
            # Create the input data for the template
            # Create the input data for the template
            input_data = {
                "title": request.title,
                "description": request.description,
                "additional_notes": request.additional_notes or "None"
}
            
            # Run the classification chain
            print("Invoking OpenAI API for classification...")
            try:
                result = await self.chain.ainvoke(input_data)
                print(f"Classification API result: {result}")
            except Exception as api_error:
                print(f"OpenAI API error: {str(api_error)}")
                import traceback
                traceback.print_exc()
                raise
            
            # Create and return the classification result
            classification = ClassificationResult(
                request_id=request.id,
                category=result["category"],
                confidence=result["confidence"],
                reasoning=result["reasoning"]
            )
            print(f"Created classification result: {classification.category}")
            return classification
        except Exception as e:
            print(f"Error in classification agent: {str(e)}")
            import traceback
            traceback.print_exc()
            raise