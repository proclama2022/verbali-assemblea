"""
Template Completo per Verbale di Assemblea dei Soci
Questo template include tutte le opzioni possibili per verbali di assemblea.
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

class VerbaleAssembleaCompletoTemplate(BaseVerbaleTemplate):
    """Template Completo per Verbale di Assemblea dei Soci"""
    
    def get_template_name(self) -> str:
        return "Verbale Assemblea Approvazione Bilancio"
    
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
        
        # Configurazioni specifiche del template completo
        st.subheader("📋 Configurazioni Specifiche Template Completo")
        
        # Data chiusura bilancio
        form_data["data_chiusura"] = st.date_input("Data chiusura bilancio", 
                                                   CommonDataHandler.get_default_date_chiusura())
        
        # Ora inizio e fine assemblea
        col1, col2 = st.columns(2)
        with col1:
            ora_inizio = st.text_input("Ora inizio assemblea", value=form_data.get('ora_inizio', '10:00'))
            form_data["ora_inizio"] = ora_inizio
        with col2:
            ora_fine = st.text_input("Ora fine assemblea", value=form_data.get('ora_fine', '11:30'))
            form_data["ora_fine"] = ora_fine
        
        # Tipo di amministrazione
        form_data["tipo_amministrazione"] = st.selectbox(
            "Tipo di amministrazione", 
            ["Amministratore Unico", "Consiglio di Amministrazione"]
        )
        
        # Collegio Sindacale
        form_data["has_collegio_sindacale"] = st.checkbox("Collegio Sindacale presente")
        if form_data["has_collegio_sindacale"]:
            form_data["tipo_collegio"] = st.selectbox("Tipo collegio sindacale", ["Collegio Sindacale", "Sindaco Unico"])
            
            if form_data["tipo_collegio"] == "Sindaco Unico":
                form_data["sindaco_unico"] = st.text_input("Nome Sindaco Unico", "")
                form_data["sindaci"] = [{"nome": form_data["sindaco_unico"], "carica": "Sindaco Unico", "presente": True}]
            else:
                df_sindaci = pd.DataFrame([
                    {"nome": "", "carica": "Presidente", "presente": True},
                    {"nome": "", "carica": "Sindaco Effettivo", "presente": True},
                    {"nome": "", "carica": "Sindaco Effettivo", "presente": True}
                ])
                
                column_config_sindaci = {
                    "presente": st.column_config.CheckboxColumn("Presente"),
                    "nome": st.column_config.TextColumn("Nome", required=True),
                    "carica": st.column_config.SelectboxColumn(
                        "Carica",
                        options=["Presidente", "Sindaco Effettivo", "Sindaco Supplente"],
                        default="Sindaco Effettivo"
                    )
                }
                
                df_sindaci_edited = st.data_editor(
                    df_sindaci, 
                    num_rows="dynamic", 
                    use_container_width=True,
                    column_config=column_config_sindaci,
                    key="sindaci_editor_completo"
                )
                form_data["sindaci"] = df_sindaci_edited.to_dict("records")
        else:
            form_data["sindaci"] = []
        
        # Altri partecipanti
        form_data["has_altri_partecipanti"] = st.checkbox("Altri partecipanti presenti")
        if form_data["has_altri_partecipanti"]:
            df_altri = pd.DataFrame([{"nome": "", "qualita": ""}])
            df_altri_edited = st.data_editor(df_altri, num_rows="dynamic", use_container_width=True, key="altri_editor_completo")
            form_data["altri_partecipanti"] = df_altri_edited.to_dict("records")
        else:
            form_data["altri_partecipanti"] = []
        
        # Ripianamento perdite
        st.subheader("💰 Gestione Perdite")
        form_data["has_ripianamento"] = st.checkbox("Include ripianamento perdite")
        if form_data["has_ripianamento"]:
            form_data["importo_perdita"] = st.text_input("Importo perdita da ripianare (€)", "")
            form_data["tipo_credito"] = st.selectbox(
                "Tipo di credito per ripianamento", 
                ["finanziamento infruttifero soci", "finanziamento fruttifero soci", "altro"]
            )
            
            # Dettaglio rinunce per socio
            st.write("**Dettaglio rinunce per socio:**")
            df_rinunce = pd.DataFrame([{"socio": "", "importo_rinuncia": "", "percentuale": "", "residuo": ""}])
            df_rinunce_edited = st.data_editor(df_rinunce, num_rows="dynamic", use_container_width=True, key="rinunce_editor_completo")
            form_data["rinunce_soci"] = df_rinunce_edited.to_dict("records")
        
        # Ordine del giorno
        st.subheader("📋 Ordine del Giorno")
        default_odg = f"1. Approvazione del Bilancio al {form_data['data_chiusura'].strftime('%d/%m/%Y')} e dei documenti correlati\n2. Delibere consequenziali"
        if form_data["has_ripianamento"]:
            default_odg += "\n3. Ripianamento perdite"
        punti_odg = st.text_area("Punti all'ordine del giorno", default_odg, height=120)
        form_data["punti_ordine_giorno"] = [p.strip() for p in punti_odg.split("\n") if p.strip()]
        
        # Gestione dei soci dalla visura
        st.subheader("👥 Soci dalla Visura")
        
        # Verifica se ci sono dati dei soci dalla visura
        soci_visura = extracted_data.get('soci', [])
        if soci_visura:
            st.info(f"Trovati {len(soci_visura)} soci nella visura")
            
            # Prepara i dati dei soci per il data editor
            soci_data = []
            for socio in soci_visura:
                socio_dict = {
                    "nome": socio.get('nome', ''),
                    "quota_euro": socio.get('quota_euro', ''),
                    "quota_percentuale": socio.get('quota_percentuale', ''),
                    "tipo_soggetto": socio.get('tipo_soggetto', 'Persona Fisica'),
                    "presente": True,
                    "tipo_partecipazione": "Diretto",
                    "delegato": "",
                    "rappresentante_legale": ""
                }
                
                # Se è una società, aggiungi il rappresentante legale
                if socio.get('tipo_soggetto') == 'Società':
                    socio_dict["rappresentante_legale"] = socio.get('rappresentante_legale', '')
                
                soci_data.append(socio_dict)
            
            # Se non ci sono soci dalla visura, aggiungi una riga vuota
            if not soci_data:
                soci_data = [{"nome": "", "quota_euro": "", "quota_percentuale": "", "tipo_soggetto": "Persona Fisica", "presente": True, "tipo_partecipazione": "Diretto", "delegato": "", "rappresentante_legale": ""}]
            
            # Configura le colonne per il data editor
            column_config_soci = {
                "presente": st.column_config.CheckboxColumn("Presente"),
                "nome": st.column_config.TextColumn("Nome", required=True),
                "quota_euro": st.column_config.TextColumn("Quota (€)"),
                "quota_percentuale": st.column_config.TextColumn("Quota (%)"),
                "tipo_soggetto": st.column_config.SelectboxColumn(
                    "Tipo Soggetto",
                    options=["Persona Fisica", "Società"],
                    default="Persona Fisica"
                ),
                "tipo_partecipazione": st.column_config.SelectboxColumn(
                    "Tipo Partecipazione",
                    options=["Diretto", "Delegato"],
                    default="Diretto"
                ),
                "delegato": st.column_config.TextColumn("Nome Delegato"),
                "rappresentante_legale": st.column_config.TextColumn("Rappresentante Legale (per società)")
            }
            
            # Mostra istruzioni per i rappresentanti e delegati
            st.info("Per le società, inserisci il nome del rappresentante legale nella colonna apposita. Per i soci rappresentati da delegati, seleziona 'Delegato' come tipo di partecipazione e inserisci il nome del delegato nella colonna 'Nome Delegato'.")
            
            # Crea il data editor per i soci
            df_soci = pd.DataFrame(soci_data)
            df_soci_edited = st.data_editor(
                df_soci,
                num_rows="dynamic",
                use_container_width=True,
                column_config=column_config_soci,
                key="soci_editor_completo"
            )
            form_data["soci"] = df_soci_edited.to_dict("records")
            
            # Calcola e mostra la percentuale totale dei soci presenti
            soci_presenti = [s for s in form_data["soci"] if s.get("presente", False)]
            total_quota_percentuale = 0.0
            
            for socio in soci_presenti:
                try:
                    quota_percentuale_str = str(socio.get('quota_percentuale', '0')).replace('.', '').replace(',', '.')
                    total_quota_percentuale += float(quota_percentuale_str)
                except ValueError:
                    pass  # Ignora valori non numerici
            
            # Formatta il totale per la visualizzazione
            formatted_total_percentuale = f"{total_quota_percentuale:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            st.success(f"Percentuale totale dei soci presenti: {formatted_total_percentuale}% del Capitale Sociale")
            
        else:
            # Se non ci sono dati dalla visura, usa il CommonDataHandler standard per i soci
            st.warning("Nessun socio trovato nella visura. Inserire manualmente i dati.")
            participants_data = CommonDataHandler.extract_and_populate_participants_data(
                extracted_data, 
                unique_key_suffix="completo_soci",
                extended_admin_columns=False
            )
            form_data.update(participants_data)
        
        # Gestione degli amministratori dalla visura
        st.subheader("👤 Amministratori dalla Visura")
        
        # Verifica se ci sono dati degli amministratori dalla visura
        amministratori_visura = extracted_data.get('amministratori', [])
        if amministratori_visura:
            st.info(f"Trovati {len(amministratori_visura)} amministratori nella visura")
            
            # Prepara i dati degli amministratori per il data editor
            amministratori_data = []
            for amm in amministratori_visura:
                amm_dict = {
                    "nome": amm.get('nome', ''),
                    "carica": amm.get('carica', 'Amministratore'),
                    "presente": True,
                    "assente_giustificato": False
                }
                
                # Adatta la carica in base al tipo di amministrazione
                if form_data["tipo_amministrazione"] == "Amministratore Unico" and "unico" not in amm_dict["carica"].lower():
                    amm_dict["carica"] = "Amministratore Unico"
                elif form_data["tipo_amministrazione"] == "Consiglio di Amministrazione" and "unico" in amm_dict["carica"].lower():
                    amm_dict["carica"] = "Presidente CDA"
                
                amministratori_data.append(amm_dict)
            
            # Se non ci sono amministratori dalla visura, aggiungi una riga vuota
            if not amministratori_data:
                carica_default = "Amministratore Unico" if form_data["tipo_amministrazione"] == "Amministratore Unico" else "Presidente CDA"
                amministratori_data = [{"nome": "", "carica": carica_default, "presente": True, "assente_giustificato": False}]
            
            # Configura le colonne per il data editor
            column_config_amministratori = {
                "presente": st.column_config.CheckboxColumn("Presente"),
                "nome": st.column_config.TextColumn("Nome", required=True),
                "assente_giustificato": st.column_config.CheckboxColumn("Assente Giustificato"),
            }
            
            # Aggiungi opzioni di carica in base al tipo di amministrazione
            if form_data["tipo_amministrazione"] == "Amministratore Unico":
                column_config_amministratori["carica"] = st.column_config.SelectboxColumn(
                    "Carica",
                    options=["Amministratore Unico"],
                    default="Amministratore Unico"
                )
            else:
                column_config_amministratori["carica"] = st.column_config.SelectboxColumn(
                    "Carica",
                    options=["Presidente CDA", "Vice Presidente", "Consigliere", "Amministratore Delegato"],
                    default="Consigliere"
                )
            
            # Crea il data editor per gli amministratori
            df_amministratori = pd.DataFrame(amministratori_data)
            df_amministratori_edited = st.data_editor(
                df_amministratori,
                num_rows="dynamic",
                use_container_width=True,
                column_config=column_config_amministratori,
                key="amministratori_editor_completo"
            )
            form_data["amministratori"] = df_amministratori_edited.to_dict("records")
            
            # Imposta il presidente come il primo amministratore con carica di presidente
            for amm in form_data["amministratori"]:
                if "presidente" in amm.get("carica", "").lower() and amm.get("presente", False):
                    form_data["presidente"] = amm.get("nome", "")
                    break
            
            # Se non è stato trovato un presidente, usa il primo amministratore presente
            if not form_data.get("presidente"):
                for amm in form_data["amministratori"]:
                    if amm.get("presente", False):
                        form_data["presidente"] = amm.get("nome", "")
                        break
        else:
            # Se non ci sono dati dalla visura, usa il CommonDataHandler standard per gli amministratori
            st.warning("Nessun amministratore trovato nella visura. Inserire manualmente i dati.")
            admin_data = CommonDataHandler.extract_and_populate_admin_data(
                extracted_data, 
                unique_key_suffix="completo_admin",
                extended_admin_columns=True
            )
            
            # Aggiungi solo i dati degli amministratori se non sono già stati aggiunti
            if "amministratori" not in form_data:
                form_data["amministratori"] = admin_data.get("amministratori", [])
            
            # Imposta il presidente se non è già stato impostato
            if not form_data.get("presidente") and admin_data.get("presidente"):
                form_data["presidente"] = admin_data.get("presidente")
        
        # Campo specifico per il segretario
        st.subheader("📝 Segretario dell'Assemblea")
        
        # Verifica se c'è già un segretario nei dati estratti
        segretario_default = extracted_data.get('segretario', '')
        
        # Raccogli tutti i possibili candidati per il ruolo di segretario
        candidati_segretario = []
        
        # Aggiungi i soci presenti come possibili candidati
        for socio in form_data.get('soci', []):
            if socio.get('presente', False) and socio.get('nome'):
                candidati_segretario.append(socio.get('nome'))
        
        # Aggiungi gli amministratori presenti che non sono il presidente
        for amm in form_data.get('amministratori', []):
            if amm.get('presente', False) and amm.get('nome') != form_data.get('presidente') and amm.get('nome'):
                candidati_segretario.append(amm.get('nome'))
        
        # Opzione per inserire un soggetto esterno
        candidati_segretario.append("Altro (inserire manualmente)")
        
        # Selettore per il segretario
        segretario_selezionato = st.selectbox(
            "Seleziona il Segretario", 
            options=candidati_segretario,
            index=0 if candidati_segretario else 0,
            key="segretario_selectbox"
        )
        
        # Se è stato selezionato "Altro", mostra un campo per inserire manualmente il nome
        if segretario_selezionato == "Altro (inserire manualmente)":
            segretario_manuale = st.text_input("Nome del Segretario (esterno)", value=segretario_default)
            form_data["segretario"] = segretario_manuale
        else:
            form_data["segretario"] = segretario_selezionato
        
        # Post-processing per gestire amministratore unico vs CDA
        if form_data["tipo_amministrazione"] == "Amministratore Unico":
            # Se è AU, assicurati che ci sia solo un amministratore
            if form_data.get("amministratori"):
                # Prendi il primo amministratore o usa il rappresentante estratto
                primo_amm = form_data["amministratori"][0] if form_data["amministratori"] else {}
                nome_au = primo_amm.get("nome", extracted_data.get("rappresentante", ""))
                form_data["amministratori"] = [{"nome": nome_au, "carica": "Amministratore Unico", "presente": True}]
                # Aggiorna anche il presidente se necessario
                if not form_data.get("presidente") or form_data["presidente"] != nome_au:
                    form_data["presidente"] = nome_au
        else:
            # Se è CDA, assicurati che le cariche siano appropriate per il CDA
            for amm in form_data.get("amministratori", []):
                if amm.get("carica") == "Amministratore Unico":
                    amm["carica"] = "Presidente CDA"
        
        return form_data

    def show_preview(self, form_data: dict):
        """Mostra l'anteprima del documento"""
        st.subheader("📄 Anteprima Verbale")
        preview_text = self._generate_preview_text(form_data)
        st.text_area("", preview_text, height=600, disabled=True)

    def _generate_preview_text(self, data: dict) -> str:
        """Genera il testo di anteprima del verbale"""
        
        # Header
        preview = f"""
{data.get('denominazione', '[DENOMINAZIONE]')}
Sede in {data.get('sede_legale', '[SEDE]')}
Capitale sociale Euro {data.get('capitale_sociale', '[CAPITALE]')} i.v.
Codice fiscale: {data.get('codice_fiscale', '[CF]')}

Verbale di assemblea dei soci
del {data.get('data_assemblea', '[DATA]').strftime('%d/%m/%Y') if hasattr(data.get('data_assemblea'), 'strftime') else '[DATA]'}

Oggi {data.get('data_assemblea', '[DATA]').strftime('%d/%m/%Y') if hasattr(data.get('data_assemblea'), 'strftime') else '[DATA]'} alle ore {data.get('ora_inizio', '[ORA]')} presso {data.get('luogo_assemblea', 'la sede sociale')}, si è tenuta l'assemblea generale dei soci, per discutere e deliberare sul seguente:

ORDINE DEL GIORNO
"""
        
        # Ordine del giorno
        for i, punto in enumerate(data.get('punti_ordine_giorno', []), 1):
            preview += f"{i}. {punto}\n"
        
        # Presidente
        presidente = data.get('presidente', '[PRESIDENTE]')
        if data.get('tipo_amministrazione') == "Amministratore Unico":
            ruolo_presidente = "Amministratore Unico"
        else:
            # Trova il ruolo del presidente negli amministratori
            ruolo_presidente = "Presidente del Consiglio di Amministrazione"
            for amm in data.get('amministratori', []):
                if amm.get('nome') == presidente and 'Presidente' in amm.get('carica', ''):
                    ruolo_presidente = amm.get('carica')
                    break
        
        preview += f"""
Assume la presidenza ai sensi dell'art. […] dello statuto sociale il Sig. {presidente} {ruolo_presidente}, il quale dichiara e constata:

1 - che"""
        
        if data.get('audioconferenza'):
            preview += " (come indicato anche nell'avviso di convocazione ed in conformità alle previsioni dell'art. […] dello statuto sociale) l'intervento all'assemblea può avvenire anche in audioconferenza"
        
        preview += f"""
2 - che sono presenti/partecipano all'assemblea:

{ruolo_presidente} nella persona del suddetto Presidente Sig. {presidente}
"""
        
        # Amministratori
        if data.get('tipo_amministrazione') == "Consiglio di Amministrazione":
            preview += "\nper il Consiglio di Amministrazione:\n"
            for amm in data.get('amministratori', []):
                if amm.get('presente'):
                    nome_amm = amm.get('nome', '')
                    if nome_amm != presidente:
                        preview += f"il Sig. {nome_amm} - {amm.get('carica', '')}\n"
                elif amm.get('assente_giustificato'):
                    nome_amm = amm.get('nome', '')
                    if nome_amm != presidente:
                        preview += f"assente giustificato il Sig. {nome_amm} il quale ha tuttavia rilasciato apposita dichiarazione scritta\n"
        
        # Collegio Sindacale
        if data.get('has_collegio_sindacale'):
            if data.get('tipo_collegio') == "Sindaco Unico":
                preview += f"\nil Sindaco Unico nella persona del Sig. {data.get('sindaco_unico', '')}\n"
            else:
                preview += "\nper il Collegio Sindacale:\n"
                for sindaco in data.get('sindaci', []):
                    if sindaco.get('presente'):
                        preview += f"il Dott. {sindaco.get('nome', '')} - {sindaco.get('carica', '')}\n"
        
        # Revisore
        if data.get('has_revisore'):
            preview += f"\nil revisore contabile Dott. {data.get('nome_revisore', '')}\n"
        
        # Altri partecipanti
        if data.get('has_altri_partecipanti'):
            for altro in data.get('altri_partecipanti', []):
                if altro.get('nome'):
                    preview += f"\nil Sig. {altro.get('nome', '')} in qualità di {altro.get('qualita', '')}\n"
        
        # Soci
        soci = data.get('soci', [])
        soci_presenti = [s for s in soci if s.get('presente', False)]
        total_quota_euro = 0.0
        total_quota_percentuale = 0.0

        for socio in soci_presenti:
            if isinstance(socio, dict):
                try:
                    # Rimuovi punti e sostituisci virgola con punto per la conversione a float
                    quota_euro_str = str(socio.get('quota_euro', '0')).replace('.', '').replace(',', '.')
                    total_quota_euro += float(quota_euro_str)
                except ValueError:
                    pass # Ignora valori non numerici
                try:
                    quota_percentuale_str = str(socio.get('quota_percentuale', '0')).replace('.', '').replace(',', '.')
                    total_quota_percentuale += float(quota_percentuale_str)
                except ValueError:
                    pass # Ignora valori non numerici
        
        # Formatta i totali per la visualizzazione
        formatted_total_quota_euro = f"{total_quota_euro:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') # Formato italiano
        formatted_total_quota_percentuale = f"{total_quota_percentuale:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') # Formato italiano

        preview += f"\nnonché i seguenti soci o loro rappresentanti, recanti complessivamente una quota pari a nominali euro {formatted_total_quota_euro} pari al {formatted_total_quota_percentuale}% del Capitale Sociale:\n"
        
        for socio in soci_presenti:
            nome = socio.get('nome', '')
            quota_euro = socio.get('quota_euro', '')
            quota_percentuale = socio.get('quota_percentuale', '')
            tipo_partecipazione = socio.get('tipo_partecipazione', 'Diretto')
            delegato = socio.get('delegato', '').strip()
            tipo_soggetto = socio.get('tipo_soggetto', 'Persona Fisica')
            rappresentante_legale = socio.get('rappresentante_legale', '').strip()
            
            # Gestione completa: delegati e rappresentanti legali
            if tipo_partecipazione == 'Delegato' and delegato:
                if tipo_soggetto == 'Società':
                    preview += f"il Sig. {delegato} delegato della società {nome}"
                    if rappresentante_legale:
                        preview += f" (nella persona del legale rappresentante {rappresentante_legale})"
                    preview += f" recante una quota pari a nominali euro {quota_euro} pari al {quota_percentuale}% del Capitale Sociale\n"
                else:
                    preview += f"il Sig. {delegato} delegato del socio {nome} recante una quota pari a nominali euro {quota_euro} pari al {quota_percentuale}% del Capitale Sociale\n"
            else:
                if tipo_soggetto == 'Società':
                    if rappresentante_legale:
                        preview += f"la società {nome} nella persona del legale rappresentante {rappresentante_legale} recante una quota pari a nominali euro {quota_euro} pari al {quota_percentuale}% del Capitale Sociale\n"
                    else:
                        preview += f"la società {nome} recante una quota pari a nominali euro {quota_euro} pari al {quota_percentuale}% del Capitale Sociale\n"
                else:
                    preview += f"il Sig. {nome} socio recante una quota pari a nominali euro {quota_euro} pari al {quota_percentuale}% del Capitale Sociale\n"
        
        preview += """
2 - che gli intervenuti sono legittimati alla presente assemblea;
3 - che tutti gli intervenuti si dichiarano edotti sugli argomenti posti all'ordine del giorno.

I presenti all'unanimità chiamano a fungere da segretario il signor {}, che accetta l'incarico.

Il Presidente identifica tutti i partecipanti e si accerta che ai soggetti collegati mediante mezzi di telecomunicazione sia consentito seguire la discussione, trasmettere e ricevere documenti, intervenire in tempo reale, con conferma da parte di ciascun partecipante.
""".format(data.get('segretario', '[SEGRETARIO]'))
        
        # Lingua straniera
        if data.get('lingua_straniera'):
            preview += f"""
In particolare, preso atto che il Sig. {data.get('nome_straniero', '')} non conosce la lingua italiana ma dichiara di conoscere la lingua {data.get('lingua_conosciuta', 'inglese')}, il Presidente dichiara che provvederà a tradurre dall'italiano all'{data.get('lingua_conosciuta', 'inglese')} (e viceversa) gli interventi dei partecipanti alla discussione nonché a tradurre dall'italiano all'{data.get('lingua_conosciuta', 'inglese')} il verbale che sarà redatto al termine della riunione.
"""
        
        preview += f"""
Il Presidente constata e fa constatare che l'assemblea risulta {data.get('tipo_convocazione', 'regolarmente convocata')} e deve ritenersi valida ed atta a deliberare sul citato ordine del giorno.

Si passa quindi allo svolgimento dell'ordine del giorno.

*     *     *

In relazione al primo punto il presidente legge il bilancio al {data.get('data_chiusura', '[DATA]').strftime('%d/%m/%Y') if hasattr(data.get('data_chiusura'), 'strftime') else '[DATA]'} composto da stato patrimoniale, conto economico e nota integrativa (allegati di seguito al presente verbale).
"""
        
        # Relazione Collegio Sindacale
        if data.get('has_collegio_sindacale'):
            if data.get('tipo_collegio') == "Sindaco Unico":
                preview += f"Prende la parola il Sindaco Unico che legge la relazione al Bilancio chiuso al {data.get('data_chiusura', '[DATA]').strftime('%d/%m/%Y') if hasattr(data.get('data_chiusura'), 'strftime') else '[DATA]'} (allegata di seguito al presente verbale).\n"
            else:
                preview += f"Prende la parola il Presidente del Collegio Sindacale che legge la relazione del collegio sindacale al Bilancio chiuso al {data.get('data_chiusura', '[DATA]').strftime('%d/%m/%Y') if hasattr(data.get('data_chiusura'), 'strftime') else '[DATA]'} (allegata di seguito al presente verbale).\n"
        
        # Relazione Revisore
        if data.get('has_revisore'):
            preview += f"Prende infine la parola il Dott. {data.get('nome_revisore', '')} che legge la relazione del revisore contabile (allegata di seguito al presente verbale).\n"
        
        preview += f"""
Segue breve discussione tra i soci al termine della quale si passa alla votazione con voto {'palese' if data.get('voto_palese') else 'segreto'} in forza della quale il Presidente constata che, {data.get('esito_votazione', 'all\'unanimità')} l'assemblea

DELIBERA

l'approvazione del bilancio di esercizio chiuso al {data.get('data_chiusura', '[DATA]').strftime('%d/%m/%Y') if hasattr(data.get('data_chiusura'), 'strftime') else '[DATA]'} e dei relativi documenti che lo compongono.

*     *     *
"""
        
        # Ripianamento perdite
        if data.get('has_ripianamento'):
            preview += f"""
In relazione al secondo punto posto all'ordine del giorno, il Presidente"""
            
            if data.get('has_collegio_sindacale'):
                preview += ", sentito il parere favorevole del Collegio Sindacale,"
            
            preview += f""" propone all'assemblea di ripianare la perdita mediante la rinuncia al rimborso di una corrispondente quota del credito vantato dai soci nei confronti della società a titolo di {data.get('tipo_credito', 'finanziamento infruttifero soci')}."

Segue breve discussione tra i soci al termine della quale si passa alla votazione con voto {'palese' if data.get('voto_palese') else 'segreto'} in forza della quale il Presidente constata che, {data.get('esito_votazione', 'all\'unanimità')} l'assemblea

DELIBERA

di approvare la proposta del Presidente e di ripianare, con effetto dalla data odierna, la perdita di euro {data.get('importo_perdita', '')} mediante la rinuncia al rimborso di una corrispondente quota del credito vantato dai soci nei confronti della società a titolo di {data.get('tipo_credito', 'finanziamento infruttifero soci')}.

Le rinunce al rimborso avverranno in proporzione alla quota di {data.get('tipo_credito', 'finanziamento infruttifero soci')} attualmente in essere e quindi:
"""
            
            for rinuncia in data.get('rinunce_soci', []):
                if rinuncia.get('socio'):
                    preview += f"socio {rinuncia.get('socio', '')} per euro {rinuncia.get('importo_rinuncia', '')} pari al {rinuncia.get('percentuale', '')}% della perdita da ripianare;\n"
            
            preview += f"""
Con effetto dalla data odierna, il residuo credito verso i soci a titolo di {data.get('tipo_credito', 'finanziamento infruttifero soci')} continuerà ad essere regolato dalle condizioni previgenti, ma solo per il residuo importo (al netto dell'avvenuta rinuncia) qui riepilogato:
"""
            
            for rinuncia in data.get('rinunce_soci', []):
                if rinuncia.get('socio'):
                    preview += f"socio {rinuncia.get('socio', '')} per euro {rinuncia.get('residuo', '')};\n"
            
            preview += """
Ciascun socio rilascia seduta stante al Presidente una dichiarazione sostitutiva di atto notorio che attesta il valore fiscale del credito a cui ha testé rinunciato.
Le dichiarazioni rilasciate dai soci verranno conservate agli atti della società.

*     *     *
"""
        
        preview += f"""
Il Presidente constata che l'ordine del giorno è esaurito e che nessuno chiede la parola.

Viene quindi redatto il presente verbale e dopo averne data lettura, il Presidente constata che l'assemblea {data.get('esito_votazione', 'all\'unanimità')}, con voto {'palese' if data.get('voto_palese') else 'segreto'}, ne approva il testo{'unitamente a quanto allegato' if data.get('documenti_allegati') else ''}.

L'assemblea viene sciolta alle ore {data.get('ora_fine', '[ORA]')}.


Il Presidente                           Il Segretario

_____________________                  _____________________
{data.get('presidente', '[PRESIDENTE]')}                         {data.get('segretario', '[SEGRETARIO]')}
"""
        
        return preview

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
                # Imposta gli stili anche quando usiamo un template
                self._setup_document_styles(doc)
            else:
                doc = Document()
                self._setup_document_styles(doc)
        except Exception as e:
            # Fallback a documento vuoto se il template non può essere caricato
            doc = Document()
            self._setup_document_styles(doc)
        
        # Header società
        self._add_company_header(doc, data)
        
        # Titolo verbale
        self._add_verbale_title(doc, data)
        
        # Sezione di apertura
        self._add_opening_section(doc, data)
        
        # Partecipanti
        self._add_participants_section(doc, data)
        
        # Dichiarazioni preliminari
        self._add_preliminary_statements(doc, data)
        
        # Discussione punti OdG
        self._add_discussion_section(doc, data)
        
        # Ripianamento perdite se presente
        if data.get('has_ripianamento'):
            self._add_ripianamento_section(doc, data)
        
        # Chiusura
        self._add_closing_section(doc, data)
        
        # Firme
        self._add_signatures(doc, data)
        
        return doc

    def _setup_document_styles(self, doc):
        """Imposta gli stili del documento in modo completo"""
        styles = doc.styles
        
        # Stile per il titolo della società
        if 'TitoloSocieta' not in styles:
            title_style = styles.add_style('TitoloSocieta', WD_STYLE_TYPE.PARAGRAPH)
            title_style.font.name = 'Times New Roman'
            title_style.font.size = Pt(14)
            title_style.font.bold = True
            title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            title_style.paragraph_format.space_after = Pt(6)
        
        # Stile per il titolo del verbale
        if 'TitoloVerbale' not in styles:
            verbale_title_style = styles.add_style('TitoloVerbale', WD_STYLE_TYPE.PARAGRAPH)
            verbale_title_style.font.name = 'Times New Roman'
            verbale_title_style.font.size = Pt(16)
            verbale_title_style.font.bold = True
            verbale_title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            verbale_title_style.paragraph_format.space_before = Pt(18)
            verbale_title_style.paragraph_format.space_after = Pt(18)
        
        # Stile per gli heading 1
        if 'Heading1' not in styles:
            heading1_style = styles.add_style('Heading1', WD_STYLE_TYPE.PARAGRAPH)
            heading1_style.font.name = 'Times New Roman'
            heading1_style.font.size = Pt(14)
            heading1_style.font.bold = True
            heading1_style.paragraph_format.space_before = Pt(12)
            heading1_style.paragraph_format.space_after = Pt(6)
            heading1_style.paragraph_format.keep_with_next = True
        
        # Stile per gli heading 2
        if 'Heading2' not in styles:
            heading2_style = styles.add_style('Heading2', WD_STYLE_TYPE.PARAGRAPH)
            heading2_style.font.name = 'Times New Roman'
            heading2_style.font.size = Pt(13)
            heading2_style.font.bold = True
            heading2_style.paragraph_format.space_before = Pt(6)
            heading2_style.paragraph_format.space_after = Pt(6)
            heading2_style.paragraph_format.keep_with_next = True
        
        # Stile per il corpo del testo
        if 'BodyText' not in styles:
            body_style = styles.add_style('BodyText', WD_STYLE_TYPE.PARAGRAPH)
            body_style.font.name = 'Times New Roman'
            body_style.font.size = Pt(12)
            body_style.paragraph_format.space_after = Pt(6)
            body_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        # Stile per le firme
        if 'Firma' not in styles:
            firma_style = styles.add_style('Firma', WD_STYLE_TYPE.PARAGRAPH)
            firma_style.font.name = 'Times New Roman'
            firma_style.font.size = Pt(12)
            firma_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            firma_style.paragraph_format.space_before = Pt(24)

    def _add_company_header(self, doc, data):
        """Aggiunge l'header con i dati della società"""
        p = doc.add_paragraph(style='TitoloSocieta')
        p.add_run(data.get('denominazione', '[DENOMINAZIONE]')).bold = True
        
        p = doc.add_paragraph(style='TitoloSocieta')
        p.add_run(f"Sede in {data.get('sede_legale', '[SEDE]')}")
        
        p = doc.add_paragraph(style='TitoloSocieta')
        p.add_run(f"Capitale sociale Euro {data.get('capitale_sociale', '[CAPITALE]')} i.v.")
        
        p = doc.add_paragraph(style='TitoloSocieta')
        p.add_run(f"Codice fiscale: {data.get('codice_fiscale', '[CF]')}")

    def _add_verbale_title(self, doc, data):
        """Aggiunge il titolo del verbale"""
        doc.add_paragraph()
        p = doc.add_paragraph(style='TitoloVerbale')
        p.add_run("Verbale di assemblea dei soci").bold = True
        
        data_str = data.get('data_assemblea').strftime('%d/%m/%Y') if hasattr(data.get('data_assemblea'), 'strftime') else '[DATA]'
        p = doc.add_paragraph(style='TitoloVerbale')
        p.add_run(f"del {data_str}").bold = True

    def _add_opening_section(self, doc, data):
        """Aggiunge la sezione di apertura"""
        doc.add_paragraph()
        
        data_str = data.get('data_assemblea').strftime('%d/%m/%Y') if hasattr(data.get('data_assemblea'), 'strftime') else '[DATA]'
        luogo = data.get('luogo_assemblea', 'la sede sociale')
        ora = data.get('ora_inizio', '[ORA]')
        
        p = doc.add_paragraph(style='BodyText')
        p.add_run(f"Oggi {data_str} alle ore {ora} presso {luogo}, si è tenuta l'assemblea generale dei soci, per discutere e deliberare sul seguente:")
        
        doc.add_paragraph()
        p = doc.add_paragraph(style='Heading1')
        p.add_run("ORDINE DEL GIORNO")
        
        for i, punto in enumerate(data.get('punti_ordine_giorno', []), 1):
            p = doc.add_paragraph(style='BodyText')
            p.add_run(f"{i}. {punto}")

    def _add_participants_section(self, doc, data):
        """Aggiunge la sezione dei partecipanti"""
        doc.add_paragraph()
        
        presidente = data.get('presidente', '[PRESIDENTE]')
        if data.get('tipo_amministrazione') == "Amministratore Unico":
            ruolo_presidente = "Amministratore Unico"
        else:
            ruolo_presidente = "Presidente del Consiglio di Amministrazione"
            for amm in data.get('amministratori', []):
                if amm.get('nome') == presidente and 'Presidente' in amm.get('carica', ''):
                    ruolo_presidente = amm.get('carica')
                    break
        
        p = doc.add_paragraph()
        p.add_run(f"Assume la presidenza ai sensi dell'art. […] dello statuto sociale il Sig. {presidente} {ruolo_presidente}, il quale dichiara e constata:")

    def _add_preliminary_statements(self, doc, data):
        """Aggiunge le dichiarazioni preliminari"""
        # Punto 1 - Audioconferenza
        p = doc.add_paragraph()
        text = "1 - che"
        if data.get('audioconferenza'):
            text += " (come indicato anche nell'avviso di convocazione ed in conformità alle previsioni dell'art. […] dello statuto sociale) l'intervento all'assemblea può avvenire anche in audioconferenza"
        p.add_run(text)
        
        # Punto 2 - Partecipanti
        p = doc.add_paragraph()
        p.add_run("2 - che sono presenti/partecipano all'assemblea:")
        
        # Presidente
        presidente = data.get('presidente', '[PRESIDENTE]')
        ruolo_presidente = "Amministratore Unico" if data.get('tipo_amministrazione') == "Amministratore Unico" else "Presidente del Consiglio di Amministrazione"
        for amm in data.get('amministratori', []):
            if amm.get('nome') == presidente and 'Presidente' in amm.get('carica', ''):
                ruolo_presidente = amm.get('carica')
                break
                
        p = doc.add_paragraph()
        p.add_run(f"{ruolo_presidente} nella persona del suddetto Presidente Sig. {presidente}")
        
        # Amministratori
        if data.get('tipo_amministrazione') == "Consiglio di Amministrazione":
            p = doc.add_paragraph()
            p.add_run("per il Consiglio di Amministrazione:")
            
            for amm in data.get('amministratori', []):
                nome_amm = amm.get('nome', '')
                if nome_amm != presidente and amm.get('presente', False):
                    p = doc.add_paragraph()
                    p.add_run(f"il Sig. {nome_amm} - {amm.get('carica', '')}")
                elif nome_amm != presidente and amm.get('assente_giustificato', False):
                    p = doc.add_paragraph()
                    p.add_run(f"assente giustificato il Sig. {nome_amm} il quale ha tuttavia rilasciato apposita dichiarazione scritta")
        
        # Collegio Sindacale
        if data.get('has_collegio_sindacale'):
            if data.get('tipo_collegio') == "Sindaco Unico":
                p = doc.add_paragraph()
                p.add_run(f"il Sindaco Unico nella persona del Sig. {data.get('sindaco_unico', '')}")
            else:
                p = doc.add_paragraph()
                p.add_run("per il Collegio Sindacale:")
                
                for sindaco in data.get('sindaci', []):
                    if sindaco.get('presente', False):
                        p = doc.add_paragraph()
                        p.add_run(f"il Dott. {sindaco.get('nome', '')} - {sindaco.get('carica', '')}")
        
        # Altri partecipanti
        if data.get('has_altri_partecipanti'):
            for altro in data.get('altri_partecipanti', []):
                if altro.get('nome'):
                    p = doc.add_paragraph()
                    p.add_run(f"il Sig. {altro.get('nome', '')} in qualità di {altro.get('qualita', '')}")
        
        # Calcola il totale delle quote dei soci presenti
        soci = data.get('soci', [])
        soci_presenti = [s for s in soci if s.get('presente', False)]
        total_quota_euro = 0.0
        total_quota_percentuale = 0.0

        for socio in soci_presenti:
            if isinstance(socio, dict):
                try:
                    # Rimuovi punti e sostituisci virgola con punto per la conversione a float
                    quota_euro_str = str(socio.get('quota_euro', '0')).replace('.', '').replace(',', '.')
                    total_quota_euro += float(quota_euro_str)
                except ValueError:
                    pass # Ignora valori non numerici
                try:
                    quota_percentuale_str = str(socio.get('quota_percentuale', '0')).replace('.', '').replace(',', '.')
                    total_quota_percentuale += float(quota_percentuale_str)
                except ValueError:
                    pass # Ignora valori non numerici
        
        # Formatta i totali per la visualizzazione
        formatted_total_quota_euro = f"{total_quota_euro:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') # Formato italiano
        formatted_total_quota_percentuale = f"{total_quota_percentuale:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') # Formato italiano
        
        # Soci
        p = doc.add_paragraph()
        p.add_run(f"nonché i seguenti soci o loro rappresentanti, recanti complessivamente una quota pari a nominali euro {formatted_total_quota_euro} pari al {formatted_total_quota_percentuale}% del Capitale Sociale:")
        
        for socio in soci_presenti:
            nome = socio.get('nome', '')
            quota_euro = socio.get('quota_euro', '')
            quota_percentuale = socio.get('quota_percentuale', '')
            tipo_partecipazione = socio.get('tipo_partecipazione', 'Diretto')
            delegato = socio.get('delegato', '').strip()
            tipo_soggetto = socio.get('tipo_soggetto', 'Persona Fisica')
            rappresentante_legale = socio.get('rappresentante_legale', '').strip()
            
            p = doc.add_paragraph()
            
            # Gestione completa: delegati e rappresentanti legali
            if tipo_partecipazione == 'Delegato' and delegato:
                if tipo_soggetto == 'Società':
                    text = f"il Sig. {delegato} delegato della società {nome}"
                    if rappresentante_legale:
                        text += f" (nella persona del legale rappresentante {rappresentante_legale})"
                    text += f" recante una quota pari a nominali euro {quota_euro} pari al {quota_percentuale}% del Capitale Sociale"
                else:
                    text = f"il Sig. {delegato} delegato del socio {nome} recante una quota pari a nominali euro {quota_euro} pari al {quota_percentuale}% del Capitale Sociale"
            else:
                if tipo_soggetto == 'Società':
                    if rappresentante_legale:
                        text = f"la società {nome} nella persona del legale rappresentante {rappresentante_legale} recante una quota pari a nominali euro {quota_euro} pari al {quota_percentuale}% del Capitale Sociale"
                    else:
                        text = f"la società {nome} recante una quota pari a nominali euro {quota_euro} pari al {quota_percentuale}% del Capitale Sociale"
                else:
                    text = f"il Sig. {nome} socio recante una quota pari a nominali euro {quota_euro} pari al {quota_percentuale}% del Capitale Sociale"
            
            p.add_run(text)
        
        # Dichiarazioni finali
        p = doc.add_paragraph()
        p.add_run("2 - che gli intervenuti sono legittimati alla presente assemblea;")
        
        p = doc.add_paragraph()
        p.add_run("3 - che tutti gli intervenuti si dichiarano edotti sugli argomenti posti all'ordine del giorno.")
        
        # Segretario
        p = doc.add_paragraph()
        segretario = data.get('segretario', '')
        if segretario:
            p.add_run(f"I presenti all'unanimità chiamano a fungere da segretario il signor {segretario}, che accetta l'incarico.")
        else:
            p.add_run("I presenti all'unanimità chiamano a fungere da segretario un membro dell'assemblea, che accetta l'incarico.")
        
        # Identificazione partecipanti
        p = doc.add_paragraph()
        p.add_run("Il Presidente identifica tutti i partecipanti e si accerta che ai soggetti collegati mediante mezzi di telecomunicazione sia consentito seguire la discussione, trasmettere e ricevere documenti, intervenire in tempo reale, con conferma da parte di ciascun partecipante.")
        
        # Lingua straniera
        if data.get('lingua_straniera'):
            p = doc.add_paragraph()
            p.add_run(f"In particolare, preso atto che il Sig. {data.get('nome_straniero', '')} non conosce la lingua italiana ma dichiara di conoscere la lingua {data.get('lingua_conosciuta', 'inglese')}, il Presidente dichiara che provvederà a tradurre dall'italiano all'{data.get('lingua_conosciuta', 'inglese')} (e viceversa) gli interventi dei partecipanti alla discussione nonché a tradurre dall'italiano all'{data.get('lingua_conosciuta', 'inglese')} il verbale che sarà redatto al termine della riunione.")
        
        # Validità dell'assemblea
        p = doc.add_paragraph()
        p.add_run(f"Il Presidente constata e fa constatare che l'assemblea risulta {data.get('tipo_convocazione', 'regolarmente convocata')} e deve ritenersi valida ed atta a deliberare sul citato ordine del giorno.")
        
        p = doc.add_paragraph()
        p.add_run("Si passa quindi allo svolgimento dell'ordine del giorno.")

    def _add_discussion_section(self, doc, data):
        """Aggiunge la discussione dei punti all'OdG"""
        doc.add_paragraph()
        p = doc.add_paragraph()
        p.add_run("*     *     *").bold = True
        
        data_chiusura = data.get('data_chiusura').strftime('%d/%m/%Y') if hasattr(data.get('data_chiusura'), 'strftime') else '[DATA]'
        
        p = doc.add_paragraph()
        p.add_run(f"In relazione al primo punto il presidente legge il bilancio al {data_chiusura} composto da stato patrimoniale, conto economico e nota integrativa (allegati di seguito al presente verbale).")

    def _add_ripianamento_section(self, doc, data):
        """Aggiunge la sezione del ripianamento perdite"""
        doc.add_paragraph()
        p = doc.add_paragraph()
        p.add_run("*     *     *").bold = True
        
        p = doc.add_paragraph()
        text = "In relazione al secondo punto posto all'ordine del giorno, il Presidente"
        if data.get('has_collegio_sindacale'):
            text += ", sentito il parere favorevole del Collegio Sindacale,"
        text += f" propone all'assemblea di ripianare la perdita mediante la rinuncia al rimborso di una corrispondente quota del credito vantato dai soci nei confronti della società a titolo di {data.get('tipo_credito', 'finanziamento infruttifero soci')}."
        p.add_run(text)
        
        p = doc.add_paragraph()
        text = f"Segue breve discussione tra i soci al termine della quale si passa alla votazione con voto {'palese' if data.get('voto_palese') else 'segreto'} in forza della quale il Presidente constata che, {data.get('esito_votazione', 'all\'unanimità')} l'assemblea"
        p.add_run(text)
        
        p = doc.add_paragraph()
        p.add_run("DELIBERA").bold = True
        
        p = doc.add_paragraph()
        text = f"di approvare la proposta del Presidente e di ripianare, con effetto dalla data odierna, la perdita di euro {data.get('importo_perdita', '')} mediante la rinuncia al rimborso di una corrispondente quota del credito vantato dai soci nei confronti della società a titolo di {data.get('tipo_credito', 'finanziamento infruttifero soci')}."
        p.add_run(text)
        
        p = doc.add_paragraph()
        text = f"Le rinunce al rimborso avverranno in proporzione alla quota di {data.get('tipo_credito', 'finanziamento infruttifero soci')} attualmente in essere e quindi:"
        p.add_run(text)
        
        for rinuncia in data.get('rinunce_soci', []):
            if rinuncia.get('socio'):
                p = doc.add_paragraph()
                text = f"socio {rinuncia.get('socio', '')} per euro {rinuncia.get('importo_rinuncia', '')} pari al {rinuncia.get('percentuale', '')}% della perdita da ripianare;"
                p.add_run(text)
        
        p = doc.add_paragraph()
        text = f"Con effetto dalla data odierna, il residuo credito verso i soci a titolo di {data.get('tipo_credito', 'finanziamento infruttifero soci')} continuerà ad essere regolato dalle condizioni previgenti, ma solo per il residuo importo (al netto dell'avvenuta rinuncia) qui riepilogato:"
        p.add_run(text)
        
        for rinuncia in data.get('rinunce_soci', []):
            if rinuncia.get('socio'):
                p = doc.add_paragraph()
                text = f"socio {rinuncia.get('socio', '')} per euro {rinuncia.get('residuo', '')};"
                p.add_run(text)
        
        p = doc.add_paragraph()
        text = "Ciascun socio rilascia seduta stante al Presidente una dichiarazione sostitutiva di atto notorio che attesta il valore fiscale del credito a cui ha testé rinunciato."
        p.add_run(text)
        
        p = doc.add_paragraph()
        text = "Le dichiarazioni rilasciate dai soci verranno conservate agli atti della società."
        p.add_run(text)
        
        p = doc.add_paragraph()
        p.add_run("*     *     *").bold = True

    def _add_closing_section(self, doc, data):
        """Aggiunge la sezione di chiusura"""
        doc.add_paragraph()
        p = doc.add_paragraph()
        p.add_run("Il Presidente constata che l'ordine del giorno è esaurito e che nessuno chiede la parola.")
        
        esito = data.get('esito_votazione', 'all\'unanimità')
        voto = 'palese' if data.get('voto_palese') else 'segreto'
        allegati = 'unitamente a quanto allegato' if data.get('documenti_allegati') else ''
        
        p = doc.add_paragraph()
        p.add_run(f"Viene quindi redatto il presente verbale e dopo averne data lettura, il Presidente constata che l'assemblea {esito}, con voto {voto}, ne approva il testo {allegati}.")
        
        ora_fine = data.get('ora_fine', '[ORA]')
        p = doc.add_paragraph()
        p.add_run(f"L'assemblea viene sciolta alle ore {ora_fine}.")

    def _add_signatures(self, doc, data):
        """Aggiunge le firme con formattazione professionale"""
        # Aggiunge un'interruzione di pagina prima delle firme
        doc.add_page_break()
        
        # Aggiunge le firme con stile dedicato
        p = doc.add_paragraph(style='Firma')
        p.add_run("_____________________")
        
        p = doc.add_paragraph(style='Firma')
        p.add_run(data.get('presidente', '[PRESIDENTE]'))
        
        p = doc.add_paragraph(style='Firma')
        p.add_run("Il Presidente")
        
        doc.add_paragraph()
        
        p = doc.add_paragraph(style='Firma')
        p.add_run("_____________________")
        
        # Usa il segretario specificato o un placeholder se non disponibile
        segretario = data.get('segretario', '[SEGRETARIO]')
        
        p = doc.add_paragraph(style='Firma')
        p.add_run(segretario)
        
        p = doc.add_paragraph(style='Firma')
        p.add_run("Il Segretario")
        
        # Aggiunge la data di generazione
        doc.add_paragraph()
        p = doc.add_paragraph(style='BodyText')
        p.add_run(f"Generato il {date.today().strftime('%d/%m/%Y')}")

# Registra il template
DocumentTemplateFactory.register_template('verbale_assemblea_approvazione_bilancio', VerbaleAssembleaCompletoTemplate)
