"""
Template per Verbale di Assemblea - Nomina del Collegio Sindacale
Questo template è specifico per verbali di nomina del Collegio Sindacale della società.
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
from datetime import date, datetime
import streamlit as st
import pandas as pd
import re

class VerbaleNominaCollegioSindacaleTemplate(BaseVerbaleTemplate):
    """Template per Verbale di Assemblea dei Soci - Nomina del Collegio Sindacale"""
    
    def get_template_name(self) -> str:
        return "Nomina del Collegio Sindacale"
    
    def get_required_fields(self) -> list:
        return [
            "denominazione", "sede_legale", "capitale_sociale", "codice_fiscale",
            "data_assemblea", "ora_assemblea", "presidente", "segretario", 
            "soci", "amministratori", "collegio_sindacale"
        ]
    
    def get_form_fields(self, extracted_data: dict) -> dict:
        """Genera i campi del form per Streamlit utilizzando il CommonDataHandler"""
        form_data = {}
        
        # Utilizza il CommonDataHandler per i dati standard
        # Dati azienda standardizzati
        form_data.update(CommonDataHandler.extract_and_populate_company_data(extracted_data))
        
        # Dati assemblea standardizzati
        form_data.update(CommonDataHandler.extract_and_populate_assembly_data(extracted_data))
        
        # Campi specifici per nomina collegio sindacale
        st.subheader("🏛️ Configurazioni Specifiche Nomina Collegio Sindacale")
        
        col1, col2 = st.columns(2)
        with col1:
            form_data["ruolo_presidente"] = st.selectbox("Ruolo del presidente", 
                                                        CommonDataHandler.get_standard_ruoli_presidente())
            form_data["tipo_assemblea"] = st.selectbox("Tipo di assemblea", 
                                                      ["regolarmente convocata", "totalitaria"])
        with col2:
            form_data["modalita_partecipazione"] = st.checkbox("Partecipazione in audioconferenza consentita", value=True)
            form_data["motivo_nomina"] = st.selectbox("Motivo della nomina", [
                "sopravvenuta scadenza del Collegio Sindacale in carica",
                "superamento dei limiti dell'art. 2477 C.C.",
                "prima nomina per nuova società",
                "dimissioni del collegio precedente",
                "altro (specificare nelle note)"
            ])
        
        # Partecipanti standardizzati usando il CommonDataHandler
        participants_data = CommonDataHandler.extract_and_populate_participants_data(
            extracted_data, 
            unique_key_suffix="collegio_sindacale"
        )
        form_data.update(participants_data)
        
        # Dati specifici del Collegio Sindacale
        st.subheader("👥 Composizione del Collegio Sindacale")
        
        # Durata e compenso generale
        col1, col2 = st.columns(2)
        with col1:
            durata_incarico = st.text_input("Durata incarico (es. 'un triennio')", "un triennio")
            form_data["durata_incarico"] = durata_incarico
        with col2:
            compenso_complessivo = st.text_input("Compenso annuo complessivo membri effettivi (€)", "5.000,00")
            form_data["compenso_complessivo"] = compenso_complessivo
        
        # Membri del collegio sindacale
        st.markdown("**👨‍💼 Membri del Collegio Sindacale**")
        
        # Inizializza la lista dei membri se non esiste
        if 'collegio_members' not in st.session_state:
            st.session_state.collegio_members = [
                {"ruolo": "PRESIDENTE", "nome": "", "nato_a": "", "nato_il": date(1970, 1, 1), 
                 "residente": "", "codice_fiscale": "", "albo_data_gu": date.today(), 
                 "albo_num_gu": "", "albo_serie_gu": ""},
                {"ruolo": "SINDACO EFFETTIVO", "nome": "", "nato_a": "", "nato_il": date(1970, 1, 1), 
                 "residente": "", "codice_fiscale": "", "albo_data_gu": date.today(), 
                 "albo_num_gu": "", "albo_serie_gu": ""},
                {"ruolo": "SINDACO EFFETTIVO", "nome": "", "nato_a": "", "nato_il": date(1970, 1, 1), 
                 "residente": "", "codice_fiscale": "", "albo_data_gu": date.today(), 
                 "albo_num_gu": "", "albo_serie_gu": ""},
                {"ruolo": "SINDACO SUPPLENTE", "nome": "", "nato_a": "", "nato_il": date(1970, 1, 1), 
                 "residente": "", "codice_fiscale": "", "albo_data_gu": date.today(), 
                 "albo_num_gu": "", "albo_serie_gu": ""},
                {"ruolo": "SINDACO SUPPLENTE", "nome": "", "nato_a": "", "nato_il": date(1970, 1, 1), 
                 "residente": "", "codice_fiscale": "", "albo_data_gu": date.today(), 
                 "albo_num_gu": "", "albo_serie_gu": ""}
            ]
        
        # Form per ogni membro
        for i, membro in enumerate(st.session_state.collegio_members):
            with st.expander(f"📋 {membro['ruolo']} {i+1}", expanded=i < 3):  # I primi 3 espansi di default
                col1, col2 = st.columns(2)
                with col1:
                    membro["nome"] = st.text_input(f"Nome completo", value=membro["nome"], key=f"nome_{i}")
                    membro["nato_a"] = st.text_input(f"Nato a", value=membro["nato_a"], key=f"nato_a_{i}")
                    membro["nato_il"] = st.date_input(f"Nato il", value=membro["nato_il"], key=f"nato_il_{i}")
                    membro["residente"] = st.text_input(f"Residente in", value=membro["residente"], key=f"residente_{i}")
                with col2:
                    membro["codice_fiscale"] = st.text_input(f"Codice fiscale", value=membro["codice_fiscale"], key=f"cf_{i}")
                    membro["albo_data_gu"] = st.date_input(f"Data pubblicazione GU", value=membro["albo_data_gu"], key=f"albo_data_{i}")
                    membro["albo_num_gu"] = st.text_input(f"Numero GU", value=membro["albo_num_gu"], key=f"albo_num_{i}")
                    membro["albo_serie_gu"] = st.text_input(f"Serie GU", value=membro["albo_serie_gu"], key=f"albo_serie_{i}")
        
        form_data["collegio_sindacale"] = st.session_state.collegio_members
        
        # Presenza membri in assemblea
        st.subheader("📋 Dettagli Assemblea")
        col1, col2 = st.columns(2)
        with col1:
            membri_presenti = st.checkbox("I membri del collegio sono presenti in assemblea", value=False)
            form_data["membri_presenti"] = membri_presenti
            if membri_presenti:
                form_data["qualita_presenza"] = st.selectbox("In qualità di", ["invitati", "osservatori"])
        with col2:
            socio_proponente = st.text_input("Socio che propone la nomina", "")
            form_data["socio_proponente"] = socio_proponente
        
        # Controllo contabile
        st.subheader("📊 Controllo Contabile")
        form_data["controllo_contabile_collegio"] = st.checkbox(
            "Il controllo contabile è esercitato dal collegio sindacale", 
            value=True,
            help="Se l'atto costitutivo non dispone diversamente"
        )
        
        # Ordine del giorno
        st.subheader("📋 Ordine del Giorno")
        default_odg = "nomina del Collegio Sindacale della società"
        punti_odg = st.text_area("Punti all'ordine del giorno", 
                                default_odg, height=100)
        form_data["punti_ordine_giorno"] = [p.strip() for p in punti_odg.split("\n") if p.strip()]
        
        # Note aggiuntive
        st.subheader("📝 Note Aggiuntive")
        form_data["note_aggiuntive"] = st.text_area("Note aggiuntive (opzionale)", 
                                                   help="Eventuali note specifiche da inserire nel verbale")
        
        return form_data
    
    def show_preview(self, form_data: dict):
        """Mostra l'anteprima del documento fuori dal form"""
        # Sezione Anteprima
        st.markdown("---")
        st.subheader("👁️ Anteprima Documento")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            show_preview = st.checkbox("Mostra anteprima", value=False, key="preview_checkbox")
        
        if show_preview:
            try:
                # Debug dettagliato: mostra i dati estratti
                with st.expander("Debug: Dati estratti dal form"):
                    st.json(form_data)
                    
                    # Debug specifico per i soci
                    if 'soci' in form_data and form_data['soci']:
                        st.subheader("Debug Soci:")
                        for i, socio in enumerate(form_data['soci']):
                            st.write(f"Socio {i+1}:")
                            st.write(f"  - Nome: {socio.get('nome', 'N/A')}")
                            st.write(f"  - Tipo Soggetto: {socio.get('tipo_soggetto', 'N/A')}")
                            st.write(f"  - Tipo Partecipazione: {socio.get('tipo_partecipazione', 'N/A')}")
                            st.write(f"  - Delegato: {socio.get('delegato', 'N/A')}")
                            st.write(f"  - Rappresentante Legale: {socio.get('rappresentante_legale', 'N/A')}")
                            st.write(f"  - Presente: {socio.get('presente', 'N/A')}")
                            st.write("---")
                
                preview_text = self._generate_preview_text(form_data)
                st.text_area(
                    "Contenuto del verbale:",
                    value=preview_text,
                    height=600,
                    key="preview_text_nomina_collegio"
                )
            except Exception as e:
                st.error(f"Errore nell'anteprima: {e}")
    
    def _generate_preview_text(self, data: dict) -> str:
        """Genera il testo di anteprima del verbale"""
        
        # Estrazione dati di base
        denominazione = data.get('denominazione', '[DENOMINAZIONE]')
        sede = data.get('sede_legale', '[SEDE]')
        capitale = data.get('capitale_sociale', '[CAPITALE]')
        cf = data.get('codice_fiscale', '[CODICE FISCALE]')
        
        data_assemblea = data.get('data_assemblea', date.today())
        ora_assemblea = data.get('ora_assemblea', '10:00')
        presidente = data.get('presidente', '[PRESIDENTE]')
        segretario = data.get('segretario', '[SEGRETARIO]')
        
        # Dati collegio sindacale
        collegio_members = data.get('collegio_sindacale', [])
        durata_incarico = data.get('durata_incarico', '[DURATA INCARICO]')
        compenso = data.get('compenso_complessivo', '[COMPENSO]')
        motivo_nomina = data.get('motivo_nomina', '[MOTIVO NOMINA]')
        
        if isinstance(data_assemblea, str):
            data_str = data_assemblea
        else:
            data_str = data_assemblea.strftime('%d/%m/%Y')
        
        # Generazione testo anteprima
        text = f"""{denominazione.upper()}
Sede in {sede}
Capitale sociale Euro {capitale} i.v.
Codice fiscale: {cf}

Verbale di assemblea dei soci
del {data_str}

Oggi {data_str} alle ore {ora_assemblea} presso la sede sociale {sede}, si è tenuta l'assemblea generale dei soci, per discutere e deliberare sul seguente:

Ordine del giorno
{', '.join(data.get('punti_ordine_giorno', ['nomina del Collegio Sindacale della società']))}

Assume la presidenza ai sensi dell'art. [...] dello statuto sociale il Sig. {presidente} {data.get('ruolo_presidente', 'Amministratore Unico')}, il quale dichiara e constata:

1 - che l'assemblea risulta {data.get('tipo_assemblea', 'regolarmente convocata')}
"""

        # Aggiungi partecipazione in audioconferenza se prevista
        if data.get('modalita_partecipazione', False):
            text += "2 - che (come indicato anche nell'avviso di convocazione ed in conformità alle previsioni dell'art. [...] dello statuto sociale) l'intervento all'assemblea può avvenire anche in audioconferenza\n"
            next_num = 3
        else:
            next_num = 2
        
        # Aggiungi sezione partecipanti
        text += f"{next_num} - che sono presenti/partecipano all'assemblea:\n"
        text += f"l'Amministratore Unico nella persona del suddetto Presidente Sig. {presidente}\n"
        
        # Aggiungi soci
        soci = data.get('soci', [])
        if soci:
            total_quota_euro = 0.0
            total_quota_percentuale = 0.0

            for socio in soci:
                if isinstance(socio, dict):
                    try:
                        # Rimuovi punti e sostituisci virgola con punto per la conversione a float
                        quota_euro_str = str(socio.get('quota_euro', '0')).replace('.', '').replace(',', '.')
                        total_quota_euro += float(quota_euro_str)
                    except ValueError:
                        pass # Ignora valori non numerici

                    try:
                        quota_percentuale_str = str(socio.get('quota_percentuale', '0')).replace(',', '.')
                        total_quota_percentuale += float(quota_percentuale_str)
                    except ValueError:
                        pass # Ignora valori non numerici

            # Formattazione per l'output italiano
            formatted_total_quota_euro = f"{total_quota_euro:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            formatted_total_quota_percentuale = f"{total_quota_percentuale:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            text += f"- Soci presenti: {len(soci)} per un totale di Euro {formatted_total_quota_euro} ({formatted_total_quota_percentuale}% del capitale sociale)\n"
                        total_quota_percentuale += float(quota_percentuale_str)
                    except ValueError:
                        pass # Ignora valori non numerici
            
            # Formatta i totali per la visualizzazione
            formatted_total_quota_euro = f"{total_quota_euro:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') # Formato italiano
            formatted_total_quota_percentuale = f"{total_quota_percentuale:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') # Formato italiano

            text += f"nonché i seguenti soci o loro rappresentanti, recanti complessivamente una quota pari a nominali euro {formatted_total_quota_euro} pari al {formatted_total_quota_percentuale}% del Capitale Sociale:\n"
            for socio in soci:
                if isinstance(socio, dict):
                    nome = socio.get('nome', '[Nome Socio]')
                    quota_value = socio.get('quota_euro', '')
                    percentuale_value = socio.get('quota_percentuale', '')
                    
                    # Gestione robusta dei valori nulli o vuoti
                    quota = '[Quota]' if quota_value is None or str(quota_value).strip() == '' else str(quota_value).strip()
                    percentuale = '[%]' if percentuale_value is None or str(percentuale_value).strip() == '' else str(percentuale_value).strip()
                    
                    tipo_partecipazione = socio.get('tipo_partecipazione', 'Diretta')
                    tipo_soggetto = socio.get('tipo_soggetto', 'Persona Fisica')
                    rappresentante_legale = socio.get('rappresentante_legale', '')
                    
                    # Determina il prefisso basato sul tipo di soggetto
                    if tipo_soggetto == 'Società':
                        prefisso = "la società"
                        if rappresentante_legale:
                            rappresentante_text = f" nella persona del suo rappresentante legale {rappresentante_legale}"
                        else:
                            rappresentante_text = " nella persona del suo rappresentante legale [Nome Rappresentante]"
                    else:
                        prefisso = "il Sig"
                        rappresentante_text = ""
                    
                    if tipo_partecipazione == 'Delegato':
                        delegato = socio.get('delegato', '[Delegato]')
                        if tipo_soggetto == 'Società':
                            text += f"il Sig {delegato} delegato di {prefisso} {nome}{rappresentante_text} recante una quota pari a nominali euro {quota} pari al {percentuale}% del Capitale Sociale\n"
                        else:
                            text += f"il Sig {delegato} delegato del socio {prefisso} {nome} recante una quota pari a nominali euro {quota} pari al {percentuale}% del Capitale Sociale\n"
                    else:
                        if tipo_soggetto == 'Società':
                            text += f"{prefisso} {nome}{rappresentante_text} socio recante una quota pari a nominali euro {quota} pari al {percentuale}% del Capitale Sociale\n"
                        else:
                            text += f"{prefisso} {nome} socio recante una quota pari a nominali euro {quota} pari al {percentuale}% del Capitale Sociale\n"
                else:
                    text += f"il Sig {socio} socio recante una quota pari a nominali euro [Quota] pari al [%]% del Capitale Sociale\n"
        
        text += f"""
{next_num+1} - che gli intervenuti sono legittimati alla presente assemblea;
{next_num+2} - che tutti gli intervenuti si dichiarano edotti sugli argomenti posti all'ordine del giorno.

I presenti all'unanimità chiamano a fungere da segretario il signor {segretario}, che accetta l'incarico.

Il Presidente identifica tutti i partecipanti e si accerta che ai soggetti collegati mediante mezzi di telecomunicazione sia consentito seguire la discussione, trasmettere e ricevere documenti, intervenire in tempo reale, con conferma da parte di ciascun partecipante.

Il Presidente constata e fa constatare che l'assemblea risulta {data.get('tipo_assemblea', 'regolarmente convocata')} e deve ritenersi valida ed atta a deliberare sul citato ordine del giorno.

Si passa quindi allo svolgimento dell'ordine del giorno.

*     *     *

Il Presidente informa l'assemblea che si rende necessaria la nomina del Collegio Sindacale poiché {motivo_nomina}.

Il Presidente ricorda all'assemblea quanto previsto dall'art. 2477 del Codice Civile e dall'atto costitutivo della società.

Prende la parola il socio sig. {data.get('socio_proponente', '[SOCIO PROPONENTE]')} che propone di affidare il controllo legale dei conti ad un collegio sindacale composto dai Sigg. [nomi]. Ai sensi dell'art. 2400, ultimo comma del Codice Civile, prima dell'accettazione dell'incarico, i candidati hanno reso noti all'assemblea gli incarichi di amministrazione e di controllo da essi ricoperti presso altre società, mediante dichiarazioni scritte che resteranno depositate agli atti societari.

Segue breve discussione tra i soci al termine della quale si passa alla votazione con voto palese in forza della quale il Presidente constata che, all'unanimità, l'assemblea

DELIBERA:

di nominare un Collegio Sindacale, composto di tre membri effettivi e due supplenti, che dureranno in carica {durata_incarico}, nelle persone dei signori:
"""

        # Aggiungi membri del collegio
        for i, membro in enumerate(collegio_members):
            nome = membro.get('nome', '[NOME]')
            nato_a = membro.get('nato_a', '[LUOGO NASCITA]')
            nato_il = membro.get('nato_il', '[DATA NASCITA]')
            if isinstance(nato_il, date):
                nato_il_str = nato_il.strftime('%d/%m/%Y')
            else:
                nato_il_str = str(nato_il)
            residente = membro.get('residente', '[LUOGO RESIDENZA]')
            cf_membro = membro.get('codice_fiscale', '[CODICE FISCALE]')
            
            albo_data = membro.get('albo_data_gu', '[DATA GU]')
            if isinstance(albo_data, date):
                albo_data_str = albo_data.strftime('%d/%m/%Y')
            else:
                albo_data_str = str(albo_data)
                
            albo_num = membro.get('albo_num_gu', '[NUM GU]')
            albo_serie = membro.get('albo_serie_gu', '[SERIE GU]')
            ruolo = membro.get('ruolo', '[RUOLO]')
            
            text += f"{nome} nato a {nato_a} il {nato_il_str}, residente in {residente}, codice fiscale {cf_membro}, Revisore Contabile pubblicato sulla G.U. in data {albo_data_str} N. {albo_num}, {albo_serie} serie speciale; {ruolo};\n"

        text += f"""
di corrispondere ai membri effettivi del Collegio Sindacale un compenso annuo complessivo pari a euro {compenso}
"""

        # Aggiunta presenza membri se applicabile
        if data.get('membri_presenti', False):
            qualita = data.get('qualita_presenza', 'invitati')
            text += f"""
I Sigg. [nomi], presenti in assemblea in qualità di {qualita} accettano l'incarico e ringraziano l'assemblea per la fiducia accordata.
"""
        else:
            text += f"""
[L'accettazione della carica da parte dei neo-nominati potrà avvenire successivamente]
"""

        # Nota sul controllo contabile
        if data.get('controllo_contabile_collegio', True):
            text += f"""
[Verificare se l'atto costitutivo non dispone diversamente, il controllo contabile è esercitato dal collegio sindacale].
"""

        text += """
*     *     *

Il Presidente constata che l'ordine del giorno è esaurito e che nessuno chiede la parola.

Viene quindi redatto il presente verbale e dopo averne data lettura, il Presidente constata che l'assemblea all'unanimità, con voto palese, ne approva il testo.

L'assemblea viene sciolta alle ore [...].


Il Presidente                    Il Segretario
_________________            _________________
"""

        return text
    
    def generate_document(self, data: dict) -> Document:
        """Genera il documento Word utilizzando i dati forniti"""
        import os
        
        # Utilizza il template .docx esistente per mantenere la formattazione
        template_path = os.path.join(os.path.dirname(__file__), 'template.docx')
        
        try:
            if os.path.exists(template_path):
                doc = Document(template_path)
                # Rimuovi il contenuto esistente del template mantenendo gli stili
                for paragraph in doc.paragraphs[:]:
                    p = paragraph._element
                    p.getparent().remove(p)
            else:
                doc = Document()
                # Setup stili solo se non usiamo template
                self._setup_document_styles(doc)
        except Exception as e:
            # Fallback a documento vuoto se il template non può essere caricato
            doc = Document()
            self._setup_document_styles(doc)
        
        # Imposta stili del documento
        self._setup_document_styles(doc)
        
        # Aggiungi intestazione azienda
        self._add_company_header(doc, data)
        
        # Aggiungi titolo verbale
        self._add_verbale_title(doc, data)
        
        # Aggiungi sezione di apertura
        self._add_opening_section(doc, data)
        
        # Aggiungi sezione partecipanti
        self._add_participants_section(doc, data)
        
        # Aggiungi dichiarazioni preliminari
        self._add_preliminary_statements(doc, data)
        
        # Aggiungi discussione nomina collegio sindacale
        self._add_nomina_collegio_discussion(doc, data)
        
        # Aggiungi sezione di chiusura
        self._add_closing_section(doc, data)
        
        # Aggiungi firme
        self._add_signatures(doc, data)
        
        return doc
    
    def _setup_document_styles(self, doc):
        """Imposta gli stili del documento"""
        styles = doc.styles
        
        # Stile per l'intestazione
        if 'Intestazione' not in [s.name for s in styles]:
            header_style = styles.add_style('Intestazione', WD_STYLE_TYPE.PARAGRAPH)
            header_style.font.name = 'Times New Roman'
            header_style.font.size = Pt(12)
            header_style.font.bold = True
            header_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Stile per il titolo principale
        if 'Titolo Principale' not in [s.name for s in styles]:
            title_style = styles.add_style('Titolo Principale', WD_STYLE_TYPE.PARAGRAPH)
            title_style.font.name = 'Times New Roman'
            title_style.font.size = Pt(14)
            title_style.font.bold = True
            title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Stile per il testo normale
        normal_style = styles['Normal']
        normal_style.font.name = 'Times New Roman'
        normal_style.font.size = Pt(11)
        normal_style.paragraph_format.line_spacing = 1.15
    
    def _add_company_header(self, doc, data):
        """Aggiungi intestazione dell'azienda"""
        # Denominazione
        p = doc.add_paragraph()
        p.style = 'Intestazione'
        run = p.add_run(data.get('denominazione', '[DENOMINAZIONE]').upper())
        run.bold = True
        
        # Sede
        p = doc.add_paragraph()
        p.style = 'Intestazione'
        p.add_run(f"Sede in {data.get('sede_legale', '[SEDE]')}")
        
        # Capitale sociale
        p = doc.add_paragraph()
        p.style = 'Intestazione'
        p.add_run(f"Capitale sociale Euro {data.get('capitale_sociale', '[CAPITALE]')} i.v.")
        
        # Codice fiscale
        p = doc.add_paragraph()
        p.style = 'Intestazione'
        p.add_run(f"Codice fiscale: {data.get('codice_fiscale', '[CODICE FISCALE]')}")
        
        # Spazio
        doc.add_paragraph()
    
    def _add_verbale_title(self, doc, data):
        """Aggiungi titolo del verbale"""
        p = doc.add_paragraph()
        p.style = 'Titolo Principale'
        p.add_run("Verbale di assemblea dei soci")
        
        # Data
        data_assemblea = data.get('data_assemblea', date.today())
        if isinstance(data_assemblea, str):
            data_str = data_assemblea
        else:
            data_str = data_assemblea.strftime('%d/%m/%Y')
        
        p = doc.add_paragraph()
        p.style = 'Titolo Principale'
        p.add_run(f"del {data_str}")
        
        # Spazio
        doc.add_paragraph()
    
    def _add_opening_section(self, doc, data):
        """Aggiungi sezione di apertura"""
        data_assemblea = data.get('data_assemblea', date.today())
        if isinstance(data_assemblea, str):
            data_str = data_assemblea
        else:
            data_str = data_assemblea.strftime('%d/%m/%Y')
        
        ora = data.get('ora_assemblea', '10:00')
        sede = data.get('sede_legale', '[SEDE]')
        
        p = doc.add_paragraph()
        p.add_run(f"Oggi {data_str} alle ore {ora} presso la sede sociale {sede}, si è tenuta l'assemblea generale dei soci, per discutere e deliberare sul seguente:")
        
        # Ordine del giorno
        doc.add_paragraph()
        p = doc.add_paragraph()
        run = p.add_run("Ordine del giorno")
        run.bold = True
        
        punti_odg = data.get('punti_ordine_giorno', ['nomina del Collegio Sindacale della società'])
        for punto in punti_odg:
            p = doc.add_paragraph()
            p.add_run(punto)
        
        doc.add_paragraph()
    
    def _add_participants_section(self, doc, data):
        """Aggiungi sezione partecipanti"""
        presidente = data.get('presidente', '[PRESIDENTE]')
        ruolo_presidente = data.get('ruolo_presidente', 'Amministratore Unico')
        
        # Presidenza
        p = doc.add_paragraph()
        p.add_run(f"Assume la presidenza ai sensi dell'art. [...] dello statuto sociale il Sig. {presidente} {ruolo_presidente}, il quale dichiara e constata:")
        
        # Dichiarazioni
        counter = 1
        
        # Tipo assemblea
        p = doc.add_paragraph()
        p.add_run(f"{counter} - che l'assemblea risulta {data.get('tipo_assemblea', 'regolarmente convocata')}")
        counter += 1
        
        # Audioconferenza se prevista
        if data.get('modalita_partecipazione', False):
            p = doc.add_paragraph()
            p.add_run(f"{counter} - che (come indicato anche nell'avviso di convocazione ed in conformità alle previsioni dell'art. [...] dello statuto sociale) l'intervento all'assemblea può avvenire anche in audioconferenza")
            counter += 1
        
        # Presenti
        p = doc.add_paragraph()
        p.add_run(f"{counter} - che sono presenti/partecipano all'assemblea:")
        
        p = doc.add_paragraph()
        p.add_run(f"l'Amministratore Unico nella persona del suddetto Presidente Sig. {presidente}")
        
        # Soci
        soci = data.get('soci', [])
        if soci:
            p = doc.add_paragraph()
            p.add_run("nonché i seguenti soci o loro rappresentanti, recanti complessivamente una quota pari a nominali euro [...] pari al [...]% del Capitale Sociale:")
            
            for socio in soci:
                nome_socio = socio.get('nome', '[NOME SOCIO]')
                quota_value = socio.get('quota_euro', '')
                perc_value = socio.get('quota_percentuale', '')
                
                # Gestione robusta dei valori nulli o vuoti
                quota = '[QUOTA]' if quota_value is None or str(quota_value).strip() == '' else str(quota_value).strip()
                perc = '[%]' if perc_value is None or str(perc_value).strip() == '' else str(perc_value).strip()
                
                p = doc.add_paragraph()
                p.add_run(f"il Sig. {nome_socio} socio recante una quota pari a nominali euro {quota} pari al {perc}% del Capitale Sociale")
        
        counter += 1
        
        # Altre dichiarazioni
        p = doc.add_paragraph()
        p.add_run(f"{counter} - che gli intervenuti sono legittimati alla presente assemblea;")
        counter += 1
        
        p = doc.add_paragraph()
        p.add_run(f"{counter} - che tutti gli intervenuti si dichiarano edotti sugli argomenti posti all'ordine del giorno.")
        
        doc.add_paragraph()
    
    def _add_preliminary_statements(self, doc, data):
        """Aggiungi dichiarazioni preliminari"""
        segretario = data.get('segretario', '[SEGRETARIO]')
        
        p = doc.add_paragraph()
        p.add_run(f"I presenti all'unanimità chiamano a fungere da segretario il signor {segretario}, che accetta l'incarico.")
        
        p = doc.add_paragraph()
        p.add_run("Il Presidente identifica tutti i partecipanti e si accerta che ai soggetti collegati mediante mezzi di telecomunicazione sia consentito seguire la discussione, trasmettere e ricevere documenti, intervenire in tempo reale, con conferma da parte di ciascun partecipante.")
        
        p = doc.add_paragraph()
        tipo_assemblea = data.get('tipo_assemblea', 'regolarmente convocata')
        p.add_run(f"Il Presidente constata e fa constatare che l'assemblea risulta {tipo_assemblea} e deve ritenersi valida ed atta a deliberare sul citato ordine del giorno.")
        
        p = doc.add_paragraph()
        p.add_run("Si passa quindi allo svolgimento dell'ordine del giorno.")
        
        # Separatore
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run("*     *     *")
        
        doc.add_paragraph()
    
    def _add_nomina_collegio_discussion(self, doc, data):
        """Aggiungi sezione discussione nomina collegio sindacale"""
        motivo_nomina = data.get('motivo_nomina', '[MOTIVO NOMINA]')
        socio_proponente = data.get('socio_proponente', '[SOCIO PROPONENTE]')
        collegio_members = data.get('collegio_sindacale', [])
        
        # Informativa presidente
        p = doc.add_paragraph()
        p.add_run(f"Il Presidente informa l'assemblea che si rende necessaria la nomina del Collegio Sindacale poiché {motivo_nomina}.")
        
        p = doc.add_paragraph()
        p.add_run("Il Presidente ricorda all'assemblea quanto previsto dall'art. 2477 del Codice Civile e dall'atto costitutivo della società.")
        
        # Proposta
        p = doc.add_paragraph()
        p.add_run(f"Prende la parola il socio sig. {socio_proponente} che propone di affidare il controllo legale dei conti ad un collegio sindacale composto dai Sigg. [nomi]. Ai sensi dell'art. 2400, ultimo comma del Codice Civile, prima dell'accettazione dell'incarico, i candidati hanno reso noti all'assemblea gli incarichi di amministrazione e di controllo da essi ricoperti presso altre società, mediante dichiarazioni scritte che resteranno depositate agli atti societari.")
        
        # Discussione e votazione
        p = doc.add_paragraph()
        p.add_run("Segue breve discussione tra i soci al termine della quale si passa alla votazione con voto palese in forza della quale il Presidente constata che, all'unanimità, l'assemblea")
        
        # DELIBERA
        doc.add_paragraph()
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run("D E L I B E R A:")
        run.bold = True
        
        doc.add_paragraph()
        
        # Nomina collegio
        durata_incarico = data.get('durata_incarico', '[DURATA INCARICO]')
        
        p = doc.add_paragraph()
        p.add_run(f"di nominare un Collegio Sindacale, composto di tre membri effettivi e due supplenti, che dureranno in carica {durata_incarico}, nelle persone dei signori:")
        
        # Elenco membri
        for membro in collegio_members:
            nome = membro.get('nome', '[NOME]')
            nato_a = membro.get('nato_a', '[LUOGO NASCITA]')
            nato_il = membro.get('nato_il', '[DATA NASCITA]')
            if isinstance(nato_il, date):
                nato_il_str = nato_il.strftime('%d/%m/%Y')
            else:
                nato_il_str = str(nato_il)
            
            residente = membro.get('residente', '[LUOGO RESIDENZA]')
            cf_membro = membro.get('codice_fiscale', '[CODICE FISCALE]')
            
            albo_data = membro.get('albo_data_gu', '[DATA GU]')
            if isinstance(albo_data, date):
                albo_data_str = albo_data.strftime('%d/%m/%Y')
            else:
                albo_data_str = str(albo_data)
                
            albo_num = membro.get('albo_num_gu', '[NUM GU]')
            albo_serie = membro.get('albo_serie_gu', '[SERIE GU]')
            ruolo = membro.get('ruolo', '[RUOLO]')
            
            p = doc.add_paragraph()
            p.add_run(f"{nome} nato a {nato_a} il {nato_il_str}, residente in {residente}, codice fiscale {cf_membro}, Revisore Contabile pubblicato sulla G.U. in data {albo_data_str} N. {albo_num}, {albo_serie} serie speciale; {ruolo};")
        
        # Compenso
        compenso = data.get('compenso_complessivo', '[COMPENSO]')
        p = doc.add_paragraph()
        p.add_run(f"di corrispondere ai membri effettivi del Collegio Sindacale un compenso annuo complessivo pari a euro {compenso}")
        
        doc.add_paragraph()
        
        # Accettazione
        if data.get('membri_presenti', False):
            qualita = data.get('qualita_presenza', 'invitati')
            p = doc.add_paragraph()
            p.add_run(f"I Sigg. [nomi], presenti in assemblea in qualità di {qualita} accettano l'incarico e ringraziano l'assemblea per la fiducia accordata.")
        else:
            p = doc.add_paragraph()
            p.add_run("[L'accettazione della carica da parte dei neo-nominati potrà avvenire successivamente]")
        
        # Nota controllo contabile
        if data.get('controllo_contabile_collegio', True):
            p = doc.add_paragraph()
            p.add_run("[Verificare se l'atto costitutivo non dispone diversamente, il controllo contabile è esercitato dal collegio sindacale].")
        
        # Separatore
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run("*     *     *")
        
        doc.add_paragraph()
    
    def _add_closing_section(self, doc, data):
        """Aggiungi sezione di chiusura"""
        p = doc.add_paragraph()
        p.add_run("Il Presidente constata che l'ordine del giorno è esaurito e che nessuno chiede la parola.")
        
        p = doc.add_paragraph()
        p.add_run("Viene quindi redatto il presente verbale e dopo averne data lettura, il Presidente constata che l'assemblea all'unanimità, con voto palese, ne approva il testo.")
        
        p = doc.add_paragraph()
        p.add_run("L'assemblea viene sciolta alle ore [...].")
        
        doc.add_paragraph()
        doc.add_paragraph()
    
    def _add_signatures(self, doc, data):
        """Aggiungi sezione firme"""
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        
        # Crea una tabella per le firme
        table = doc.add_table(rows=2, cols=2)
        table.autofit = False
        
        # Intestazioni
        table.cell(0, 0).text = "Il Presidente"
        table.cell(0, 1).text = "Il Segretario"
        
        # Linee per le firme
        table.cell(1, 0).text = "_________________"
        table.cell(1, 1).text = "_________________"
        
        # Centra la tabella
        for row in table.rows:
            for cell in row.cells:
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

# Registra il template
DocumentTemplateFactory.register_template("nomina_collegio_sindacale", VerbaleNominaCollegioSindacaleTemplate)