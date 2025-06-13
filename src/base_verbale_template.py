from docx import Document
from docx.shared import Pt, Inches
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date
import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from document_templates import DocumentTemplate

class BaseVerbaleTemplate(DocumentTemplate):
    """Base template semplificato per tutti i verbali di assemblea"""
    
    def _setup_document_styles(self, doc):
        """Configura gli stili base del documento"""
        styles = doc.styles
        
        # Stile per intestazione società
        try:
            if 'TitoloSocieta' not in [s.name for s in styles]:
                title_style = styles.add_style('TitoloSocieta', WD_STYLE_TYPE.PARAGRAPH)
            else:
                title_style = styles['TitoloSocieta']
            
            title_style.font.name = 'Times New Roman'
            title_style.font.size = Pt(14)
            title_style.font.bold = True
            title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            title_style.paragraph_format.space_after = Pt(6)
        except Exception as e:
            print(f"Warning: Could not create/configure TitoloSocieta style: {e}")
        
        # Stile per titolo verbale
        try:
            if 'TitoloVerbale' not in [s.name for s in styles]:
                verbale_title_style = styles.add_style('TitoloVerbale', WD_STYLE_TYPE.PARAGRAPH)
            else:
                verbale_title_style = styles['TitoloVerbale']
            
            verbale_title_style.font.name = 'Times New Roman'
            verbale_title_style.font.size = Pt(16)
            verbale_title_style.font.bold = True
            verbale_title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            verbale_title_style.paragraph_format.space_before = Pt(18)
            verbale_title_style.paragraph_format.space_after = Pt(18)
        except Exception as e:
            print(f"Warning: Could not create/configure TitoloVerbale style: {e}")
        
        # Stile per testo normale
        try:
            if 'BodyText' not in [s.name for s in styles]:
                body_style = styles.add_style('BodyText', WD_STYLE_TYPE.PARAGRAPH)
            else:
                body_style = styles['BodyText']
            
            body_style.font.name = 'Times New Roman'
            body_style.font.size = Pt(12)
            body_style.paragraph_format.space_after = Pt(6)
            body_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        except Exception as e:
            print(f"Warning: Could not create/configure BodyText style: {e}")

    def _add_company_header(self, doc, data):
        """Aggiunge l'intestazione della società"""
        try:
            p = doc.add_paragraph(style='TitoloSocieta')
        except KeyError:
            # Fallback: usa stile normale con formattazione diretta
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        run = p.add_run(data.get('denominazione', '[DENOMINAZIONE]'))
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        
        try:
            p = doc.add_paragraph(style='TitoloSocieta')
        except KeyError:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        run = p.add_run(f"Sede in {data.get('sede_legale', '[SEDE]')}")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        
        try:
            p = doc.add_paragraph(style='TitoloSocieta')
        except KeyError:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        run = p.add_run(f"Capitale sociale Euro {data.get('capitale_sociale', '[CAPITALE]')} i.v.")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        
        try:
            p = doc.add_paragraph(style='TitoloSocieta')
        except KeyError:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        run = p.add_run(f"Codice fiscale: {data.get('codice_fiscale', '[CF]')}")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)

    def _add_verbale_title(self, doc, data):
        """Aggiunge il titolo del verbale"""
        doc.add_paragraph()
        
        try:
            p = doc.add_paragraph(style='TitoloVerbale')
        except KeyError:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        run = p.add_run("Verbale di assemblea dei soci")
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(16)
        
        data_str = data.get('data_assemblea').strftime('%d/%m/%Y') if hasattr(data.get('data_assemblea'), 'strftime') else '[DATA]'
        
        try:
            p = doc.add_paragraph(style='TitoloVerbale')
        except KeyError:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        run = p.add_run(f"del {data_str}")
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(16)

    def _add_signatures(self, doc, data):
        """Aggiunge le firme"""
        doc.add_paragraph()
        doc.add_paragraph()
        
        # Presidente
        try:
            p = doc.add_paragraph(style='BodyText')
        except KeyError:
            p = doc.add_paragraph()
        
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = p.add_run("_____________________")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        try:
            p = doc.add_paragraph(style='BodyText')
        except KeyError:
            p = doc.add_paragraph()
        
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = p.add_run(data.get('presidente', '[PRESIDENTE]'))
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        try:
            p = doc.add_paragraph(style='BodyText')
        except KeyError:
            p = doc.add_paragraph()
        
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = p.add_run("Il Presidente")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        doc.add_paragraph()
        
        # Segretario
        try:
            p = doc.add_paragraph(style='BodyText')
        except KeyError:
            p = doc.add_paragraph()
        
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = p.add_run("_____________________")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        try:
            p = doc.add_paragraph(style='BodyText')
        except KeyError:
            p = doc.add_paragraph()
        
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = p.add_run(data.get('segretario', '[SEGRETARIO]'))
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        try:
            p = doc.add_paragraph(style='BodyText')
        except KeyError:
            p = doc.add_paragraph()
        
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = p.add_run("Il Segretario")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)

    def _setup_professional_document(self, data):
        """Configura un documento con formattazione professionale"""
        doc = Document()
        self._setup_document_styles(doc)
        return doc

    # Nuovo helper comune per i template che necessitano di tabelle formattate
    def _create_table_with_style(self, doc: Document, rows: int, cols: int, style_name: str = "Table Grid"):
        """Crea una tabella con il numero di righe/colonne indicato ed applica uno stile predefinito.

        Questo metodo centralizza la creazione delle tabelle per evitare duplicazioni nei singoli
        template e garantire una formattazione omogenea. Di default viene applicato lo stile
        "Table Grid" (bordo completo). Se lo stile richiesto non è presente, viene utilizzato lo
        stile di default della libreria python-docx senza generare eccezioni.
        """
        try:
            table = doc.add_table(rows=rows, cols=cols)
            if style_name and style_name in [s.name for s in doc.styles]:
                table.style = style_name
            elif "Table Grid" in [s.name for s in doc.styles]:
                table.style = "Table Grid"
            # In caso lo stile non esista semplicemente si procede senza impostarlo
        except Exception:
            # Fallback di emergenza: crea comunque la tabella senza stile specifico
            table = doc.add_table(rows=rows, cols=cols)
        return table
