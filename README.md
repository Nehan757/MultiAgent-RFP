# Multi-Agent AI Procurement Automation System

This project implements an AI-driven procurement automation system using LangChain, LangGraph, and OpenAI. The system consists of three specialized AI agents working together to process procurement requests, generate RFPs, and validate them before sending to suppliers.

## Features

- **Request Classification**: Automatically categorizes procurement requests into Software, Hardware, Services, or Raw Materials
- **RFP Generation**: Creates comprehensive Request for Proposal documents from user inputs
- **Approval Validation**: Validates RFPs for completeness, clarity, and compliance
- **Supplier Communication**: Sends approved RFPs to suppliers via email
- **User Interface**: Streamlit-based UI for submitting requests and tracking progress
- **Multi-agent Orchestration**: LangGraph workflow for coordinating the agents
- **Governance & Guardrails**: Built-in safeguards for budget limits and content validation

## System Architecture

### Workflow

1. User submits a procurement request through the UI
2. Classification Agent categorizes the request into one of four categories
3. RFP Generation Agent creates a detailed RFP document following category-specific templates
4. Approval Agent validates the RFP and checks for issues or anomalies
5. If approved, the RFP is sent to suppliers via email
6. User receives feedback throughout the process and can track status

### Components

- **Agents**: Three specialized AI agents handling different parts of the workflow
  - Classification Agent: Analyzes request details to determine the appropriate category
  - RFP Generation Agent: Extracts and structures information into standardized RFP documents
  - Approval Agent: Validates content and applies business rules before approval
- **LangGraph Workflow**: Orchestrates the agent interactions with conditional branching
- **Streamlit UI**: User-friendly interface for submitting and tracking requests
- **Email Service**: Handles supplier communications with PDF generation
- **Data Models**: Structured representation of requests and RFPs using Pydantic

## Setup Instructions

### Prerequisites

- Python 3.9+
- OpenAI API key
- SMTP email server (for sending RFPs)

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/Nehan757/MultiAgent-RFP.git
   cd MultiAgent-RFP
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
   MODEL_NAME=gpt-4  # Or another suitable model like gpt-3.5-turbo
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USERNAME=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   EMAIL_FROM=your_sender_email@domain.com
   ```

### Running the Application

To start the application:

```
python main.py
```

This will launch the Streamlit UI in your default web browser. Navigate to the displayed URL (typically http://localhost:8501).

For a quick test of your OpenAI API connectivity:

```
python test_openai.py
```

## API Documentation

The system uses internal APIs between components:

### Workflow API

- `execute(request: ProcurementRequest) -> Dict[str, Any]`: Process a procurement request through the entire workflow

### Agent APIs

- Classification Agent: `classify(request: ProcurementRequest) -> ClassificationResult`
- RFP Generation Agent: `generate_rfp(request: ProcurementRequest, classification: ClassificationResult) -> RFP`
- Approval Agent: `validate_rfp(rfp: RFP) -> ApprovalResult`
- Email Service: `send_rfp(rfp: RFP) -> bool`

## Project Structure

```
procurement-automation/
├── agents/                  # AI agent implementations
│   ├── __init__.py
│   ├── classification_agent.py
│   ├── rfp_generation_agent.py
│   └── approval_agent.py
├── api/                     # API implementations
│   ├── __init__.py
│   └── email_service.py
├── config/                  # Configuration settings
│   ├── __init__.py
│   └── settings.py
├── models/                  # Data models
│   ├── __init__.py
│   ├── request.py
│   └── rfp.py
├── tests/                   # Unit tests
│   └── __init__.py
├── ui/                      # Streamlit UI
│   ├── __init__.py
│   └── app.py
├── workflows/               # Workflow orchestration
│   ├── __init__.py
│   └── procurement_workflow.py
├── .env                     # Environment variables (create this)
├── .gitignore
├── LICENSE
├── README.md
├── main.py                  # Application entry point
├── requirements.txt
└── test_openai.py           # OpenAI API test script
```

## Assumptions and Trade-offs

- **OpenAI Dependency**: The system relies on OpenAI's API for AI capabilities
- **Email Configuration**: For full functionality, SMTP email credentials must be provided
- **No Persistent Storage**: Data is stored in-memory during the session
- **Limited Feedback Loop**: The feedback collection is implemented but not processed
- **Simplified Supplier Management**: Suppliers are managed on a per-request basis

## Scalability Strategy

### Agent Deployment

- Each agent is designed to be containerized using Docker
- Kubernetes can be used to manage agent instances
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

- Budget threshold limit for automatic approval ($1,000,000)
- Required sections in RFP documents (Overview, Requirements, Timeline, Budget)
- Validation checks for completeness and clarity
- Error handling throughout the workflow

### Governance Policies

- Audit logging of all agent actions and decisions
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
- **Persistent Storage**: Database integration for long-term data storage
- **Authentication System**: User login and role-based access control

## License

MIT
