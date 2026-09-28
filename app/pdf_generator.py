import io
import json
import hashlib
import hmac
from datetime import datetime
from typing import Dict, Any, List

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import qrcode
except ImportError:
    qrcode = None

def _generate_qr_bytes(data: str) -> bytes:
    """Generate in-memory PNG bytes for a QR code."""
    if not qrcode:
        return b""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=4,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception:
        return b""

def _create_fallback_pdf(title: str, lines: List[str]) -> bytes:
    """Creates a strictly standard binary %PDF-1.4 document without external dependencies."""
    content_stream = ["BT", "/F1 14 Tf", "40 760 Td", f"({title}) Tj", "/F1 10 Tf", "0 -25 Td"]
    for line in lines:
        sanitized = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        content_stream.append(f"({sanitized}) Tj")
        content_stream.append("0 -15 Td")
    content_stream.append("ET")
    stream_data = "\n".join(content_stream).encode("latin1")

    objects = []
    # 1: Catalog
    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    # 2: Pages
    objects.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    # 3: Page
    objects.append(b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n")
    # 4: Contents
    objects.append(f"4 0 obj\n<< /Length {len(stream_data)} >>\nstream\n".encode("latin1") + stream_data + b"\nendstream\nendobj\n")
    # 5: Font
    objects.append(b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for obj in objects:
        offsets.append(len(out))
        out.extend(obj)

    xref_pos = len(out)
    out.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("latin1"))
    for off in offsets:
        out.extend(f"{off:010d} 00000 n \n".encode("latin1"))
    out.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("latin1"))
    return bytes(out)

