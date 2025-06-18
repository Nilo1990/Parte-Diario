from io import BytesIO
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.units import inch
from xhtml2pdf import pisa

def export_to_pdf(template_src, context_dict={}):
    """
    Función genérica para exportar HTML a PDF usando xhtml2pdf
    """
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte.pdf"'
    
    html = template_src.render(context_dict)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error al generar PDF', status=500)
    return response

def generate_pdf_report(title, headers, data, summary=None):
    """
    Función para generar PDF directamente con ReportLab
    """
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_{title.lower()}.pdf"'
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Title', fontSize=16, alignment=1, spaceAfter=20))
    styles.add(ParagraphStyle(name='Header', fontSize=12, alignment=1, textColor=colors.white, backColor=colors.HexColor('#3a7bd5')))
    styles.add(ParagraphStyle(name='Body', fontSize=10))
    
    elements = []
    
    # Título del reporte
    elements.append(Paragraph(title, styles['Title']))
    
    # Tabla de datos
    table_data = [headers]
    for row in data:
        table_data.append(row)
    
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3a7bd5')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.lightgrey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Resumen si existe
    if summary:
        elements.append(Paragraph("Resumen", styles['Heading2']))
        summary_data = []
        for key, value in summary.items():
            summary_data.append([key, str(value)])
        
        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f5f5f5')),
            ('GRID', (0,0), (-1,-1), 1, colors.lightgrey),
        ]))
        elements.append(summary_table)
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response