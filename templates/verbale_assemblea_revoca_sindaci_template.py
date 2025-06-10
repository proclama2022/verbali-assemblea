"""
Template per Verbale di Assemblea - Revoca dei sindaci e provvedimenti conseguenti
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

class VerbaleRevocaSindaciTemplate(DocumentTemplate):
    """Template per Verbale di Assemblea - Revoca dei sindaci e provvedimenti conseguenti"""
    
    def get_template_name(self) -> str:
        return "Revoca dei sindaci e provvedimenti conseguenti"
    
    def get_required_fields(self) -> list:
        return [
            "denominazione", "sede_legale", "capitale_sociale", "codice_fiscale",
            "data_assemblea", "ora_assemblea", "presidente", "segretario", 
            "soci", "occasione_irregolarita", "gravi_irregolarita"
        ]
    
    def get_form_fields(self, extracted_data: dict) -> dict:
        """Genera i campi del form per Streamlit"""
        form_data = {}
        
        # Dati azienda standardizzati
        form_data.update(CommonDataHandler.extract_and_populate_company_data(extracted_data))
        
        # Dati assemblea standardizzati
        form_data.update(CommonDataHandler.extract_and_populate_assembly_data(extracted_data))
        
        # Configurazioni specifiche
        st.subheader("⚖️ Configurazioni Specifiche Revoca Sindaci")
        
        col1, col2 = st.columns(2)
        with col1:
            form_data["ruolo_presidente"] = st.selectbox("Ruolo del presidente", 
                                                        ["Amministratore Unico", 
                                                         "Presidente del Consiglio di Amministrazione",
                                                         "Altro (come da statuto)"])
            form_data["tipo_collegio"] = st.selectbox("Tipo di collegio sindacale", 
                                                     ["Collegio Sindacale (3 membri)", 
                                                      "Sindaco Unico"])
        with col2:
            form_data["include_consiglio_amministrazione"] = st.checkbox("Include Consiglio di Amministrazione", value=False)
            form_data["include_revisore"] = st.checkbox("Include revisore contabile", value=False)
        
        # Partecipanti standardizzati
        participants_data = CommonDataHandler.extract_and_populate_participants_data(
            extracted_data, 
            unique_key_suffix="revoca_sindaci"
        )
        form_data.update(participants_data)
        
        # Sindaci in carica da revocare
        st.subheader("👥 Sindaci da Revocare")
        
        if form_data["tipo_collegio"] == "Collegio Sindacale (3 membri)":
            num_sindaci = 3
            st.info("Collegio Sindacale completo (Presidente + 2 Sindaci Effettivi)")
        else:
            num_sindaci = 1
            st.info("Sindaco Unico")
        
        sindaci_revocandi = []
        for i in range(num_sindaci):
            if num_sindaci == 1:
                st.write("**Sindaco Unico**")
            else:
                ruolo = "Presidente" if i == 0 else f"Sindaco Effettivo {i}"
                st.write(f"**{ruolo}**")
            
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input(f"Nome e Cognome", key=f"sindaco_nome_{i}",
                                   placeholder="es. Dott. Mario Rossi")
            with col2:
                titolo = st.text_input(f"Titolo/Qualifica", key=f"sindaco_titolo_{i}",
                                     placeholder="es. Dottore Commercialista",
                                     value="Dott.")
            
            if nome:
                sindaci_revocandi.append({
                    "nome": nome,
                    "titolo": titolo,
                    "ruolo": "Sindaco Unico" if num_sindaci == 1 else ("Presidente del Collegio Sindacale" if i == 0 else "Sindaco Effettivo")
                })
        
        form_data["sindaci_revocandi"] = sindaci_revocandi
        
        # Dettagli delle irregolarità
        st.subheader("📋 Irregolarità e Circostanze")
        
        form_data["occasione_irregolarita"] = st.text_area(
            "Occasione in cui sono emerse le irregolarità",
            placeholder="es. in occasione di controllo interno, audit, verifica documentale, etc.",
            help="Descrivi quando e in quale contesto sono emerse le irregolarità"
        )
        
        form_data["gravi_irregolarita"] = st.text_area(
            "Descrizione delle gravi irregolarità",
            placeholder="Descrivi dettagliatamente le gravi irregolarità commesse dai sindaci...\n\nEsempio:\n- Mancata partecipazione alle riunioni senza giustificato motivo\n- Omessa vigilanza sui controlli interni\n- Violazione dei doveri di diligenza e correttezza\n- Altri comportamenti contrari ai doveri dell'ufficio",
            height=150,
            help="Elencare in modo dettagliato le irregolarità che giustificano la revoca"
        )
        
        # Dichiarazioni di altri soggetti
        st.subheader("💬 Dichiarazioni Aggiuntive")
        
        col1, col2 = st.columns(2)
        with col1:
            form_data["soggetto_dichiarante"] = st.text_input("Nome del soggetto che prende la parola", 
                                                             placeholder="es. Sig. Luigi Bianchi")
        with col2:
            form_data["ruolo_dichiarante"] = st.selectbox("Ruolo del dichiarante", 
                                                         ["Socio", "Amministratore", "Altro"])
        
        form_data["dichiarazione_aggiuntiva"] = st.text_area(
            "Dichiarazione del soggetto",
            placeholder="Inserire la dichiarazione del soggetto che prende la parola...",
            help="Eventuale dichiarazione di sostegno o chiarimento"
        )
        
        # Votazione
        st.subheader("🗳️ Configurazioni Votazione")
        
        col1, col2 = st.columns(2)
        with col1:
            form_data["votazione_unanime"] = st.checkbox("Votazione unanime", value=True)
            if not form_data["votazione_unanime"]:
                form_data["voti_contrari"] = st.text_input("Voti contrari", 
                                                          placeholder="es. Sig. Rossi, Sig. Verdi")
                form_data["astensioni"] = st.text_input("Astensioni", 
                                                       placeholder="es. Sig. Neri")
        
        with col2:
            form_data["ricorso_tribunale"] = st.checkbox("Include incarico ricorso al Tribunale", value=True)
            form_data["chi_presenta_ricorso"] = st.selectbox("Chi presenta il ricorso", 
                                                           ["Amministratore Unico", 
                                                            "Presidente del Consiglio di Amministrazione"])
        
        # Configurazioni aggiuntive
        st.subheader("⚙️ Configurazioni Aggiuntive")
        
        col1, col2 = st.columns(2)
        with col1:
            form_data["include_traduzione"] = st.checkbox("Include sezione traduzione", value=False)
        with col2:
            form_data["include_presenti_qualita"] = st.checkbox("Include sezione 'presenti in qualità di'", value=False)
        
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
                                                  placeholder="Eventuali note specifiche sulla revoca...",
                                                  height=80)
        
        return form_data
    
    def show_preview(self, form_data: dict):
        """Mostra l'anteprima del documento"""
        st.markdown("---")
        st.subheader("👁️ Anteprima Documento")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            show_preview = st.checkbox("Mostra anteprima", value=False, key="preview_checkbox_revoca_sindaci")
        
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

