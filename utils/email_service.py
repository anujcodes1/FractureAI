"""
FractureAI Email Service
=========================
Sends PDF reports to patients via email using Flask-Mail.
"""

import os
from flask_mail import Mail, Message

# Mail instance (initialized in app.py)
mail = Mail()


def send_report_email(recipient_email, recipient_name, report_path, scan_summary):
    """
    Send the PDF report to the patient's email.

    Args:
        recipient_email: Patient's email address
        recipient_name: Patient's full name
        report_path: Path to the generated PDF report
        scan_summary: Brief summary text of the scan results

    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        msg = Message(
            subject="Your FractureAI X-Ray Analysis Report",
            recipients=[recipient_email],
        )

        # HTML email body
        msg.html = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto;
                    background: linear-gradient(135deg, #0f172a, #1e293b); color: #e2e8f0;
                    border-radius: 12px; overflow: hidden;">

            <!-- Header -->
            <div style="background: linear-gradient(135deg, #0ea5e9, #8b5cf6);
                        padding: 30px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px; color: white;">
                    🦴 FractureAI
                </h1>
                <p style="margin: 8px 0 0; color: rgba(255,255,255,0.85); font-size: 14px;">
                    AI-Powered Bone Fracture Detection
                </p>
            </div>

            <!-- Body -->
            <div style="padding: 30px;">
                <p style="font-size: 16px; color: #e2e8f0;">
                    Dear <strong>{recipient_name}</strong>,
                </p>
                <p style="color: #94a3b8; line-height: 1.6;">
                    Your X-ray analysis has been completed. Please find your detailed
                    medical report attached to this email.
                </p>

                <!-- Summary Card -->
                <div style="background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.3);
                            border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <h3 style="color: #38bdf8; margin: 0 0 10px;">📋 Scan Summary</h3>
                    <p style="color: #cbd5e1; margin: 0; line-height: 1.6;">
                        {scan_summary}
                    </p>
                </div>

                <p style="color: #94a3b8; font-size: 13px; line-height: 1.6;">
                    ⚠️ <em>This report is AI-generated and should not replace professional
                    medical advice. Please consult your doctor for a definitive diagnosis.</em>
                </p>
            </div>

            <!-- Footer -->
            <div style="background: rgba(0,0,0,0.3); padding: 20px; text-align: center;">
                <p style="color: #64748b; font-size: 12px; margin: 0;">
                    © 2026 FractureAI | Confidential Medical Report
                </p>
            </div>
        </div>
        """

        # Attach the PDF report
        if report_path and os.path.exists(report_path):
            with open(report_path, "rb") as f:
                msg.attach(
                    filename="FractureAI_Report.pdf",
                    content_type="application/pdf",
                    data=f.read()
                )

        mail.send(msg)
        return True

    except Exception as e:
        print(f"[FractureAI] ERROR: Email send failed: {e}")
        return False