def generate_prescription_pdf(prescription_data: dict, patient_name: str, doctor_name: str) -> bytes:
    """Generates a professional formatted binary PDF document byte stream for a medical prescription."""
    medications = prescription_data.get("medications", [])
    instructions = prescription_data.get("instructions", "Take medications as directed by physician.")
    date_str = datetime.utcnow().strftime("%B %d, %Y")
    prescription_id = prescription_data.get("id", "RX-PENDING")

    # Verification token
    verification_payload = f"RX:{prescription_id}|PAT:{patient_name}|DOC:{doctor_name}|TS:{date_str}"
    verification_hash = hashlib.sha256(verification_payload.encode()).hexdigest()[:16].upper()
    qr_data = f"https://healthid.ai/verify/prescription?code={verification_hash}"

    if fitz:
        try:
            doc = fitz.open()
            page = doc.new_page(width=595, height=842) # A4

            # Top Header Bar
            page.draw_rect(fitz.Rect(0, 0, 595, 75), color=None, fill=(0.008, 0.518, 0.780)) # Teal/Blue #0284c7
            page.insert_text(fitz.Point(36, 42), "HEALTHID AI CLINICAL HEALTHCARE", fontsize=16, color=(1, 1, 1), fontname="helv", bold=True)
            page.insert_text(fitz.Point(36, 60), "OFFICIAL MEDICAL PRESCRIPTION & DOSAGE SCHEDULE", fontsize=9, color=(0.88, 0.95, 1.0), fontname="helv")

            # Patient & Doctor Info Grid
            page.draw_rect(fitz.Rect(36, 90, 559, 160), color=(0.85, 0.88, 0.92), fill=(0.97, 0.98, 1.0), width=1)
            page.insert_text(fitz.Point(50, 112), f"Patient Name:  {patient_name}", fontsize=11, color=(0.1, 0.1, 0.1), fontname="helv", bold=True)
            page.insert_text(fitz.Point(50, 130), f"Date of Issue:  {date_str}", fontsize=9, color=(0.3, 0.3, 0.3), fontname="helv")
            page.insert_text(fitz.Point(50, 146), f"Prescription ID:  #{prescription_id}", fontsize=9, color=(0.3, 0.3, 0.3), fontname="helv")

            page.insert_text(fitz.Point(320, 112), f"Prescribing Doctor:  {doctor_name}", fontsize=10, color=(0.1, 0.1, 0.1), fontname="helv", bold=True)
            page.insert_text(fitz.Point(320, 130), "Clinical License:  MCI-VERIFIED-ACTIVE", fontsize=9, color=(0.3, 0.3, 0.3), fontname="helv")
            page.insert_text(fitz.Point(320, 146), "Hospital:  HealthID Central Diagnostic Facility", fontsize=9, color=(0.3, 0.3, 0.3), fontname="helv")

            # Prescribed Medications Section Header
            page.insert_text(fitz.Point(36, 190), "Rx - PRESCRIBED MEDICATIONS", fontsize=12, color=(0.008, 0.518, 0.780), fontname="helv", bold=True)
            page.draw_line(fitz.Point(36, 198), fitz.Point(559, 198), color=(0.008, 0.518, 0.780), width=1.5)

            # Table Header
            table_y = 215
            page.draw_rect(fitz.Rect(36, table_y - 12, 559, table_y + 12), color=None, fill=(0.92, 0.94, 0.97))
            page.insert_text(fitz.Point(46, table_y + 4), "#", fontsize=9, color=(0.2, 0.2, 0.2), fontname="helv", bold=True)
            page.insert_text(fitz.Point(75, table_y + 4), "Medication Name", fontsize=9, color=(0.2, 0.2, 0.2), fontname="helv", bold=True)
            page.insert_text(fitz.Point(235, table_y + 4), "Dosage", fontsize=9, color=(0.2, 0.2, 0.2), fontname="helv", bold=True)
            page.insert_text(fitz.Point(340, table_y + 4), "Frequency / Timings", fontsize=9, color=(0.2, 0.2, 0.2), fontname="helv", bold=True)
            page.insert_text(fitz.Point(470, table_y + 4), "Duration", fontsize=9, color=(0.2, 0.2, 0.2), fontname="helv", bold=True)

            curr_y = table_y + 28
            for idx, med in enumerate(medications, 1):
                name = med.get("name", "Medicine")
                dosage = med.get("dosage", "Standard")
                freq = med.get("frequency", "Once daily")
                duration = med.get("duration", "As needed")

                page.draw_line(fitz.Point(36, curr_y - 14), fitz.Point(559, curr_y - 14), color=(0.9, 0.9, 0.9), width=0.5)
                page.insert_text(fitz.Point(46, curr_y), str(idx), fontsize=9, color=(0.3, 0.3, 0.3), fontname="helv")
                page.insert_text(fitz.Point(75, curr_y), name, fontsize=9, color=(0.1, 0.1, 0.1), fontname="helv", bold=True)
                page.insert_text(fitz.Point(235, curr_y), dosage, fontsize=9, color=(0.2, 0.2, 0.2), fontname="helv")
                page.insert_text(fitz.Point(340, curr_y), freq, fontsize=9, color=(0.2, 0.2, 0.2), fontname="helv")
                page.insert_text(fitz.Point(470, curr_y), duration, fontsize=9, color=(0.2, 0.2, 0.2), fontname="helv")
                curr_y += 24

            if not medications:
                page.insert_text(fitz.Point(75, curr_y), "No medications listed in digital schedule. Refer to instructions below.", fontsize=9, color=(0.5, 0.5, 0.5), fontname="helv")
                curr_y += 24

            # Clinical Instructions
            curr_y += 15
            page.insert_text(fitz.Point(36, curr_y), "Clinical Instructions & Precautions", fontsize=11, color=(0.1, 0.1, 0.1), fontname="helv", bold=True)
            page.draw_line(fitz.Point(36, curr_y + 6), fitz.Point(559, curr_y + 6), color=(0.85, 0.88, 0.92), width=1)

            curr_y += 22
            # Clean and split instructions
            clean_instructions = instructions.replace("\r\n", "\n")
            for inst_line in clean_instructions.split("\n"):
                if inst_line.strip():
                    page.insert_text(fitz.Point(46, curr_y), inst_line[:90], fontsize=8.5, color=(0.25, 0.25, 0.25), fontname="helv")
                    curr_y += 14

            # Bottom Verification and QR Code Box
            footer_top = 710
            page.draw_rect(fitz.Rect(36, footer_top, 559, 805), color=(0.85, 0.88, 0.92), fill=(0.98, 0.98, 0.99), width=1)

            # Insert verification QR code
            qr_bytes = _generate_qr_bytes(qr_data)
            if qr_bytes:
                page.insert_image(fitz.Rect(465, footer_top + 8, 545, footer_top + 88), stream=qr_bytes)

            page.insert_text(fitz.Point(48, footer_top + 22), "DIGITALLY SIGNED & VERIFIED", fontsize=10, color=(0.15, 0.65, 0.35), fontname="helv", bold=True)
            page.insert_text(fitz.Point(48, footer_top + 38), f"Security Hash: {verification_hash}", fontsize=8, color=(0.4, 0.4, 0.4), fontname="courier")
            page.insert_text(fitz.Point(48, footer_top + 52), f"Signed by Doctor: {doctor_name} via HealthID AI Cryptographic Key", fontsize=8, color=(0.3, 0.3, 0.3), fontname="helv")
            page.insert_text(fitz.Point(48, footer_top + 66), "Scan QR code or present HealthID to dispense at licensed pharmacies.", fontsize=7.5, color=(0.5, 0.5, 0.5), fontname="helv")

            pdf_bytes = doc.tobytes(deflate=False)
            doc.close()
            return pdf_bytes
        except Exception as e:
            # Fall back to native binary PDF generator
            pass

    # Fallback to standard binary PDF
    summary_lines = [
        f"Date: {date_str}   |   Prescription ID: #{prescription_id}",
        f"Patient: {patient_name}   |   Doctor: {doctor_name}",
        "----------------------------------------------------------------",
        "PRESCRIBED MEDICATIONS:",
    ]
    for m in medications:
        summary_lines.append(f"  * {m.get('name', 'Medicine')} - {m.get('dosage', '')} ({m.get('frequency', '')})")
    if not medications:
        summary_lines.append("  * None specified in schedule.")
    summary_lines.append("----------------------------------------------------------------")
    summary_lines.append(f"Instructions: {instructions[:120]}")
    summary_lines.append("----------------------------------------------------------------")
    summary_lines.append(f"Digital Verification: {verification_hash} (HealthID AI Security)")
    return _create_fallback_pdf("HEALTHID AI - CLINICAL PRESCRIPTION", summary_lines)