Oggi {data.get('data_assemblea', '[Data]').strftime('%d/%m/%Y') if hasattr(data.get('data_assemblea'), 'strftime') else '[Data]'} alle ore {data.get('ora_assemblea', '[Ora]').strftime('%H:%M') if hasattr(data.get('ora_assemblea'), 'strftime') else '[Ora]'} presso la sede sociale {data.get('sede_legale', '[Sede]')}, si è tenuta l'assemblea generale dei soci, per discutere e deliberare sul seguente:

Ordine del giorno
Revoca dei sindaci e provvedimenti conseguenti"""
            
            # Sezione presidenza
            ruolo_presidente = data.get('ruolo_presidente', 'Amministratore Unico')
            presidente_section = f"""

Assume la presidenza ai sensi dell'art. […] dello statuto sociale il Sig. {data.get('presidente', '[Presidente]')} {ruolo_presidente}, il quale dichiara e constata:

1 - che (come indicato anche nell'avviso di convocazione ed in conformità alle previsioni dell'art. […] dello statuto sociale) l'intervento all'assemblea può avvenire anche in audioconferenza

2 - che sono presenti/partecipano all'assemblea:
l'{ruolo_presidente} nella persona del suddetto Presidente Sig. {data.get('presidente', '[Presidente]')}"""
            
            # Consiglio di Amministrazione se applicabile
            if data.get('include_consiglio_amministrazione', False):
                presidente_section += """
[oppure
per il Consiglio di Amministrazione:
il Sig […]
il Sig […]
il Sig […]
assente giustificato il Sig […]]"""
            
            # Collegio sindacale
            sindaci = data.get('sindaci_revocandi', [])
            if sindaci:
                if data.get('tipo_collegio') == "Sindaco Unico":
                    sindaco = sindaci[0] if sindaci else {}
                    nome = sindaco.get('nome', '[Nome]')
                    presidente_section += f"""
[eventualmente
il Sindaco Unico nella persona del Sig. {nome}]"""
                else:
                    presidente_section += """
[eventualmente
per il Collegio Sindacale"""
                    for sindaco in sindaci:
                        nome = sindaco.get('nome', '[Nome]')
                        presidente_section += f"\nil {nome}"
                    presidente_section += "]"
            
            # Revisore se presente
            if data.get('include_revisore', False):
                presidente_section += """
[eventualmente, se invitato
il revisore contabile Dott. […]]"""
            
            # Soci presenti
            soci_section = "\nnonché i seguenti soci o loro rappresentanti, [eventualmente così come iscritti a libro soci e] recanti complessivamente una quota pari a nominali euro […] pari al […]% del Capitale Sociale:"
            soci = data.get('soci', [])
            
            for socio in soci:
                if isinstance(socio, dict):
                    nome = socio.get('nome', '[Nome Socio]')
                    quota = socio.get('quota', '[Quota]')
                    percentuale = socio.get('percentuale', '[%]')
                    soci_section += f"\nil Sig {nome} socio recante una quota pari a nominali euro {quota} pari al {percentuale}% del Capitale Sociale"
            
            soci_section += "\n2 - che gli intervenuti sono legittimati alla presente assemblea;\n3 - che tutti gli intervenuti si dichiarano edotti sugli argomenti posti all'ordine del giorno."
            
            # Segretario e traduzione
            segretario_section = f"""

I presenti all'unanimità chiamano a fungere da segretario il signor {data.get('segretario', '[Segretario]')}, che accetta l'incarico.

Il Presidente identifica tutti i partecipanti e si accerta che ai soggetti collegati mediante mezzi di telecomunicazione sia consentito seguire la discussione, trasmettere e ricevere documenti, intervenire in tempo reale, con conferma da parte di ciascun partecipante."""
            
            # Traduzione se necessaria
            if data.get('include_traduzione', False):
                persona_traduzione = data.get('persona_traduzione', '[Nome]')
                lingua = data.get('lingua_traduzione', 'inglese').lower()
                segretario_section += f"""
In particolare, preso atto che il Sig. {persona_traduzione} non conosce la lingua italiana ma dichiara di conoscere la lingua {lingua}, il Presidente dichiara che provvederà a tradurre dall'italiano al {lingua} (e viceversa) gli interventi dei partecipanti alla discussione nonché a tradurre dall'italiano al {lingua} il verbale che sarà redatto al termine della riunione."""
            
            segretario_section += """

Il Presidente constata e fa constatare che l'assemblea risulta regolarmente convocata [oppure totalitaria] e deve ritenersi valida ed atta a deliberare sul citato ordine del giorno.

Si passa quindi allo svolgimento dell'ordine del giorno.

*     *     *"""
            
            # Discussione revoca sindaci
            occasione = data.get('occasione_irregolarita', '[occasione delle irregolarità]')
            irregolarita = data.get('gravi_irregolarita', '[gravi irregolarità riscontrate]')
            
            revoca_section = f"""

Il Presidente [o altro soggetto presente in assemblea (amministratore o socio)] prende la parola dichiarando che, in occasione di {occasione} i sindaci attualmente in carica sono incorsi in gravi irregolarità nell'adempimento dei loro doveri. Più precisamente le gravi irregolarità riscontrate sono le seguenti:

{irregolarita}"""
            
            # Dichiarazione aggiuntiva
            soggetto_dichiarante = data.get('soggetto_dichiarante', '[Nome]')
            dichiarazione = data.get('dichiarazione_aggiuntiva', '[dichiarazione]')
            
            if soggetto_dichiarante and soggetto_dichiarante != '[Nome]':
                revoca_section += f"""

Prende la parola il Sig. {soggetto_dichiarante} che dichiara {dichiarazione}."""
            
            # Votazione
            if data.get('votazione_unanime', True):
                votazione_text = "all'unanimità"
            else:
                voti_contrari = data.get('voti_contrari', '')
                astensioni = data.get('astensioni', '')
                votazione_text = f"con il voto contrario dei Sigg. {voti_contrari}"
                if astensioni:
                    votazione_text += f" e l'astensione dei Sigg. {astensioni}"
            
            chi_ricorso = data.get('chi_presenta_ricorso', 'Amministratore Unico')
            
            deliberazione_section = f"""

Esaurita la discussione, si passa alla votazione con voto palese in forza della quale il Presidente constata che, {votazione_text}, l'assemblea

d e l i b e r a:

la revoca dei sindaci della società dal loro ufficio per giusta causa, dando incarico all'{chi_ricorso} di presentare ricorso al Tribunale per l'approvazione della presente delibera."""
            
            # Chiusura
            chiusura_section = f"""

*     *     *

Il Presidente constata che l'ordine del giorno è esaurito e che nessuno chiede la parola.

Viene quindi redatto il presente verbale e dopo averne data lettura, il Presidente constata che l'assemblea all'unanimità, con voto palese, ne approva il testo [eventualmente unitamente a quanto allegato].

L'assemblea viene sciolta alle ore [{data.get('ora_chiusura', '[Ora]')}].


Il Presidente                    Il Segretario
{data.get('presidente', '[PRESIDENTE]')}            {data.get('segretario', '[SEGRETARIO]')}"""
            
            # Combina tutte le sezioni
            full_text = (header + presidente_section + soci_section + segretario_section + 
                        revoca_section + deliberazione_section + chiusura_section)
            
            return full_text
            
        except Exception as e:
            return f"Errore nella generazione dell'anteprima: {str(e)}"
    
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
        
        p = doc.add_paragraph("Revoca dei sindaci e provvedimenti conseguenti")
    
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
        
        # Consiglio di Amministrazione se presente
        if data.get('include_consiglio_amministrazione', False):
            p = doc.add_paragraph("[oppure")
            p = doc.add_paragraph("per il Consiglio di Amministrazione:")
            p = doc.add_paragraph("il Sig […]")
            p = doc.add_paragraph("il Sig […]")
            p = doc.add_paragraph("il Sig […]")
            p = doc.add_paragraph("assente giustificato il Sig […]]")
        
        # Collegio sindacale
        sindaci = data.get('sindaci_revocandi', [])
        if sindaci:
            if data.get('tipo_collegio') == "Sindaco Unico":
                sindaco = sindaci[0] if sindaci else {}
                nome = sindaco.get('nome', '[Nome]')
                p = doc.add_paragraph("[eventualmente")
                p = doc.add_paragraph(f"il Sindaco Unico nella persona del Sig. {nome}]")
            else:
                p = doc.add_paragraph("[eventualmente")
                p = doc.add_paragraph("per il Collegio Sindacale")
                for sindaco in sindaci:
                    nome = sindaco.get('nome', '[Nome]')
                    p = doc.add_paragraph(f"il {nome}")
                p = doc.add_paragraph("]")
        
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
        
        # Presenti in qualità di
        if data.get('include_presenti_qualita', False):
            p = doc.add_paragraph("[eventualmente")
            p = doc.add_paragraph("4 - che sono altresì presenti, in qualità di […]:")
            p = doc.add_paragraph("il Sig. […]")
            p = doc.add_paragraph("il Sig. […]]")
    
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
        """Aggiunge discussione revoca sindaci"""
        doc.add_paragraph()
        
        occasione = data.get('occasione_irregolarita', '[occasione delle irregolarità]')
        irregolarita = data.get('gravi_irregolarita', '[gravi irregolarità riscontrate]')
        
        p = doc.add_paragraph(f"Il Presidente [o altro soggetto presente in assemblea (amministratore o socio)] prende la parola dichiarando che, in occasione di {occasione} i sindaci attualmente in carica sono incorsi in gravi irregolarità nell'adempimento dei loro doveri. Più precisamente le gravi irregolarità riscontrate sono le seguenti:")
        
        # Irregolarità specifiche
        if irregolarita and irregolarita.strip():
            righe = irregolarita.split('\n')
            for riga in righe:
                if riga.strip():
                    p = doc.add_paragraph(riga.strip())
        else:
            p = doc.add_paragraph("[Inserire le gravi irregolarità]")
        
        # Dichiarazione aggiuntiva
        soggetto_dichiarante = data.get('soggetto_dichiarante', '')
        dichiarazione = data.get('dichiarazione_aggiuntiva', '')
        
        if soggetto_dichiarante and soggetto_dichiarante.strip():
            p = doc.add_paragraph(f"Prende la parola il Sig. {soggetto_dichiarante} che dichiara {dichiarazione if dichiarazione else '[dichiarazione]'}.")
        
        # Votazione
        if data.get('votazione_unanime', True):
            votazione_text = "all'unanimità"
        else:
            voti_contrari = data.get('voti_contrari', '')
            astensioni = data.get('astensioni', '')
            votazione_text = f"con il voto contrario dei Sigg. {voti_contrari}"
            if astensioni:
                votazione_text += f" e l'astensione dei Sigg. {astensioni}"
        
        p = doc.add_paragraph(f"Esaurita la discussione, si passa alla votazione con voto palese in forza della quale il Presidente constata che, {votazione_text}, l'assemblea")
        
        p = doc.add_paragraph("d e l i b e r a:")
        run = p.runs[0]
        run.font.bold = True
        run.font.underline = True
        
        # Deliberazione
        chi_ricorso = data.get('chi_presenta_ricorso', 'Amministratore Unico')
        
        if data.get('ricorso_tribunale', True):
            p = doc.add_paragraph(f"la revoca dei sindaci della società dal loro ufficio per giusta causa, dando incarico all'{chi_ricorso} di presentare ricorso al Tribunale per l'approvazione della presente delibera.")
        else:
            p = doc.add_paragraph("la revoca dei sindaci della società dal loro ufficio per giusta causa.")
        
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
DocumentTemplateFactory.register_template('verbale_assemblea_revoca_sindaci', VerbaleRevocaSindaciTemplate) 