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
from base_verbale_template import BaseVerbaleTemplate
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from datetime import date
import streamlit as st
import pandas as pd
import re

class VerbaleAmministratoreUnicoTemplate(BaseVerbaleTemplate):
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
            form_data["tipo_assemblea"] = st.selectbox("Tipo assemblea", 
                                                      ["regolarmente convocata", 
                                                       "totalitaria"])
        with col2:
            form_data["durata_incarico"] = st.selectbox("Durata incarico", 
                                                       ["A tempo indeterminato fino a revoca o dimissioni",
                                                        "Tre esercizi", 
                                                        "Un esercizio", 
                                                        "Altra durata"])
            form_data["include_compensi"] = st.checkbox("Includi attribuzione compensi", value=True)
            form_data["socio_proponente"] = st.text_input("Socio proponente la nomina", 
                                                         placeholder="es. Mario Rossi")
        
        # Opzioni avanzate
        st.subheader("⚙️ Opzioni Avanzate del Verbale")
        col1, col2 = st.columns(2)
        with col1:
            form_data["articolo_statuto_presidenza"] = st.text_input("Articolo statuto per presidenza", 
                                                                    placeholder="es. 15", 
                                                                    value="15")
            form_data["articolo_statuto_audioconferenza"] = st.text_input("Articolo statuto per audioconferenza", 
                                                                         placeholder="es. 16", 
                                                                         value="16")
            form_data["articolo_statuto_compensi"] = st.text_input("Articolo statuto per compensi", 
                                                                  placeholder="es. 20", 
                                                                  value="20")
        with col2:
            form_data["include_audioconferenza"] = st.checkbox("Includi riferimento audioconferenza", value=True)
            form_data["include_collegio_sindacale"] = st.checkbox("Includi collegio sindacale", value=False)
            form_data["include_revisore"] = st.checkbox("Includi revisore", value=False)
        
        if form_data["include_collegio_sindacale"]:
            st.subheader("🔍 Collegio Sindacale")
            col1, col2 = st.columns(2)
            with col1:
                form_data["tipo_organo_controllo"] = st.selectbox("Tipo organo di controllo", 
                                                                ["Collegio Sindacale", 
                                                                 "Sindaco Unico"])
            
            if form_data["tipo_organo_controllo"] == "Collegio Sindacale":
                with col2:
                    form_data["sindaci"] = []
                    form_data["sindaci"].append(st.text_input("Presidente Collegio Sindacale", key="presidente_cs"))
                    form_data["sindaci"].append(st.text_input("Sindaco Effettivo 1", key="sindaco_1"))
                    form_data["sindaci"].append(st.text_input("Sindaco Effettivo 2", key="sindaco_2"))
            else:
                with col2:
                    form_data["sindaco_unico"] = st.text_input("Nome Sindaco Unico")
        
        if form_data["include_revisore"]:
            st.subheader("🔍 Revisore")
            col1, col2 = st.columns(2)
            with col1:
                form_data["tipo_revisore"] = st.selectbox("Tipo revisore", 
                                                         ["Revisore contabile", 
                                                          "Società di revisione"])
            with col2:
                form_data["nome_revisore"] = st.text_input("Nome revisore o società")
        
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
        
        # Votazione
        st.subheader("🗳️ Votazione")
        col1, col2 = st.columns(2)
        with col1:
            form_data["tipo_votazione"] = st.selectbox("Tipo di votazione", 
                                                      ["Unanimità", 
                                                       "Maggioranza"])
        
        if form_data["tipo_votazione"] == "Maggioranza":
            with col2:
                form_data["contrari"] = st.text_input("Soci contrari (separati da virgola)")
                form_data["astenuti"] = st.text_input("Soci astenuti (separati da virgola)")
        
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
                    key="preview_text_amministratore_unico"
                )
            except Exception as e:
                st.error(f"Errore nell'anteprima: {e}")
                st.exception(e)
    
    def _generate_preview_text(self, data: dict) -> str:
        """Genera il testo di anteprima del verbale"""
        try:
            # Header dell'azienda con gestione dati mancanti
            denominazione = data.get('denominazione', '[Denominazione]')
            sede_legale = data.get('sede_legale', '[Sede]')
            
            # Gestione capitale sociale - usa il capitale versato se disponibile, altrimenti quello deliberato
            capitale_sociale_raw = data.get('capitale_versato') or data.get('capitale_deliberato') or data.get('capitale_sociale', '[Capitale]')
            capitale_sociale = CommonDataHandler.format_currency(capitale_sociale_raw)
            
            codice_fiscale = data.get('codice_fiscale', '[CF]')
            data_assemblea = data.get('data_assemblea', '[Data]')
            ora_assemblea = data.get('ora_assemblea', '[Ora]')
            
            # Formatta le date se presenti
            data_assemblea_str = data_assemblea.strftime('%d/%m/%Y') if hasattr(data_assemblea, 'strftime') else data_assemblea
            ora_assemblea_str = ora_assemblea.strftime('%H:%M') if hasattr(ora_assemblea, 'strftime') else ora_assemblea
            
            header = f"""{denominazione}
Sede in {sede_legale}
Capitale sociale Euro {capitale_sociale} i.v.
Codice fiscale: {codice_fiscale}

Verbale di assemblea dei soci
del {data_assemblea_str}

Oggi {data_assemblea_str} alle ore {ora_assemblea_str} presso la sede sociale {sede_legale}, si è tenuta l'assemblea generale dei soci, per discutere e deliberare sul seguente:

Ordine del giorno
1. nomina dell'amministratore della società"""
            
            if data.get('include_compensi', True):
                header += "\n2. attribuzione di compensi all'amministratore della società"
            
            # Presidenza
            presidente = data.get('presidente', '[Presidente]')
            ruolo_presidente = data.get('ruolo_presidente', 'Amministratore Unico')
            articolo_statuto_presidenza = data.get('articolo_statuto_presidenza', '15')
            
            presidente_section = f"""
Assume la presidenza ai sensi dell'art. {articolo_statuto_presidenza} dello statuto sociale il Sig. {presidente} {ruolo_presidente}, il quale dichiara e constata:"""

            # Audioconferenza se inclusa
            if data.get('include_audioconferenza', True):
                articolo_statuto_audioconferenza = data.get('articolo_statuto_audioconferenza', '16')
                presidente_section += f"""

1 - che (come indicato anche nell'avviso di convocazione ed in conformità alle previsioni dell'art. {articolo_statuto_audioconferenza} dello statuto sociale) l'intervento all'assemblea può avvenire anche in audioconferenza"""

            presidente_section += f"""

2 - che sono presenti/partecipano all'assemblea:     
l'Amministratore Unico nella persona del suddetto Presidente Sig. {presidente}"""
            
            # Collegio sindacale se presente
            if data.get('include_collegio_sindacale', False):
                tipo_organo_controllo = data.get('tipo_organo_controllo', 'Collegio Sindacale')
                
                if tipo_organo_controllo == 'Collegio Sindacale':
                    sindaci = data.get('sindaci', [])
                    presidente_section += "\n\nper il Collegio Sindacale:"
                    
                    for i, sindaco in enumerate(sindaci):
                        if i == 0 and sindaco:
                            presidente_section += f"\nil Dott. {sindaco} - Presidente"
                        elif sindaco:
                            presidente_section += f"\nil Dott. {sindaco} - Sindaco Effettivo"
                else:
                    sindaco_unico = data.get('sindaco_unico', '')
                    if sindaco_unico:
                        presidente_section += f"\n\nil Sindaco Unico nella persona del Sig. {sindaco_unico}"
            
            # Revisore se presente
            if data.get('include_revisore', False):
                tipo_revisore = data.get('tipo_revisore', 'Revisore contabile')
                nome_revisore = data.get('nome_revisore', '')
                
                if nome_revisore:
                    if tipo_revisore == 'Revisore contabile':
                        presidente_section += f"\n\nil revisore contabile Dott. {nome_revisore}"
                    else:
                        presidente_section += f"\n\nil dott. {nome_revisore} in rappresentanza della società di revisione incaricata del controllo contabile"
            
            # Soci presenti
            soci = data.get('soci', [])
            total_quota_euro = 0.0
            total_quota_percentuale = 0.0
            
            # Calcola totali
            capitale_sociale_float = 0.0
            try:
                capitale_per_calcoli = data.get('capitale_versato') or data.get('capitale_deliberato') or data.get('capitale_sociale', '0')
                capitale_sociale_str = str(capitale_per_calcoli).replace('.', '').replace(',', '.')
                capitale_sociale_float = float(capitale_sociale_str)
            except ValueError:
                pass
                
            for socio in soci:
                if isinstance(socio, dict):
                    try:
                        quota_euro_str = str(socio.get('quota_euro', '0')).replace('.', '').replace(',', '.')
                        if quota_euro_str and quota_euro_str != '0':
                            total_quota_euro += float(quota_euro_str)
                    except ValueError:
                        pass
                    
                    quota_percentuale_raw = socio.get('quota_percentuale', '')
                    if quota_percentuale_raw and str(quota_percentuale_raw).strip() != '':
                        try:
                            perc_clean = str(quota_percentuale_raw).replace('%', '').replace(',', '.').strip()
                            total_quota_percentuale += float(perc_clean)
                        except ValueError:
                            pass
                    else:
                        try:
                            quota_euro_val = float(str(socio.get('quota_euro', '0')).replace('.', '').replace(',', '.'))
                            if quota_euro_val > 0 and capitale_sociale_float > 0:
                                perc_individuale = (quota_euro_val / capitale_sociale_float * 100)
                                total_quota_percentuale += perc_individuale
                        except ValueError:
                            pass

            # Formatta i totali per la visualizzazione
            formatted_total_quota_euro = CommonDataHandler.format_currency(total_quota_euro)
            formatted_total_quota_percentuale = CommonDataHandler.format_percentage(total_quota_percentuale)

            # Sezione soci - inserita dopo il presidente e prima della sezione partecipanti
            soci_section = f"""
nonché i seguenti soci o loro rappresentanti, recanti complessivamente una quota pari a nominali euro {formatted_total_quota_euro} pari al {formatted_total_quota_percentuale} del Capitale Sociale:"""
            
            for socio in soci:
                if isinstance(socio, dict):
                    nome = socio.get('nome', '[Nome Socio]')
                    
                    quota_euro_raw = socio.get('quota_euro', '')
                    quota_percentuale_raw = socio.get('quota_percentuale', '')
                    
                    if not quota_euro_raw or str(quota_euro_raw).strip() == '':
                        quota = '[Quota]'
                    else:
                        quota = CommonDataHandler.format_currency(quota_euro_raw)
                    
                    if quota_percentuale_raw and str(quota_percentuale_raw).strip() != '':
                        try:
                            perc_clean = str(quota_percentuale_raw).replace('%', '').replace(',', '.').strip()
                            perc_val = float(perc_clean)
                            percentuale = CommonDataHandler.format_percentage(perc_val)
                        except ValueError:
                            percentuale = str(quota_percentuale_raw)
                            if not percentuale.endswith('%'):
                                percentuale += '%'
                    else:
                        quota_euro_val = 0.0
                        try:
                            quota_euro_val = float(str(quota_euro_raw).replace('.', '').replace(',', '.'))
                        except ValueError:
                            pass
                        
                        if quota_euro_val > 0 and capitale_sociale_float > 0:
                            quota_percentuale_individuale = (quota_euro_val / capitale_sociale_float * 100)
                            percentuale = CommonDataHandler.format_percentage(quota_percentuale_individuale)
                        else:
                            percentuale = '[Percentuale]'
                    
                    tipo_soggetto = socio.get('tipo_soggetto', 'Persona Fisica')
                    tipo_partecipazione = socio.get('tipo_partecipazione', 'Diretta')
                    
                    if tipo_partecipazione == 'Delegato':
                        delegato = socio.get('delegato', '')
                        if delegato:
                            soci_section += f"\nil Sig {nome} delegato del socio Sig {delegato} recante una quota pari a nominali euro {quota} pari al {percentuale} del Capitale Sociale"
                        else:
                            soci_section += f"\nil Sig {nome} socio recante una quota pari a nominali euro {quota} pari al {percentuale} del Capitale Sociale"
                    else:
                        soci_section += f"\nil Sig {nome} socio recante una quota pari a nominali euro {quota} pari al {percentuale} del Capitale Sociale"
            
            # Concludi la sezione dei partecipanti
            partecipanti_section = """
2 - che gli intervenuti sono legittimati alla presente assemblea;
3 - che tutti gli intervenuti si dichiarano edotti sugli argomenti posti all'ordine del giorno."""
            
            # Segretario
            segretario = data.get('segretario', '[Segretario]')
            segretario_section = f"""
I presenti all'unanimità chiamano a fungere da segretario il signor {segretario}, che accetta l'incarico.

Il Presidente identifica tutti i partecipanti e si accerta che ai soggetti collegati mediante mezzi di telecomunicazione sia consentito seguire la discussione, trasmettere e ricevere documenti, intervenire in tempo reale, con conferma da parte di ciascun partecipante."""
            
            # Tipo assemblea
            tipo_assemblea = data.get('tipo_assemblea', 'regolarmente convocata')
            
            segretario_section += f"""

Il Presidente constata e fa constatare che l'assemblea risulta {tipo_assemblea} e deve ritenersi valida ed atta a deliberare sul citato ordine del giorno.

Si passa quindi allo svolgimento dell'ordine del giorno.

*     *     *"""
            
            # Discussione nomina amministratore unico
            motivo_nomina = data.get('motivo_nomina', 'Dimissioni dell\'organo in carica')
            admin_unico = data.get('amministratore_unico', {})
            nome_admin = admin_unico.get('nome', '')
            socio_proponente = data.get('socio_proponente', '')
            
            nomina_section = f"""
Il Presidente informa l'assemblea che si rende necessaria la nomina di un nuovo organo amministrativo per {motivo_nomina.lower()}. 

Il Presidente ricorda all'assemblea quanto previsto dall'art. 2475 del Codice Civile e dall'atto costitutivo della società."""

            if socio_proponente:
                nomina_section += f"""

Prende la parola il socio sig. {socio_proponente} che propone di nominare Amministratore Unico della società il sig. {nome_admin}, dando evidenza della comunicazione scritta con cui il candidato, prima di accettare l'eventuale nomina, ha dichiarato:"""
            else:
                nomina_section += f"""

Il Presidente propone di nominare Amministratore Unico della società il sig. {nome_admin}, dando evidenza della comunicazione scritta con cui il candidato, prima di accettare l'eventuale nomina, ha dichiarato:"""
                
            nomina_section += """

l'insussistenza a suo carico di cause di ineleggibilità alla carica di amministratore di società ed in particolare di non essere stato dichiarato interdetto, inabilitato o fallito e di non essere stato condannato ad una pena che importa l'interdizione, anche temporanea, dai pubblici uffici o l'incapacità ad esercitare uffici direttivi. 

l'insussistenza a suo carico di interdizioni dal ruolo di amministratore adottate da una Stato membro dell'Unione Europea."""
            
            # Compensi se inclusi
            compensi_section = ""
            if data.get('include_compensi', True):
                articolo_statuto_compensi = data.get('articolo_statuto_compensi', '20')
                compensi_section = f"""

Il Presidente invita anche l'assemblea a deliberare il compenso da attribuire all'organo amministrativo che verrà nominato, ai sensi dell'art. {articolo_statuto_compensi} dello statuto sociale."""
            
            # Deliberazione
            durata_incarico = data.get('durata_incarico', 'A tempo indeterminato fino a revoca o dimissioni')
            compenso_annuo = data.get('compenso_annuo', '0,00')
            tipo_votazione = data.get('tipo_votazione', 'Unanimità')
            
            deliberazione_section = """
Segue breve discussione tra i soci al termine della quale si passa alla votazione con voto palese in forza della quale il Presidente constata che,"""
            
            if tipo_votazione == 'Unanimità':
                deliberazione_section += " all'unanimità,"
            else:
                contrari = data.get('contrari', '')
                astenuti = data.get('astenuti', '')
                
                if contrari:
                    deliberazione_section += f" con il voto contrario dei Sigg. {contrari}"
                    if astenuti:
                        deliberazione_section += f" e l'astensione dei Sigg. {astenuti},"
                    else:
                        deliberazione_section += ","
                elif astenuti:
                    deliberazione_section += f" con l'astensione dei Sigg. {astenuti},"
            
            deliberazione_section += f"""

l'assemblea

d e l i b e r a:

che la società sia amministrata da un amministratore unico nominato nella persona del sig. {nome_admin}

che l'amministratore resti in carica {durata_incarico.lower()}"""

            if data.get('include_compensi', True):
                rimborso_text = " oltre al rimborso delle spese sostenute in ragione del suo ufficio" if data.get('rimborso_spese', True) else ""
                modalita_liquidazione = data.get('modalita_liquidazione', 'periodicamente')
                
                deliberazione_section += f"""

di attribuire all'amministratore unico testè nominato il compenso annuo ed omnicomprensivo pari a nominali euro {compenso_annuo} al lordo di ritenute fiscali e previdenziali{rimborso_text}. Il compenso verrà liquidato {modalita_liquidazione.lower()}, in ragione della permanenza in carica."""
            
            # Accettazione
            qualifica = admin_unico.get('qualifica', 'socio')
            accettazione_section = f"""

Il sig. {nome_admin}, presente in assemblea in qualità di {qualifica.lower()}, accetta l'incarico e ringrazia l'assemblea per la fiducia accordata."""
            
            # Chiusura
            ora_chiusura = data.get('ora_chiusura', data.get('ora_assemblea', '[Ora]'))
            ora_chiusura_str = ora_chiusura.strftime('%H:%M') if hasattr(ora_chiusura, 'strftime') else ora_chiusura
            
            chiusura_section = f"""

*     *     *

Il Presidente constata che l'ordine del giorno è esaurito e che nessuno chiede la parola. 

Viene quindi redatto il presente verbale e dopo averne data lettura, il Presidente constata che l'assemblea all'unanimità, con voto palese, ne approva il testo. 

L'assemblea viene sciolta alle ore {ora_chiusura_str}.


Il Presidente                    Il Segretario
{presidente}            {segretario}"""
            
            # Combina tutte le sezioni
            full_text = (header + presidente_section + soci_section + partecipanti_section + 
                        segretario_section + nomina_section + compensi_section + 
                        deliberazione_section + accettazione_section + chiusura_section)
            
            return full_text
            
        except Exception as e:
            return f"Errore nella generazione dell'anteprima: {str(e)}"
    
    def generate_document(self, data: dict) -> Document:
        """Genera il documento Word del verbale"""
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
                # Setup stili del documento anche quando usiamo template
                self._setup_document_styles(doc)
            else:
                doc = Document()
                # Setup stili del documento
                self._setup_document_styles(doc)
        except Exception as e:
            # Fallback a documento vuoto se il template non può essere caricato
            doc = Document()
            self._setup_document_styles(doc)
        
        # Assicurati che la variabile soci sia definita per evitare errori
        if 'soci' not in data:
            data['soci'] = []
        
        # Aggiungi header azienda
        self._add_company_header(doc, data)
        
        # Aggiungi titolo verbale
        self._add_verbale_title(doc, data)
        
        # Aggiungi sezione di apertura
        self._add_opening_section(doc, data)
        
        # Aggiungi partecipanti
        self._add_participants_section(doc, data)
        
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
        
        # Stile per il titolo della società
        if 'TitoloSocieta' not in styles:
            title_style = styles.add_style('TitoloSocieta', WD_STYLE_TYPE.PARAGRAPH)
            title_style.font.name = 'Times New Roman'
            title_style.font.size = Pt(14)
            title_style.font.bold = True
            title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            title_style.paragraph_format.space_after = Pt(6)
        
        # Stile per il corpo del testo
        if 'BodyText' not in styles:
            body_style = styles.add_style('BodyText', WD_STYLE_TYPE.PARAGRAPH)
            body_style.font.name = 'Times New Roman'
            body_style.font.size = Pt(12)
            body_style.paragraph_format.space_after = Pt(6)
            body_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    def _add_company_header(self, doc, data):
        """Aggiunge l'header con i dati della società"""
        try:
            p = doc.add_paragraph(style='TitoloSocieta')
        except KeyError:
            p = doc.add_paragraph()
        
        run = p.add_run(data.get('denominazione', '[DENOMINAZIONE]'))
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        try:
            p = doc.add_paragraph(style='TitoloSocieta')
        except KeyError:
            p = doc.add_paragraph()
        
        run = p.add_run(f"Sede in {data.get('sede_legale', '[SEDE]')}")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        try:
            p = doc.add_paragraph(style='TitoloSocieta')
        except KeyError:
            p = doc.add_paragraph()
        
        capitale_sociale = CommonDataHandler.format_currency(data.get('capitale_sociale', '[CAPITALE]'))
        run = p.add_run(f"Capitale sociale Euro {capitale_sociale} i.v.")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        try:
            p = doc.add_paragraph(style='TitoloSocieta')
        except KeyError:
            p = doc.add_paragraph()
        
        run = p.add_run(f"Codice fiscale: {data.get('codice_fiscale', '[CF]')}")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def _add_verbale_title(self, doc, data):
        """Aggiunge il titolo del verbale"""
        doc.add_paragraph()
        
        try:
            p = doc.add_paragraph(style='TitoloSocieta')
        except KeyError:
            p = doc.add_paragraph()
        
        run = p.add_run("Verbale di assemblea dei soci")
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(16)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        data_str = data.get('data_assemblea').strftime('%d/%m/%Y') if hasattr(data.get('data_assemblea'), 'strftime') else '[DATA]'
        
        try:
            p = doc.add_paragraph(style='TitoloSocieta')
        except KeyError:
            p = doc.add_paragraph()
        
        run = p.add_run(f"del {data_str}")
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(16)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def _add_opening_section(self, doc, data):
        """Aggiunge la sezione di apertura del verbale"""
        doc.add_paragraph()
        
        try:
            p = doc.add_paragraph(style='BodyText')
        except KeyError:
            p = doc.add_paragraph()
        
        # Format data assemblea
        data_val = data.get('data_assemblea', '[DATA]')
        if hasattr(data_val, 'strftime'):
            data_str = data_val.strftime('%d/%m/%Y')
        else:
            data_str = str(data_val)
        
        # Format ora assemblea - usa ora_chiusura se non c'è ora_assemblea
        ora_val = data.get('ora_assemblea') or data.get('ora_chiusura', '[ORA]')
        if hasattr(ora_val, 'strftime'):
            ora_str = ora_val.strftime('%H:%M')
        else:
            ora_str = str(ora_val) or '[ORA]'
        
        sede = data.get('sede_legale', '[SEDE]')
        
        opening_text = f"Oggi {data_str} alle ore {ora_str} presso la sede sociale {sede}, si è tenuta l'assemblea generale dei soci, per discutere e deliberare sul seguente:"
        
        run = p.add_run(opening_text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        # Ordine del giorno
        doc.add_paragraph()
        
        try:
            p = doc.add_paragraph(style='BodyText')
        except KeyError:
            p = doc.add_paragraph()
        
        run = p.add_run("Ordine del giorno")
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        try:
            p = doc.add_paragraph(style='BodyText')
        except KeyError:
            p = doc.add_paragraph()
        
        run = p.add_run("1. nomina dell'amministratore della società")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        if data.get('include_compensi', True):
            try:
                p = doc.add_paragraph(style='BodyText')
            except KeyError:
                p = doc.add_paragraph()
            
            run = p.add_run("2. attribuzione di compensi all'amministratore della società")
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)

    def _add_participants_section(self, doc, data):
        """Aggiunge la sezione dei partecipanti"""
        doc.add_paragraph()
        
        try:
            p = doc.add_paragraph(style='BodyText')
        except KeyError:
            p = doc.add_paragraph()
        
        presidente = data.get('presidente', '[PRESIDENTE]')
        ruolo_presidente = data.get('ruolo_presidente', 'Amministratore Unico')
        
        participants_text = f"Assume la presidenza ai sensi dell'art. [...] dello statuto sociale il Sig. {presidente} {ruolo_presidente}, il quale dichiara e constata:"
        
        run = p.add_run(participants_text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        # Aggiungi la sezione dei soci se presenti
        soci = data.get('soci', [])
        if soci:
            self._add_soci_section(doc, data)

    def _add_soci_section(self, doc, data):
        """Aggiunge la sezione dettagliata dei soci"""
        soci = data.get('soci', [])
        
        if not soci:
            return
        
        # Calcola totali
        total_quota_euro = 0.0
        total_quota_percentuale = 0.0
        
        # Parse capitale_sociale as float
        capitale_sociale_float = 0.0
        try:
            capitale_per_calcoli = data.get('capitale_versato') or data.get('capitale_deliberato') or data.get('capitale_sociale', '0')
            capitale_sociale_str = str(capitale_per_calcoli).replace('.', '').replace(',', '.')
            capitale_sociale_float = float(capitale_sociale_str)
        except ValueError:
            pass
        
        for socio in soci:
            if isinstance(socio, dict):
                # Calcola totale quote in euro
                try:
                    quota_euro_str = str(socio.get('quota_euro', '0')).replace('.', '').replace(',', '.')
                    if quota_euro_str and quota_euro_str != '0':
                        total_quota_euro += float(quota_euro_str)
                except ValueError:
                    pass
                
                # Calcola totale percentuali
                quota_percentuale_raw = socio.get('quota_percentuale', '')
                if quota_percentuale_raw and str(quota_percentuale_raw).strip() != '':
                    try:
                        perc_clean = str(quota_percentuale_raw).replace('%', '').replace(',', '.').strip()
                        total_quota_percentuale += float(perc_clean)
                    except ValueError:
                        pass
                else:
                    # Calcola basandosi sulla quota euro
                    try:
                        quota_euro_val = float(str(socio.get('quota_euro', '0')).replace('.', '').replace(',', '.'))
                        if quota_euro_val > 0 and capitale_sociale_float > 0:
                            perc_individuale = (quota_euro_val / capitale_sociale_float * 100)
                            total_quota_percentuale += perc_individuale
                    except ValueError:
                        pass
        
        # Formatta i totali
        formatted_total_quota_euro = CommonDataHandler.format_currency(total_quota_euro)
        formatted_total_quota_percentuale = CommonDataHandler.format_percentage(total_quota_percentuale)
        
        # Intestazione soci
        try:
            p = doc.add_paragraph(style='BodyText')
        except KeyError:
            p = doc.add_paragraph()
        
        run = p.add_run(f"nonché i seguenti soci o loro rappresentanti, recanti complessivamente una quota pari a nominali euro {formatted_total_quota_euro} pari al {formatted_total_quota_percentuale} del Capitale Sociale:")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        # Lista dei soci
        for socio in soci:
            if isinstance(socio, dict):
                nome = socio.get('nome', '[Nome Socio]')
                
                # Gestione quote
                quota_euro_raw = socio.get('quota_euro', '')
                quota_percentuale_raw = socio.get('quota_percentuale', '')
                
                # Formatta quota in euro
                if not quota_euro_raw or str(quota_euro_raw).strip() == '':
                    quota = '[Quota]'
                else:
                    quota = CommonDataHandler.format_currency(quota_euro_raw)
                
                # Gestione percentuale
                if quota_percentuale_raw and str(quota_percentuale_raw).strip() != '':
                    try:
                        perc_clean = str(quota_percentuale_raw).replace('%', '').replace(',', '.').strip()
                        perc_val = float(perc_clean)
                        percentuale = CommonDataHandler.format_percentage(perc_val)
                    except ValueError:
                        percentuale = str(quota_percentuale_raw)
                        if not percentuale.endswith('%'):
                            percentuale += '%'
                else:
                    # Calcola la percentuale
                    quota_euro_val = 0.0
                    try:
                        quota_euro_val = float(str(quota_euro_raw).replace('.', '').replace(',', '.'))
                    except ValueError:
                        pass
                    
                    if quota_euro_val > 0 and capitale_sociale_float > 0:
                        quota_percentuale_individuale = (quota_euro_val / capitale_sociale_float * 100)
                        percentuale = CommonDataHandler.format_percentage(quota_percentuale_individuale)
                    else:
                        percentuale = '[Percentuale]'
                
                tipo_soggetto = socio.get('tipo_soggetto', 'Persona Fisica')
                
                # Crea il paragrafo per il socio
                try:
                    p = doc.add_paragraph(style='BodyText')
                except KeyError:
                    p = doc.add_paragraph()
                
                if tipo_soggetto == 'Società':
                    socio_text = f"la società {nome} socio recante una quota pari a nominali euro {quota} pari al {percentuale} del Capitale Sociale"
                else:
                    socio_text = f"il Sig {nome} socio recante una quota pari a nominali euro {quota} pari al {percentuale} del Capitale Sociale"
                
                run = p.add_run(socio_text)
                run.font.name = 'Times New Roman'
                run.font.size = Pt(12)

    def _add_nomination_discussion(self, doc, data):
        """Aggiunge la discussione sulla nomina"""
        admin_unico = data.get('amministratore_unico', {})
        nome_admin = admin_unico.get('nome', '[NOME AMMINISTRATORE]')
        
        try:
            p = doc.add_paragraph(style='BodyText')
        except KeyError:
            p = doc.add_paragraph()
        
        run = p.add_run(f"Il Presidente propone di nominare Amministratore Unico della società il sig. {nome_admin}.")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        # Deliberazione
        durata_incarico = data.get('durata_incarico', 'A tempo indeterminato fino a revoca o dimissioni')
        compenso_annuo = data.get('compenso_annuo', '0,00')
        
        try:
            p = doc.add_paragraph(style='BodyText')
        except KeyError:
            p = doc.add_paragraph()
        
        run = p.add_run("L'assemblea delibera:")
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        try:
            p = doc.add_paragraph(style='BodyText')
        except KeyError:
            p = doc.add_paragraph()
        
        run = p.add_run(f"- di nominare Amministratore Unico il sig. {nome_admin}")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        try:
            p = doc.add_paragraph(style='BodyText')
        except KeyError:
            p = doc.add_paragraph()
        
        run = p.add_run(f"- durata incarico: {durata_incarico}")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        if data.get('include_compensi', True):
            try:
                p = doc.add_paragraph(style='BodyText')
            except KeyError:
                p = doc.add_paragraph()
            
            run = p.add_run(f"- compenso annuo: euro {compenso_annuo}")
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)

    def _add_closing_section(self, doc, data):
        """Aggiunge la sezione di chiusura"""
        try:
            p = doc.add_paragraph(style='BodyText')
        except KeyError:
            p = doc.add_paragraph()
        
        # Ora di chiusura (usa ora_assemblea se non specificata)
        ora_val = data.get('ora_chiusura', data.get('ora_assemblea', '[ORA]'))
        if hasattr(ora_val, 'strftime'):
            ora_str = ora_val.strftime('%H:%M')
        else:
            ora_str = str(ora_val) or '[ORA]'
        
        run = p.add_run(f"L'assemblea viene sciolta alle ore {ora_str}.")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)

    def _add_signatures(self, doc, data):
        """Aggiunge le firme"""
        doc.add_paragraph()
        doc.add_paragraph()
        
        try:
            p = doc.add_paragraph(style='BodyText')
        except KeyError:
            p = doc.add_paragraph()
        
        run = p.add_run("Il Presidente                    Il Segretario")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        try:
            p = doc.add_paragraph(style='BodyText')
        except KeyError:
            p = doc.add_paragraph()
        
        presidente = data.get('presidente', '[PRESIDENTE]')
        segretario = data.get('segretario', '[SEGRETARIO]')
        run = p.add_run(f"{presidente}            {segretario}")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)

# Registrazione del template nel factory
DocumentTemplateFactory.register_template('verbale_assemblea_amministratore_unico_template', VerbaleAmministratoreUnicoTemplate)
