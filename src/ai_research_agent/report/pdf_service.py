from html import escape
import re

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


class PDFService:
    """Convert report Markdown into a readable PDF document."""

    @staticmethod
    def _inline_markup(text: str) -> str:
        """Escape text and translate a safe subset of inline Markdown."""
        text = escape(text, quote=True)
        text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
        text = re.sub(r"(?<!\*)\*([^*]+)\*", r"<i>\1</i>", text)
        text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
        text = re.sub(
            r"\[([^\]]+)\]\((https?://[^)]+)\)",
            r"<link href='\2' color='blue'>\1</link>",
            text,
        )
        return text

    def generate_pdf(self, markdown_text: str, output_path: str):
        """Render Markdown headings, lists, links, and paragraphs to PDF."""
        doc = SimpleDocTemplate(output_path)
        styles = getSampleStyleSheet()
        styles["Heading1"].alignment = TA_CENTER
        elements = []

        for raw_line in markdown_text.splitlines():
            line = raw_line.strip()
            if not line:
                elements.append(Spacer(1, 8))
                continue

            if line.startswith("### "):
                style, text = styles["Heading3"], line[4:]
            elif line.startswith("## "):
                style, text = styles["Heading2"], line[3:]
            elif line.startswith("# "):
                style, text = styles["Heading1"], line[2:]
            elif line.startswith(("- ", "* ")):
                style, text = styles["Bullet"], "• " + line[2:]
            elif re.match(r"^\d+\.\s", line):
                style, text = styles["BodyText"], line
            else:
                style, text = styles["BodyText"], line

            elements.append(Paragraph(self._inline_markup(text), style))

        doc.build(elements)
