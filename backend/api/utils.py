from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))

styles = getSampleStyleSheet()
style_normal = styles['Normal']
style_normal.fontName = 'Arial'


def generate_pdf(request, html_content):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="file.pdf"'

    pdf = SimpleDocTemplate(response, pagesize=letter)

    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_heading = styles['Heading1']

    paragraphs = [Paragraph(html_content, style_normal)]
    pdf.build(paragraphs)

    return response
