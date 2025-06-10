"""
Template per verbale di assemblea - Nomina Consiglio di Amministrazione
"""

import sys
import os

# Aggiungi il path della cartella src (relativo alla root del progetto)
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(os.path.dirname(current_dir), 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from document_templates import DocumentTemplate
import streamlit as st
from datetime import datetime, date
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

class VerbaleConsiglioAmministrazioneTemplate(DocumentTemplate):
    """Template per verbale di nomina Consiglio di Amministrazione"""
    
    def get_template_name(self) -> str:
        return "Nomina Consiglio di Amministrazione"
    
    def get_required_fields(self) -> list:
        return ['denominazione', 'sede_legale', 'capitale_sociale', 'codice_fiscale', 
                'data_assemblea', 'ora_inizio', 'presidente', 'segretario', 'consiglieri']
    
    def get_form_fields(self, extracted_data: dict) -> dict:
        """Definisce i campi del form per questo template"""
        
        # Informazioni base azienda
        st.subheader("📋 Informazioni Azienda")
        col1, col2 = st.columns(2)
        
        with col1:
            denominazione = st.text_input("Denominazione Società", 
                                        value=extracted_data.get('denominazione', ''))
            sede_legale = st.text_input("Sede Legale", 
                                      value=extracted_data.get('sede_legale', ''))
        
        with col2:
            capitale_sociale = st.text_input("Capitale Sociale", 
                                           value=extracted_data.get('capitale_sociale', ''))
            codice_fiscale = st.text_input("Codice Fiscale", 
                                         value=extracted_data.get('codice_fiscale', ''))
        
        # Informazioni assemblea
        st.subheader("📅 Informazioni Assemblea")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            data_assemblea = st.date_input("Data Assemblea", 
                                         value=extracted_data.get('data_assemblea', date.today()))
        
        with col2:
            ora_inizio = st.time_input("Ora Inizio", 
                                     value=extracted_data.get('ora_inizio'))
        
        with col3:
            ora_chiusura = st.time_input("Ora Chiusura", 
                                       value=extracted_data.get('ora_chiusura'))
        
        # Partecipanti
        st.subheader("👥 Partecipanti")
        col1, col2 = st.columns(2)
        
        with col1:
            presidente = st.text_input("Presidente Assemblea", 
                                     value=extracted_data.get('presidente', ''))
        
        with col2:
            segretario = st.text_input("Segretario", 
                                     value=extracted_data.get('segretario', ''))
        
        # Motivo nomina
        st.subheader("📝 Dettagli Nomina")
        motivo_nomina = st.text_area("Motivo della nomina", 
                                   value=extracted_data.get('motivo_nomina', 'Dimissioni dell\'organo in carica'),
                                   height=60)
        
        # Numero consiglieri
        num_consiglieri = st.number_input("Numero Consiglieri", min_value=1, max_value=10, value=3)
        
        # Consiglieri
        st.subheader("👨‍💼 Consiglieri da Nominare")
        consiglieri = []
        
        for i in range(num_consiglieri):
            st.write(f"**Consigliere {i+1}**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                nome = st.text_input(f"Nome Completo {i+1}", key=f"cons_nome_{i}")
                data_nascita = st.date_input(f"Data Nascita {i+1}", key=f"cons_data_{i}")
            
            with col2:
                luogo_nascita = st.text_input(f"Luogo Nascita {i+1}", key=f"cons_luogo_{i}")
                codice_fiscale_cons = st.text_input(f"Codice Fiscale {i+1}", key=f"cons_cf_{i}")
            
            with col3:
                residenza = st.text_input(f"Residenza {i+1}", key=f"cons_res_{i}")
                qualifica = st.selectbox(f"Qualifica {i+1}", 
                                       ["Socio", "Amministratore uscente", "Invitato", "Altro"],
                                       key=f"cons_qual_{i}")
            
            consiglieri.append({
                'nome': nome,
                'data_nascita': data_nascita,
                'luogo_nascita': luogo_nascita,
                'codice_fiscale': codice_fiscale_cons,
                'residenza': residenza,
                'qualifica': qualifica
            })
        
        # Presidente CdA
        st.subheader("🎯 Presidente del Consiglio")
        presidente_cda_option = st.radio("Nomina Presidente CdA",
                                       ["Nomina diretta in assemblea", "Rimanda al Consiglio"])
        
        presidente_cda = ""
        if presidente_cda_option == "Nomina diretta in assemblea":
            presidente_cda = st.selectbox("Seleziona Presidente CdA", 
                                        [c['nome'] for c in consiglieri if c['nome']])
        
        # Compensi
        st.subheader("💰 Compensi")
        include_compensi = st.checkbox("Includi delibera sui compensi", value=True)
        
        compenso_annuo = "0,00"
        rimborso_spese = True
        
        if include_compensi:
            compenso_annuo = st.text_input("Compenso Annuo Totale (€)", value="0,00")
            rimborso_spese = st.checkbox("Rimborso spese", value=True)
        
        # Durata incarico
        durata_incarico = st.text_input("Durata Incarico", 
                                      value="A tempo indeterminato fino a revoca o dimissioni")
        
        return {
            'denominazione': denominazione,
            'sede_legale': sede_legale,
            'capitale_sociale': capitale_sociale,
            'codice_fiscale': codice_fiscale,
            'data_assemblea': data_assemblea,
            'ora_inizio': ora_inizio,
            'ora_chiusura': ora_chiusura,
            'presidente': presidente,
            'segretario': segretario,
            'motivo_nomina': motivo_nomina,
            'consiglieri': consiglieri,
            'presidente_cda': presidente_cda,
            'presidente_cda_option': presidente_cda_option,
            'include_compensi': include_compensi,
            'compenso_annuo': compenso_annuo,
            'rimborso_spese': rimborso_spese,
            'durata_incarico': durata_incarico
        }
    
    def show_preview(self, form_data: dict):
        """Mostra l'anteprima del verbale"""
        st.subheader("📄 Anteprima Verbale")
        
        preview_text = self._generate_preview_text(form_data)
        
        # Mostra anteprima in un container scrollabile
        st.text_area("Anteprima del documento:", 
                    value=preview_text, 
                    height=400, 
                    disabled=True)
    
    def _generate_preview_text(self, data: dict) -> str:
        """Genera il testo di anteprima del verbale"""
        try:
            # Header azienda
            header = f"""{data.get('denominazione', '[DENOMINAZIONE SOCIETÀ]')}
Sede in {data.get('sede_legale', '[SEDE]')}
Capitale sociale Euro {data.get('capitale_sociale', '[CAPITALE]')} i.v.
Codice fiscale: {data.get('codice_fiscale', '[CODICE FISCALE]')}

Verbale di assemblea dei soci
del {data.get('data_assemblea', '[DATA]').strftime('%d/%m/%Y') if hasattr(data.get('data_assemblea'), 'strftime') else '[DATA]'}

Oggi {data.get('data_assemblea', '[DATA]').strftime('%d/%m/%Y') if hasattr(data.get('data_assemblea'), 'strftime') else '[DATA]'} alle ore {data.get('ora_inizio', '[ORA]')} presso la sede sociale {data.get('sede_legale', '[SEDE]')}, si è tenuta l'assemblea generale dei soci, per discutere e deliberare sul seguente:

Ordine del giorno
• nomina del Consiglio di Amministrazione della società"""
            
            if data.get('include_compensi', True):
                header += "\n• attribuzione di compensi al Consiglio di Amministrazione della società"
            
            # Sezione presidente
            presidente_section = f"""

Assume la presidenza ai sensi dell'art. […] dello statuto sociale il Sig. {data.get('presidente', '[PRESIDENTE]')} Amministratore Unico [oppure Presidente del Consiglio di Amministrazione o altro (come da statuto)], il quale dichiara e constata:

1 - che (come indicato anche nell'avviso di convocazione ed in conformità alle previsioni dell'art. […] dello statuto sociale) l'intervento all'assemblea può avvenire anche in audioconferenza

2 - che sono presenti/partecipano all'assemblea:
l'Amministratore Unico nella persona del suddetto Presidente Sig. {data.get('presidente', '[PRESIDENTE]')}

nonché i seguenti soci o loro rappresentanti, recanti complessivamente una quota pari a nominali euro […] pari al […]% del Capitale Sociale:
[Elenco soci partecipanti]

2 - che gli intervenuti sono legittimati alla presente assemblea;
3 - che tutti gli intervenuti si dichiarano edotti sugli argomenti posti all'ordine del giorno.

I presenti all'unanimità chiamano a fungere da segretario il signor {data.get('segretario', '[SEGRETARIO]')}, che accetta l'incarico.

Il Presidente identifica tutti i partecipanti e si accerta che ai soggetti collegati mediante mezzi di telecomunicazione sia consentito seguire la discussione, trasmettere e ricevere documenti, intervenire in tempo reale, con conferma da parte di ciascun partecipante.

Il Presidente constata e fa constatare che l'assemblea risulta regolarmente convocata [oppure totalitaria] e deve ritenersi valida ed atta a deliberare sul citato ordine del giorno.

Si passa quindi allo svolgimento dell'ordine del giorno.

*     *     *"""
            
            # Discussione nomina
            motivo_nomina = data.get('motivo_nomina', 'Dimissioni dell\'organo in carica')
            
            nomina_section = f"""

Il Presidente informa l'assemblea che si rende necessaria la nomina di un nuovo organo amministrativo [{motivo_nomina.lower()}].

Il Presidente ricorda all'assemblea quanto previsto dall'art. 2475 del Codice Civile e dall'atto costitutivo della società [verificare quanto previsto dall'atto costitutivo in tema di amministrazione].

Prende la parola il socio sig. […] che propone di affidare l'amministrazione della società ad un Consiglio di Amministrazione di {len(data.get('consiglieri', []))} membri e composto dai Sigg.:"""
            
            # Lista consiglieri
            consiglieri = data.get('consiglieri', [])
            for cons in consiglieri:
                if cons.get('nome'):
                    data_nascita_str = cons.get('data_nascita').strftime('%d/%m/%Y') if hasattr(cons.get('data_nascita'), 'strftime') else '[Data nascita]'
                    nomina_section += f"\n- {cons.get('nome', '[Nome]')}, nato a {cons.get('luogo_nascita', '[Luogo nascita]')} il {data_nascita_str}, C.F. {cons.get('codice_fiscale', '[CF]')}, residente in {cons.get('residenza', '[Residenza]')}"
            
            nomina_section += """\n\ndando evidenza della comunicazione scritta con cui i candidati, prima di accettare l'eventuale nomina, hanno dichiarato:
• l'insussistenza a loro carico di cause di ineleggibilità alla carica di amministratore di società ed in particolare di non essere stati dichiarati interdetti, inabilitati o falliti e di non essere stati condannati ad una pena che importa l'interdizione, anche temporanea, dai pubblici uffici o l'incapacità ad esercitare uffici direttivi.
• l'insussistenza a loro carico di interdizioni dal ruolo di amministratore adottate da una Stato membro dell'Unione Europea.

[verificare che l'atto costitutivo non preveda ulteriori requisiti per l'assunzione della carica e quanto previsto da leggi speciali in relazione all'esercizio di particolari attività] [se esiste il collegio sindacale o il revisore, verificare eventuali incompatibilità con i neo amministratori]."""
            
            # Compensi
            compensi_section = ""
            if data.get('include_compensi', True):
                compensi_section = """

Il Presidente invita anche l'assemblea a deliberare il compenso da attribuire all'organo amministrativo che verrà nominato, ai sensi dell'art. […] dello statuto sociale."""
            
            # Deliberazione
            deliberazione_section = f"""

Segue breve discussione tra i soci al termine della quale si passa alla votazione con voto palese in forza della quale il Presidente constata che, all'unanimità [oppure con il voto contrario dei Sigg. […] e [eventualmente l'astensione dei Sigg. […]]], l'assemblea

d e l i b e r a:

di affidare l'amministrazione della società ad un Consiglio di Amministrazione composto da {len(consiglieri)} membri che resterà in carica {data.get('durata_incarico', 'a tempo indeterminato fino a revoca o dimissioni').lower()} [verificare che l'atto costitutivo non preveda una durata massima per l'incarico]

di nominare Consiglieri di Amministrazione della società i Sigg.:"""
            
            for cons in consiglieri:
                if cons.get('nome'):
                    data_nascita_str = cons.get('data_nascita').strftime('%d/%m/%Y') if hasattr(cons.get('data_nascita'), 'strftime') else '[Data nascita]'
                    deliberazione_section += f"\n- {cons.get('nome', '[Nome]')}, nato a {cons.get('luogo_nascita', '[Luogo nascita]')} il {data_nascita_str}, C.F. {cons.get('codice_fiscale', '[CF]')}, residente in {cons.get('residenza', '[Residenza]')}"
            
            # Presidente CdA
            if data.get('presidente_cda_option') == "Nomina diretta in assemblea" and data.get('presidente_cda'):
                deliberazione_section += f"\n\ndi nominare Presidente del Consiglio di Amministrazione della società il Sig. {data.get('presidente_cda')} ai sensi dell'art. […] dello statuto sociale"
            else:
                deliberazione_section += "\n\ndi rimandare al Consiglio di Amministrazione testé deliberato la nomina del Presidente ai sensi dell'art. […] dello statuto sociale"
            
            # Compensi nella deliberazione
            if data.get('include_compensi', True):
                compenso = data.get('compenso_annuo', '0,00')
                rimborso_text = " oltre al rimborso delle spese sostenute dai consiglieri in ragione del loro ufficio" if data.get('rimborso_spese', True) else ""
                deliberazione_section += f"\n\ndi attribuire all'organo amministrativo testè nominato il compenso annuo ed omnicomprensivo pari a nominali euro {compenso} al lordo di ritenute fiscali e previdenziali{rimborso_text}. L'organo amministrativo delibererà in merito alla ripartizione del compenso tra i suoi membri, anche in considerazione dei compiti e delle deleghe che verranno attribuite a ciascun consigliere."
            
            # Accettazione
            nomi_cons = [c.get('nome', '[Nome]') for c in consiglieri if c.get('nome')]
            if len(nomi_cons) > 1:
                nomi_str = " e ".join(nomi_cons)
                accettazione_section = f"\n\nI sigg. {nomi_str}, presenti in assemblea in qualità di [indicare (socio, amministratore uscente, invitato o altro)] accettano l'incarico e ringraziano l'assemblea per la fiducia accordata."
            else:
                accettazione_section = f"\n\nIl sig. {nomi_cons[0] if nomi_cons else '[Nome]'}, presente in assemblea accetta l'incarico e ringrazia l'assemblea per la fiducia accordata."
            
            # Chiusura
            chiusura_section = f"""

*     *     *

Il Presidente constata che l'ordine del giorno è esaurito e che nessuno chiede la parola.

Viene quindi redatto il presente verbale e dopo averne data lettura, il Presidente constata che l'assemblea all'unanimità, con voto palese, ne approva il testo [eventualmente unitamente a quanto allegato].

L'assemblea viene sciolta alle ore {data.get('ora_chiusura', '[ORA]')}.


Il Presidente                    Il Segretario
{data.get('presidente', '[PRESIDENTE]')}            {data.get('segretario', '[SEGRETARIO]')}"""
            
            # Combina tutte le sezioni
            full_text = (header + presidente_section + nomina_section + compensi_section + 
                        deliberazione_section + accettazione_section + chiusura_section)
            
            return full_text
            
        except Exception as e:
            return f"Errore nella generazione dell'anteprima: {str(e)}"
    
    def generate_document(self, data: dict) -> Document:
        """Genera il documento Word del verbale"""
        doc = Document()
        return doc
