"""
Template per Verbale di Assemblea - Approvazione Bilancio
Questo template è specifico per verbali di approvazione bilancio.
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

class VerbaleApprovazioneBilancioTemplate(DocumentTemplate):
    """Template per Verbale di Assemblea dei Soci - Approvazione Bilancio"""
    
    def get_template_name(self) -> str:
        return "Approvazione Bilancio di Assemblea"
    
    def get_required_fields(self) -> list:
        return [
            "denominazione", "sede_legale", "capitale_sociale", "codice_fiscale",
            "data_assemblea", "ora_assemblea", "presidente", "segretario", 
            "soci", "amministratori"
        ]
    
    def get_form_fields(self, extracted_data: dict) -> dict:
        """Genera i campi del form per Streamlit utilizzando il CommonDataHandler"""
        form_data = {}
        
        # Utilizza il CommonDataHandler per i dati standard
        # Dati azienda standardizzati
        form_data.update(CommonDataHandler.extract_and_populate_company_data(extracted_data))
        
        # Dati assemblea standardizzati
        form_data.update(CommonDataHandler.extract_and_populate_assembly_data(extracted_data))
        
        # Campi specifici per approvazione bilancio
        st.subheader("📋 Configurazioni Specifiche Approvazione Bilancio")
        
        col1, col2 = st.columns(2)
        with col1:
            form_data["ruolo_presidente"] = st.selectbox("Ruolo del presidente", 
                                                        CommonDataHandler.get_standard_ruoli_presidente())
            form_data["data_chiusura"] = st.date_input("Data chiusura bilancio", 
                                                      CommonDataHandler.get_default_date_chiusura())
        with col2:
            # Campi specifici per questo template
            form_data["tipo_bilancio"] = st.selectbox("Tipo di bilancio", 
                                                     ["Ordinario", "Abbreviato", "Micro"])
            form_data["presenza_nota_integrativa"] = st.checkbox("Nota integrativa presente", value=True)
        
        # Partecipanti standardizzati usando il CommonDataHandler
        participants_data = CommonDataHandler.extract_and_populate_participants_data(
            extracted_data, 
            unique_key_suffix="bilancio"
        )
        form_data.update(participants_data)
        
        # Ordine del giorno specifico per approvazione bilancio
        st.subheader("📋 Ordine del Giorno")
        default_odg = f"1. Approvazione del Bilancio di esercizio chiuso al {form_data['data_chiusura'].strftime('%d/%m/%Y')} e dei relativi documenti che lo compongono\n2. Destinazione del risultato dell'esercizio\n3. Deliberazioni inerenti e conseguenti"
        punti_odg = st.text_area("Punti all'ordine del giorno (numerati automaticamente)", 
                                default_odg, height=120)
        form_data["punti_ordine_giorno"] = [p.strip() for p in punti_odg.split("\n") if p.strip()]
        
        # Destinazione risultato migliorata
        st.subheader("💰 Destinazione del Risultato")
        
        col1, col2 = st.columns(2)
        with col1:
            utile_esercizio = st.text_input("Utile dell'esercizio (€)", "0,00", 
                                          help="Inserisci l'utile dell'esercizio per calcolare automaticamente le destinazioni")
            form_data["utile_esercizio"] = utile_esercizio
            
            # Calcola automaticamente le percentuali se c'è un utile
            try:
                utile_value = float(utile_esercizio.replace(",", "."))
                riserva_legale_suggerita = utile_value * 0.05  # 5% a riserva legale
                utile_residuo = utile_value - riserva_legale_suggerita
            except:
                riserva_legale_suggerita = 0
                utile_residuo = 0
        with col2:
            form_data["riserva_legale"] = st.text_input("A riserva legale (€)", 
                                                       f"{riserva_legale_suggerita:.2f}".replace(".", ","))
            form_data["altre_riserve"] = st.text_input("Ad altre riserve (€)", "0,00")
        
        col1, col2 = st.columns(2)
        with col1:
            form_data["dividendi"] = st.text_input("A dividendi (€)", "0,00")
            form_data["riporto_nuovo"] = st.text_input("A nuovo (€)", 
                                                      f"{utile_residuo:.2f}".replace(".", ","))
        with col2:
            form_data["tipo_destinazione"] = st.selectbox("Tipo principale di destinazione", 
                                                         ["A nuovo", "A riserve", "A dividendi", "Mista"])
        
        return form_data
    
    def show_preview(self, form_data: dict):
        """Mostra l'anteprima del documento fuori dal form"""
        # Sezione Anteprima
        st.markdown("---")
        st.subheader("👁️ Anteprima Documento")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            show_preview = st.checkbox("Mostra anteprima", value=False, key="preview_checkbox")
        
        with col2:
            if show_preview:
                st.info("💡 L'anteprima si aggiorna automaticamente con i dati inseriti sopra")
        
        if show_preview:
            try:
                # Debug avanzato: mostra alcuni dati per verificare
                with st.expander("🔍 Debug - Informazioni sui dati", expanded=False):
                    st.write(f"**Tipo dati ricevuti:** {type(form_data)}")
                    st.write(f"**Numero di campi:** {len(form_data) if form_data else 0}")
                    st.write("**Campi principali:**")
                    st.write(f"- Denominazione: {form_data.get('denominazione', 'NON IMPOSTATA')}")
                    st.write(f"- Presidente: {form_data.get('presidente', 'NON IMPOSTATO')}")
                    st.write(f"- Data assemblea: {form_data.get('data_assemblea', 'NON IMPOSTATA')}")
                    st.write(f"- Soci: {len(form_data.get('soci', []))} presenti")
                    
                    # Debug specifico per i soci
                    soci_debug = form_data.get('soci', [])
                    if soci_debug:
                        st.write("**Debug Soci Dettagliato:**")
                        for i, socio in enumerate(soci_debug):
                            st.write(f"  Socio {i+1}: {socio}")
                            # Debug specifico per i nuovi campi
                            tipo_soggetto = socio.get('tipo_soggetto', 'NON TROVATO')
                            rappresentante = socio.get('rappresentante_legale', 'NON TROVATO')
                            st.write(f"    - Tipo Soggetto: {tipo_soggetto}")
                            st.write(f"    - Rappresentante Legale: {rappresentante}")
                            
                            # ⚠️ DEBUG SPECIFICO PER IL PROBLEMA
                            if tipo_soggetto == 'Società':
                                if rappresentante and rappresentante != 'NON TROVATO' and rappresentante.strip():
                                    st.success(f"✅ Società '{socio.get('nome', '')}' ha rappresentante legale: '{rappresentante}'")
                                else:
                                    st.error(f"❌ Società '{socio.get('nome', '')}' NON ha rappresentante legale specificato!")
                                    st.write(f"   Valore grezzo: '{repr(rappresentante)}'")
                            elif tipo_soggetto == 'Persona Fisica':
                                st.info(f"ℹ️ '{socio.get('nome', '')}' è una Persona Fisica (rappresentante legale non necessario)")
                    else:
                        st.write("❌ Nessun dato sui soci trovato")
                    
                    # Mostra tutti i campi disponibili
                    st.write("**Tutti i campi disponibili:**")
                    if form_data:
                        for key, value in form_data.items():
                            if isinstance(value, list):
                                st.write(f"- {key}: lista con {len(value)} elementi")
                            else:
                                preview_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                                st.write(f"- {key}: {preview_value}")
                    else:
                        st.error("❌ form_data è vuoto o None!")
                
                with st.expander("📄 Anteprima del Verbale", expanded=True):
                    # Debug UI per i soci nell'anteprima
                    if st.checkbox("🔍 Debug Soci nell'Anteprima", key="debug_soci_anteprima"):
                        soci_debug = form_data.get('soci', [])
                        st.write("**Dati soci che arrivano all'anteprima:**")
                        for i, socio in enumerate(soci_debug):
                            tipo_soggetto = socio.get('tipo_soggetto', 'NON TROVATO')
                            rappresentante = socio.get('rappresentante_legale', 'NON TROVATO')
                            tipo_part = socio.get('tipo_partecipazione', 'NON TROVATO')
                            delegato = socio.get('delegato', 'NON TROVATO')
                            
                            st.write(f"**Socio {i+1}: {socio.get('nome', 'NOME MANCANTE')}**")
                            st.write(f"  - Tipo Partecipazione: '{tipo_part}'")
                            st.write(f"  - Tipo Soggetto: '{tipo_soggetto}'")
                            st.write(f"  - Delegato: '{delegato}'")
                            st.write(f"  - Rappresentante Legale: '{rappresentante}'")
                            
                            # Test delle condizioni
                            if tipo_part == 'Delegato' and delegato:
                                st.success(f"✅ MATCH: È un delegato")
                                if tipo_soggetto == 'Società':
                                    st.success(f"✅ MATCH: È una società")
                                    if rappresentante:
                                        st.success(f"✅ MATCH: Ha rappresentante legale")
                                    else:
                                        st.error(f"❌ NO MATCH: Rappresentante legale vuoto")
                                else:
                                    st.info(f"ℹ️ INFO: Non è una società")
                            else:
                                st.info(f"ℹ️ INFO: Non è un delegato")
                                if tipo_soggetto == 'Società':
                                    st.success(f"✅ MATCH: È una società diretta")
                                    if rappresentante:
                                        st.success(f"✅ MATCH: Ha rappresentante legale")
                                    else:
                                        st.error(f"❌ NO MATCH: Rappresentante legale vuoto")
                    
                    # Genera anteprima con try/catch dettagliato
                    try:
                        preview_text = self._generate_preview_text(form_data)
                        
                        if not preview_text:
                            st.error("❌ Anteprima vuota - nessun testo generato")
                        elif len(preview_text) < 100:
                            st.warning("⚠️ Anteprima molto breve - possibile errore nei dati")
                            st.code(preview_text)
                        else:
                    # Campo di testo modificabile per l'anteprima
                    edited_preview_text = st.text_area(
                        "Modifica l'anteprima qui (il documento finale userà questo testo):",
                        value=preview_text,
                        height=400,
                        key="editable_preview_text"
                    )
                    # Salva il testo modificato nello stato della sessione per usarlo nella generazione del documento
                    st.session_state['final_document_text'] = edited_preview_text
                            
                            # Statistiche anteprima
                            word_count = len(preview_text.split())
                            char_count = len(preview_text)
                            st.caption(f"📊 Statistiche: {word_count} parole, {char_count} caratteri")
                            
                            # Pulsante per copiare
                            st.code(preview_text[:200] + "..." if len(preview_text) > 200 else preview_text)
                            
                    except Exception as e:
                        st.error(f"❌ Errore nella generazione dell'anteprima: {str(e)}")
                        st.code(f"Errore dettagliato: {repr(e)}")
                        
                        # Debug traceback
                        import traceback
                        st.code(traceback.format_exc())
                        
                        # Mostra i dati per debug
                        st.write("🔍 **Dati completi per debug:**")
                        st.json(form_data)
                        
            except Exception as e:
                st.error(f"❌ Errore generale nell'anteprima: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    
    def _generate_preview_text(self, data: dict) -> str:
        """Genera un'anteprima testuale del verbale seguendo il formato esatto richiesto"""
        try:
            # Verifica che abbiamo i dati essenziali
            if not data:
                return "❌ Nessun dato disponibile per l'anteprima"
            
            if not isinstance(data, dict):
                return f"❌ Dati non validi per l'anteprima: tipo {type(data)} invece di dict"
            
            # Intestazione società
            denominazione = data.get('denominazione', '[DENOMINAZIONE]')
            sede_legale = data.get('sede_legale', '[SEDE]')
            capitale_deliberato = str(data.get('capitale_deliberato', '10.000,00')).strip()
            capitale_versato = str(data.get('capitale_versato', '10.000,00')).strip()
            capitale_sottoscritto = str(data.get('capitale_sottoscritto', '10.000,00')).strip()
            codice_fiscale = data.get('codice_fiscale', '[CODICE FISCALE]')
            
            # Gestione "i.v." (interamente versato) - solo se versato = deliberato per la preview
            if capitale_versato == capitale_deliberato:
                capitale_preview = f"Capitale sociale Euro {capitale_deliberato} i.v."
            else:
                capitale_preview = f"Capitale sociale deliberato Euro {capitale_deliberato}, sottoscritto Euro {capitale_sottoscritto}, versato Euro {capitale_versato}"
            
            preview = f"{denominazione}\n"
            preview += f"Sede in {sede_legale}\n"
            preview += f"{capitale_preview}\n"
            preview += f"Codice fiscale e Partita IVA: {codice_fiscale}\n\n"
            
            # Titolo
            preview += "Verbale di assemblea dei soci\n"
            
            # Data
            data_assemblea = data.get('data_assemblea')
            if data_assemblea:
                try:
                    if hasattr(data_assemblea, 'strftime'):
                        data_str = data_assemblea.strftime('%d/%m/%Y')
                    else:
                        data_str = str(data_assemblea)
                except:
                    data_str = '[DATA]'
            else:
                data_str = '[DATA]'
            
            preview += f"del {data_str}\n\n"
            
            # Apertura assemblea
            ora_inizio = data.get('ora_inizio', '[ORA]')
            luogo = data.get('luogo_assemblea', sede_legale)
            
            preview += f"Oggi {data_str} alle ore {ora_inizio} presso la sede sociale {luogo}, si è tenuta l'assemblea generale dei soci, per discutere e deliberare sul seguente:\n"
            
            # Ordine del giorno
            preview += "Ordine del giorno\n"
            
            # Data chiusura bilancio
            data_chiusura = data.get('data_chiusura')
            if data_chiusura:
                try:
                    if hasattr(data_chiusura, 'strftime'):
                        data_chiusura_str = data_chiusura.strftime('%d/%m/%Y')
                    else:
                        data_chiusura_str = str(data_chiusura)
                except:
                    data_chiusura_str = '[DATA CHIUSURA]'
            else:
                data_chiusura_str = '[DATA CHIUSURA]'
            
            preview += f"Approvazione del Bilancio al {data_chiusura_str} e dei documenti correlati;\n"
            preview += "Delibere consequenziali.\n"
            
            # Presidenza
            presidente = data.get('presidente', '[PRESIDENTE]')
            ruolo_presidente = data.get('ruolo_presidente', 'Amministratore Unico')
            
            preview += f"Assume la presidenza ai sensi dell'art. […] dello statuto sociale il Sig. {presidente} {ruolo_presidente}, il quale dichiara e constata:\n"
            
            # Dichiarazioni preliminari
            preview += "1 - che (come indicato anche nell'avviso di convocazione ed in conformità alle previsioni dell'art. […] dello statuto sociale) l'intervento all'assemblea può avvenire anche in audioconferenza\n"
            preview += "2 - che sono presenti/partecipano all'assemblea:\n"
            
            # Amministratori
            amministratori = data.get('amministratori', [])
            ruolo_presidente = data.get('ruolo_presidente', 'Amministratore Unico')
            
            # Determina se è Amministratore Unico o CdA
            if ruolo_presidente == 'Amministratore Unico' or len(amministratori) <= 1:
                preview += f"l'Amministratore Unico nella persona del suddetto Presidente Sig. {presidente}\n"
            else:
                preview += "per il Consiglio di Amministrazione:\n"
                for amm in amministratori:
                    if isinstance(amm, dict) and amm.get('nome', '').strip():
                        nome = amm.get('nome', '')
                        carica = amm.get('carica', 'Consigliere')
                        if nome != presidente:  # Evita la duplicazione del presidente
                            preview += f"il Sig {nome} ({carica})\n"
            
            # Collegio sindacale (se presente)
            if data.get('collegio_sindacale'):
                preview += "per il Collegio Sindacale:\n"
                preview += "il Dott. [SINDACO 1]\n"
                preview += "il Dott. [SINDACO 2]\n"
                preview += "il Dott. [SINDACO 3]\n"
            
            # Revisore (se presente)
            if data.get('revisore'):
                nome_revisore = data.get('nome_revisore', '[NOME REVISORE]')
                preview += f"il revisore contabile Dott. {nome_revisore}\n"
            
            # Soci presenti - calcolo automatico dei totali
            soci = data.get('soci', [])
            totale_quote_euro = 0
            totale_quote_perc = 0
            soci_presenti = []
            
            if soci and isinstance(soci, list):
                for socio in soci:
                    if isinstance(socio, dict) and socio.get('nome', '').strip() and socio.get('presente', True):
                        nome = socio.get('nome', '').strip()
                        quota_euro_str = socio.get('quota_euro', '0').replace('€', '').replace('Euro', '').strip()
                        quota_perc_str = socio.get('quota_percentuale', '0').replace('%', '').replace(',', '.').strip()
                        tipo_partecipazione = socio.get('tipo_partecipazione', 'Diretto')
                        delegato = socio.get('delegato', '').strip()
                        tipo_soggetto = socio.get('tipo_soggetto', 'Persona Fisica')
                        rappresentante_legale = socio.get('rappresentante_legale', '').strip()
                        
                        # Debug: mostra i valori dei nuovi campi
                        print(f"DEBUG Socio {nome}: tipo_soggetto={tipo_soggetto}, rappresentante_legale={rappresentante_legale}")
                        
                        # Calcola i totali - gestione CORRETTA del formato italiano
                        try:
                            if quota_euro_str:
                                # Gestione del formato italiano: "10.000,00" dove punto=migliaia, virgola=decimali
                                if ',' in quota_euro_str:
                                    # Se c'è una virgola, è il separatore decimale
                                    quota_clean = quota_euro_str.replace('.', '').replace(',', '.')
                                else:
                                    # Se non c'è virgola, rimuovi solo i punti delle migliaia
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
            
            preview += f"nonché i seguenti soci o loro rappresentanti, recanti complessivamente una quota pari a nominali euro {totale_quote_euro:,.2f} pari al {totale_quote_perc:.1f}% del Capitale Sociale:\n"
            
            for socio_info in soci_presenti:
                nome = socio_info['nome']
                quota_euro = socio_info['quota_euro']
                quota_perc = socio_info['quota_percentuale']
                tipo = socio_info['tipo_partecipazione']
                delegato = socio_info['delegato']
                tipo_soggetto = socio_info['tipo_soggetto']
                rappresentante_legale = socio_info['rappresentante_legale']
                
                # DEBUG: Aggiungiamo output dettagliato per ogni socio
                print(f"DEBUG ANTEPRIMA - Socio: {nome}")
                print(f"  - tipo_partecipazione: '{tipo}'")
                print(f"  - tipo_soggetto: '{tipo_soggetto}'")
                print(f"  - delegato: '{delegato}'")
                print(f"  - rappresentante_legale: '{rappresentante_legale}'")
                print(f"  - delegato truthy: {bool(delegato)}")
                print(f"  - rappresentante_legale truthy: {bool(rappresentante_legale)}")
                
                # Gestione completa: delegati e rappresentanti legali
                if tipo == 'Delegato' and delegato:
                    print(f"  -> BRANCH: Delegato")
                    if tipo_soggetto == 'Società':
                        print(f"  -> SUB-BRANCH: Società delegata")
                        preview += f"il Sig {delegato} delegato della società {nome}"
                        if rappresentante_legale:
                            print(f"  -> ADDING: rappresentante legale ({rappresentante_legale})")
                            preview += f" (nella persona del legale rappresentante {rappresentante_legale})"
                        else:
                            print(f"  -> NOT ADDING: rappresentante legale (vuoto o False)")
                        preview += f" recante una quota pari a nominali euro {quota_euro} pari al {quota_perc} del Capitale Sociale\n"
                    else:
                        print(f"  -> SUB-BRANCH: Persona fisica delegata")
                        preview += f"il Sig {delegato} delegato del socio {nome} recante una quota pari a nominali euro {quota_euro} pari al {quota_perc} del Capitale Sociale\n"
                else:
                    print(f"  -> BRANCH: Diretto")
                    if tipo_soggetto == 'Società':
                        print(f"  -> SUB-BRANCH: Società diretta")
                        if rappresentante_legale:
                            print(f"  -> ADDING: rappresentante legale ({rappresentante_legale})")
                            preview += f"la società {nome} nella persona del legale rappresentante {rappresentante_legale} recante una quota pari a nominali euro {quota_euro} pari al {quota_perc} del Capitale Sociale\n"
                        else:
                            print(f"  -> NOT ADDING: rappresentante legale (vuoto o False)")
                            preview += f"la società {nome} recante una quota pari a nominali euro {quota_euro} pari al {quota_perc} del Capitale Sociale\n"
                    else:
                        print(f"  -> SUB-BRANCH: Persona fisica diretta")
                        preview += f"il Sig {nome} socio recante una quota pari a nominali euro {quota_euro} pari al {quota_perc} del Capitale Sociale\n"
            
            preview += "2 - che gli intervenuti sono legittimati alla presente assemblea;\n"
            preview += "3 - che tutti gli intervenuti si dichiarano edotti sugli argomenti posti all'ordine del giorno.\n"
            
            # Segretario
            segretario = data.get('segretario', '[SEGRETARIO]')
            preview += f"I presenti all'unanimità chiamano a fungere da segretario il signor {segretario}, che accetta l'incarico.\n"
            
            # Identificazione partecipanti
            preview += "Il Presidente identifica tutti i partecipanti e si accerta che ai soggetti collegati mediante mezzi di telecomunicazione sia consentito seguire la discussione, trasmettere e ricevere documenti, intervenire in tempo reale, con conferma da parte di ciascun partecipante.\n"
            
            # Constatazione validità
            tipo_convocazione = data.get('tipo_convocazione', 'regolarmente convocata')
            if 'totalitaria' in tipo_convocazione.lower():
                preview += "Il Presidente constata e fa constatare che l'assemblea risulta totalitaria e deve ritenersi valida ed atta a deliberare sul citato ordine del giorno.\n"
            else:
                preview += "Il Presidente constata e fa constatare che l'assemblea risulta regolarmente convocata e deve ritenersi valida ed atta a deliberare sul citato ordine del giorno.\n"
            
            preview += "Si passa quindi allo svolgimento dell'ordine del giorno.\n"
            preview += "*     *     *\n"
            
            # Primo punto - Bilancio
            preview += f"In relazione al primo punto il presidente legge il bilancio al {data_chiusura_str} composto da stato patrimoniale, conto economico e nota integrativa (allegati di seguito al presente verbale);\n"
            
            # Collegio sindacale (se presente)
            if data.get('collegio_sindacale'):
                preview += f"Prende la parola il Presidente del Collegio Sindacale che legge la relazione del collegio sindacale al Bilancio chiuso al {data_chiusura_str} (allegata di seguito al presente verbale).\n"
            
            # Revisore (se presente)
            if data.get('revisore'):
                nome_revisore = data.get('nome_revisore', '[NOME REVISORE]')
                preview += f"Prende infine la parola il Dott. {nome_revisore} che legge la relazione del revisore contabile (allegata di seguito al presente verbale).\n"
            
            # Votazione
            esito = data.get('esito_votazione', 'approvato all\'unanimità')
            if 'unanimità' in esito:
                preview += "Segue breve discussione tra i soci al termine della quale si passa alla votazione con voto palese in forza della quale il Presidente constata che, all'unanimità, l'assemblea\n"
            else:
                preview += "Segue breve discussione tra i soci al termine della quale si passa alla votazione con voto palese in forza della quale il Presidente constata che, [ESITO VOTAZIONE], l'assemblea\n"
            
            preview += "delibera\n"
            preview += f"l'approvazione del bilancio di esercizio chiuso al {data_chiusura_str} e dei relativi documenti che lo compongono.\n"
            preview += "*     *     *\n"
            
            # Secondo punto - Destinazione risultato
            preview += "In relazione al secondo punto posto all'ordine del giorno, il Presidente, "
            if data.get('sentito_parere_sindaci'):
                preview += "sentito il parere favorevole del Collegio Sindacale, "
            
            tipo_risultato = data.get('tipo_risultato', 'Utile')
            if tipo_risultato == 'Perdita':
                preview += "propone all'assemblea di ripianare la perdita:\n"
            else:
                preview += "propone all'assemblea di così destinare il risultato d'esercizio:\n"
            
            destinazioni = data.get('destinazioni_risultato', [])
            if destinazioni and isinstance(destinazioni, list):
                for dest in destinazioni:
                    if dest and str(dest).strip():
                        preview += f"{str(dest).strip()}\n"
            else:
                if tipo_risultato == 'Perdita':
                    preview += "- al ripianamento della perdita per Euro [SPECIFICARE]\n"
                else:
                    preview += "- a riserva legale per il 5% dell'utile di esercizio\n- a riserva straordinaria\n- a dividendo\n"
            
            preview += "\n*     *     *\n"
            
            # Chiusura
            preview += "Il Presidente constata che l'ordine del giorno è esaurito e che nessuno chiede la parola.\n"
            preview += "Viene quindi redatto il presente verbale e dopo averne data lettura, il Presidente constata che l'assemblea all'unanimità, con voto palese, ne approva il testo.\n"
            
            ora_fine = data.get('ora_fine', '[ORA FINE]')
            preview += f"L'assemblea viene sciolta alle ore {ora_fine}.\n"
            
            return preview
            
        except Exception as e:
            import traceback
            error_msg = f"❌ ERRORE nella generazione dell'anteprima:\n{str(e)}\n\n"
            error_msg += f"Tipo errore: {type(e).__name__}\n"
            error_msg += f"Traceback completo:\n{traceback.format_exc()}\n\n"
            error_msg += f"Dati ricevuti: {type(data)} con {len(data) if data else 0} elementi\n"
            if data:
                error_msg += f"Chiavi disponibili: {list(data.keys())}\n"
                error_msg += f"Primi 3 elementi: {dict(list(data.items())[:3])}\n"
            return error_msg
    
    def generate_document(self, data: dict) -> Document:
        """Genera il documento Word con formattazione professionale"""
        import streamlit as st
        
        # Controlla se c'è un testo modificato dall'utente nell'anteprima
        if hasattr(st.session_state, 'final_document_text') and st.session_state.final_document_text:
            # Usa il testo modificato dall'utente
            return self._create_document_from_text(st.session_state.final_document_text)
        else:
            # Genera il documento normalmente se non c'è testo modificato
            doc = Document()
            
            # Configurazione stili del documento
            self._setup_document_styles(doc)
            
            # Intestazione società
            self._add_company_header(doc, data)
            
            # Titolo verbale
            self._add_verbale_title(doc, data)
            
            # Apertura assemblea
            self._add_opening_section(doc, data)
            
            # Partecipanti
            self._add_participants_section(doc, data)
            
            # Constatazioni preliminari
            self._add_preliminary_statements(doc, data)
            
            # Svolgimento ordine del giorno (specifico per approvazione bilancio)
            self._add_bilancio_discussion(doc, data)
            
            # Chiusura
            self._add_closing_section(doc, data)
            
            # Firme
            self._add_signatures(doc, data)
            
            return doc
    
    def _create_document_from_text(self, text: str) -> Document:
        """Crea un documento Word dal testo modificato dall'utente"""
        doc = Document()
        
        # Configurazione stili di base
        self._setup_document_styles(doc)
        
        # Dividi il testo in paragrafi e aggiungili al documento
        paragraphs = text.split('\n')
        
        for paragraph_text in paragraphs:
            if paragraph_text.strip():  # Ignora le righe vuote
                p = doc.add_paragraph(paragraph_text)
                # Applica formattazione di base
                p.style.font.name = 'Times New Roman'
                p.style.font.size = Pt(11)
            else:
                # Aggiungi una riga vuota
                doc.add_paragraph()
        
        return doc
    
    def _setup_document_styles(self, doc):
        """Configura gli stili del documento"""
        # Stile per intestazione società
        try:
            company_style = doc.styles.add_style('CompanyHeader', WD_STYLE_TYPE.PARAGRAPH)
            company_style.font.name = 'Times New Roman'
            company_style.font.size = Pt(12)
            company_style.font.bold = True
            company_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            company_style.paragraph_format.space_after = Pt(6)
        except:
            pass
        
        # Stile per titolo verbale
        try:
            title_style = doc.styles.add_style('VerbaleTitle', WD_STYLE_TYPE.PARAGRAPH)
            title_style.font.name = 'Times New Roman'
            title_style.font.size = Pt(14)
            title_style.font.bold = True
            title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            title_style.paragraph_format.space_before = Pt(12)
            title_style.paragraph_format.space_after = Pt(12)
        except:
            pass
        
        # Stile per sezioni
        try:
            section_style = doc.styles.add_style('SectionHeader', WD_STYLE_TYPE.PARAGRAPH)
            section_style.font.name = 'Times New Roman'
            section_style.font.size = Pt(11)
            section_style.font.bold = True
            section_style.paragraph_format.space_before = Pt(12)
            section_style.paragraph_format.space_after = Pt(6)
        except:
            pass
    
    def _add_company_header(self, doc, data):
        """Aggiunge l'intestazione della società"""
        # Denominazione
        p = doc.add_paragraph(data['denominazione'])
        p.style = 'CompanyHeader' if 'CompanyHeader' in [s.name for s in doc.styles] else 'Normal'
        if p.style == 'Normal':
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.runs[0]
            run.font.bold = True
            run.font.size = Pt(12)
        
        # Sede
        p = doc.add_paragraph(f"Sede legale: {data['sede_legale']}")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Capitale sociale
        capitale_deliberato = str(data.get('capitale_deliberato', '10.000,00')).strip()
        capitale_versato = str(data.get('capitale_versato', '10.000,00')).strip()
        capitale_sottoscritto = str(data.get('capitale_sottoscritto', '10.000,00')).strip()
        
        # Gestione "i.v." (interamente versato) - solo se versato = deliberato
        if capitale_versato == capitale_deliberato:
            capitale_text = f"Capitale sociale Euro {capitale_deliberato} i.v."
        else:
            capitale_text = f"Capitale sociale deliberato Euro {capitale_deliberato}, sottoscritto Euro {capitale_sottoscritto}, versato Euro {capitale_versato}"
        
        p = doc.add_paragraph(capitale_text)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Codice fiscale
        p = doc.add_paragraph(f"Codice fiscale e Partita IVA: {data['codice_fiscale']}")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Riga separatrice
        doc.add_paragraph("_" * 60).alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    def _add_verbale_title(self, doc, data):
        """Aggiunge il titolo del verbale"""
        doc.add_paragraph()  # Spazio
        
        p = doc.add_paragraph("VERBALE DI ASSEMBLEA DEI SOCI")
        p.style = 'VerbaleTitle' if 'VerbaleTitle' in [s.name for s in doc.styles] else 'Normal'
        if p.style == 'Normal':
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.runs[0]
            run.font.bold = True
            run.font.size = Pt(14)
        
        tipo = data.get('tipo_assemblea', 'Ordinaria').upper()
        p = doc.add_paragraph(f"({tipo})")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        p = doc.add_paragraph(f"del {data['data_assemblea'].strftime('%d/%m/%Y')}")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.runs[0]
        run.font.bold = True
    
    def _add_opening_section(self, doc, data):
        """Aggiunge la sezione di apertura"""
        doc.add_paragraph()  # Spazio
        
        data_str = data['data_assemblea'].strftime('%d/%m/%Y')
        ora_str = data.get('ora_inizio', '09:00')
        luogo = data.get('luogo_assemblea', data['sede_legale'])
        
        text = f"In data {data_str}, alle ore {ora_str}, presso {luogo}, "
        if data.get('audioconferenza'):
            text += "e con la possibilità di partecipazione mediante mezzi di telecomunicazione, "
        text += f"si è riunita l'Assemblea {data.get('tipo_assemblea', 'Ordinaria')} dei Soci della Società, {data.get('tipo_convocazione', 'regolarmente convocata')} per discutere e deliberare sul seguente:"
        
        doc.add_paragraph(text)
    
    def _add_participants_section(self, doc, data):
        """Aggiunge la sezione partecipanti"""
        # Ordine del giorno
        doc.add_paragraph().style = 'SectionHeader' if 'SectionHeader' in [s.name for s in doc.styles] else 'Heading 2'
        p = doc.add_paragraph("ORDINE DEL GIORNO")
        run = p.runs[0]
        run.font.bold = True
        
        for i, punto in enumerate(data.get('punti_ordine_giorno', []), 1):
            punto_clean = punto.strip()
            if not punto_clean.startswith(f"{i}."):
                punto_clean = f"{i}. {punto_clean}"
            doc.add_paragraph(punto_clean, style='List Number')
        
        doc.add_paragraph()
        
        # Presidenza
        presidente = data.get('presidente', '')
        ruolo = data.get('ruolo_presidente', 'Amministratore Unico')
        text = f"Assume la presidenza dell'Assemblea, ai sensi dell'art. [...] dello Statuto Sociale, il Sig. {presidente} in qualità di {ruolo}, il quale constata e dichiara:"
        doc.add_paragraph(text)
        
        # Dichiarazioni del presidente
        dichiarazioni = [
            "che l'Assemblea risulta regolarmente costituita e validamente convocata secondo le modalità previste dalla legge e dallo Statuto Sociale;",
            "che tutti i partecipanti sono legittimati all'intervento;"
        ]
        
        if data.get('audioconferenza'):
            dichiarazioni.append("che, come previsto dall'avviso di convocazione, è consentita la partecipazione all'assemblea mediante mezzi di telecomunicazione;")
        
        for i, dich in enumerate(dichiarazioni, 1):
            doc.add_paragraph(f"{i}) {dich}")
        
        # Nomina segretario
        segretario = data.get('segretario', '')
        doc.add_paragraph(f"I presenti nominano all'unanimità quale Segretario il Sig. {segretario}, che accetta l'incarico.")
    
    def _add_preliminary_statements(self, doc, data):
        """Aggiunge le constatazioni preliminari"""
        doc.add_paragraph()
        
        # Soci presenti
        p = doc.add_paragraph("SOCI PRESENTI E RAPPRESENTATI")
        run = p.runs[0]
        run.font.bold = True
        
        totale_quote = 0
        for socio in data.get('soci', []):
            if socio.get('nome', '').strip() and socio.get('presente', True):
                nome = socio.get('nome', '')
                quota_perc = socio.get('quota_percentuale', '')
                quota_euro = socio.get('quota_euro', '')
                tipo_partecipazione = socio.get('tipo_partecipazione', 'Diretto')
                delegato = socio.get('delegato', '').strip()
                tipo_soggetto = socio.get('tipo_soggetto', 'Persona Fisica')
                rappresentante_legale = socio.get('rappresentante_legale', '').strip()
                
                # Gestione completa: delegati e rappresentanti legali - stessa logica dell'anteprima
                if tipo_partecipazione == 'Delegato' and delegato:
                    if tipo_soggetto == 'Società':
                        if rappresentante_legale:
                            doc.add_paragraph(f"• {delegato} (delegato della società {nome} - legale rappresentante: {rappresentante_legale}) - quota {quota_perc} pari a Euro {quota_euro}", style='List Bullet')
                        else:
                            doc.add_paragraph(f"• {delegato} (delegato della società {nome}) - quota {quota_perc} pari a Euro {quota_euro}", style='List Bullet')
                    else:
                        doc.add_paragraph(f"• {delegato} (delegato del socio {nome}) - quota {quota_perc} pari a Euro {quota_euro}", style='List Bullet')
                else:
                    if tipo_soggetto == 'Società':
                        if rappresentante_legale:
                            doc.add_paragraph(f"• {nome} (società - legale rappresentante: {rappresentante_legale}) - quota {quota_perc} pari a Euro {quota_euro}", style='List Bullet')
                        else:
                            doc.add_paragraph(f"• {nome} (società) - quota {quota_perc} pari a Euro {quota_euro}", style='List Bullet')
                    else:
                        doc.add_paragraph(f"• {nome} (socio) - quota {quota_perc} pari a Euro {quota_euro}", style='List Bullet')
                
                # Calcola totale
                try:
                    if '%' in quota_perc:
                        perc_num = float(quota_perc.replace('%', '').replace(',', '.'))
                        totale_quote += perc_num
                except:
                    pass
        
        if totale_quote > 0:
            doc.add_paragraph(f"Totale quote rappresentate: {totale_quote:.1f}%")
        
        doc.add_paragraph()
        
        # Amministratori presenti
        p = doc.add_paragraph("AMMINISTRATORI PRESENTI")
        run = p.runs[0]
        run.font.bold = True
        
        for amm in data.get('amministratori', []):
            if amm.get('nome', '').strip() and amm.get('presente', True):
                nome = amm.get('nome', '')
                carica = amm.get('carica', '')
                doc.add_paragraph(f"• {nome} - {carica}", style='List Bullet')
        
        # Altri presenti
        if data.get('collegio_sindacale') or data.get('revisore'):
            doc.add_paragraph()
            p = doc.add_paragraph("ALTRI PRESENTI")
            run = p.runs[0]
            run.font.bold = True
            
            if data.get('collegio_sindacale'):
                doc.add_paragraph("• Collegio Sindacale", style='List Bullet')
            if data.get('revisore'):
                doc.add_paragraph("• Revisore Legale", style='List Bullet')
    
    def _add_bilancio_discussion(self, doc, data):
        """Aggiunge la discussione dell'ordine del giorno"""
        doc.add_paragraph()
        doc.add_paragraph("Il Presidente dichiara aperta la discussione sull'ordine del giorno.")
        doc.add_paragraph()
        
        # Separatore
        doc.add_paragraph("* * *")
        doc.add_paragraph()
        
        # Primo punto - Bilancio
        p = doc.add_paragraph("PRIMO PUNTO ALL'ORDINE DEL GIORNO")
        run = p.runs[0]
        run.font.bold = True
        
        data_chiusura = data.get('data_chiusura', data['data_assemblea']).strftime('%d/%m/%Y')
        text = f"Il Presidente illustra il Bilancio di esercizio chiuso al {data_chiusura}, "
        text += "composto da Stato Patrimoniale, Conto Economico e Nota Integrativa, "
        if data.get('documenti_allegati'):
            text += "allegati al presente verbale. "
        else:
            text += "già in possesso dei Soci. "
        
        if data.get('sentito_parere_sindaci'):
            text += "Sentito il parere favorevole del Collegio Sindacale, "
        
        text += "dopo breve discussione, "
        if data.get('voto_palese'):
            text += "si procede alla votazione per alzata di mano. "
        else:
            text += "si procede alla votazione a scrutinio segreto. "
        
        esito = data.get('esito_votazione', 'approvato all\'unanimità')
        text += f"L'Assemblea, con voti {esito}, delibera:"
        
        doc.add_paragraph(text)
        
        doc.add_paragraph(f"di approvare il Bilancio di esercizio chiuso al {data_chiusura} e tutti i documenti che lo compongono.", style='List Bullet')
        
        doc.add_paragraph()
        doc.add_paragraph("* * *")
        doc.add_paragraph()
        
        # Secondo punto - Destinazione risultato
        p = doc.add_paragraph("SECONDO PUNTO ALL'ORDINE DEL GIORNO")
        run = p.runs[0]
        run.font.bold = True
        
        doc.add_paragraph("Il Presidente propone all'Assemblea la destinazione del risultato dell'esercizio come segue:")
        
        for dest in data.get('destinazioni_risultato', []):
            if dest.strip():
                doc.add_paragraph(dest.strip(), style='List Bullet')
        
        esito = data.get('esito_votazione', 'approvato all\'unanimità')
        doc.add_paragraph(f"L'Assemblea, con voti {esito}, approva la proposta di destinazione del risultato dell'esercizio.")
    
    def _add_closing_section(self, doc, data):
        """Aggiunge la sezione di chiusura"""
        doc.add_paragraph()
        doc.add_paragraph("* * *")
        doc.add_paragraph()
        
        doc.add_paragraph("Il Presidente constata che l'ordine del giorno è esaurito e che nessuno chiede di prendere la parola.")
        
        doc.add_paragraph("Viene quindi redatto il presente verbale che, previa lettura, viene approvato all'unanimità e sottoscritto.")
        
        ora_fine = data.get('ora_fine', '10:00')
        doc.add_paragraph(f"L'Assemblea viene dichiarata chiusa alle ore {ora_fine}.")
        
        # Allegati
        if data.get('allegati'):
            doc.add_paragraph()
            p = doc.add_paragraph("ALLEGATI")
            run = p.runs[0]
            run.font.bold = True
            
            for allegato in data['allegati']:
                if allegato.strip():
                    doc.add_paragraph(allegato.strip(), style='List Bullet')
    
    def _add_signatures(self, doc, data):
        """Aggiunge le firme"""
        doc.add_paragraph()
        doc.add_paragraph()
        
        # Tabella per le firme
        table = doc.add_table(rows=3, cols=2)
        table.style = 'Table Grid'
        
        # Intestazioni
        table.cell(0, 0).text = "IL PRESIDENTE"
        table.cell(0, 1).text = "IL SEGRETARIO"
        
        # Nomi
        presidente = data.get('presidente', '')
        segretario = data.get('segretario', '')
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
DocumentTemplateFactory.register_template("verbale_assemblea_template", VerbaleApprovazioneBilancioTemplate)