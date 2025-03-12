"""
Streamlit UI for the Procurement Automation System
"""
import streamlit as st
import uuid
import json
import asyncio
from datetime import datetime, timedelta, time
from datetime import datetime as dt
import pandas as pd
import io
from fpdf import FPDF

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the necessary components
from models.request import ProcurementRequest
from models.rfp import RFP, RFPStatus, Supplier
from workflows.procurement_workflow import ProcurementWorkflow

# Function to generate PDF from RFP content
def generate_rfp_pdf(rfp):
    # Create PDF object
    pdf = FPDF()
    pdf.add_page()
    
    # Add title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, rfp.title, 0, 1, "C")
    pdf.ln(5)
    
    # Add RFP content
    pdf.set_font("Arial", "", 11)
    
    # Split content by lines and add each line
    lines = rfp.content.split("\n")
    for line in lines:
        # Check if line is a heading (starts with #)
        if line.strip().startswith("#"):
            # Count the level of heading
            heading_level = len(line.split(" ")[0])
            heading_text = " ".join(line.split(" ")[1:])
            
            if heading_level == 1:
                pdf.set_font("Arial", "B", 14)
            elif heading_level == 2:
                pdf.set_font("Arial", "B", 12)
            else:
                pdf.set_font("Arial", "B", 11)
                
            pdf.cell(0, 10, heading_text, 0, 1)
            pdf.set_font("Arial", "", 11)
        else:
            # Regular text
            if line.strip():  # Skip empty lines
                pdf.multi_cell(0, 5, line)
    
    # Return PDF as bytes
    return pdf.output(dest="S").encode("latin1")

# Initialize the procurement workflow
workflow = ProcurementWorkflow()

