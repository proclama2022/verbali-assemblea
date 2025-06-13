"""
Template per Verbale di Assemblea Irregolare dei Soci
Questo template è specifico per verbali di assemblee irregolari per mancanza del numero legale.
"""

import sys
import os

# Aggiungi il path della cartella src (relativo alla root del progetto)
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(os.path.dirname(current_dir), 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from document_templates import DocumentTemplate, DocumentTemplateFactory
from common_data_handler import CommonDataHandler
from base_verbale_template import BaseVerbaleTemplate
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from datetime import date
import streamlit as st
import pandas as pd
import re

class VerbaleAssembleaIrregolareTemplate(BaseVerbaleTemplate):
    """Template per Verbale di Assemblea Irregolare dei Soci"""
    
    def get_template_name(self) -> str:
        return "Verbale Assemblea Irregolare"
    
    def get_required_fields(self) -> list:
        return [
            "denominazione", "sede_legale", "capitale_sociale", "codice_fiscale",
            "data_assemblea", "ora_assemblea", "presidente", "segretario", 
            "soci", "amministratori", "ordine_giorno"
        ]
    
    def get_form_fields(self, extracted_data: dict) -> dict:
        """Genera i campi del form per Streamlit utilizzando il CommonDataHandler"""
        form_data = {}
        
        # Utilizza il CommonDataHandler per i dati standard
        # Dati azienda standardizzati
        form_data.update(CommonDataHandler.extract_and_populate_company_data(extracted_data))
        
        # Dati assemblea standardizzati
        form_data.update(CommonDataHandler.extract_and_populate_assembly_data(extracted_data))
        
        # Configurazioni specifiche per assemblea irregolare
        st.subheader("📋 Configurazioni Specifiche Assemblea Irregolare")
        
        col1, col2 = st.columns(2)
        with col1:
            form_data["ruolo_presidente"] = st.selectbox("Ruolo del presidente", 
                                                        CommonDataHandler.get_standard_ruoli_presidente())
            form_data["percentuale_presente"] = st.text_input("Percentuale capitale presente (%)", "40")
        with col2:
            form_data["motivo_irregolarita"] = st.selectbox("Motivo irregolarità", 
                ["Mancanza numero legale", "Assenza totale soci", "Quorum non raggiunto"])
            form_data["percentuale_necessaria"] = st.text_input("Percentuale necessaria per il quorum (%)", "50")
        
        # Partecipanti standardizzati usando il CommonDataHandler
        participants_data = CommonDataHandler.extract_and_populate_participants_data(
            extracted_data, 
            unique_key_suffix="irregolare"
        )
        form_data.update(participants_data)
        
        # Ordine del giorno
        st.subheader("📋 Ordine del Giorno")
        odg_input = st.text_area("Punti all'ordine del giorno (uno per riga)", 
                                 value=extracted_data.get("ordine_giorno", "Approvazione bilancio\nDestinazione utili"),
                                 height=100)
        form_data["ordine_giorno"] = [punto.strip() for punto in odg_input.split('\n') if punto.strip()]
        
        return form_data
    
    def show_preview(self, form_data: dict):
        """Mostra un'anteprima del documento che verrà generato"""
        st.subheader("📄 Anteprima Documento")
        
        preview_text = self._generate_preview_text(form_data)
        st.text_area("", value=preview_text, height=600, disabled=True)
    
    def _generate_preview_text(self, data: dict) -> str:
        """Genera il testo di anteprima del documento"""
        lines = []
        
        # Header
        denominazione = data.get('denominazione', '[DENOMINAZIONE]')
        sede = data.get('sede_legale', '[SEDE]')
        
        # Gestione capitale sociale con tre campi
        capitale_deliberato = str(data.get('capitale_deliberato', '10.000,00')).strip()
        capitale_versato = str(data.get('capitale_versato', '10.000,00')).strip()
        capitale_sottoscritto = str(data.get('capitale_sottoscritto', '10.000,00')).strip()
        
        # Gestione "i.v." (interamente versato) - solo se versato = deliberato
        if capitale_versato == capitale_deliberato:
            capitale_text = f"Capitale sociale Euro {capitale_deliberato} i.v."
        else:
            capitale_text = f"Capitale sociale Euro deliberato: {capitale_deliberato}, sottoscritto: {capitale_sottoscritto}, versato: {capitale_versato}"
        
        cf = data.get('codice_fiscale', '[CF]')
        
        lines.extend([
            f"{denominazione}",
            f"Sede in {sede}",
            capitale_text,
            f"Codice fiscale: {cf}",
            "",
            "Verbale di assemblea dei soci",
            f"del {data.get('data_assemblea', date.today()).strftime('%d/%m/%Y')}",
            "",
        ])
        
        # Apertura assemblea
        ora_inizio = data.get('ora_inizio', '09:00')
        luogo = data.get('luogo_assemblea', sede)
        lines.extend([
            f"Oggi {data.get('data_assemblea', date.today()).strftime('%d/%m/%Y')} alle ore {ora_inizio} presso {luogo}, si è tenuta l'assemblea generale dei soci, per discutere e deliberare sul seguente:",
            "",
            "Ordine del giorno"
        ])
        
        # Ordine del giorno
        for punto in data.get('ordine_giorno', []):
            lines.append(f"[{punto}]")
        
        lines.append("")
        
        # Presidente
        presidente = data.get('presidente', '[PRESIDENTE]')
        ruolo = data.get('ruolo_presidente', 'Amministratore Unico')
        
        lines.extend([
            f"Assume la presidenza ai sensi dell'art. [...] dello statuto sociale il Sig. {presidente} {ruolo}", 
            # Aggiungi il testo condizionale per AU
            f"{'[oppure Presidente del Consiglio di Amministrazione o altro (come da statuto)]' if ruolo == 'Amministratore Unico' else ''}, il quale dichiara e constata:",
            "",
            "1 - che (come indicato anche nell'avviso di convocazione ed in conformità alle previsioni dell'art. [...] dello statuto sociale) l'intervento all'assemblea può avvenire anche in audioconferenza" if data.get('audioconferenza') else "1 - che l'assemblea è regolarmente convocata",
            "",
            "2 - che sono presenti/partecipano all'assemblea:",
            f"     l'{ruolo} nella persona del suddetto Presidente Sig. {presidente}",
            ""
        ])
        
        # Amministratori
        amministratori_presenti = [a for a in data.get('amministratori', []) if a.get('presente', True) and a.get('nome', '').strip()]
        if len(amministratori_presenti) > 1:
            lines.append("per il Consiglio di Amministrazione:")
            for amm in amministratori_presenti:
                if amm.get('nome') != presidente:  # Non ripetere il presidente
                    lines.append(f"il Sig {amm.get('nome', '')}")
        
        # Collegio sindacale
        if data.get('collegio_sindacale'):
            lines.extend([
                "per il Collegio Sindacale",
                "il Dott. [NOME_SINDACO_1]",
                "il Dott. [NOME_SINDACO_2]",
                "il Dott. [NOME_SINDACO_3]"
            ])
        
        # Revisore
        if data.get('revisore'):
            nome_revisore = data.get('nome_revisore', '[NOME_REVISORE]')
            lines.append(f"il revisore contabile Dott. {nome_revisore}")
        
        lines.append("")
        
        # Calcola soci presenti e totali
        soci_presenti = []
        totale_quote_euro = 0
        totale_quote_perc = 0
        
        for socio in data.get('soci', []):
            if socio.get('nome', '').strip() and socio.get('presente', True):
                nome = socio.get('nome', '')
                quota_perc_str = str(socio.get('quota_percentuale', '0')).replace('%', '').replace(',', '.').strip()
                quota_euro_str = str(socio.get('quota_euro', '0')).replace('€', '').replace('Euro', '').strip()
                tipo_partecipazione = socio.get('tipo_partecipazione', 'Diretto')
                delegato = socio.get('delegato', '').strip()
                tipo_soggetto = socio.get('tipo_soggetto', 'Persona Fisica')
                rappresentante_legale = socio.get('rappresentante_legale', '').strip()
                
                # Calcola i totali
                try:
                    if quota_euro_str:
                        if ',' in quota_euro_str:
                            quota_clean = quota_euro_str.replace('.', '').replace(',', '.')
                        else:
                            quota_clean = quota_euro_str.replace('.', '')
                        totale_quote_euro += float(quota_clean)
                except:
                    pass
                
                try:
                    if quota_perc_str:
                        totale_quote_perc += float(quota_perc_str)
                except:
                    pass
                
                soci_presenti.append({
                    'nome': nome,
                    'quota_euro': socio.get('quota_euro', '0'),
                    'quota_percentuale': socio.get('quota_percentuale', '0%'),
                    'tipo_partecipazione': tipo_partecipazione,
                    'delegato': delegato,
                    'tipo_soggetto': tipo_soggetto,
                    'rappresentante_legale': rappresentante_legale
                })
        
        # Gestione soci presenti
        if soci_presenti:
            # Se ci sono soci presenti, usa la percentuale calcolata
            # Formatta i totali per la visualizzazione
            formatted_total_quota_euro = f"{totale_quote_euro:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') # Formato italiano
            formatted_total_quota_percentuale = f"{totale_quote_perc:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') # Formato italiano

            lines.append(f"nonché i seguenti soci o loro rappresentanti, recanti complessivamente una quota pari a nominali euro {formatted_total_quota_euro} pari al {formatted_total_quota_percentuale}% del Capitale Sociale:")
            
            for socio_info in soci_presenti:
                nome = socio_info['nome']
                quota_euro = socio_info['quota_euro']
                quota_perc = socio_info['quota_percentuale']
                tipo = socio_info['tipo_partecipazione']
                delegato = socio_info['delegato']
                tipo_soggetto = socio_info['tipo_soggetto']
                rappresentante_legale = socio_info['rappresentante_legale']
                
                if tipo == 'Delegato' and delegato:
                    if tipo_soggetto == 'Società':
                        if rappresentante_legale:
                            lines.append(f"il Sig {delegato} delegato del socio {nome} (società - legale rappresentante: {rappresentante_legale}) recante una quota pari a nominali euro {quota_euro} pari al {quota_perc} del Capitale Sociale")
                        else:
                            lines.append(f"il Sig {delegato} delegato del socio {nome} (società) recante una quota pari a nominali euro {quota_euro} pari al {quota_perc} del Capitale Sociale")
                    else:
                        lines.append(f"il Sig {delegato} delegato del socio Sig {nome} recante una quota pari a nominali euro {quota_euro} pari al {quota_perc} del Capitale Sociale")
                else:
                    if tipo_soggetto == 'Società':
                        if rappresentante_legale:
                            lines.append(f"il Sig {nome} socio (società - legale rappresentante: {rappresentante_legale}) recante una quota pari a nominali euro {quota_euro} pari al {quota_perc} del Capitale Sociale")
                        else:
                            lines.append(f"il Sig {nome} socio (società) recante una quota pari a nominali euro {quota_euro} pari al {quota_perc} del Capitale Sociale")
                    else:
                        lines.append(f"il Sig {nome} socio recante una quota pari a nominali euro {quota_euro} pari al {quota_perc} del Capitale Sociale")
            
            # Calcolo e visualizzazione quote totali soci
            total_quota_euro = 0.0
            total_quota_percentuale = 0.0

            for socio in soci_presenti:
                try:
                    quota_euro_str = str(socio.get('quota_euro', '0')).replace('.', '').replace(',', '.')
                    total_quota_euro += float(quota_euro_str)
                except (ValueError, TypeError):
                    pass # Ignora valori non numerici

                try:
                    quota_percentuale_str = str(socio.get('quota_percentuale', '0')).replace(',', '.')
                    total_quota_percentuale += float(quota_percentuale_str)
                except (ValueError, TypeError):
                    pass # Ignora valori non numerici

            # Formattazione per l'output italiano
            formatted_total_quota_euro = f"{total_quota_euro:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            formatted_total_quota_percentuale = f"{total_quota_percentuale:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            lines.append(f"- Soci presenti: {len(soci_presenti)} per un totale di Euro {formatted_total_quota_euro} ({formatted_total_quota_percentuale}% del capitale sociale)")
            lines.append("")
            lines.append("3 - che gli intervenuti sono legittimati alla presente assemblea;")
            lines.append("4 - che tutti gli intervenuti si dichiarano edotti sugli argomenti posti all'ordine del giorno.")
        else:
            # Assemblea deserta - nessun socio presente
            lines.append("3 - che all'assemblea non risultano presenti o rappresentati soci;")
            lines.append("4 - che pertanto l'assemblea non può considerarsi validamente costituita.")
        
        lines.append("")
        
        # Altri presenti (solo se ci sono soci)
        if soci_presenti and (data.get('collegio_sindacale') or data.get('revisore')):
            counter = 5 if soci_presenti else 5
            lines.append(f"{counter} - che sono altresì presenti, in qualità di:")
            if data.get('collegio_sindacale'):
                lines.append("il Sig. [NOME_SINDACO]")
            if data.get('revisore'):
                lines.append(f"il Sig. {data.get('nome_revisore', '[NOME_REVISORE]')}")
            lines.append("")
        
        # Segretario (solo se ci sono soci presenti)
        if soci_presenti:
            segretario = data.get('segretario', '[SEGRETARIO]')
            lines.extend([
                f"I presenti all'unanimità chiamano a fungere da segretario il signor {segretario}, che accetta l'incarico.",
                "",
                "Il Presidente identifica tutti i partecipanti e si accerta che ai soggetti collegati mediante mezzi di telecomunicazione sia consentito seguire la discussione, trasmettere e ricevere documenti, intervenire in tempo reale, con conferma da parte di ciascun partecipante." if data.get('audioconferenza') else "Il Presidente identifica tutti i partecipanti.",
                ""
            ])
        
        # Constatazione irregolarità
        if soci_presenti:
            percentuale_effettiva = totale_quote_perc if totale_quote_perc > 0 else float(data.get('percentuale_presente', '0'))
            lines.extend([
                f"Il Presidente constata e fa constatare che l'assemblea risulta regolarmente convocata ma che sono presenti soci rappresentanti soltanto il {percentuale_effettiva:.1f}% del capitale sociale; dichiara pertanto che l'Assemblea deve considerarsi irregolarmente costituita per mancanza del numero legale.",
                "",
                "Viene quindi redatto il presente verbale e dopo averne data lettura, il Presidente constata che l'assemblea all'unanimità, con voto palese, ne approva il testo.",
            ])
        else:
            lines.extend([
                "Il Presidente constata e fa constatare che l'assemblea risulta regolarmente convocata ma che non sono presenti soci; dichiara pertanto che l'Assemblea deve considerarsi deserta per mancanza totale di partecipazione.",
                "",
                "Viene quindi redatto il presente verbale di assemblea deserta.",
            ])
        
        lines.append("")
        lines.append(f"L'assemblea viene sciolta alle ore {data.get('ora_fine', '09:30')}.")
        
        return '\n'.join(lines)
    
    def generate_document(self, data: dict) -> Document:
        """Genera il documento Word"""
        doc = Document()
        self._setup_document_styles(doc)
        self._add_company_header(doc, data)
        self._add_verbale_title(doc, data)
        self._add_opening_section(doc, data)
        self._add_participants_section(doc, data)
        self._add_preliminary_statements(doc, data)
        self._add_irregularity_section(doc, data)
        self._add_closing_section(doc, data)
        self._add_signatures(doc, data)
        
        return doc
    
    def _setup_document_styles(self, doc):
        """Configura gli stili del documento"""
        # First call parent's method to setup all base styles
        super()._setup_document_styles(doc)
        
        # Imposta font di default
        style = doc.styles['Normal']
        style.font.name = 'Times New Roman'
        style.font.size = Pt(12)
    
    def _add_company_header(self, doc, data):
        """Aggiunge l'intestazione della società"""
        denominazione = data.get('denominazione', '[DENOMINAZIONE]')
        sede = data.get('sede_legale', '[SEDE]')
        
        # Gestione capitale sociale con tre campi
        capitale_deliberato = str(data.get('capitale_deliberato', '10.000,00')).strip()
        capitale_versato = str(data.get('capitale_versato', '10.000,00')).strip()
        capitale_sottoscritto = str(data.get('capitale_sottoscritto', '10.000,00')).strip()
        
        # Gestione "i.v." (interamente versato) - solo se versato = deliberato
        if capitale_versato == capitale_deliberato:
            capitale_text = f"Capitale sociale Euro {capitale_deliberato} i.v."
        else:
            capitale_text = f"Capitale sociale Euro deliberato: {capitale_deliberato}, sottoscritto: {capitale_sottoscritto}, versato: {capitale_versato}"
        
        cf = data.get('codice_fiscale', '[CF]')
        
        # Denominazione centrata e in grassetto
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(denominazione)
        run.font.bold = True
        run.font.size = Pt(14)
        
        # Sede
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"Sede in {sede}")
        run.font.size = Pt(12)
        
        # Capitale sociale
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(capitale_text)
        run.font.size = Pt(12)
        
        # Codice fiscale
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"Codice fiscale: {cf}")
        run.font.size = Pt(12)
        
        doc.add_paragraph()
    
    def _add_verbale_title(self, doc, data):
        """Aggiunge il titolo del verbale"""
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run("Verbale di assemblea dei soci")
        run.font.bold = True
        run.font.size = Pt(14)
        
        data_assemblea = data.get('data_assemblea', date.today())
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"del {data_assemblea.strftime('%d/%m/%Y')}")
        run.font.bold = True
        run.font.size = Pt(14)
        
        doc.add_paragraph()
    
    def _add_opening_section(self, doc, data):
        """Aggiunge la sezione di apertura"""
        data_assemblea = data.get('data_assemblea', date.today())
        ora_inizio = data.get('ora_inizio', '09:00')
        luogo = data.get('luogo_assemblea', data.get('sede_legale', '[SEDE]'))
        
        text = f"Oggi {data_assemblea.strftime('%d/%m/%Y')} alle ore {ora_inizio} presso {luogo}, si è tenuta l'assemblea generale dei soci, per discutere e deliberare sul seguente:"
        doc.add_paragraph(text)
        
        # Ordine del giorno
        p = doc.add_paragraph("Ordine del giorno")
        run = p.runs[0]
        run.font.bold = True
        
        for punto in data.get('ordine_giorno', []):
            doc.add_paragraph(f"[{punto}]")
        
        doc.add_paragraph()
    
    def _add_participants_section(self, doc, data):
        """Aggiunge la sezione dei partecipanti"""
        presidente = data.get('presidente', '[PRESIDENTE]')
        ruolo = data.get('ruolo_presidente', 'Amministratore Unico')
        
        text = f"Assume la presidenza ai sensi dell'art. [...] dello statuto sociale il Sig. {presidente} {ruolo}"
        if ruolo == "Amministratore Unico":
            text += " [oppure Presidente del Consiglio di Amministrazione o altro (come da statuto)]"
        text += ", il quale dichiara e constata:"
        
        doc.add_paragraph(text)
        doc.add_paragraph()
        
        # Dichiarazioni
        dichiarazioni = []
        if data.get('audioconferenza'):
            dichiarazioni.append("che (come indicato anche nell'avviso di convocazione ed in conformità alle previsioni dell'art. [...] dello statuto sociale) l'intervento all'assemblea può avvenire anche in audioconferenza")
        else:
            dichiarazioni.append("che l'assemblea è regolarmente convocata secondo le modalità statutarie")
        
        dichiarazioni.append("che sono presenti/partecipano all'assemblea:")
        
        for i, dich in enumerate(dichiarazioni, 1):
            doc.add_paragraph(f"{i} - {dich}")
        
        # Lista partecipanti
        doc.add_paragraph(f"     l'{ruolo} nella persona del suddetto Presidente Sig. {presidente}")
        
        # Amministratori
        amministratori_presenti = [a for a in data.get('amministratori', []) if a.get('presente', True) and a.get('nome', '').strip()]
        if len(amministratori_presenti) > 1:
            doc.add_paragraph()
            doc.add_paragraph("per il Consiglio di Amministrazione:")
            for amm in amministratori_presenti:
                if amm.get('nome') != presidente:  # Non ripetere il presidente
                    doc.add_paragraph(f"il Sig {amm.get('nome', '')}")
        
        # Collegio sindacale
        if data.get('collegio_sindacale'):
            doc.add_paragraph()
            doc.add_paragraph("per il Collegio Sindacale")
            doc.add_paragraph("il Dott. [NOME_SINDACO_1]")
            doc.add_paragraph("il Dott. [NOME_SINDACO_2]")
            doc.add_paragraph("il Dott. [NOME_SINDACO_3]")
        
        # Revisore
        if data.get('revisore'):
            doc.add_paragraph()
            nome_revisore = data.get('nome_revisore', '[NOME_REVISORE]')
            doc.add_paragraph(f"il revisore contabile Dott. {nome_revisore}")
        
        doc.add_paragraph()
    
    def _add_preliminary_statements(self, doc, data):
        """Aggiunge le constatazioni preliminari"""
        # Calcola soci presenti e totali
        soci_presenti = []
        totale_quote_euro = 0
        totale_quote_perc = 0
        
        for socio in data.get('soci', []):
            if socio.get('nome', '').strip() and socio.get('presente', True):
                nome = socio.get('nome', '')
                quota_perc_str = socio.get('quota_percentuale', '0').replace('%', '').replace(',', '.').strip()
                quota_euro_str = socio.get('quota_euro', '0').replace('€', '').replace('Euro', '').strip()
                tipo_partecipazione = socio.get('tipo_partecipazione', 'Diretto')
                delegato = socio.get('delegato', '').strip()
                tipo_soggetto = socio.get('tipo_soggetto', 'Persona Fisica')
                rappresentante_legale = socio.get('rappresentante_legale', '').strip()
                
                # Calcola i totali
                try:
                    if quota_euro_str:
                        if ',' in quota_euro_str:
                            quota_clean = quota_euro_str.replace('.', '').replace(',', '.')
                        else:
                            quota_clean = quota_euro_str.replace('.', '')
                        totale_quote_euro += float(quota_clean)
                except:
                    pass
                
                try:
                    if quota_perc_str:
                        totale_quote_perc += float(quota_perc_str)
                except:
                    pass
                
                soci_presenti.append({
                    'nome': nome,
                    'quota_euro': socio.get('quota_euro', '0'),
                    'quota_percentuale': socio.get('quota_percentuale', '0%'),
                    'tipo_partecipazione': tipo_partecipazione,
                    'delegato': delegato,
                    'tipo_soggetto': tipo_soggetto,
                    'rappresentante_legale': rappresentante_legale
                })
        
        # Gestione soci presenti
        if soci_presenti:
            # Se ci sono soci presenti, usa la percentuale calcolata
            percentuale_effettiva = totale_quote_perc if totale_quote_perc > 0 else float(data.get('percentuale_presente', '0'))
            doc.add_paragraph(f"nonché i seguenti soci o loro rappresentanti, recanti complessivamente una quota pari a nominali euro {totale_quote_euro:,.2f} pari al {percentuale_effettiva:.1f}% del Capitale Sociale:")
            
            for socio_info in soci_presenti:
                nome = socio_info['nome']
                quota_euro = socio_info['quota_euro']
                quota_perc = socio_info['quota_percentuale']
                tipo = socio_info['tipo_partecipazione']
                delegato = socio_info['delegato']
                tipo_soggetto = socio_info['tipo_soggetto']
                rappresentante_legale = socio_info['rappresentante_legale']
                
                if tipo == 'Delegato' and delegato:
                    if tipo_soggetto == 'Società':
                        if rappresentante_legale:
                            text = f"il Sig {delegato} delegato del socio {nome} (società - legale rappresentante: {rappresentante_legale}) recante una quota pari a nominali euro {quota_euro} pari al {quota_perc} del Capitale Sociale"
                        else:
                            text = f"il Sig {delegato} delegato del socio {nome} (società) recante una quota pari a nominali euro {quota_euro} pari al {quota_perc} del Capitale Sociale"
                    else:
                        text = f"il Sig {delegato} delegato del socio Sig {nome} recante una quota pari a nominali euro {quota_euro} pari al {quota_perc} del Capitale Sociale"
                else:
                    if tipo_soggetto == 'Società':
                        if rappresentante_legale:
                            text = f"il Sig {nome} socio (società - legale rappresentante: {rappresentante_legale}) recante una quota pari a nominali euro {quota_euro} pari al {quota_perc} del Capitale Sociale"
                        else:
                            text = f"il Sig {nome} socio (società) recante una quota pari a nominali euro {quota_euro} pari al {quota_perc} del Capitale Sociale"
                    else:
                        text = f"il Sig {nome} socio recante una quota pari a nominali euro {quota_euro} pari al {quota_perc} del Capitale Sociale"
                
                doc.add_paragraph(text)
            
            doc.add_paragraph("3 - che gli intervenuti sono legittimati alla presente assemblea;")
            doc.add_paragraph("4 - che tutti gli intervenuti si dichiarano edotti sugli argomenti posti all'ordine del giorno.")
        else:
            # Assemblea deserta - nessun socio presente
            doc.add_paragraph("3 - che all'assemblea non risultano presenti o rappresentati soci;")
            doc.add_paragraph("4 - che pertanto l'assemblea non può considerarsi validamente costituita.")
        
        # Altri presenti (solo se ci sono soci)
        if soci_presenti and (data.get('collegio_sindacale') or data.get('revisore')):
            doc.add_paragraph("5 - che sono altresì presenti, in qualità di:")
            if data.get('collegio_sindacale'):
                doc.add_paragraph("il Sig. [NOME_SINDACO]")
            if data.get('revisore'):
                doc.add_paragraph(f"il Sig. {data.get('nome_revisore', '[NOME_REVISORE]')}")
        
        # Nomina segretario (solo se ci sono soci presenti)
        if soci_presenti:
            segretario = data.get('segretario', '[SEGRETARIO]')
            doc.add_paragraph(f"I presenti all'unanimità chiamano a fungere da segretario il signor {segretario}, che accetta l'incarico.")
            
            # Identificazione partecipanti
            if data.get('audioconferenza'):
                text = "Il Presidente identifica tutti i partecipanti e si accerta che ai soggetti collegati mediante mezzi di telecomunicazione sia consentito seguire la discussione, trasmettere e ricevere documenti, intervenire in tempo reale, con conferma da parte di ciascun partecipante."
            else:
                text = "Il Presidente identifica tutti i partecipanti."
            
            doc.add_paragraph(text)
        
        doc.add_paragraph()
    
    def _add_irregularity_section(self, doc, data):
        """Aggiunge la sezione di constatazione dell'irregolarità"""
        # Verifica se ci sono soci presenti
        soci_presenti = [s for s in data.get('soci', []) if s.get('nome', '').strip() and s.get('presente', True)]
        
        if soci_presenti:
            # Calcola la percentuale effettiva
            totale_quote_perc = 0
            for socio in soci_presenti:
                try:
                    quota_perc_str = socio.get('quota_percentuale', '0').replace('%', '').replace(',', '.').strip()
                    if quota_perc_str:
                        totale_quote_perc += float(quota_perc_str)
                except:
                    pass
            
            percentuale_effettiva = totale_quote_perc if totale_quote_perc > 0 else float(data.get('percentuale_presente', '0'))
            convocazione = "regolarmente convocata" if data.get('tipo_convocazione') == "regolarmente convocata" else "convocata"
            
            text = f"Il Presidente constata e fa constatare che l'assemblea risulta {convocazione} ma che sono presenti soci rappresentanti soltanto il {percentuale_effettiva:.1f}% del capitale sociale; dichiara pertanto che l'Assemblea deve considerarsi irregolarmente costituita per mancanza del numero legale."
        else:
            # Assemblea deserta
            convocazione = "regolarmente convocata" if data.get('tipo_convocazione') == "regolarmente convocata" else "convocata"
            text = f"Il Presidente constata e fa constatare che l'assemblea risulta {convocazione} ma che non sono presenti soci; dichiara pertanto che l'Assemblea deve considerarsi deserta per mancanza totale di partecipazione."
        
        doc.add_paragraph(text)
        doc.add_paragraph()
    
    def _add_closing_section(self, doc, data):
        """Aggiunge la sezione di chiusura"""
        # Verifica se ci sono soci presenti
        soci_presenti = [s for s in data.get('soci', []) if s.get('nome', '').strip() and s.get('presente', True)]
        
        if soci_presenti:
            # Assemblea irregolare (con soci presenti ma sotto il numero legale)
            doc.add_paragraph("Viene quindi redatto il presente verbale e dopo averne data lettura, il Presidente constata che l'assemblea all'unanimità, con voto palese, ne approva il testo.")
        else:
            # Assemblea deserta (nessun socio presente)
            doc.add_paragraph("Viene quindi redatto il presente verbale di assemblea deserta.")
        
        ora_fine = data.get('ora_fine', '09:30')
        doc.add_paragraph(f"L'assemblea viene sciolta alle ore {ora_fine}.")
        doc.add_paragraph()
    
    def _add_signatures(self, doc, data):
        """Aggiunge le firme"""
        doc.add_paragraph()
        doc.add_paragraph()
        
        # Tabella per le firme usando il metodo sicuro
        table = self._create_table_with_style(doc, rows=3, cols=2)
        
        # Intestazioni
        table.cell(0, 0).text = "IL PRESIDENTE"
        table.cell(0, 1).text = "IL SEGRETARIO"
        
        # Nomi
        presidente = data.get('presidente', '[PRESIDENTE]')
        segretario = data.get('segretario', '[SEGRETARIO]')
        table.cell(1, 0).text = presidente
        table.cell(1, 1).text = segretario
        
        # Linee per le firme
        table.cell(2, 0).text = "_" * 30
        table.cell(2, 1).text = "_" * 30
        
        # Centra la tabella
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER


# Registra il template nel factory
DocumentTemplateFactory.register_template("verbale_assemblea_irregolare", VerbaleAssembleaIrregolareTemplate)