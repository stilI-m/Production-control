import os
from typing import List, Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_batches_pdf_report(data: List[Dict[str, Any]], output_path: str, title: str = "Отчет по производственным партиям") -> str:
    """
    Генерирует PDF-отчет из списка словарей с данными о партиях.
    Использует альбомную ориентацию (landscape A4) для широких таблиц.
    """
    # Если папки для файла нет - создаем её
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Настраиваем документ (альбомный А4, чтобы влезло много колонок)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(A4),
        rightMargin=30, leftMargin=30,
        topMargin=30, bottomMargin=30
    )

    elements: List = []
    styles = getSampleStyleSheet()

    # 1. Добавляем заголовок
    title_style = styles['Heading1']
    title_style.alignment = 1  # По центру
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 20))  # Отступ

    if not data:
        elements.append(Paragraph("Нет данных для отображения.", styles['Normal']))
        doc.build(elements)
        return output_path

    # 2. Подготавливаем данные для таблицы
    # Берем ключи первого словаря как заголовки
    headers = list(data[0].keys())
    table_data = [headers]

    # Добавляем строки
    for row_dict in data:
        # Преобразуем все значения в строки для корректного отображения
        row = [str(row_dict.get(h, "")) for h in headers]
        table_data.append(row)

    # 3. Рисуем и стилизуем таблицу
    # Вычисляем примерную ширину колонок (делим ширину страницы на количество колонок)
    page_width = landscape(A4)[0] - 60 # Минус поля
    col_width = page_width / len(headers)

    table = Table(table_data, colWidths=[col_width] * len(headers))

    # Задаем стиль: сетка, цвета, шрифты
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2c3e50")), # Темно-синяя шапка
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),           # Белый текст в шапке
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),                       # Текст по центру
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),             # Жирный шрифт для шапки
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#ecf0f1")),# Светлый фон для данных
        ('GRID', (0, 0), (-1, -1), 1, colors.black),                 # Черная сетка
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),                      # Выравнивание по вертикали
    ])
    table.setStyle(style)

    elements.append(table)

    # 4. Собираем PDF
    doc.build(elements)

    return output_path