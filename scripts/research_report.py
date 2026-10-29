"""Build a shareable design research PDF and HTML from the versioned findings."""
from pathlib import Path
import json, html, shutil
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'docs/premium-research.json').read_text(encoding='utf-8'))
pdfmetrics.registerFont(TTFont('Research','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('ResearchBold','C:/Windows/Fonts/arialbd.ttf'))
body=ParagraphStyle('Body',fontName='Research',fontSize=10,leading=15,textColor=HexColor('#24374d'),spaceAfter=12)
heading=ParagraphStyle('Heading',fontName='ResearchBold',fontSize=21,leading=26,textColor=HexColor('#0758b9'),spaceAfter=20)
small=ParagraphStyle('Small',parent=body,fontSize=9,leading=13,textColor=HexColor('#566b87'))
source=ParagraphStyle('Source',parent=body,fontSize=9,leading=13,spaceAfter=13)
story=[]
parts=[]
for i,section in enumerate(data['sections']):
    if i:story.append(PageBreak())
    story.append(Paragraph(html.escape(section['title']),heading))
    if not i:
        story.append(Paragraph(html.escape(data['date']+' · '+data['scope']),small))
        story.append(Spacer(1,10))
    parts.append('<section><h2>'+html.escape(section['title'])+'</h2>')
    for text in section['paragraphs']:
        story.append(Paragraph(html.escape(text),body))
        parts.append('<p>'+html.escape(text)+'</p>')
    parts.append('</section>')
story.append(PageBreak());story.append(Paragraph('Источники',heading))
parts.append('<section><h2>Источники</h2>')
for num,title,url in data['sources']:
    item=f'[{num}] <a href="{html.escape(url,quote=True)}" color="#0758b9">{html.escape(title)}</a>'
    story.append(Paragraph(item,source))
    parts.append('<p>'+item+'</p>')
parts.append('</section>')
def page_footer(c,doc):
    c.saveState();c.setStrokeColor(HexColor('#dce4ec'));c.line(48,40,547,40)
    c.setFont('Research',8);c.setFillColor(HexColor('#566b87'))
    c.drawString(48,27,'Туррис · Исследование дизайна · 29.10.2026')
    c.drawRightString(547,27,str(doc.page));c.restoreState()
pdf=ROOT/'docs/Turris-premium-design-research.pdf'
SimpleDocTemplate(str(pdf),pagesize=(595,842),leftMargin=48,rightMargin=48,topMargin=48,bottomMargin=58,title=data['title'],author='Turris project').build(story,onFirstPage=page_footer,onLaterPages=page_footer)
style='body{max-width:900px;margin:50px auto;padding:0 24px;font:17px/1.75 Arial,sans-serif;color:#24374d}h1,h2{color:#0758b9;line-height:1.25}section{margin:50px 0}a{color:#0758b9}header{border-bottom:1px solid #ddd;padding-bottom:30px}@media print{section{break-before:page}body{font-size:11pt;margin:0}}'
report='<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>'+html.escape(data['title'])+'</title><style>'+style+'</style><body><header><h1>'+html.escape(data['title'])+'</h1><p>'+html.escape(data['date']+' · '+data['scope'])+'</p><a href="Turris-premium-design-research.pdf">Скачать PDF</a> · <a href="../">Открыть прототип</a></header>'+''.join(parts)+'</body></html>'
(ROOT/'docs/premium-design-research.html').write_text(report,encoding='utf-8')
deliver=ROOT.parent/'deliverables/premium-design';deliver.mkdir(exist_ok=True,parents=True)
shutil.copy2(pdf,deliver/pdf.name)
print('Research report:',pdf)
