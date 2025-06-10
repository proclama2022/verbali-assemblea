"""
Template per Verbale di Assemblea - Revoca dell'Amministratore Unico e nomina di nuovo Organo Amministrativo
"""

import sys
import os

# Aggiungi il path della cartella src
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

class VerbaleRevocaNominaTemplate(DocumentTemplate):
    """Template per Verbale di Assemblea - Revoca dell'Amministratore Unico e nomina di nuovo Organo Amministrativo"""
    
    def get_template_name(self) -> str:
        return "Revoca dell'Amministratore Unico e nomina di nuovo Organo Amministrativo"
    
    def get_required_fields(self) -> list:
        return [
            "denominazione", "sede_legale", "capitale_sociale", "codice_fiscale",
            "data_assemblea", "ora_assemblea", "presidente", "segretario", 
            "soci", "amministratore_revocato", "nuovo_amministratore"
        ]
    
    def get_form_fields(self, extracted_data: dict) -> dict:
        """Genera i campi del form per Streamlit"""
        form_data = {}
        
        # Dati azienda standardizzati
        form_data.update(CommonDataHandler.extract_and_populate_company_data(extracted_data))
        
        # Dati assemblea standardizzati
        form_data.update(CommonDataHandler.extract_and_populate_assembly_data(extracted_data))
        
        # Configurazioni specifiche
        st.subheader("⚖️ Configurazioni Specifiche Revoca e Nomina")
        
        col1, col2 = st.columns(2)
        with col1:
            form_data["ruolo_presidente"] = st.selectbox("Ruolo del presidente", 
                                                        ["Amministratore Unico", 
                                                         "Presidente del Consiglio di Amministrazione",
                                                         "Altro (come da statuto)"])
            form_data["motivo_revoca"] = st.selectbox("Motivo della revoca", 
                                                     ["Impedimento a svolgere le funzioni", 
                                                      "Gravi inadempimenti o irregolarità per giusta causa"])
        with col2:
            form_data["include_collegio_sindacale"] = st.checkbox("Include Collegio Sindacale", value=False)
            form_data["include_revisore"] = st.checkbox("Include revisore contabile", value=False)
        
        # Partecipanti standardizzati
        participants_data = CommonDataHandler.extract_and_populate_participants_data(
            extracted_data, 
            unique_key_suffix="revoca_nomina"
        )
        form_data.update(participants_data)
        
        # Amministratore da revocare
        st.subheader("👤 Amministratore da Revocare")
        
        col1, col2 = st.columns(2)
        with col1:
            nome_revocato = st.text_input("Nome e Cognome amministratore da revocare", 
                                        placeholder="es. Mario Rossi")
        with col2:
            if form_data["motivo_revoca"] == "Gravi inadempimenti o irregolarità per giusta causa":
                inadempimenti = st.text_area("Dettagli inadempimenti/irregolarità", 
                                            placeholder="Descrivi i gravi inadempimenti...",
                                            height=100)
            else:
                inadempimenti = ""
        
        form_data["amministratore_revocato"] = {
            "nome": nome_revocato,
            "inadempimenti": inadempimenti
        }
        
        # Nuovo Amministratore
        st.subheader("👤 Nuovo Amministratore da Nominare")
        
        col1, col2 = st.columns(2)
        with col1:
            nome_nuovo = st.text_input("Nome e Cognome nuovo amministratore", 
                                     placeholder="es. Luigi Bianchi")
            qualifica_nuovo = st.selectbox("Qualifica nella società", 
                                         ["Socio", "Amministratore uscente", "Invitato", "Altro"])
        
        with col2:
            durata_incarico = st.selectbox("Durata incarico", 
                                         ["A tempo indeterminato fino a revoca o dimissioni",
                                          "Tre esercizi", 
                                          "Un esercizio", 
                                          "Altra durata"])
            compenso = st.text_input("Compenso annuo (€)", 
                                   value="0,00",
                                   help="Compenso annuo lordo")
        
        form_data["nuovo_amministratore"] = {
            "nome": nome_nuovo,
            "qualifica": qualifica_nuovo,
            "durata_incarico": durata_incarico,
            "compenso": compenso
        }
        
        # Votazioni
        st.subheader("🗳️ Configurazioni Votazione")
        
        col1, col2 = st.columns(2)
        with col1:
            form_data["votazione_revoca_unanime"] = st.checkbox("Votazione revoca unanime", value=True)
            if not form_data["votazione_revoca_unanime"]:
                form_data["voti_contrari_revoca"] = st.text_input("Voti contrari revoca", 
                                                                placeholder="es. Sig. Rossi")
        
        with col2:
            form_data["votazione_nomina_unanime"] = st.checkbox("Votazione nomina unanime", value=True)
            if not form_data["votazione_nomina_unanime"]:
                form_data["voti_contrari_nomina"] = st.text_input("Voti contrari nomina", 
                                                                placeholder="es. Sig. Verdi")
        
        # Configurazioni aggiuntive
        st.subheader("⚙️ Configurazioni Aggiuntive")
        
        col1, col2 = st.columns(2)
        with col1:
            form_data["include_traduzione"] = st.checkbox("Include sezione traduzione", value=False)
            form_data["include_compensi"] = st.checkbox("Include deliberazione compensi", value=True)
        with col2:
            form_data["rimborso_spese"] = st.checkbox("Rimborso spese", value=True)
            form_data["verifica_requisiti"] = st.checkbox("Verifica requisiti completata", value=True)
        
        # Traduzione se necessaria
        if form_data["include_traduzione"]:
            st.subheader("🌐 Traduzione")
            col1, col2 = st.columns(2)
            with col1:
                form_data["persona_traduzione"] = st.text_input("Persona che necessita traduzione")
            with col2:
                form_data["lingua_traduzione"] = st.selectbox("Lingua", 
                                                             ["Inglese", "Francese", "Tedesco", "Spagnolo"])
        
        # Note aggiuntive
        st.subheader("📝 Note Aggiuntive")
        form_data["note_aggiuntive"] = st.text_area("Note aggiuntive", 
                                                  placeholder="Eventuali note specifiche...",
                                                  height=80)
        
        return form_data
    
    def show_preview(self, form_data: dict):
        """Mostra l'anteprima del documento"""
        st.markdown("---")
        st.subheader("👁️ Anteprima Documento")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            show_preview = st.checkbox("Mostra anteprima", value=False, key="preview_checkbox_revoca_nomina")
        
        with col2:
            if show_preview:
                st.info("💡 L'anteprima si aggiorna automaticamente")
        
        if show_preview:
            with st.expander("📄 Anteprima del Verbale", expanded=True):
                try:
                    preview_text = self._generate_preview_text(form_data)
                    st.text(preview_text)
                except Exception as e:
                    st.error(f"Errore nell'anteprima: {e}")
    
    def _generate_preview_text(self, data: dict) -> str:
        """Genera il testo di anteprima"""
        try:
            # Header
            header = f"""{data.get('denominazione', '[Denominazione]')}
Sede in {data.get('sede_legale', '[Sede]')}
Capitale sociale Euro {data.get('capitale_sociale', '[Capitale]')} i.v.
Codice fiscale: {data.get('codice_fiscale', '[CF]')}

Verbale di assemblea dei soci
del {data.get('data_assemblea', '[Data]').strftime('%d/%m/%Y') if hasattr(data.get('data_assemblea'), 'strftime') else '[Data]'}

Ordine del giorno
Revoca dell'Amministratore Unico e nomina di nuovo Organo Amministrativo."""
            
            # Resto del verbale... (truncated per brevità)
            return header + "\n\n[... resto del verbale ...]"
            
        except Exception as e:
            return f"Errore: {str(e)}"
    
    def generate_document(self, data: dict) -> Document:
        """Genera il documento Word"""
        doc = Document()
        
        # Setup stili
        self._setup_document_styles(doc)
        
        # Header azienda
        self._add_company_header(doc, data)
        
        # Titolo verbale
        self._add_verbale_title(doc, data)
        
        # Sezioni del verbale
        self._add_opening_section(doc, data)
        self._add_participants_section(doc, data)
        self._add_preliminary_statements(doc, data)
        self._add_revoca_discussion(doc, data)
        self._add_nomina_discussion(doc, data)
        self._add_closing_section(doc, data)
        self._add_signatures(doc, data)
        
        return doc
    
    def _setup_document_styles(self, doc):
        """Imposta gli stili del documento"""
        styles = doc.styles
        
        if 'Titolo Principale' not in [s.name for s in styles]:
            title_style = styles.add_style('Titolo Principale', WD_STYLE_TYPE.PARAGRAPH)
            title_style.font.name = 'Times New Roman'
            title_style.font.size = Pt(14)
            title_style.font.bold = True
            title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        normal_style = styles['Normal']
        normal_style.font.name = 'Times New Roman'
        normal_style.font.size = Pt(12)
        normal_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        normal_style.paragraph_format.line_spacing = 1.15
    
    def _add_company_header(self, doc, data):
        """Aggiunge header azienda"""
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(data.get('denominazione', '[DENOMINAZIONE]'))
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.font.bold = True
        
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"Sede in {data.get('sede_legale', '[SEDE]')}")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"Capitale sociale Euro {data.get('capitale_sociale', '[CAPITALE]')} i.v.")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"Codice fiscale: {data.get('codice_fiscale', '[CF]')}")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        doc.add_paragraph()
    
    def _add_verbale_title(self, doc, data):
        """Aggiunge titolo verbale"""
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run("Verbale di assemblea dei soci")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.font.bold = True
        
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
        """Aggiunge sezione apertura"""
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
        
        doc.add_paragraph()
        p = doc.add_paragraph()
        run = p.add_run("Ordine del giorno")
        run.font.bold = True
        
        p = doc.add_paragraph("Revoca dell'Amministratore Unico e nomina di nuovo Organo Amministrativo.")
    
    def _add_participants_section(self, doc, data):
        """Aggiunge sezione partecipanti"""
        doc.add_paragraph()
        
        ruolo_presidente = data.get('ruolo_presidente', 'Amministratore Unico')
        presidente = data.get('presidente', '[PRESIDENTE]')
        
        text = f"Assume la presidenza ai sensi dell'art. […] dello statuto sociale il Sig. {presidente} {ruolo_presidente}, il quale dichiara e constata:"
        
        p = doc.add_paragraph(text)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        p = doc.add_paragraph("1 - che (come indicato anche nell'avviso di convocazione ed in conformità alle previsioni dell'art. […] dello statuto sociale) l'intervento all'assemblea può avvenire anche in audioconferenza")
        
        p = doc.add_paragraph("2 - che sono presenti/partecipano all'assemblea:")
        p = doc.add_paragraph(f"l'{ruolo_presidente} nella persona del suddetto Presidente Sig. {presidente}")
        
        # Collegio sindacale se presente
        if data.get('include_collegio_sindacale', False):
            p = doc.add_paragraph("[eventualmente")
            p = doc.add_paragraph("per il Collegio Sindacale")
            p = doc.add_paragraph("il Dott. […]")
            p = doc.add_paragraph("il Dott. […]")
            p = doc.add_paragraph("il Dott. […]]")
        
        # Revisore se presente
        if data.get('include_revisore', False):
            p = doc.add_paragraph("[eventualmente, se invitato")
            p = doc.add_paragraph("il revisore contabile Dott. […]]")
        
        # Soci
        p = doc.add_paragraph("nonché i seguenti soci o loro rappresentanti, [eventualmente così come iscritti a libro soci e] recanti complessivamente una quota pari a nominali euro […] pari al […]% del Capitale Sociale:")
        
        soci = data.get('soci', [])
        for socio in soci:
            if isinstance(socio, dict):
                nome = socio.get('nome', '[Nome Socio]')
                quota = socio.get('quota', '[Quota]')
                percentuale = socio.get('percentuale', '[%]')
                p = doc.add_paragraph(f"il Sig {nome} socio recante una quota pari a nominali euro {quota} pari al {percentuale}% del Capitale Sociale")
        
        p = doc.add_paragraph("2 - che gli intervenuti sono legittimati alla presente assemblea;")
        p = doc.add_paragraph("3 - che tutti gli intervenuti si dichiarano edotti sugli argomenti posti all'ordine del giorno.")
    
    def _add_preliminary_statements(self, doc, data):
        """Aggiunge dichiarazioni preliminari"""
        doc.add_paragraph()
        
        segretario = data.get('segretario', '[SEGRETARIO]')
        p = doc.add_paragraph(f"I presenti all'unanimità chiamano a fungere da segretario il signor {segretario}, che accetta l'incarico.")
        
        p = doc.add_paragraph("Il Presidente identifica tutti i partecipanti e si accerta che ai soggetti collegati mediante mezzi di telecomunicazione sia consentito seguire la discussione, trasmettere e ricevere documenti, intervenire in tempo reale, con conferma da parte di ciascun partecipante.")
        
        # Traduzione se necessaria
        if data.get('include_traduzione', False):
            persona_traduzione = data.get('persona_traduzione', '[Nome]')
            lingua = data.get('lingua_traduzione', 'inglese').lower()
            p = doc.add_paragraph(f"In particolare, preso atto che il Sig. {persona_traduzione} non conosce la lingua italiana ma dichiara di conoscere la lingua {lingua}, il Presidente dichiara che provvederà a tradurre dall'italiano al {lingua} (e viceversa) gli interventi dei partecipanti alla discussione nonché a tradurre dall'italiano al {lingua} il verbale che sarà redatto al termine della riunione.")
        
        p = doc.add_paragraph("Il Presidente constata e fa constatare che l'assemblea risulta regolarmente convocata [oppure totalitaria] e deve ritenersi valida ed atta a deliberare sul citato ordine del giorno.")
        
        p = doc.add_paragraph("Si passa quindi allo svolgimento dell'ordine del giorno.")
        
        # Separatore
        p = doc.add_paragraph("*     *     *")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    def _add_revoca_discussion(self, doc, data):
        """Aggiunge discussione revoca"""
        doc.add_paragraph()
        
        admin_revocato = data.get('amministratore_revocato', {})
        nome_revocato = admin_revocato.get('nome', '[Nome]')
        motivo_revoca = data.get('motivo_revoca', 'Impedimento a svolgere le funzioni')
        
        if motivo_revoca == "Impedimento a svolgere le funzioni":
            p = doc.add_paragraph(f"Prende la parola il Sig. […] che illustra all'assemblea l'impedimento dell'Amministratore Unico in carica Sig {nome_revocato} a svolgere le sue funzioni ed invita pertanto l'Assemblea dei soci a deliberare in merito.")
        else:
            inadempimenti = admin_revocato.get('inadempimenti', '[Dettagli inadempimenti]')
            p = doc.add_paragraph(f"Prende la parola il Sig. […] che dichiara che a carico dell'Amministratore Unico in carica Sig {nome_revocato} sono da imputare gravi inadempimenti o irregolarità, tali da giustificarne l'immediata revoca per giusta causa. In particolare il Sig. […] imputa all'Amministratore Unico in carica Sig {nome_revocato} quanto segue:")
            p = doc.add_paragraph(inadempimenti)
            p = doc.add_paragraph("L'Assemblea dei soci è quindi chiamata a deliberare in merito.")
        
        p = doc.add_paragraph("Prende la parola il Sig. […] che dichiara […].")
        
        # Votazione revoca
        if data.get('votazione_revoca_unanime', True):
            votazione_text = "all'unanimità"
        else:
            voti_contrari = data.get('voti_contrari_revoca', '')
            votazione_text = f"con il voto contrario dei Sigg. {voti_contrari}"
        
        p = doc.add_paragraph(f"Esaurita la discussione, si passa alla votazione con voto palese in forza della quale il Presidente constata che, {votazione_text}, l'assemblea")
        
        p = doc.add_paragraph("d e l i b e r a:")
        run = p.runs[0]
        run.font.bold = True
        run.font.underline = True
        
        p = doc.add_paragraph(f"di revocare il Sig {nome_revocato} dalla carica di Amministratore Unico;")
    
    def _add_nomina_discussion(self, doc, data):
        """Aggiunge discussione nomina"""
        doc.add_paragraph()
        
        nuovo_admin = data.get('nuovo_amministratore', {})
        nome_nuovo = nuovo_admin.get('nome', '[Nome]')
        qualifica = nuovo_admin.get('qualifica', 'socio')
        durata = nuovo_admin.get('durata_incarico', 'a tempo indeterminato fino a revoca o dimissioni')
        compenso = nuovo_admin.get('compenso', '0,00')
        
        p = doc.add_paragraph("Il Presidente informa l'assemblea che si rende ora necessaria la nomina di un nuovo organo amministrativo.")
        
        p = doc.add_paragraph("Il Presidente ricorda all'assemblea quanto previsto dall'art. 2475 del Codice Civile e dall'atto costitutivo della società.")
        
        p = doc.add_paragraph(f"Prende la parola il socio sig. […] che propone di nominare Amministratore Unico della società il sig. {nome_nuovo}, dando evidenza della comunicazione scritta con cui il candidato, prima di accettare l'eventuale nomina, ha dichiarato:")
        
        p = doc.add_paragraph("l'insussistenza a suo carico di cause di ineleggibilità alla carica di amministratore di società ed in particolare di non essere stato dichiarato interdetto, inabilitato o fallito e di non essere stato condannato ad una pena che importa l'interdizione, anche temporanea, dai pubblici uffici o l'incapacità ad esercitare uffici direttivi.")
        
        p = doc.add_paragraph("l'insussistenza a suo carico di interdizioni dal ruolo di amministratore adottate da una Stato membro dell'Unione Europea.")
        
        if data.get('include_compensi', True):
            p = doc.add_paragraph("Il Presidente invita anche l'assemblea a deliberare il compenso da attribuire all'organo amministrativo che verrà nominato, ai sensi dell'art. […] dello statuto sociale.")
        
        # Votazione nomina
        if data.get('votazione_nomina_unanime', True):
            votazione_text = "all'unanimità"
        else:
            voti_contrari = data.get('voti_contrari_nomina', '')
            votazione_text = f"con il voto contrario dei Sigg. {voti_contrari}"
        
        p = doc.add_paragraph(f"Segue breve discussione tra i soci al termine della quale si passa alla votazione con voto palese in forza della quale il Presidente constata che, {votazione_text}, l'assemblea")
        
        p = doc.add_paragraph("d e l i b e r a:")
        run = p.runs[0]
        run.font.bold = True
        run.font.underline = True
        
        p = doc.add_paragraph(f"che la società sia amministrata da un amministratore unico nominato nella persona del sig. {nome_nuovo}")
        
        p = doc.add_paragraph(f"che l'amministratore resti in carica {durata.lower()}")
        
        if data.get('include_compensi', True):
            rimborso_text = " oltre al rimborso delle spese sostenute in ragione del suo ufficio" if data.get('rimborso_spese', True) else ""
            p = doc.add_paragraph(f"di attribuire all'amministratore unico testè nominato il compenso annuo ed omnicomprensivo pari a nominali euro {compenso} al lordo di ritenute fiscali e previdenziali{rimborso_text}. Il compenso verrà liquidato periodicamente, in ragione della permanenza in carica.")
        
        # Accettazione
        p = doc.add_paragraph(f"Il sig. {nome_nuovo}, presente in assemblea in qualità di {qualifica.lower()} accetta l'incarico e ringrazia l'assemblea per la fiducia accordata.")
        
        # Separatore
        p = doc.add_paragraph("*     *     *")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    def _add_closing_section(self, doc, data):
        """Aggiunge sezione chiusura"""
        doc.add_paragraph()
        
        p = doc.add_paragraph("Il Presidente constata che l'ordine del giorno è esaurito e che nessuno chiede la parola.")
        
        p = doc.add_paragraph("Viene quindi redatto il presente verbale e dopo averne data lettura, il Presidente constata che l'assemblea all'unanimità, con voto palese, ne approva il testo [eventualmente unitamente a quanto allegato].")
        
        ora_chiusura = data.get('ora_chiusura', '[ORA]')
        p = doc.add_paragraph(f"L'assemblea viene sciolta alle ore {ora_chiusura}.")
    
    def _add_signatures(self, doc, data):
        """Aggiunge firme"""
        doc.add_paragraph()
        doc.add_paragraph()
        
        table = doc.add_table(rows=2, cols=2)
        table.style = 'Table Grid'
        table.autofit = False
        
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Il Presidente'
        hdr_cells[1].text = 'Il Segretario'
        
        row_cells = table.rows[1].cells
        row_cells[0].text = data.get('presidente', '[PRESIDENTE]')
        row_cells[1].text = data.get('segretario', '[SEGRETARIO]')
        
        for row in table.rows:
            for cell in row.cells:
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

# Registra il template
DocumentTemplateFactory.register_template('verbale_assemblea_revoca_nomina', VerbaleRevocaNominaTemplate) 