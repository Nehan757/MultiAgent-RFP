"""
Email Service - Handles sending emails to suppliers
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import logging
from typing import List
import asyncio
from fpdf import FPDF
import io

from config.settings import EMAIL_HOST, EMAIL_PORT, EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_FROM
from models.rfp import RFP, Supplier

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails to suppliers."""
    
    def _generate_rfp_pdf(self, rfp):
        """
        Generate a PDF from RFP content.
        
        Args:
            rfp: The RFP to convert to PDF
            
        Returns:
            bytes: The generated PDF as bytes
        """
        # Create PDF object
        pdf = FPDF()
        pdf.add_page()
        
        # Add title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, rfp.title, 0, 1, "C")
        pdf.ln(5)
        
        # Add category
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Category: {rfp.category}", 0, 1)
        pdf.ln(5)
        
        # Add RFP content
        pdf.set_font("Arial", "", 11)
        
        # Split content by lines and add each line
        lines = rfp.content.split("\n")
        for line in lines:
            # Check if line is a heading (starts with #)
            if line.strip().startswith("#"):
                # Count the level of heading
                heading_level = len(line.split(" ")[0].strip("#"))
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
    
    async def send_rfp(self, rfp: RFP) -> bool:
        """
        Send the RFP to all specified suppliers.
        
        Args:
            rfp: The RFP to send
            
        Returns:
            bool: Whether all emails were sent successfully
        """
        if not rfp.suppliers:
            logger.warning(f"No suppliers specified for RFP {rfp.id}")
            return False
        
        success = True
        for supplier in rfp.suppliers:
            try:
                # Create the email message
                msg = self._create_email_message(rfp, supplier)
                
                # Send the email
                if await self._send_email(msg, supplier.email):
                    logger.info(f"Successfully sent RFP {rfp.id} to {supplier.email}")
                else:
                    logger.error(f"Failed to send RFP {rfp.id} to {supplier.email}")
                    success = False
            except Exception as e:
                logger.error(f"Error sending RFP to {supplier.email}: {str(e)}")
                success = False
        
        return success
    
    def _create_email_message(self, rfp: RFP, supplier: Supplier) -> MIMEMultipart:
        """
        Create an email message for a specific supplier.
        
        Args:
            rfp: The RFP to send
            supplier: The supplier to send to
            
        Returns:
            MIMEMultipart: The email message
        """
        # Create message container
        msg = MIMEMultipart()
        msg['Subject'] = f"Request for Proposal: {rfp.title}"
        msg['From'] = EMAIL_FROM
        msg['To'] = supplier.email
        
        # Create the body of the message
        text = f"""
        Dear {supplier.contact_person or supplier.name},
        
        Please find attached our Request for Proposal for {rfp.title}.
        
        We look forward to your submission.
        
        Best regards,
        Procurement Team
        """
        
        # Attach text part
        msg.attach(MIMEText(text, 'plain'))
        
        # Generate RFP PDF
        try:
            pdf_bytes = self._generate_rfp_pdf(rfp)
            
            # Attach PDF
            attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
            attachment.add_header('Content-Disposition', 'attachment', filename=f"RFP_{rfp.id}.pdf")
            msg.attach(attachment)
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            # If PDF generation fails, fall back to text attachment
            text_attachment = MIMEText(rfp.content)
            text_attachment.add_header('Content-Disposition', 'attachment', filename=f"RFP_{rfp.id}.txt")
            msg.attach(text_attachment)
        
        return msg
    
    async def _send_email(self, msg: MIMEMultipart, recipient: str) -> bool:
        """
        Send an email using SMTP.
        
        Args:
            msg: The email message
            recipient: The recipient email address
            
        Returns:
            bool: Whether the email was sent successfully
        """
        try:
            # Convert to async operation with executor
            return await asyncio.to_thread(self._send_email_sync, msg, recipient)
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {str(e)}")
            return False
    
    def _send_email_sync(self, msg: MIMEMultipart, recipient: str) -> bool:
        """
        Synchronous method to send an email via SMTP.
        """
        try:
            logger.info(f"Connecting to SMTP server {EMAIL_HOST}:{EMAIL_PORT}")
            # Connect to the server
            with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
                server.starttls()
                
                # Login if credentials are provided
                if EMAIL_USERNAME and EMAIL_PASSWORD:
                    logger.info(f"Logging in with username: {EMAIL_USERNAME}")
                    server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
                
                # Send the email
                logger.info(f"Sending email from {EMAIL_FROM} to {recipient}")
                server.sendmail(EMAIL_FROM, recipient, msg.as_string())
                logger.info(f"Email successfully sent to {recipient}")
            
            return True
        except Exception as e:
            logger.error(f"SMTP Error sending to {recipient}: {str(e)}")
            return False