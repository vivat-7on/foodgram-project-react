from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# Загрузка шрифта
pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))

# Создание объекта для добавления контента в PDF
styles = getSampleStyleSheet()
style_normal = styles['Normal']
style_normal.fontName = 'Arial'  # Используем шрифт Arial


def generate_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="file.pdf"'

    pdf = SimpleDocTemplate(response, pagesize=letter)

    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_heading = styles['Heading1']

    html_content = """
    <h1>Список покупок:</h1>
    <table width="100%" border="1" cellspacing="0" cellpadding="5">
        <tr>
            <th bgcolor="#f2f2f2">Ингредиент</th>
            <th bgcolor="#f2f2f2">Количество</th>
            <th bgcolor="#f2f2f2">Единицы измерения</th>
        </tr>
        <tr>
            <td>Молоко</td>
            <td>1</td>
            <td>литр</td>
        </tr>
        <tr>
            <td>Хлеб</td>
            <td>2</td>
            <td>буханки</td>
        </tr>
    </table>
    """

    paragraphs = [Paragraph(html_content, style_normal)]
    pdf.build(paragraphs)

    return response