# Set page config
st.set_page_config(
    page_title="AI Procurement Automation",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

#st.session_state is a special feature in Streamlit that allows to persist data between reruns.

# I am intializing the  session state to store the requests, current request, workflow results, and form visibility
if 'requests' not in st.session_state:
    st.session_state.requests = []

if 'current_request' not in st.session_state:
    st.session_state.current_request = None

if 'workflow_result' not in st.session_state:
    st.session_state.workflow_result = None

if 'show_form' not in st.session_state:
    st.session_state.show_form = True

# Streamlit UI
st.title("AI-Driven Procurement Automation")
st.markdown("""
This system uses multi-agent AI to automate the procurement process:
1. **Classification** - Categorize your procurement request
2. **RFP Generation** - Create a detailed Request for Proposal
3. **Approval** - Validate the RFP for completeness and compliance
4. **Supplier Communication** - Send the approved RFP to suppliers
""")

# Sidebar for request history
with st.sidebar:
    st.header("Procurement Requests")
    
    if st.button("New Request"):
        st.session_state.current_request = None
        st.session_state.workflow_result = None
        st.session_state.show_form = True
    
    if st.session_state.requests:
        st.subheader("Recent Requests")
        for i, req in enumerate(st.session_state.requests):
            if st.button(f"{req.title} ({req.created_at.strftime('%Y-%m-%d')})", key=f"history_{i}"):
                st.session_state.current_request = req
                # Find the corresponding workflow result
                for result in st.session_state.get('workflow_results', []):
                    if result['request'].id == req.id:
                        st.session_state.workflow_result = result
                        break
                st.session_state.show_form = False
                st.rerun()

# Main content area
if st.session_state.show_form:
    # Request form
    st.header("Procurement Request Form")
    
    with st.form("procurement_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Request Title*", 
                                 placeholder="e.g., Office Laptops Procurement")
            
            department = st.text_input("Department", 
                                     placeholder="e.g., IT, Marketing, HR")
            
            requester = st.text_input("Requester Name", 
                                    placeholder="Your name")
        
        with col2:
            estimated_budget = st.number_input("Estimated Budget ($)", 
                                             min_value=0.0, 
                                             step=1000.0)
            
            timeline = st.text_input("Timeline", 
                                   placeholder="e.g., Needed within 3 months")
            
            required_by_date = st.date_input("Required By Date", 
                                           value=None)
        
        st.subheader("Request Details")
        description = st.text_area("Request Description*", 
                                height=150, 
                                placeholder="Provide a detailed description of what you need to procure...")
        
        additional_notes = st.text_area("Additional Notes", 
                                      height=100, 
                                      placeholder="Any additional information that might be helpful...")
        
        st.subheader("Supplier Information")
        supplier_name = st.text_input("Supplier Name*", 
                                      value="Sample Supplier Inc.",
                                      placeholder="Company name of the supplier")
        
        supplier_email = st.text_input("Supplier Email*", 
                                      placeholder="Email address to send the RFP to")
        
        supplier_contact = st.text_input("Contact Person", 
                                        placeholder="Name of the contact person at the supplier")
        
        submitted = st.form_submit_button("Submit Request")
        
        if submitted:
            if not title or not description or not supplier_name or not supplier_email:
                st.error("Please fill in all required fields marked with *")
            else:
                # Creating a new procurement request
                req_id = str(uuid.uuid4())
                
                # Converting the date to datetime if provided
                req_date = None
                if required_by_date:
                    req_date = datetime.combine(required_by_date, datetime.min.time())
                
                new_request = ProcurementRequest(
                    id=req_id,
                    title=title,
                    description=description,
                    estimated_budget=estimated_budget,
                    timeline=timeline,
                    department=department,
                    requester=requester,
                    required_by_date=req_date,
                    additional_notes=additional_notes
                )
                
                # Add to session state
                st.session_state.current_request = new_request
                st.session_state.requests.insert(0, new_request)  # Add  new request to start of list to show the most recent req first
                
                # Process with the workflow
                with st.spinner("Processing your request..."):
                    # Create a supplier with the provided information
                    supplier = Supplier(
                        name=supplier_name,
                        email=supplier_email,
                        contact_person=supplier_contact
                    )
                    
                    # Store supplier in session state to use later
                    st.session_state.current_supplier = supplier
                    
                    # Run the workflow
                    result = asyncio.run(workflow.execute(new_request))
                    
                    # Add supplier to the RFP if the RFP was generated
                    if result.get("rfp"):
                        result["rfp"].suppliers = [supplier]
                        
                        # If the RFP was approved, try to send the email
                        if result.get("approval") and result["approval"].approved:
                            try:
                                email_sent = asyncio.run(workflow.approval_agent.send_to_suppliers(result["rfp"]))
                                result["email_sent"] = email_sent
                                # Update the status message to reflect that email was sent
                                result["status"] = "RFP sent to suppliers" if email_sent else "Failed to send RFP to suppliers"
                            except Exception as e:
                                st.error(f"Error sending email: {str(e)}")
                                result["error"] = f"Email sending error: {str(e)}"
                                result["email_sent"] = False
                    
                    st.session_state.workflow_result = result
                    
                    # Store the workflow result
                    if 'workflow_results' not in st.session_state:
                        st.session_state.workflow_results = []
                    st.session_state.workflow_results.append(result)
                
                # Switch to results view
                st.session_state.show_form = False
                st.rerun()

else:
    # Results view
    if st.session_state.current_request and st.session_state.workflow_result:
        request = st.session_state.current_request
        result = st.session_state.workflow_result
        
        # Display the current status
        st.info(f"Status: {result['status']}")
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs(["Request", "Classification", "RFP", "Approval"])
        
        with tab1:
            st.header("Procurement Request")
            st.markdown(f"**Title:** {request.title}")
            st.markdown(f"**Department:** {request.department or 'Not specified'}")
            st.markdown(f"**Requester:** {request.requester or 'Not specified'}")
            st.markdown(f"**Budget:** ${request.estimated_budget or 0:,.2f}")
            st.markdown(f"**Timeline:** {request.timeline or 'Not specified'}")
            
            if request.required_by_date:
                st.markdown(f"**Required By:** {request.required_by_date.strftime('%Y-%m-%d')}")
            
            st.subheader("Description")
            st.write(request.description)
            
            if request.additional_notes:
                st.subheader("Additional Notes")
                st.write(request.additional_notes)
            
            # Display supplier information
            if hasattr(st.session_state, 'current_supplier'):
                supplier = st.session_state.current_supplier
                st.subheader("Supplier Information")
                st.markdown(f"**Name:** {supplier.name}")
                st.markdown(f"**Email:** {supplier.email}")
                if supplier.contact_person:
                    st.markdown(f"**Contact Person:** {supplier.contact_person}")
        
        with tab2:
            st.header("Classification Results")
            
            if result.get("classification"):
                classification = result["classification"]
                
                # Create a gauge chart for confidence
                confidence = classification.confidence
                
                # Display classification results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"### Category: **{classification.category}**")
                    st.markdown(f"Confidence: {confidence:.2f}")
                    
                    # Simple confidence meter
                    st.progress(confidence)
                
                with col2:
                    st.markdown("### Reasoning")
                    st.write(classification.reasoning)
            else:
                st.warning("Classification has not been completed yet.")
        
        with tab3:
            st.header("Generated RFP")
            
            if result.get("rfp"):
                rfp = result["rfp"]
                
                st.markdown(f"**Title:** {rfp.title}")
                st.markdown(f"**Category:** {rfp.category}")
                st.markdown(f"**Status:** {rfp.status}")
                
                st.subheader("RFP Content")
                st.markdown(rfp.content)
                
                # Generate and download PDF
                if st.button("Generate PDF"):
                    try:
                        pdf_bytes = generate_rfp_pdf(rfp)
                        st.success("PDF generated successfully!")
                        
                        # Add download button for PDF
                        st.download_button(
                            label="Download RFP PDF",
                            data=pdf_bytes,
                            file_name=f"RFP_{rfp.id}.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")
            else:
                st.warning("RFP has not been generated yet.")
        
        with tab4:
            st.header("Approval Process")
            
            if result.get("approval"):
                approval = result["approval"]
                
                if approval.approved:
                    st.success("RFP has been approved!")
                else:
                    st.error("RFP has been rejected.")
                
                st.subheader("Feedback")
                st.write(approval.feedback)
                
                if approval.issues:
                    st.subheader("Issues to Address")
                    for issue in approval.issues:
                        st.warning(issue)
                
                # Email status
                if result.get("email_sent"):
                    st.success("RFP has been sent to suppliers.")
                    
                    # Display supplier list
                    if result.get("rfp") and result["rfp"].suppliers:
                        suppliers_data = []
                        for supplier in result["rfp"].suppliers:
                            suppliers_data.append({
                                "Supplier": supplier.name,
                                "Email": supplier.email,
                                "Status": "Sent"
                            })
                        
                        st.subheader("Supplier Communication")
                        st.table(pd.DataFrame(suppliers_data))
                else:
                    st.warning("RFP has not been sent to suppliers yet.")
            else:
                st.warning("Approval process has not been completed yet.")
        
        # Feedback section
        st.header("Feedback")
        feedback = st.text_area("Provide feedback on this procurement process", key="feedback")
        if st.button("Submit Feedback"):
            st.success("Thank you for your feedback! It will help improve the system.")
    else:
        st.warning("No request data available. Please submit a new request.")

# Footer
st.markdown("---")
st.caption("AI-Driven Procurement Automation System | Built with LangChain, LangGraph, and OpenAI")