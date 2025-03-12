# Multi-Agent AI Procurement Automation System

This project implements an AI-driven procurement automation system using LangChain, LangGraph, and OpenAI. The system consists of three specialized AI agents working together to process procurement requests, generate RFPs, and validate them before sending to suppliers.

## Features

- **Request Classification**: Automatically categorizes procurement requests into Software, Hardware, Services, or Raw Materials
- **RFP Generation**: Creates comprehensive Request for Proposal documents from user inputs
- **Approval Validation**: Validates RFPs for completeness, clarity, and compliance
- **Supplier Communication**: Sends approved RFPs to suppliers via email
- **User Interface**: Streamlit-based UI for submitting requests and tracking progress
- **Multi-agent Orchestration**: LangGraph workflow for coordinating the agents

## System Architecture

### Workflow

1. User submits a procurement request through the UI
2. Classification Agent categorizes the request
3. RFP Generation Agent creates a detailed RFP document
4. Approval Agent validates the RFP and checks for issues
5. If approved, the RFP is sent to suppliers
6. User receives feedback throughout the process

### Components

- **Agents**: Three specialized AI agents handling different parts of the workflow
- **LangGraph Workflow**: Orchestrates the agent interactions
- **Streamlit UI**: User interface for submitting and tracking requests
- **Email Service**: Handles supplier communications
- **Data Models**: Structured representation of requests and RFPs

## Setup Instructions

### Prerequisites

- Python 3.9+
- OpenAI API key

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/procurement-automation.git
   cd procurement-automation
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   MODEL_NAME=gpt-4  # Or another suitable model
   ```

### Running the Application

To start the application:

```
python main.py
```

This will launch the Streamlit UI in your default web browser. Navigate to the displayed URL (typically http://localhost:8501).

## API Documentation

The system does not expose external APIs in this implementation, but uses internal APIs between components:

### Workflow API

- `execute(request: ProcurementRequest) -> Dict[str, Any]`: Process a procurement request through the entire workflow

### Agent APIs

- Classification Agent: `classify(request: ProcurementRequest) -> ClassificationResult`
- RFP Generation Agent: `generate_rfp(request: ProcurementRequest, classification: ClassificationResult) -> RFP`
- Approval Agent: `validate_rfp(rfp: RFP) -> ApprovalResult`

## Assumptions and Trade-offs

- **OpenAI Dependency**: The system relies on OpenAI's API for AI capabilities
- **Simulated Email Service**: The email service is simulated for this prototype
- **Simplified Authentication**: No authentication system is implemented
- **No Persistent Storage**: Data is stored in-memory during the session
- **Limited Feedback Loop**: The feedback collection is implemented but not processed
- **Simplified Supplier Management**: Suppliers are hardcoded for demonstration purposes

## Scalability Strategy

### Agent Deployment

- Each agent would be containerized using Docker
- Kubernetes would be used to manage agent instances
- Horizontal Pod Autoscaler would adjust the number of agents based on load

### Orchestrator Scaling

- The LangGraph orchestrator would be deployed as a separate service
- Multiple instances would be managed by Kubernetes
- Inter-agent communication would use a message queue (e.g., RabbitMQ, Kafka)

### Database Integration

- A distributed database would store requests, RFPs, and results
- Redis could be used for caching frequently accessed data
- Database sharding for high-volume scenarios

## Governance and Guardrails

### Implemented Guardrails

- Budget threshold limit for automatic approval
- Required sections in RFP documents
- Validation checks for completeness and clarity

### Governance Policies

- Role-based access control (to be implemented)
- Audit logging of all agent actions
- Human-in-the-loop for high-value requests
- Anomaly detection in approval process

## Feedback Loop Implementation

- UI collects user feedback on agent decisions
- Feedback would be used to fine-tune agent prompts
- Performance metrics tracked for each agent
- Continuous improvement process based on feedback

## Future Enhancements

- **Supplier Database Integration**: Connect to real supplier database
- **Document Parsing**: Extract information from uploaded documents
- **Advanced Analytics**: Dashboard for procurement trends and insights
- **Multi-language Support**: Process requests in different languages
- **Custom RFP Templates**: Allow customization of RFP templates by category
- **Advanced Workflow Rules**: Complex approval hierarchies and conditions

## License

MIT