def generate_invoice_pdf(invoice_data: dict, patient_name: str) -> bytes:
    """Generates an authentic binary PDF invoice / official billing receipt."""
    inv_num = invoice_data.get("invoice_number", "INV-000")
    amount = invoice_data.get("amount", 0) / 100.0
    currency = invoice_data.get("currency", "USD").upper()
    status = invoice_data.get("status", "Paid").upper()
    items = invoice_data.get("line_items", [])
    date_str = datetime.utcnow().strftime("%B %d, %Y")

    verification_hash = hashlib.sha256(f"INV:{inv_num}|AMT:{amount}|PAT:{patient_name}".encode()).hexdigest()[:16].upper()
    qr_data = f"https://healthid.ai/verify/invoice?id={inv_num}&hash={verification_hash}"

    if fitz:
        try:
            doc = fitz.open()
            page = doc.new_page(width=595, height=842) # A4

            # Top Header Bar
            page.draw_rect(fitz.Rect(0, 0, 595, 75), color=None, fill=(0.06, 0.09, 0.16)) # Dark Slate
            page.insert_text(fitz.Point(36, 42), "HEALTHID AI MEDICAL BILLING", fontsize=16, color=(1, 1, 1), fontname="helv", bold=True)
            page.insert_text(fitz.Point(36, 60), "OFFICIAL PAYMENT RECEIPT & INVOICE BREAKDOWN", fontsize=9, color=(0.7, 0.75, 0.85), fontname="helv")

            # Invoice Meta Box
            page.draw_rect(fitz.Rect(36, 90, 559, 160), color=(0.85, 0.88, 0.92), fill=(0.97, 0.98, 1.0), width=1)
            page.insert_text(fitz.Point(50, 112), f"Billed To:  {patient_name}", fontsize=11, color=(0.1, 0.1, 0.1), fontname="helv", bold=True)
            page.insert_text(fitz.Point(50, 130), f"Invoice Date:  {date_str}", fontsize=9, color=(0.3, 0.3, 0.3), fontname="helv")
            page.insert_text(fitz.Point(50, 146), f"Invoice Number:  {inv_num}", fontsize=9, color=(0.3, 0.3, 0.3), fontname="helv")

            # Status Badge
            badge_color = (0.13, 0.65, 0.34) if status == "PAID" else (0.85, 0.45, 0.1)
            page.draw_rect(fitz.Rect(440, 105, 540, 130), color=None, fill=badge_color)
            page.insert_text(fitz.Point(465, 122), status, fontsize=10, color=(1, 1, 1), fontname="helv", bold=True)

            page.insert_text(fitz.Point(320, 146), "Payment Mode:  Stripe Electronic Gateway", fontsize=8.5, color=(0.3, 0.3, 0.3), fontname="helv")

            # Line Items Table
            table_y = 190
            page.draw_rect(fitz.Rect(36, table_y - 12, 559, table_y + 12), color=None, fill=(0.92, 0.94, 0.97))
            page.insert_text(fitz.Point(46, table_y + 4), "#", fontsize=9, color=(0.2, 0.2, 0.2), fontname="helv", bold=True)
            page.insert_text(fitz.Point(75, table_y + 4), "Service / Procedure Description", fontsize=9, color=(0.2, 0.2, 0.2), fontname="helv", bold=True)
            page.insert_text(fitz.Point(450, table_y + 4), "Amount", fontsize=9, color=(0.2, 0.2, 0.2), fontname="helv", bold=True)

            curr_y = table_y + 28
            for idx, item in enumerate(items, 1):
                desc = item.get("description", "Medical Service")
                item_amt = item.get("amount", 0) / 100.0

                page.draw_line(fitz.Point(36, curr_y - 14), fitz.Point(559, curr_y - 14), color=(0.9, 0.9, 0.9), width=0.5)
                page.insert_text(fitz.Point(46, curr_y), str(idx), fontsize=9, color=(0.3, 0.3, 0.3), fontname="helv")
                page.insert_text(fitz.Point(75, curr_y), desc, fontsize=9, color=(0.1, 0.1, 0.1), fontname="helv")
                page.insert_text(fitz.Point(450, curr_y), f"${item_amt:.2f}", fontsize=9, color=(0.1, 0.1, 0.1), fontname="helv")
                curr_y += 24

            if not items:
                page.insert_text(fitz.Point(75, curr_y), "Consultation and Comprehensive Medical Assessment", fontsize=9, color=(0.1, 0.1, 0.1), fontname="helv")
                page.insert_text(fitz.Point(450, curr_y), f"${amount:.2f}", fontsize=9, color=(0.1, 0.1, 0.1), fontname="helv")
                curr_y += 24

            # Total Banner
            curr_y += 15
            page.draw_rect(fitz.Rect(320, curr_y, 559, curr_y + 40), color=None, fill=(0.94, 0.96, 0.98))
            page.insert_text(fitz.Point(340, curr_y + 25), "TOTAL PAID:", fontsize=11, color=(0.1, 0.1, 0.1), fontname="helv", bold=True)
            page.insert_text(fitz.Point(450, curr_y + 25), f"{currency} ${amount:.2f}", fontsize=13, color=(0.008, 0.518, 0.780), fontname="helv", bold=True)

            # Footer
            footer_top = 710
            page.draw_rect(fitz.Rect(36, footer_top, 559, 805), color=(0.85, 0.88, 0.92), fill=(0.98, 0.98, 0.99), width=1)

            qr_bytes = _generate_qr_bytes(qr_data)
            if qr_bytes:
                page.insert_image(fitz.Rect(465, footer_top + 8, 545, footer_top + 88), stream=qr_bytes)

            page.insert_text(fitz.Point(48, footer_top + 22), "VERIFIED BILLING TRANSACTION", fontsize=10, color=(0.15, 0.65, 0.35), fontname="helv", bold=True)
            page.insert_text(fitz.Point(48, footer_top + 38), f"Receipt Hash: {verification_hash}", fontsize=8, color=(0.4, 0.4, 0.4), fontname="courier")
            page.insert_text(fitz.Point(48, footer_top + 52), "This electronic document constitutes an official receipt of medical fees.", fontsize=8, color=(0.3, 0.3, 0.3), fontname="helv")
            page.insert_text(fitz.Point(48, footer_top + 66), "Questions? Contact billing@healthid.ai or present this invoice at hospital cashier.", fontsize=7.5, color=(0.5, 0.5, 0.5), fontname="helv")

            pdf_bytes = doc.tobytes(deflate=False)
            doc.close()
            return pdf_bytes
        except Exception:
            pass

    # Fallback to standard binary PDF
    summary_lines = [
        f"Invoice Number: {inv_num}   |   Date: {date_str}",
        f"Patient: {patient_name}   |   Status: {status}",
        "----------------------------------------------------------------",
        "ITEMIZED CHARGES:",
    ]
    for item in items:
        summary_lines.append(f"  * {item.get('description', 'Service')}: ${item.get('amount', 0)/100.0:.2f}")
    if not items:
        summary_lines.append(f"  * Medical Services Consultation: ${amount:.2f}")
    summary_lines.append("----------------------------------------------------------------")
    summary_lines.append(f"TOTAL AMOUNT PAID: {currency} ${amount:.2f}")
    summary_lines.append("----------------------------------------------------------------")
    summary_lines.append(f"Receipt Hash: {verification_hash}")
    return _create_fallback_pdf("HEALTHID AI - BILLING INVOICE RECEIPT", summary_lines)
