from datetime import date
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

GENERATED_DIR = Path("generated")
GENERATED_DIR.mkdir(exist_ok=True)


def generate_certificate(recipient_name: str, event_name: str, certificate_title: str, output_path: Path) -> None:
    """Generate one certificate PDF using the single predefined layout."""
    c = canvas.Canvas(str(output_path), pagesize=A4)
    width, height = A4

    c.setLineWidth(2)
    c.rect(45, 45, width - 90, height - 90)

    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(width / 2, height - 145, certificate_title)

    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 205, "This certificate is proudly presented to")

    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(width / 2, height - 270, recipient_name)

    c.setFont("Helvetica", 15)
    c.drawCentredString(width / 2, height - 330, "for successfully participating in")

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 375, event_name)

    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, 105, f"Date: {date.today().strftime('%d %B %Y')}")
    c.drawCentredString(width / 2, 82, "Bulk Certificate Generator")

    c.save()
