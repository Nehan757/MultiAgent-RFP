"""
Main entry point for the Procurement Automation System
"""
import os
import subprocess
import sys
import logging
from dotenv import load_dotenv

# Configures logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Load environment variables
load_dotenv()

def main():
    """Run the procurement automation system."""
    try:
        # Check for required environment variables
        if not os.getenv("OPENAI_API_KEY"):
            logging.error("OPENAI_API_KEY environment variable is not set. Please set it in a .env file.")
            sys.exit(1)
        
        # Launching the Streamlit UI
        logging.info("Starting Procurement Automation System...")
        
        # Command to run the Streamlit app, now we can just python main.py to run the streamlit app
        cmd = ["streamlit", "run", "ui/app.py"]
        
        # Run the command
        subprocess.run(cmd)
    
    except Exception as e:
        logging.error(f"Error starting the application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()