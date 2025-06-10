"""
Modulo per la gestione standardizzata dei dati comuni a tutti i verbali di assemblea.
Questo modulo centralizza l'estrazione e il popolamento delle informazioni standard
come dati aziendali, soci, amministratori, ecc.
"""

import streamlit as st
import pandas as pd
from datetime import date
from typing import Dict, List, Any, Optional


class CommonDataHandler:
    """Gestore centralizzato per i dati comuni a tutti i verbali"""
    
    @staticmethod
    def extract_and_populate_company_data(extracted_data: dict) -> dict:
        """Estrae e popola i dati standard dell'azienda"""
        form_data = {}
        
        # Dati base azienda - standardizzati per tutti i verbali
        st.subheader("🏢 Dati Società")
        form_data["denominazione"] = st.text_input("Denominazione", extracted_data.get("denominazione", ""))
        form_data["sede_legale"] = st.text_input("Sede legale", extracted_data.get("sede_legale", ""))
        form_data["codice_fiscale"] = st.text_input("Codice fiscale", extracted_data.get("codice_fiscale", ""))
        
        # Gestione standardizzata del capitale sociale
        capitale_data = CommonDataHandler._process_capitale_sociale(extracted_data.get("capitale_sociale", ""))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            form_data["capitale_deliberato"] = st.text_input("Capitale deliberato (€)", capitale_data["deliberato"])
        with col2:
            form_data["capitale_sottoscritto"] = st.text_input("Capitale sottoscritto (€)", capitale_data["sottoscritto"])
        with col3:
            form_data["capitale_versato"] = st.text_input("Capitale versato (€)", capitale_data["versato"])
        
        return form_data
    
    @staticmethod
    def _process_capitale_sociale(capitale_raw: Any) -> dict:
        """Processa i dati del capitale sociale in modo standardizzato"""
        if isinstance(capitale_raw, dict):
            return {
                "deliberato": capitale_raw.get("deliberato", "10.000,00"),
                "sottoscritto": capitale_raw.get("sottoscritto", "10.000,00"),
                "versato": capitale_raw.get("versato", "2.500,00")
            }
        else:
            # Se è una stringa, pulisci e usa come valore unico
            capitale_str = str(capitale_raw).strip() if capitale_raw else "10.000,00"
            capitale_str = capitale_str.replace("{", "").replace("}", "").replace("'", "")
            if capitale_str and not any(c in capitale_str for c in ",.0123456789"):
                capitale_str = "10.000,00"
            return {
                "deliberato": capitale_str,
                "sottoscritto": capitale_str,
                "versato": capitale_str
            }
    
    @staticmethod
    def extract_and_populate_assembly_data(extracted_data: dict) -> dict:
        """Estrae e popola i dati standard dell'assemblea"""
        form_data = {}
        today = date.today()
        
        st.subheader("📅 Dati Assemblea")
        
        # Date e orari standardizzati
        col1, col2 = st.columns(2)
        with col1:
            form_data["data_assemblea"] = st.date_input("Data assemblea", today)
            form_data["ora_inizio"] = st.text_input("Ora inizio assemblea", "09:00")
        with col2:
            form_data["luogo_assemblea"] = st.text_input("Luogo assemblea", extracted_data.get("sede_legale", ""))
            form_data["ora_fine"] = st.text_input("Ora fine assemblea", "10:00")
        
        # Configurazioni assemblea standardizzate
        col1, col2 = st.columns(2)
        with col1:
            form_data["tipo_assemblea"] = st.selectbox("Tipo di assemblea", ["Ordinaria", "Straordinaria"])
            form_data["tipo_convocazione"] = st.selectbox("Tipo di convocazione", ["regolarmente convocata", "totalitaria"])
        with col2:
            form_data["esito_votazione"] = st.selectbox("Esito votazione", ["approvato all'unanimità", "approvato a maggioranza", "respinto"])
            form_data["voto_palese"] = st.checkbox("Votazione con voto palese", value=True)
        
        # Checkbox standard per tutti i verbali
        st.subheader("⚙️ Configurazioni Standard")
        col1, col2, col3 = st.columns(3)
        with col1:
            form_data["audioconferenza"] = st.checkbox("Partecipazione in audioconferenza", value=True)
            form_data["documenti_allegati"] = st.checkbox("Documenti allegati al verbale", value=True)
        with col2:
            form_data["collegio_sindacale"] = st.checkbox("Collegio sindacale presente")
            form_data["revisore"] = st.checkbox("Revisore legale presente")
        with col3:
            form_data["lingua_straniera"] = st.checkbox("Partecipante lingua straniera")
        
        # Campo revisore condizionale
        if form_data["revisore"]:
            form_data["nome_revisore"] = st.text_input("Nome del revisore legale", "", 
                                                      help="Inserire il nome del revisore se presente")
        else:
            form_data["nome_revisore"] = ""
        
        return form_data
    
    @staticmethod
    def extract_and_populate_participants_data(extracted_data: dict, unique_key_suffix: str = "", 
                                              extended_admin_columns: bool = False) -> dict:
        """Estrae e popola i dati standardizzati di soci e amministratori"""
        form_data = {}
        
        # Soci e Partecipazioni - standardizzato per tutti i verbali
        st.subheader("👥 Soci e Partecipazioni")
        
        # Note informative
        st.info("""
        💡 **Guida alla compilazione:**
        
        - **Tipo Partecipazione "Delegato"** → Compilare anche "Nome Delegato"
        - **Tipo Soggetto "Società"** → Compilare anche "Rappresentante Legale"  
        - Dopo aver modificato i dati, cliccare "🔄 Aggiorna Anteprima" se l'anteprima non si aggiorna automaticamente
        """)
        
        soci_data = CommonDataHandler._prepare_soci_data(extracted_data.get("soci", []))
        df_soci = pd.DataFrame(soci_data)
        
        # Configurazione colonne standardizzata
        column_config_soci = {
            "tipo_partecipazione": st.column_config.SelectboxColumn(
                "Tipo Partecipazione",
                options=["Diretto", "Delegato"],
                default="Diretto"
            ),
            "tipo_soggetto": st.column_config.SelectboxColumn(
                "Tipo Soggetto",
                options=["Persona Fisica", "Società"],
                default="Persona Fisica"
            ),
            "presente": st.column_config.CheckboxColumn("Presente"),
            "nome": st.column_config.TextColumn("Nome Socio/Società", required=True),
            "quota_percentuale": st.column_config.TextColumn("Quota %"),
            "quota_euro": st.column_config.TextColumn("Quota €"),
            "delegato": st.column_config.TextColumn("Nome Delegato (se delegato)"),
            "rappresentante_legale": st.column_config.TextColumn(
                "Rappresentante Legale", 
                help="⚠️ IMPORTANTE: Compilare SOLO se Tipo Soggetto = 'Società'"
            )
        }
        
        df_soci_edited = st.data_editor(
            df_soci, 
            num_rows="dynamic", 
            use_container_width=True,
            column_config=column_config_soci,
            key=f"soci_editor_{unique_key_suffix}"
        )
        
        form_data["soci"] = df_soci_edited.to_dict("records")
        
        # Amministratori - standardizzato per tutti i verbali
        st.subheader("👨‍💼 Organi Sociali")
        
        amministratori_data = CommonDataHandler._prepare_amministratori_data(extracted_data.get("amministratori", []), 
                                                                            extracted_data.get("rappresentante", ""))
        df_amm = pd.DataFrame(amministratori_data)
        
        # Assicurati che la colonna 'presente' esista
        if 'presente' not in df_amm.columns:
            df_amm['presente'] = True
        
        # Configurazione colonne base
        column_config_amm = {
            "presente": st.column_config.CheckboxColumn("Presente"),
            "nome": st.column_config.TextColumn("Nome", required=True),
            "carica": st.column_config.TextColumn("Carica")
        }
        
        # Aggiungi colonne estese se richieste
        if extended_admin_columns:
            if 'assente_giustificato' not in df_amm.columns:
                df_amm['assente_giustificato'] = False
            column_config_amm["assente_giustificato"] = st.column_config.CheckboxColumn("Assente Giustificato")
            column_config_amm["carica"] = st.column_config.SelectboxColumn(
                "Carica",
                options=["Presidente CDA", "Consigliere", "Consigliere Delegato", "Amministratore Delegato", "Amministratore Unico"],
                default="Consigliere"
            )
        
        df_amm_edited = st.data_editor(df_amm, num_rows="dynamic", use_container_width=True,
                                      column_config=column_config_amm,
                                      key=f"amministratori_editor_{unique_key_suffix}")
        form_data["amministratori"] = df_amm_edited.to_dict("records")
        
        # Selezione dinamica presidente e segretario - standardizzata
        form_data.update(CommonDataHandler._get_presidente_segretario_selection(
            form_data["amministratori"], 
            form_data["soci"], 
            extracted_data.get("rappresentante", ""),
            unique_key_suffix
        ))
        
        # Bottone refresh standardizzato
        if st.button("🔄 Aggiorna Anteprima", 
                    help="Clicca se l'anteprima non si aggiorna automaticamente", 
                    key=f"refresh_preview_{unique_key_suffix}"):
            st.rerun()
        
        return form_data
    
    @staticmethod
    def _prepare_soci_data(soci_raw: List[dict]) -> List[dict]:
        """Prepara i dati dei soci in formato standardizzato"""
        if not soci_raw:
            return [{"nome": "", "quota_percentuale": "", "quota_euro": "", "presente": True, 
                    "tipo_partecipazione": "Diretto", "delegato": "", "tipo_soggetto": "Persona Fisica", 
                    "rappresentante_legale": ""}]
        
        # Filtra e pulisce i dati in ingresso
        soci_cleaned = []
        for socio in soci_raw:
            # Salta elementi che non sono dizionari o sono None/vuoti
            if not isinstance(socio, dict):
                if isinstance(socio, str) and socio.strip():
                    # Se è una stringa non vuota, creane un dizionario con nome
                    soci_cleaned.append({"nome": socio.strip()})
                continue
            
            if socio:  # Solo dizionari non vuoti
                soci_cleaned.append(socio)
        
        # Se dopo la pulizia non ci sono soci validi, restituisci il template di default
        if not soci_cleaned:
            return [{"nome": "", "quota_percentuale": "", "quota_euro": "", "presente": True, 
                    "tipo_partecipazione": "Diretto", "delegato": "", "tipo_soggetto": "Persona Fisica", 
                    "rappresentante_legale": ""}]
        
        # Assicurati che tutte le colonne necessarie esistano
        standard_keys = ['tipo_partecipazione', 'delegato', 'presente', 'tipo_soggetto', 'rappresentante_legale']
        default_values = {
            'tipo_partecipazione': 'Diretto',
            'delegato': '',
            'presente': True,
            'tipo_soggetto': 'Persona Fisica',
            'rappresentante_legale': ''
        }
        
        for socio in soci_cleaned:
            if isinstance(socio, dict):  # Doppio controllo di sicurezza
                for key in standard_keys:
                    if key not in socio:
                        socio[key] = default_values[key]
        
        return soci_cleaned
    
    @staticmethod
    def _prepare_amministratori_data(amministratori_raw: List[dict], rappresentante: str = "") -> List[dict]:
        """Prepara i dati degli amministratori in formato standardizzato"""
        if not amministratori_raw and rappresentante:
            return [{"nome": rappresentante, "carica": "Amministratore Unico", "presente": True}]
        elif not amministratori_raw:
            return [{"nome": "", "carica": "", "presente": True}]
        
        # Assicurati che tutte le colonne necessarie esistano
        for amm in amministratori_raw:
            if 'presente' not in amm:
                amm['presente'] = True
            if 'carica' not in amm or not amm['carica']:
                amm['carica'] = "Amministratore Unico"
            # Aggiungi supporto per colonne avanzate se non esistono
            if 'assente_giustificato' not in amm:
                amm['assente_giustificato'] = False
        
        return amministratori_raw
    
    @staticmethod
    def _get_presidente_segretario_selection(amministratori: List[dict], soci: List[dict], 
                                           rappresentante_default: str, unique_key_suffix: str) -> dict:
        """Gestisce la selezione standardizzata di presidente e segretario"""
        form_data = {}
        
        # Selezione presidente
        options_presidente = [a.get('nome', '') for a in amministratori if a.get('nome', '').strip()]
        if options_presidente:
            form_data["presidente"] = st.selectbox("Seleziona Presidente", options_presidente,
                                                  key=f"presidente_select_{unique_key_suffix}")
        else:
            form_data["presidente"] = st.text_input("Nome presidente", rappresentante_default,
                                                   key=f"presidente_input_{unique_key_suffix}")
        
        # Selezione segretario
        options_segretario = [item.get('nome', '') for item in soci + amministratori if item.get('nome', '').strip()]
        if options_segretario:
            form_data["segretario"] = st.selectbox("Seleziona Segretario", options_segretario,
                                                  key=f"segretario_select_{unique_key_suffix}")
        else:
            form_data["segretario"] = st.text_input("Segretario", "",
                                                   key=f"segretario_input_{unique_key_suffix}")
        
        return form_data
    
    @staticmethod
    def get_standard_ruoli_presidente() -> List[str]:
        """Restituisce la lista standardizzata dei ruoli del presidente"""
        return ["Amministratore Unico", "Presidente del Consiglio di Amministrazione", 
                "Consigliere delegato", "Altro"]
    
    @staticmethod
    def get_default_date_chiusura() -> date:
        """Restituisce la data di chiusura di default (31 dicembre dell'anno precedente)"""
        today = date.today()
        return date(today.year - 1, 12, 31)
    
    @staticmethod
    def validate_common_data(form_data: dict) -> List[str]:
        """Valida i dati comuni e restituisce una lista di errori"""
        errors = []
        
        # Validazioni base
        required_fields = ["denominazione", "sede_legale", "codice_fiscale"]
        for field in required_fields:
            if not form_data.get(field, "").strip():
                errors.append(f"Il campo '{field}' è obbligatorio")
        
        # Validazione soci
        soci = form_data.get("soci", [])
        if not soci or not any(s.get("nome", "").strip() for s in soci):
            errors.append("Almeno un socio deve essere specificato")
        
        # Validazione amministratori
        amministratori = form_data.get("amministratori", [])
        if not amministratori or not any(a.get("nome", "").strip() for a in amministratori):
            errors.append("Almeno un amministratore deve essere specificato")
        
        # Validazione presidente e segretario
        if not form_data.get("presidente", "").strip():
            errors.append("Il presidente deve essere specificato")
        
        if not form_data.get("segretario", "").strip():
            errors.append("Il segretario deve essere specificato")
        
        return errors 