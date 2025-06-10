"""
Template per Verbale di Assemblea - Nomina Amministratore Unico
Questo template è specifico per verbali di nomina dell'amministratore unico della società.
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
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from datetime import date
import streamlit as st
import pandas as pd
import re

class VerbaleAmministratoreUnicoTemplate(DocumentTemplate):
    """Template per Verbale di Assemblea dei Soci - Nomina Amministratore Unico"""
    
    def get_template_name(self) -> str:
        return "Nomina Amministratore Unico"
    
    def get_required_fields(self) -> list:
        return [
            "denominazione", "sede_legale", "capitale_sociale", "codice_fiscale",
            "data_assemblea", "ora_assemblea", "presidente", "segretario", 
            "soci", "amministratore_unico"
        ]
    
    def get_form_fields(self, extracted_data: dict) -> dict:
        """Genera i campi del form per Streamlit utilizzando il CommonDataHandler"""
        form_data = {}
        
        # Utilizza il CommonDataHandler per i dati standard
        # Dati azienda standardizzati
        form_data.update(CommonDataHandler.extract_and_populate_company_data(extracted_data))
        
        # Dati assemblea standardizzati
        form_data.update(CommonDataHandler.extract_and_populate_assembly_data(extracted_data))
        
        # Campi specifici per nomina amministratore unico
        st.subheader("👤 Configurazioni Specifiche Amministratore Unico")
        
        col1, col2 = st.columns(2)
        with col1:
            form_data["ruolo_presidente"] = st.selectbox("Ruolo del presidente", 
                                                        CommonDataHandler.get_standard_ruoli_presidente())
            form_data["motivo_nomina"] = st.selectbox("Motivo della nomina", 
                                                     ["Dimissioni dell\'organo in carica", 
                                                      "Scadenza mandato", 
                                                      "Decadenza dall'ufficio",
                                                      "Prima nomina",
                                                      "Altro"])
        with col2:
            form_data["durata_incarico"] = st.selectbox("Durata incarico", 
                                                       ["A tempo indeterminato fino a revoca o dimissioni",
                                                        "Tre esercizi", 
                                                        "Un esercizio", 
                                                        "Altra durata"])
            form_data["include_compensi"] = st.checkbox("Includi attribuzione compensi", value=True)
        
        # Partecipanti standardizzati usando il CommonDataHandler
        participants_data = CommonDataHandler.extract_and_populate_participants_data(
            extracted_data, 
            unique_key_suffix="admin_unico"
        )
        form_data.update(participants_data)
        
        # Dati dell'Amministratore Unico da nominare
        st.subheader("👤 Amministratore Unico da Nominare")
        
        col1, col2 = st.columns(2)
        with col1:
            nome_admin = st.text_input("Nome e Cognome", 
                                     placeholder="es. Mario Rossi")
            data_nascita_admin = st.date_input("Data di nascita", 
                                             value=None)
            luogo_nascita_admin = st.text_input("Luogo di nascita", 
                                              placeholder="es. Roma (RM)")
        
        with col2:
            codice_fiscale_admin = st.text_input("Codice Fiscale", 
                                                placeholder="es. RSSMRA80A01H501Z")
            residenza_admin = st.text_input("Residenza", 
                                          placeholder="es. Via Roma 1, Milano (MI)")
            qualifica_admin = st.selectbox("Qualifica nella società", 
                                         ["Socio", "Amministratore uscente", "Terzo"])
        
        form_data["amministratore_unico"] = {
            "nome": nome_admin,
            "data_nascita": data_nascita_admin,
            "luogo_nascita": luogo_nascita_admin,
            "codice_fiscale": codice_fiscale_admin,
            "residenza": residenza_admin,
            "qualifica": qualifica_admin
        }
        
        # Compensi
        if form_data["include_compensi"]:
            st.subheader("💰 Compenso Amministratore Unico")
            col1, col2 = st.columns(2)
            with col1:
                form_data["compenso_annuo"] = st.text_input("Compenso annuo (€)", 
                                                           value="0,00",
                                                           help="Compenso annuo lordo")
                form_data["tipo_compenso"] = st.selectbox("Tipo di compenso", 
                                                         ["Fisso", "Gettoni di presenza", "Percentuale utili", "Misto"])
            with col2:
                form_data["rimborso_spese"] = st.checkbox("Rimborso spese", value=True)
                form_data["modalita_liquidazione"] = st.selectbox("Modalità liquidazione", 
                                                                 ["Periodicamente", "Annuale", "A fine mandato"])
        
        # Verifiche e dichiarazioni
        st.subheader("📋 Verifiche e Dichiarazioni")
        col1, col2 = st.columns(2)
        with col1:
            form_data["verifica_requisiti"] = st.checkbox("Verifica requisiti di eleggibilità completata", value=True)
            form_data["dichiarazioni_ricevute"] = st.checkbox("Dichiarazioni dell'amministratore ricevute", value=True)
        with col2:
            form_data["collegio_sindacale_presente"] = st.checkbox("Collegio Sindacale presente", value=False)
            form_data["verifica_incompatibilita"] = st.checkbox("Verifica incompatibilità effettuata", value=True)
        
        # Note aggiuntive
        st.subheader("📝 Note Aggiuntive")
        form_data["note_aggiuntive"] = st.text_area("Note aggiuntive", 
                                                  placeholder="Eventuali note specifiche sulla nomina...",
                                                  height=80)
        
        return form_data
    
    def show_preview(self, form_data: dict):
        """Mostra l'anteprima del documento fuori dal form"""
        # Sezione Anteprima
        st.markdown("---")
        st.subheader("👁️ Anteprima Documento")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            show_preview = st.checkbox("Mostra anteprima", value=False, key="preview_checkbox_admin_unico")
        
        with col2:
            if show_preview:
                st.info("💡 L'anteprima si aggiorna automaticamente con i dati inseriti sopra")
        
        if show_preview:
            with st.expander("📄 Anteprima del Verbale", expanded=True):
                try:
                    preview_text = self._generate_preview_text(form_data)
                    st.text(preview_text)
                except Exception as e:
                    st.error(f"Errore nella generazione dell'anteprima: {e}")
                    st.exception(e)
    
    def _generate_preview_text(self, data: dict) -> str:
        """Genera il testo di anteprima del verbale"""
        try:
            # Header dell'azienda
            header = f"""{data.get('denominazione', '[Denominazione]')}
Sede in {data.get('sede_legale', '[Sede]')}
Capitale sociale Euro {data.get('capitale_sociale', '[Capitale]')} i.v.
Codice fiscale: {data.get('codice_fiscale', '[CF]')}

Verbale di assemblea dei soci
del {data.get('data_assemblea', '[Data]').strftime('%d/%m/%Y') if hasattr(data.get('data_assemblea'), 'strftime') else '[Data]'}

Oggi {data.get('data_assemblea', '[Data]').strftime('%d/%m/%Y') if hasattr(data.get('data_assemblea'), 'strftime') else '[Data]'} alle ore {data.get('ora_assemblea', '[Ora]').strftime('%H:%M') if hasattr(data.get('ora_assemblea'), 'strftime') else '[Ora]'} presso la sede sociale {data.get('sede_legale', '[Sede]')}, si è tenuta l'assemblea generale dei soci, per discutere e deliberare sul seguente:

Ordine del giorno
1. nomina dell'amministratore della società"""
            
            if data.get('include_compensi', True):
                header += "\n2. attribuzione di compensi all'amministratore della società"
            
            # Sezione presidenza
            presidente_section = f"""

Assume la presidenza ai sensi dell'art. […] dello statuto sociale il Sig. {data.get('presidente', '[Presidente]')} {data.get('ruolo_presidente', 'Amministratore Unico')}, il quale dichiara e constata:

1 - che (come indicato anche nell'avviso di convocazione ed in conformità alle previsioni dell'art. […] dello statuto sociale) l'intervento all'assemblea può avvenire anche in audioconferenza

2 - che sono presenti/partecipano all'assemblea:
l'{data.get('ruolo_presidente', 'Amministratore Unico')} nella persona del suddetto Presidente Sig. {data.get('presidente', '[Presidente]')}"""
            
            # Collegio sindacale se presente
            if data.get('collegio_sindacale_presente', False):
                presidente_section += "\n[eventualmente\nper il Collegio Sindacale\nil Dott. […]\nil Dott. […]\nil Dott. […]\n[oppure\nil Sindaco Unico nella persona del Sig. […]]]"
            
            # Soci presenti
            soci_section = "\nnonché i seguenti soci o loro rappresentanti, [eventualmente così come iscritti a libro soci e] recanti complessivamente una quota pari a nominali euro […] pari al […]% del Capitale Sociale:"
            soci = data.get('soci', [])
            
            for socio in soci:
                if isinstance(socio, dict):
                    nome = socio.get('nome', '[Nome Socio]')
                    quota = socio.get('quota', '[Quota]')
                    percentuale = socio.get('percentuale', '[%]')
                    tipo_partecipazione = socio.get('tipo_partecipazione', 'Diretta')
                    
                    if tipo_partecipazione == 'Delegato':
                        delegato = socio.get('delegato', '[Delegato]')
                        soci_section += f"\nil Sig {delegato} delegato del socio Sig {nome} recante una quota pari a nominali euro {quota} pari al {percentuale}% del Capitale Sociale"
                    else:
                        soci_section += f"\nil Sig {nome} socio [oppure delegato del socio Sig […]] recante una quota pari a nominali euro {quota} pari al {percentuale}% del Capitale Sociale"
                else:
                    soci_section += f"\nil Sig {socio} socio"
            
            soci_section += "\n2 - che gli intervenuti sono legittimati alla presente assemblea;\n3 - che tutti gli intervenuti si dichiarano edotti sugli argomenti posti all'ordine del giorno."
            
            # Segretario
            segretario_section = f"""

I presenti all'unanimità chiamano a fungere da segretario il signor {data.get('segretario', '[Segretario]')}, che accetta l'incarico.

Il Presidente identifica tutti i partecipanti e si accerta che ai soggetti collegati mediante mezzi di telecomunicazione sia consentito seguire la discussione, trasmettere e ricevere documenti, intervenire in tempo reale, con conferma da parte di ciascun partecipante.

Il Presidente constata e fa constatare che l'assemblea risulta regolarmente convocata [oppure totalitaria] e deve ritenersi valida ed atta a deliberare sul citato ordine del giorno.

Si passa quindi allo svolgimento dell'ordine del giorno.

*     *     *"""
            
            # Discussione nomina amministratore unico
            motivo_nomina = data.get('motivo_nomina', 'Dimissioni dell\'organo in carica')
            admin_unico = data.get('amministratore_unico', {})
            nome_admin = admin_unico.get('nome', '[Nome]')
            data_nascita = admin_unico.get('data_nascita', '[Data nascita]')
            luogo_nascita = admin_unico.get('luogo_nascita', '[Luogo nascita]')
            codice_fiscale = admin_unico.get('codice_fiscale', '[CF]')
            residenza = admin_unico.get('residenza', '[Residenza]')
            
            if hasattr(data_nascita, 'strftime'):
                data_nascita_str = data_nascita.strftime('%d/%m/%Y')
            else:
                data_nascita_str = str(data_nascita) if data_nascita else '[Data nascita]'
            
            nomina_section = f"""

Il Presidente informa l'assemblea che si rende necessaria la nomina di un nuovo organo amministrativo [{motivo_nomina.lower()}].

Il Presidente ricorda all'assemblea quanto previsto dall'art. 2475 del Codice Civile e dall'atto costitutivo della società.

Prende la parola il socio sig. […] che propone di nominare Amministratore Unico della società il sig. {nome_admin}, dando evidenza della comunicazione scritta con cui il candidato, prima di accettare l'eventuale nomina, ha dichiarato:

- l'insussistenza a suo carico di cause di ineleggibilità alla carica di amministratore di società ed in particolare di non essere stato dichiarato interdetto, inabilitato o fallito e di non essere stato condannato ad una pena che importa l'interdizione, anche temporanea, dai pubblici uffici o l'incapacità ad esercitare uffici direttivi.

- l'insussistenza a suo carico di interdizioni dal ruolo di amministratore adottate da una Stato membro dell'Unione Europea.

[verificare che l'atto costitutivo non preveda ulteriori requisiti per l'assunzione della carica e quanto previsto da leggi speciali in relazione all'esercizio di particolari attività] [se esiste il collegio sindacale o il revisore, verificare eventuali incompatibilità con il neo amministratore]."""
            
            # Compensi se inclusi
            compensi_section = ""
            if data.get('include_compensi', True):
                compensi_section = f"""

Il Presidente invita anche l'assemblea a deliberare il compenso da attribuire all'organo amministrativo che verrà nominato, ai sensi dell'art. […] dello statuto sociale."""
            
            # Deliberazione
            durata_incarico = data.get('durata_incarico', 'A tempo indeterminato fino a revoca o dimissioni')
            compenso_annuo = data.get('compenso_annuo', '0,00')
            
            deliberazione_section = f"""

Segue breve discussione tra i soci al termine della quale si passa alla votazione con voto palese in forza della quale il Presidente constata che, all'unanimità [oppure con il voto contrario dei Sigg. […] e [eventualmente l'astensione dei Sigg. […]]], l'assemblea

d e l i b e r a:

che la società sia amministrata da un amministratore unico nominato nella persona del sig. {nome_admin}

che l'amministratore resti in carica {durata_incarico.lower()} [verificare che l'atto costitutivo non preveda una durata massima per l'incarico]"""
            
            if data.get('include_compensi', True):
                rimborso_text = " oltre al rimborso delle spese sostenute in ragione del suo ufficio" if data.get('rimborso_spese', True) else ""
                modalita_liquidazione = data.get('modalita_liquidazione', 'periodicamente')
                
                deliberazione_section += f"""

di attribuire all'amministratore unico testè nominato il compenso annuo ed omnicomprensivo pari a nominali euro {compenso_annuo} al lordo di ritenute fiscali e previdenziali{rimborso_text}. Il compenso verrà liquidato {modalita_liquidazione.lower()}, in ragione della permanenza in carica."""
            
            # Accettazione
            qualifica = admin_unico.get('qualifica', 'socio')
            accettazione_section = f"""

Il sig. {nome_admin}, presente in assemblea in qualità di {qualifica.lower()} accetta l'incarico e ringrazia l'assemblea per la fiducia accordata."""
            
            # Chiusura
            chiusura_section = f"""

*     *     *

Il Presidente constata che l'ordine del giorno è esaurito e che nessuno chiede la parola.

Viene quindi redatto il presente verbale e dopo averne data lettura, il Presidente constata che l'assemblea all'unanimità, con voto palese, ne approva il testo [eventualmente unitamente a quanto allegato].

L'assemblea viene sciolta alle ore [{data.get('ora_chiusura', '[Ora]')}].


Il Presidente                    Il Segretario
{data.get('presidente', '[Presidente]')}            {data.get('segretario', '[Segretario]')}"""
            
            # Combina tutte le sezioni
            full_text = (header + presidente_section + soci_section + segretario_section + 
                        nomina_section + compensi_section + deliberazione_section + 
                        accettazione_section + chiusura_section)
            
            return full_text
            
        except Exception as e:
            return f"Errore nella generazione dell'anteprima: {str(e)}"
    
    def generate_document(self, data: dict) -> Document:
        """Genera il documento Word del verbale"""
        doc = Document()
        
        # Setup stili del documento
        self._setup_document_styles(doc)
        
        # Aggiungi header azienda
        self._add_company_header(doc, data)
        
        # Aggiungi titolo verbale
        self._add_verbale_title(doc, data)
        
        # Aggiungi sezione di apertura
        self._add_opening_section(doc, data)
        
        # Aggiungi partecipanti
        self._add_participants_section(doc, data)
        
        # Aggiungi dichiarazioni preliminari
        self._add_preliminary_statements(doc, data)
        
        # Aggiungi discussione nomina amministratore unico
        self._add_nomination_discussion(doc, data)
        
        # Aggiungi sezione di chiusura
        self._add_closing_section(doc, data)
        
        # Aggiungi firme
        self._add_signatures(doc, data)
        
        return doc
    
    def _setup_document_styles(self, doc):
        """Imposta gli stili del documento"""
        styles = doc.styles
        
        # Stile per il titolo principale
        if 'Titolo Principale' not in [s.name for s in styles]:
            title_style = styles.add_style('Titolo Principale', WD_STYLE_TYPE.PARAGRAPH)
            title_style.font.name = 'Times New Roman'
            title_style.font.size = Pt(14)
            title_style.font.bold = True
            title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            title_style.paragraph_format.space_after = Pt(12)
        
        # Stile per il testo normale
        normal_style = styles['Normal']
        normal_style.font.name = 'Times New Roman'
        normal_style.font.size = Pt(12)
        normal_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        normal_style.paragraph_format.line_spacing = 1.15
    
    def _add_company_header(self, doc, data):
        """Aggiunge l'header dell'azienda"""
        # Nome azienda
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(data.get('denominazione', '[DENOMINAZIONE SOCIETÀ]'))
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.font.bold = True
        
        # Sede
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"Sede in {data.get('sede_legale', '[SEDE]')}")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        # Capitale sociale
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"Capitale sociale Euro {data.get('capitale_sociale', '[CAPITALE]')} i.v.")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        # Codice fiscale
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"Codice fiscale: {data.get('codice_fiscale', '[CODICE FISCALE]')}")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        doc.add_paragraph()
    
    def _add_verbale_title(self, doc, data):
        """Aggiunge il titolo del verbale"""
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run("Verbale di assemblea dei soci")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.font.bold = True
        
        # Data
        data_assemblea = data.get('data_assemblea')
        if hasattr(data_assemblea, 'strftime'):
            data_str = data_assemblea.strftime('%d/%m/%Y')
        else:
            data_str = '[DATA]'
        
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"del {data_str}")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        doc.add_paragraph()
    
    def _add_opening_section(self, doc, data):
        """Aggiunge la sezione di apertura"""
        # Data e ora
        data_assemblea = data.get('data_assemblea')
        ora_assemblea = data.get('ora_assemblea')
        
        if hasattr(data_assemblea, 'strftime'):
            data_str = data_assemblea.strftime('%d/%m/%Y')
        else:
            data_str = '[DATA]'
        
        if hasattr(ora_assemblea, 'strftime'):
            ora_str = ora_assemblea.strftime('%H:%M')
        else:
            ora_str = '[ORA]'
        
        text = f"Oggi {data_str} alle ore {ora_str} presso la sede sociale {data.get('sede_legale', '[SEDE]')}, si è tenuta l'assemblea generale dei soci, per discutere e deliberare sul seguente:"
        
        p = doc.add_paragraph(text)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        # Ordine del giorno
        doc.add_paragraph()
        p = doc.add_paragraph()
        run = p.add_run("Ordine del giorno")
        run.font.bold = True
        
        p = doc.add_paragraph("1. nomina dell'amministratore della società")
        
        if data.get('include_compensi', True):
            p = doc.add_paragraph("2. attribuzione di compensi all'amministratore della società")
    
    def _add_participants_section(self, doc, data):
        """Aggiunge la sezione dei partecipanti"""
        doc.add_paragraph()
        
        ruolo_presidente = data.get('ruolo_presidente', 'Amministratore Unico')
        presidente = data.get('presidente', '[PRESIDENTE]')
        
        text = f"Assume la presidenza ai sensi dell'art. […] dello statuto sociale il Sig. {presidente} {ruolo_presidente}, il quale dichiara e constata:"
        
        p = doc.add_paragraph(text)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        # Punto 1 - audioconferenza
        p = doc.add_paragraph("1 - che (come indicato anche nell'avviso di convocazione ed in conformità alle previsioni dell'art. […] dello statuto sociale) l'intervento all'assemblea può avvenire anche in audioconferenza")
        
        # Punto 2 - presenti
        p = doc.add_paragraph("2 - che sono presenti/partecipano all'assemblea:")
        p = doc.add_paragraph(f"l'{ruolo_presidente} nella persona del suddetto Presidente Sig. {presidente}")
        
        # Collegio sindacale se presente
        if data.get('collegio_sindacale_presente', False):
            p = doc.add_paragraph("[eventualmente")
            p = doc.add_paragraph("per il Collegio Sindacale")
            p = doc.add_paragraph("il Dott. […]")
            p = doc.add_paragraph("il Dott. […]")
            p = doc.add_paragraph("il Dott. […]")
            p = doc.add_paragraph("[oppure")
            p = doc.add_paragraph("il Sindaco Unico nella persona del Sig. […]]]")
        
        # Soci
        p = doc.add_paragraph("nonché i seguenti soci o loro rappresentanti, [eventualmente così come iscritti a libro soci e] recanti complessivamente una quota pari a nominali euro […] pari al […]% del Capitale Sociale:")
        
        soci = data.get('soci', [])
        for socio in soci:
            if isinstance(socio, dict):
                nome = socio.get('nome', '[Nome Socio]')
                quota = socio.get('quota', '[Quota]')
                percentuale = socio.get('percentuale', '[%]')
                tipo_partecipazione = socio.get('tipo_partecipazione', 'Diretta')
                
                if tipo_partecipazione == 'Delegato':
                    delegato = socio.get('delegato', '[Delegato]')
                    p = doc.add_paragraph(f"il Sig. {delegato} delegato del socio Sig {nome} recante una quota pari a nominali euro {quota} pari al {percentuale}% del Capitale Sociale")
                else:
                    p = doc.add_paragraph(f"il Sig. {nome} socio recante una quota pari a nominali euro {quota} pari al {percentuale}% del Capitale Sociale")
        
        # Verifica legittimazione
        p = doc.add_paragraph("2 - che gli intervenuti sono legittimati alla presente assemblea;")
        p = doc.add_paragraph("3 - che tutti gli intervenuti si dichiarano edotti sugli argomenti posti all'ordine del giorno.")
    
    def _add_preliminary_statements(self, doc, data):
        """Aggiunge le dichiarazioni preliminari"""
        doc.add_paragraph()
        
        segretario = data.get('segretario', '[SEGRETARIO]')
        p = doc.add_paragraph(f"I presenti all'unanimità chiamano a fungere da segretario il signor {segretario}, che accetta l'incarico.")
        
        p = doc.add_paragraph("Il Presidente identifica tutti i partecipanti e si accerta che ai soggetti collegati mediante mezzi di telecomunicazione sia consentito seguire la discussione, trasmettere e ricevere documenti, intervenire in tempo reale, con conferma da parte di ciascun partecipante.")
        
        p = doc.add_paragraph("Il Presidente constata e fa constatare che l'assemblea risulta regolarmente convocata [oppure totalitaria] e deve ritenersi valida ed atta a deliberare sul citato ordine del giorno.")
        
        p = doc.add_paragraph("Si passa quindi allo svolgimento dell'ordine del giorno.")
        
        # Separatore
        p = doc.add_paragraph("*     *     *")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    def _add_nomination_discussion(self, doc, data):
        """Aggiunge la discussione per la nomina dell'amministratore unico"""
        doc.add_paragraph()
        
        motivo_nomina = data.get('motivo_nomina', 'Dimissioni dell\'organo in carica')
        p = doc.add_paragraph(f"Il Presidente informa l'assemblea che si rende necessaria la nomina di un nuovo organo amministrativo [{motivo_nomina.lower()}].")
        
        p = doc.add_paragraph("Il Presidente ricorda all'assemblea quanto previsto dall'art. 2475 del Codice Civile e dall'atto costitutivo della società.")
        
        # Amministratore nominando
        admin_unico = data.get('amministratore_unico', {})
        nome_admin = admin_unico.get('nome', '[Nome]')
        
        p = doc.add_paragraph(f"Prende la parola il socio sig. […] che propone di nominare Amministratore Unico della società il sig. {nome_admin}, dando evidenza della comunicazione scritta con cui il candidato, prima di accettare l'eventuale nomina, ha dichiarato:")
        
        # Dichiarazioni
        p = doc.add_paragraph("l'insussistenza a suo carico di cause di ineleggibilità alla carica di amministratore di società ed in particolare di non essere stato dichiarato interdetto, inabilitato o fallito e di non essere stato condannato ad una pena che importa l'interdizione, anche temporanea, dai pubblici uffici o l'incapacità ad esercitare uffici direttivi.")
        p = doc.add_paragraph("l'insussistenza a suo carico di interdizioni dal ruolo di amministratore adottate da una Stato membro dell'Unione Europea.")
        p = doc.add_paragraph("[verificare che l'atto costitutivo non preveda ulteriori requisiti per l'assunzione della carica e quanto previsto da leggi speciali in relazione all'esercizio di particolari attività] [se esiste il collegio sindacale o il revisore, verificare eventuali incompatibilità con il neo amministratore].")
        
        # Compensi
        if data.get('include_compensi', True):
            p = doc.add_paragraph("Il Presidente invita anche l'assemblea a deliberare il compenso da attribuire all'organo amministrativo che verrà nominato, ai sensi dell'art. […] dello statuto sociale.")
        
        # Deliberazione
        p = doc.add_paragraph("Segue breve discussione tra i soci al termine della quale si passa alla votazione con voto palese in forza della quale il Presidente constata che, all'unanimità [oppure con il voto contrario dei Sigg. […] e [eventualmente l'astensione dei Sigg. […]]], l'assemblea")
        
        p = doc.add_paragraph("d e l i b e r a:")
        run = p.runs[0]
        run.font.bold = True
        run.font.underline = True
        
        p = doc.add_paragraph(f"che la società sia amministrata da un amministratore unico nominato nella persona del sig. {nome_admin}")
        
        # Durata incarico
        durata = data.get('durata_incarico', 'a tempo indeterminato fino a revoca o dimissioni')
        p = doc.add_paragraph(f"che l'amministratore resti in carica {durata.lower()} [verificare che l'atto costitutivo non preveda una durata massima per l'incarico]")
        
        # Compensi dettaglio
        if data.get('include_compensi', True):
            compenso = data.get('compenso_annuo', '0,00')
            rimborso_text = " oltre al rimborso delle spese sostenute in ragione del suo ufficio" if data.get('rimborso_spese', True) else ""
            modalita = data.get('modalita_liquidazione', 'periodicamente')
            
            p = doc.add_paragraph(f"di attribuire all'amministratore unico testè nominato il compenso annuo ed omnicomprensivo pari a nominali euro {compenso} al lordo di ritenute fiscali e previdenziali{rimborso_text}. Il compenso verrà liquidato {modalita.lower()}, in ragione della permanenza in carica.")
        
        # Accettazione
        qualifica = admin_unico.get('qualifica', 'socio')
        p = doc.add_paragraph(f"Il sig. {nome_admin}, presente in assemblea in qualità di {qualifica.lower()} accetta l'incarico e ringrazia l'assemblea per la fiducia accordata.")
        
        # Separatore
        p = doc.add_paragraph("*     *     *")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    def _add_closing_section(self, doc, data):
        """Aggiunge la sezione di chiusura"""
        doc.add_paragraph()
        
        p = doc.add_paragraph("Il Presidente constata che l'ordine del giorno è esaurito e che nessuno chiede la parola.")
        
        p = doc.add_paragraph("Viene quindi redatto il presente verbale e dopo averne data lettura, il Presidente constata che l'assemblea all'unanimità, con voto palese, ne approva il testo [eventualmente unitamente a quanto allegato].")
        
        ora_chiusura = data.get('ora_chiusura', '[ORA]')
        if hasattr(ora_chiusura, 'strftime'):
            ora_str = ora_chiusura.strftime('%H:%M')
        else:
            ora_str = '[ORA]'
        
        p = doc.add_paragraph(f"L'assemblea viene sciolta alle ore {ora_str}.")
    
    def _add_signatures(self, doc, data):
        """Aggiunge le firme"""
        doc.add_paragraph()
        doc.add_paragraph()
        
        # Tabella per le firme
        table = doc.add_table(rows=2, cols=2)
        table.style = 'Table Grid'
        table.autofit = False
        
        # Header
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Il Presidente'
        hdr_cells[1].text = 'Il Segretario'
        
        # Firme
        row_cells = table.rows[1].cells
        row_cells[0].text = data.get('presidente', '[PRESIDENTE]')
        row_cells[1].text = data.get('segretario', '[SEGRETARIO]')
        
        # Centra la tabella
        for row in table.rows:
            for cell in row.cells:
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

# Registra il template
DocumentTemplateFactory.register_template('verbale_assemblea_amministratore_unico', VerbaleAmministratoreUnicoTemplate)