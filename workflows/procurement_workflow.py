"""
Procurement Workflow - Orchestrates the multi-agent procurement process using LangGraph.
"""
from typing import Dict, Any, List, Tuple, Union, TypedDict, Annotated
from enum import Enum
import uuid
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.graph import add_messages

from agents.classification_agent import ClassificationAgent
from agents.rfp_generation_agent import RFPGenerationAgent
from agents.approval_agent import ApprovalAgent
from models.request import ProcurementRequest, ClassificationResult
from models.rfp import RFP, RFPStatus, ApprovalResult, Supplier

# Define the state schema for the workflow
class WorkflowState(TypedDict):
    request: ProcurementRequest
    classification: Union[ClassificationResult, None]
    rfp: Union[RFP, None]
    approval: Union[ApprovalResult, None]
    email_sent: bool
    error: Union[str, None]
    status: str

# Define the node names for clarity
class Node(str, Enum):
    CLASSIFY = "classify"
    GENERATE_RFP = "generate_rfp"
    APPROVE_RFP = "approve_rfp"
    SEND_EMAIL = "send_email"
    ERROR_HANDLER = "error_handler"  # Changed from ERROR to ERROR_HANDLER

class ProcurementWorkflow:
    """Orchestrates the multi-agent procurement process."""
    
    def __init__(self):
        """Initialize the procurement workflow with all required agents."""
        self.classification_agent = ClassificationAgent()
        self.rfp_generation_agent = RFPGenerationAgent()
        self.approval_agent = ApprovalAgent()
        self.graph = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """
        Build the workflow graph for procurement.
        
        Returns:
            StateGraph: The workflow graph
        """
        # Create workflow graph
        graph = StateGraph(WorkflowState)
        
        # Add nodes for each step
        graph.add_node(Node.CLASSIFY, self._classify_request)
        graph.add_node(Node.GENERATE_RFP, self._generate_rfp)
        graph.add_node(Node.APPROVE_RFP, self._approve_rfp)
        graph.add_node(Node.SEND_EMAIL, self._send_email)
        graph.add_node(Node.ERROR_HANDLER, self._handle_error)  # Changed to ERROR_HANDLER
        
        # Define the edges
        # Start with classification
        graph.set_entry_point(Node.CLASSIFY)
        
        # After classification, generate RFP
        graph.add_edge(Node.CLASSIFY, Node.GENERATE_RFP)
        
        # After RFP generation, go to approval
        graph.add_edge(Node.GENERATE_RFP, Node.APPROVE_RFP)
        
        # From approval, either send email or end based on approval status
        graph.add_conditional_edges(
            Node.APPROVE_RFP,
            self._route_after_approval,
            {
                "approved": Node.SEND_EMAIL,
                "rejected": END
            }
        )
        
        # After sending email, end the workflow
        graph.add_edge(Node.SEND_EMAIL, END)
        
        # Error handling from any node to error node
        graph.add_edge(Node.ERROR_HANDLER, END)  # Changed to ERROR_HANDLER
        
        return graph
    
    async def _classify_request(self, state: WorkflowState) -> WorkflowState:
        """
        Classify the procurement request.
        
        Args:
            state: The current workflow state
            
        Returns:
            WorkflowState: The updated workflow state
        """
        try:
            print("Starting classification process...")
            
            # Get the request from the state
            request = state["request"]
            print(f"Request to classify: {request.title} - {request.description[:50]}...")
            
            # Classify the request
            try:
                print("Calling classification agent...")
                classification = await self.classification_agent.classify(request)
                print(f"Classification result: {classification.category} with confidence {classification.confidence}")
            except Exception as classification_error:
                print(f"Error during classification: {str(classification_error)}")
                import traceback
                traceback.print_exc()
                return {
                    **state,
                    "error": f"Classification error: {str(classification_error)}",
                    "status": "Error during classification"
                }
            
            # Verify classification is not None
            if classification is None:
                print("ERROR: Classification result is None")
                return {
                    **state,
                    "error": "Classification returned None",
                    "status": "Error: Classification failed"
                }
            
            # Update and return the state
            updated_state = {
                **state,
                "classification": classification,
                "status": f"Classified as {classification.category} with {classification.confidence:.2f} confidence"
            }
            print(f"Updated state after classification: classification is {'present' if updated_state.get('classification') is not None else 'None'}")
            return updated_state
        except Exception as e:
            print(f"Unexpected error in _classify_request: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                **state,
                "error": f"Classification error: {str(e)}",
                "status": "Error during classification"
            }
            
    async def _generate_rfp(self, state: WorkflowState) -> WorkflowState:
        """
        Generate an RFP based on the classified request.
        
        Args:
            state: The current workflow state
            
        Returns:
            WorkflowState: The updated workflow state
        """
        try:
            print("Starting RFP generation process...")
            
            # Get the request and classification from the state
            request = state["request"]
            classification = state["classification"]
            
            if classification is None:
                print("ERROR: Classification is None in _generate_rfp")
                return {
                    **state,
                    "error": "No classification result available",
                    "status": "Error: Classification failed"
                }
            
            print(f"Generating RFP for request: {request.title}, category: {classification.category}")
            
            # Generate the RFP
            try:
                rfp = await self.rfp_generation_agent.generate_rfp(request, classification)
                print(f"RFP generated successfully with ID: {rfp.id}")
            except Exception as generation_error:
                print(f"Error during RFP generation: {str(generation_error)}")
                import traceback
                traceback.print_exc()
                return {
                    **state,
                    "error": f"RFP generation error: {str(generation_error)}",
                    "status": "Error during RFP generation"
                }
            
            # Verify the RFP object is valid
            if rfp is None:
                print("ERROR: Generated RFP is None")
                return {
                    **state,
                    "error": "RFP generation returned None",
                    "status": "Error: RFP generation failed"
                }
            
            print(f"Generated RFP with title: {rfp.title}, status: {rfp.status}")
            
            # Update and return the state
            updated_state = {
                **state,
                "rfp": rfp,
                "status": f"RFP generated for {classification.category}"
            }
            print(f"Updated state after RFP generation: RFP is {'present' if updated_state.get('rfp') is not None else 'None'}")
            return updated_state
        except Exception as e:
            print(f"Unexpected error in _generate_rfp: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                **state,
                "error": f"RFP generation error: {str(e)}",
                "status": "Error during RFP generation"
            }
    
    async def _approve_rfp(self, state: WorkflowState) -> WorkflowState:
        try:
            print("Starting RFP approval process...")
            rfp = state["rfp"]
            
            if rfp is None:
                print("ERROR: RFP is None in _approve_rfp")
                return {
                    **state,
                    "error": "No RFP to validate",
                    "status": "Error: No RFP to validate"
                }
            
            print(f"Validating RFP with ID: {rfp.id}")
            # Validate the RFP
            try:
                approval = await self.approval_agent.validate_rfp(rfp)
                print(f"Approval result: {approval.approved}")
            except Exception as validation_error:
                print(f"Error during RFP validation: {str(validation_error)}")
                import traceback
                traceback.print_exc()
                raise validation_error
            
            # Update the status message
            status = "RFP approved" if approval.approved else f"RFP rejected: {approval.feedback}"
            
            # Update and return the state
            return {
                **state,
                "approval": approval,
                "status": status
            }
        except Exception as e:
            print(f"Error in _approve_rfp: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                **state,
                "error": f"Approval error: {str(e)}",
                "status": "Error during RFP approval"
            }
    
    def _route_after_approval(self, state: WorkflowState) -> str:
        """
        Determine the next step after approval.
        
        Args:
            state: The current workflow state
            
        Returns:
            str: The next node to execute
        """
        approval = state.get("approval")
        
        # Check if approval is None
        if approval is None:
            print("Warning: Approval is None in _route_after_approval")
            return "rejected"  # Default to rejected if approval is None
        
        return "approved" if approval.approved else "rejected"
    
    async def _send_email(self, state: WorkflowState) -> WorkflowState:
        """
        Send the approved RFP to suppliers.
        
        Args:
            state: The current workflow state
            
        Returns:
            WorkflowState: The updated workflow state
        """
        try:
            # Get the RFP from the state
            rfp = state["rfp"]
            
            # Check if suppliers exist
            if not rfp.suppliers:
                print("No suppliers specified for RFP. Email will not be sent.")
                return {
                    **state,
                    "email_sent": False,
                    "status": "No suppliers specified. RFP not sent."
                }
            
            # Send the RFP to suppliers
            success = await self.approval_agent.send_to_suppliers(rfp)
            
            # Update the status message
            status = "RFP sent to suppliers" if success else "Failed to send RFP to suppliers"
            
            # Update and return the state
            return {
                **state,
                "email_sent": success,
                "status": status
            }
        except Exception as e:
            print(f"Email sending error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                **state,
                "error": f"Email sending error: {str(e)}",
                "status": "Error during email sending",
                "email_sent": False
            }
    
    async def _handle_error(self, state: WorkflowState) -> WorkflowState:
        """
        Handle errors in the workflow.
        
        Args:
            state: The current workflow state
            
        Returns:
            WorkflowState: The updated workflow state
        """
        # Log the error
        error = state.get("error", "Unknown error")
        print(f"Workflow error: {error}")
        
        # Update and return the state
        return {
            **state,
            "status": f"Workflow failed: {error}"
        }
    
    async def execute(self, request: ProcurementRequest) -> Dict[str, Any]:
        print(f"==== Starting workflow execution for request: {request.title} ====")
        print(f"Workflow graph nodes: {[node.value for node in Node]}")
        # Initialize the workflow state
        initial_state: WorkflowState = {
            "request": request,
            "classification": None,
            "rfp": None,
            "approval": None,
            "email_sent": False,
            "error": None,
            "status": "Started procurement workflow"
        }
        
        # Execute the workflow
        try:
            # Create a new instance of the workflow
            print("Compiling workflow...")
            workflow = self.graph.compile()
            
            # Run the workflow and get the final state
            print("Invoking workflow...")
            final_state = await workflow.ainvoke(initial_state)
            print("Workflow completed successfully!")
            print(f"Final state status: {final_state.get('status')}")
            
            return final_state
        except Exception as e:
            import traceback
            print(f"Workflow exception: {str(e)}")
            traceback.print_exc()
            return {
                **initial_state,
                "error": f"Workflow execution error: {str(e)}",
                "status": "Workflow execution failed"
            }