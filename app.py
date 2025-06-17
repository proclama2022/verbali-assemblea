import streamlit as st
import os
from dotenv import load_dotenv
from mistralai import Mistral
import pandas as pd
from datetime import date
import sys

# Add src directory to path for imports
sys.path.append('src')

from document_processors import DocumentProcessorFactory
from document_templates import DocumentTemplateFactory
from load_templates import load_all_templates
from multi_document_processor import MultiDocumentProcessor

# Load environment variables
load_dotenv()
api_key = os.environ.get("MISTRAL_API_KEY")

# Initialize Mistral client
client = Mistral(api_key=api_key)

# Page configuration
st.set_page_config(
    page_title="Sistema di Gestione Documenti Legali",
    page_icon="📄",
    layout="wide"
)

# Load all available templates (removed cache to fix the issue)
def load_templates():
    """Load templates and return status"""
    try:
        loaded = load_all_templates()
        available = DocumentTemplateFactory.get_available_templates()
        return len(loaded), available
    except Exception as e:
        st.error(f"Errore nel caricamento template: {e}")
        return 0, []

def display_progress_bar():
    """Display progress indicator showing current step"""
    # Check current state
    document_loaded = 'document_text' in st.session_state and st.session_state.document_text
    info_extracted = 'extracted_info' in st.session_state and st.session_state.extracted_info
    multi_doc_mode = st.session_state.get('multi_document_mode', False)
    manual_selection_completed = st.session_state.get('manual_selection_completed', False)
    
    # Create progress indicator
    st.markdown("### 🔄 Progresso Elaborazione")
    
    # Progress bar layout - adjust based on mode
    if multi_doc_mode:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.info("⏸️ **1. Documento Singolo**")
            st.caption("Modalità Multi-Documenti attiva")
        
        with col2:
            if st.session_state.get('multi_processor') and st.session_state.multi_processor.processed_documents:
                st.success("✅ **2. Multi-Documenti**")
                doc_count = len(st.session_state.multi_processor.processed_documents)
                st.caption(f"{doc_count} documenti processati")
            else:
                st.warning("⏳ **2. Multi-Documenti**")
        
        with col3:
            if manual_selection_completed:
                st.success("✅ **3. Selezione Manuale**")
                st.caption("Informazioni selezionate")
            elif st.session_state.get('multi_processor') and st.session_state.multi_processor.processed_documents:
                st.warning("⏳ **3. Selezione Manuale**")
                st.caption("Pronti per la selezione")
            else:
                st.info("⏸️ **3. Selezione Manuale**")
        
        with col4:
            if info_extracted and manual_selection_completed:
                st.warning("⏳ **4. Genera Documento**")
            else:
                st.info("⏸️ **4. Genera Documento**")
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if document_loaded:
                st.success("✅ **1. Documento Caricato**")
            else:
                st.info("🔄 **1. Carica Documento**")
        
        with col2:
            if info_extracted:
                st.success("✅ **2. Informazioni Estratte**")
            elif document_loaded:
                st.warning("⏳ **2. Estrai Informazioni**")
            else:
                st.info("⏸️ **2. Estrai Informazioni**")
        
        with col3:
            if info_extracted:
                st.warning("⏳ **3. Genera Documento**")
            else:
                st.info("⏸️ **3. Genera Documento**")
    
    # Status summary
    if multi_doc_mode:
        if info_extracted and manual_selection_completed:
            st.success("🎯 **Multi-Documenti: Pronto per generare documento!** Vai alla tab 'Genera Documento'")
        elif st.session_state.get('multi_processor') and st.session_state.multi_processor.processed_documents:
            st.info("🎯 **Multi-Documenti: Pronto per selezione manuale!** Vai alla tab 'Estrazione Multi-Documenti'")
        else:
            st.info("📤 **Multi-Documenti: Carica documenti** nella tab 'Estrazione Multi-Documenti'")
    else:
        if info_extracted:
            st.success("🎯 **Pronto per generare documento!** Vai alla tab 'Genera Documento'")
        elif document_loaded:
            st.info("🔍 **Pronto per estrarre informazioni!** Vai alla tab 'Estrai Informazioni'")
        else:
            st.info("📤 **Inizia caricando un documento** nella tab 'Carica Documento'")
    
    st.markdown("---")

def main():
    st.title("📄 Sistema di Gestione Documenti Legali")
    st.markdown("**Sistema modulare per estrazione informazioni e generazione documenti**")
    
    # Load templates at startup
    loaded_count, available_templates = load_templates()
    
    # Hotfix per rimuovere template non più esistenti
    available_templates = [t for t in available_templates if t != 'verbale_standard']
    
    if loaded_count > 0:
        st.success(f"✅ {loaded_count} template caricati: {', '.join(available_templates)}")
    else:
        st.warning("⚠️ Nessun template caricato. Verifica la cartella `templates/`")
    
    # Display progress bar
    display_progress_bar()
    
    # SIDEBAR SNELLA E PULITA
    with st.sidebar:
        st.header("🎯 Configurazione")
        
        # Selezione template semplificata
        if available_templates:
            # Mapping per nomi display
            template_display_names = {
                'verbale_semplice': '📝 Verbale Semplice',
                'nomina_amministratore': '👤 Nomina Amministratore',
                'revoca_amministratore': '❌ Revoca Amministratore',
                'bilancio': '📊 Approvazione Bilancio',
                'nomina_revisore': '🔍 Nomina del Revisore',
                'nomina_collegio_sindacale': '🏛️ Nomina Collegio Sindacale',
                'ratifica_operato': '⚖️ Ratifica Operato dell\'Organo Amministrativo',
                'verbale_assemblea_amministratore_unico_template': '👤 Amministratore Unico'
            }
            
            # Inizializzazione stato
            if 'selected_template_type' not in st.session_state:
                st.session_state.selected_template_type = None
                st.session_state.template_locked = False
            
            # Interfaccia semplificata
            if not st.session_state.template_locked:
                st.markdown("**Tipo di verbale:**")
                
                # Dropdown semplice
                display_options = [(template, template_display_names.get(template, template.replace('_', ' ').title())) 
                                 for template in available_templates]
                
                selected_option = st.selectbox(
                    "Seleziona:",
                    display_options,
                    format_func=lambda x: x[1],
                    key="template_selector",
                    label_visibility="collapsed"
                )
                template_type = selected_option[0] if selected_option else None
                
                # Conferma selezione
                if template_type and st.button("✅ Conferma", type="primary", use_container_width=True):
                    st.session_state.selected_template_type = template_type
                    st.session_state.template_locked = True
                    st.rerun()
                    
            else:
                # Template selezionato
                template_type = st.session_state.selected_template_type
                st.success(f"✅ {template_display_names.get(template_type, template_type)}")
                
                if st.button("🔄 Cambia", type="secondary", use_container_width=True):
                    # Reset stato
                    for key in ['selected_template_type', 'template_locked', 'document_text', 'extracted_info', 
                              'uploaded_file', 'generated_document_path', 'generated_document_name']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
        else:
            st.warning("⚠️ Nessun template disponibile")
            template_type = None
            
        # Tipo documento (semplificato)
        st.markdown("---")
        st.markdown("**Tipo documento:**")
        available_document_types = DocumentProcessorFactory.get_available_types()
        document_type = st.selectbox(
            "Documento:",
            available_document_types,
            format_func=lambda x: x.replace('_', ' ').title(),
            label_visibility="collapsed"
        )
        
        # Stato compatto
        st.markdown("**Stato:**")
        
        # Indicatori di stato semplici
        template_status = "✅" if st.session_state.get('template_locked', False) else "❌"
        doc_status = "✅" if st.session_state.get('document_text') else "❌"
        info_status = "✅" if st.session_state.get('extracted_info') else "❌"
        
        st.markdown(f"• Template: {template_status}")
        st.markdown(f"• Documento: {doc_status}")
        st.markdown(f"• Dati estratti: {info_status}")
        
        # Reset rapido
        if st.button("🗑️ Reset", use_container_width=True):
            for key in ['document_text', 'extracted_info', 'uploaded_file', 'generated_document_path', 'generated_document_name']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # Controlla che il template sia selezionato
    if not st.session_state.get('template_locked', False):
        st.info("👈 Seleziona un template nella sidebar per iniziare")
        return
        
    # Usa il template selezionato e bloccato
    template_type = st.session_state.selected_template_type
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Carica", "🔍 Estrai", "📑 Multi-Doc", "📝 Genera"])
    
    with tab1:
        st.header("📤 Carica Documento")
        
        # File uploader semplificato
        uploaded_file = st.file_uploader(
            "Carica PDF o file di testo",
            type=["pdf", "txt"],
            help="Carica il documento da cui estrarre le informazioni"
        )
        
        if uploaded_file is not None:
            st.success(f"📁 {uploaded_file.name}")
            
            # Store file in session state
            if 'uploaded_file' not in st.session_state or st.session_state.uploaded_file != uploaded_file:
                st.session_state.uploaded_file = uploaded_file
                st.session_state.document_text = None
                st.session_state.extracted_info = None
            
            # Process file
            processor = DocumentProcessorFactory.create_processor(document_type, client)
            try:                
                if uploaded_file.type == "text/plain":
                    document_text = uploaded_file.getvalue().decode("utf-8")
                    st.session_state.document_text = document_text
                    st.success("✅ Testo estratto")
                    
                elif uploaded_file.type == "application/pdf":
                    pdf_bytes = uploaded_file.getvalue()
                    
                    with st.spinner("🔄 Elaborazione PDF..."):
                        pypdf2_text, ocr_text = processor.extract_text_from_pdf(pdf_bytes)
                    
                    # Selezione metodo semplificata
                    options = []
                    if pypdf2_text.strip():
                        options.append(("🔤 Testo digitale", pypdf2_text))
                    if ocr_text.strip():
                        options.append(("📷 OCR", ocr_text))
                    
                    if options:
                        choice = st.radio(
                            "Metodo estrazione:",
                            options,
                            format_func=lambda x: x[0]
                        )
                        st.session_state.document_text = choice[1]
                        st.success("✅ Testo estratto")
                    else:
                        st.error("❌ Impossibile estrarre testo")
                        st.session_state.document_text = None
                
                # Show selected text
                if st.session_state.document_text:
                    with st.expander("📖 Visualizza testo estratto per elaborazione"):
                        st.text_area(
                            "Testo che verrà processato", 
                            st.session_state.document_text, 
                            height=300,
                            label_visibility="visible"
                        )
                        
            except Exception as e:
                st.error(f"❌ Errore nel processamento del file: {e}")
    
    with tab2:
        st.header("🔍 Estrai Informazioni")
        
        if 'document_text' not in st.session_state or not st.session_state.document_text:
            st.info("👈 Carica prima un documento")
        else:
            processor = DocumentProcessorFactory.create_processor(document_type, client)
            
            # Extract information button
            if st.button("🔍 Estrai Informazioni", type="primary", use_container_width=True):
                with st.spinner("🤖 Estrazione in corso..."):
                    extracted_info = processor.extract_information(st.session_state.document_text)
                    st.session_state.extracted_info = extracted_info
                st.success("✅ Informazioni estratte!")
                st.rerun()
            
            # Show extracted information
            if 'extracted_info' in st.session_state and st.session_state.extracted_info:
                st.success("✅ **Informazioni estratte e pronte per l'uso!**")
                st.subheader("📋 Informazioni Estratte")
                
                # Display as editable form
                extracted_data = st.session_state.extracted_info.copy()
                
                with st.form("edit_extracted_info"):
                    st.markdown("**✏️ Modifica le informazioni estratte:**")
                    
                    edited_data = {}
                    
                    # Create columns for better layout
                    col1, col2 = st.columns(2)
                    
                    simple_fields = []
                    list_fields = []
                    
                    # Separate simple and complex fields
                    for key, value in extracted_data.items():
                        if isinstance(value, list):
                            list_fields.append((key, value))
                        else:
                            simple_fields.append((key, value))
                    
                    # Simple fields in columns
                    for i, (key, value) in enumerate(simple_fields):
                        with col1 if i % 2 == 0 else col2:
                            edited_data[key] = st.text_input(
                                key.replace('_', ' ').title(),
                                value=str(value) if value else "",
                                key=f"input_{key}"
                            )
                    
                    # List fields full width
                    for key, value in list_fields:
                        st.markdown(f"**{key.replace('_', ' ').title()}:**")
                        if value:
                            df = pd.DataFrame(value)
                            edited_df = st.data_editor(
                                df, 
                                num_rows="dynamic", 
                                key=f"editor_{key}",
                                use_container_width=True
                            )
                            edited_data[key] = edited_df.to_dict("records")
                        else:
                            # Empty list, allow user to add data
                            st.info(f"➕ Nessun dato trovato per {key}. Usa il data editor per aggiungere manualmente.")
                            empty_df = pd.DataFrame()
                            edited_df = st.data_editor(
                                empty_df, 
                                num_rows="dynamic", 
                                key=f"editor_{key}",
                                use_container_width=True
                            )
                            edited_data[key] = edited_df.to_dict("records")
                    
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        if st.form_submit_button("💾 Salva Modifiche", type="primary", use_container_width=True):
                            st.session_state.extracted_info = edited_data
                            st.success("✅ Informazioni aggiornate!")
                            st.info("📝 **Ora puoi generare il documento** nella tab 'Genera Documento'")
                            st.rerun()
    
    with tab3:
        st.header("📑 Estrazione Multi-Documenti")
        st.markdown("**Carica diversi documenti ed estrai le informazioni separatamente, poi scegli manualmente quali utilizzare**")
        
        # Initialize multi-document processor in session state
        if 'multi_processor' not in st.session_state:
            st.session_state.multi_processor = MultiDocumentProcessor(client)
        
        multi_processor = st.session_state.multi_processor
        
        # Get processing summary
        summary = multi_processor.get_processing_summary()
        
        # Status display - simplified
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 Documenti", summary["total_documents"])
        with col2:
            processed_types = len(set(summary["document_types"])) if summary["document_types"] else 0
            st.metric("🔢 Tipi", processed_types)
        with col3:
            manual_selection_done = 'extracted_info' in st.session_state and st.session_state.extracted_info and st.session_state.get('manual_selection_completed', False)
            selection_status = "✅ Completata" if manual_selection_done else "❌ Da fare"
            st.metric("🎯 Selezione", selection_status)
        
        # Document upload section
        st.subheader("📤 Carica e Elabora Documenti")
        
        # Multiple file uploader
        uploaded_files = st.file_uploader(
            "Carica i tuoi documenti (PDF o TXT)",
            type=["pdf", "txt"],
            accept_multiple_files=True,
            help="Carica documenti aziendali di qualsiasi tipo",
            key="multi_doc_uploader"
        )
        
        # Process uploaded files with simplified interface
        if uploaded_files:
            st.success(f"📁 {len(uploaded_files)} documento/i caricato/i")
            
            # Process each file with auto-type detection
            for i, uploaded_file in enumerate(uploaded_files):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    # Auto-suggest document type
                    if uploaded_file.type == "text/plain":
                        file_content = uploaded_file.getvalue().decode("utf-8")
                    else:
                        file_content = ""
                    
                    suggested_type = multi_processor.suggest_document_type(uploaded_file.name, file_content)
                    
                    # Find index of suggested type
                    available_types = DocumentProcessorFactory.get_available_types()
                    try:
                        suggested_index = available_types.index(suggested_type)
                    except ValueError:
                        suggested_index = 0
                    
                    doc_type = st.selectbox(
                        f"📄 {uploaded_file.name}:",
                        available_types,
                        index=suggested_index,
                        format_func=lambda x: x.replace('_', ' ').title(),
                        key=f"doc_type_{i}_{uploaded_file.name}",
                        help=f"Tipo suggerito: {suggested_type.replace('_', ' ').title()}"
                    )
                
                with col2:
                    st.write(f"**{uploaded_file.size / 1024:.1f} KB**")
                
                with col3:
                    if st.button("🔄 Elabora", key=f"process_btn_{i}_{uploaded_file.name}"):
                        with st.spinner(f"Elaborazione..."):
                            file_bytes = uploaded_file.getvalue()
                            extracted_info = multi_processor.process_document(
                                file_bytes, uploaded_file.name, doc_type
                            )
                            if extracted_info:
                                st.success(f"✅ Elaborato!")
                                st.rerun()
        
        # Show processed documents with quick stats
        if summary["total_documents"] > 0:
            st.subheader("📋 Documenti Elaborati")
            
            # Quick overview table
            if st.session_state.get('template_locked', False):
                template_type = st.session_state.selected_template_type
                template_extraction = multi_processor.extract_template_fields_from_documents(template_type)
                
                if template_extraction.get("documents"):
                    # Simple summary table
                    summary_data = []
                    for doc in template_extraction["documents"]:
                        summary_data.append({
                            "📄 Documento": doc['file_name'],
                            "📊 Completezza": f"{doc['completeness_percentage']}%",
                            "✅ Campi": len(doc['available_fields'])
                        })
                    
                    if summary_data:
                        df = pd.DataFrame(summary_data)
                        st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Individual documents - collapsed by default
            with st.expander("🔍 Dettagli Documenti", expanded=False):
                for doc in multi_processor.processed_documents:
                    st.markdown(f"**📄 {doc['file_name']} ({doc['document_type']})**")
                    
                    # Simple info count
                    info_count = len([k for k, v in doc['extracted_info'].items() if v])
                    st.caption(f"Informazioni estratte: {info_count}")
                    st.markdown("---")
        
        # Manual selection section - simplified
        if summary["total_documents"] >= 1 and st.session_state.get('template_locked', False):
            st.subheader("🎯 Selezione Informazioni")
            
            template_type = st.session_state.selected_template_type
            template_extraction = multi_processor.extract_template_fields_from_documents(template_type)
            
            if template_extraction.get("documents"):
                # Create the simplified manual selection interface
                selected_data = multi_processor.create_manual_selection_interface(template_extraction)
                
                # Single confirm button
                if st.button("💾 Conferma e Procedi al Documento", type="primary", use_container_width=True):
                    if selected_data:
                        # Combina i dati estratti automaticamente con le selezioni manuali
                        final_data = {}
                        for doc in multi_processor.processed_documents:
                            final_data.update(doc.get('extracted_info', {}))
                        
                        # Sovrascrivi con le selezioni manuali, se valide
                        for k, v in selected_data.items():
                            if v not in (None, "", []):
                                final_data[k] = v
                        
                        if final_data:
                            st.session_state.extracted_info = final_data
                            st.session_state.manual_selection_completed = True
                            st.session_state.multi_document_mode = True
                            
                            st.success("✅ Selezione completata!")
                            st.info("📝 Vai alla tab 'Genera Documento' per creare il verbale.")
                            st.rerun()
                        else:
                            st.warning("⚠️ Seleziona almeno un campo.")
                    else:
                        st.warning("⚠️ Nessuna informazione selezionata.")
            else:
                st.error("❌ Errore nell'analisi dei documenti")
        
        elif summary["total_documents"] < 1:
            st.info("📤 **Carica almeno 1 documento** per iniziare")
        elif not st.session_state.get('template_locked', False):
            st.warning("⚠️ **Seleziona un template** nella sidebar")
        
        # Quick clear button
        if summary["total_documents"] > 0:
            if st.button("🗑️ Ricomincia", type="secondary"):
                multi_processor.clear_documents()
                for key in ['multi_document_mode', 'manual_selection_completed', 'manual_selections']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.success("🗑️ Documenti cancellati")
                st.rerun()
    
    with tab4:
        st.header("📝 Generazione Documento")
        
        if template_type is None:
            st.warning("⚠️ Nessun template disponibile")
            st.info("💡 Per aggiungere template, crea file Python nella cartella `templates/` seguendo l'esempio")
            
            # Debug info
            with st.expander("🔧 Debug Template"):
                st.write(f"Template caricati: {loaded_count}")
                st.write(f"Template disponibili: {available_templates}")
                
                if st.button("🔄 Ricarica Template Debug"):
                    new_count, new_templates = load_templates()
                    st.write(f"Nuovo caricamento: {new_count} template, {new_templates}")
                    
        elif 'extracted_info' not in st.session_state or not st.session_state.extracted_info:
            st.warning("⚠️ Estrai prima le informazioni nella tab 'Estrai Informazioni'")
            st.info("👈 Usa le tab precedenti per completare il processo di estrazione")
            
            # Show what's missing
            if 'document_text' not in st.session_state or not st.session_state.document_text:
                st.error("❌ **Manca:** Documento caricato")
            else:
                st.success("✅ **Disponibile:** Documento caricato")
                
            st.error("❌ **Manca:** Informazioni estratte")
            
            # Opzione per usare dati di esempio
            if st.button("🔄 Usa dati di esempio", type="secondary"):
                try:
                    from src.sample_data import get_sample_data
                except ModuleNotFoundError:
                    from sample_data import get_sample_data  # fallback se path differente

                st.session_state.extracted_info = get_sample_data(template_type)
                st.success("✅ Dati di esempio caricati! Ricarico l'app...")
                st.rerun()
            
        else:
            st.success("🎯 **Tutto pronto per la generazione del documento!**")
            
            try:
                template = DocumentTemplateFactory.create_template(template_type)
                
                st.info(f"📄 Generazione: **{template.get_template_name()}**")
                
                # Crea form_data FUORI dal form per renderli disponibili all'anteprima
                # Questa chiamata crea i widget del form e restituisce i dati aggiornati
                form_data = template.get_form_fields(st.session_state.extracted_info)
                
                # Anteprima SEMPRE disponibile fuori dal form
                template.show_preview(form_data)
                
                # Show template form
                with st.form("template_form"):
                    st.markdown("**⚙️ I dati sono configurati sopra. Clicca per generare il documento:**")
                    
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        generate_button = st.form_submit_button("📝 Genera Documento", type="primary", use_container_width=True)
                    
                    if generate_button:
                        try:
                            with st.spinner("🔄 Generazione documento in corso..."):
                                # Rigenera form_data con i valori attuali prima di generare
                                # (Questo è necessario perché i widget potrebbero essere cambiati dall'utente)
                                current_form_data = {}
                                
                                # Recupera i valori dai widget di Streamlit usando le chiavi
                                for key in form_data.keys():
                                    if key in st.session_state:
                                        current_form_data[key] = st.session_state[key]
                                    else:
                                        current_form_data[key] = form_data[key]
                                
                                # Generate document
                                doc = template.generate_document(current_form_data)
                                
                                # Save document
                                output_path = f"output/{template_type}_generated.docx"
                                os.makedirs("output", exist_ok=True)
                                doc.save(output_path)
                                
                                # Store in session state for download outside form
                                st.session_state.generated_document_path = output_path
                                st.session_state.generated_document_name = f"{template_type}_{date.today().strftime('%Y%m%d')}.docx"
                            
                            st.success("✅ Documento generato con successo!")
                            st.balloons()  # Celebration effect
                            st.info("🔄 **Processo completato!** Puoi iniziare un nuovo documento con 'Cancella Tutto' nella sidebar")
                            st.rerun()  # Rerun to show download button
                            
                        except Exception as e:
                            st.error(f"❌ Errore nella generazione del documento: {e}")
                            st.exception(e)
                
                # Download button OUTSIDE the form
                if 'generated_document_path' in st.session_state and os.path.exists(st.session_state.generated_document_path):
                    st.success("📄 **Documento pronto per il download!**")
                    
                    # Provide download
                    with open(st.session_state.generated_document_path, "rb") as file:
                        col1, col2, col3 = st.columns([1, 1, 1])
                        with col2:
                            download_success = st.download_button(
                                label="⬇️ Scarica Documento",
                                data=file,
                                file_name=st.session_state.generated_document_name,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True
                            )
                    
                    # Clear the generated document from session after showing download
                    if download_success:
                        if 'generated_document_path' in st.session_state:
                            del st.session_state['generated_document_path']
                        if 'generated_document_name' in st.session_state:
                            del st.session_state['generated_document_name']
                            
            except ValueError as e:
                st.error(f"❌ {str(e)}")
    
    # Footer
    st.markdown("---")
    with st.expander("ℹ️ Informazioni Sistema"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📄 Processori Documenti Disponibili:**")
            for doc_type in DocumentProcessorFactory.get_available_types():
                st.markdown(f"• {doc_type.replace('_', ' ').title()}")
        
        with col2:
            st.markdown("**📝 Template Disponibili:**")
            if available_templates:
                for template in available_templates:
                    st.markdown(f"• {template.replace('_', ' ').title()}")
            else:
                st.markdown("• Nessun template caricato")
    
    st.markdown("💡 **Suggerimento:** Segui la barra di progresso in alto per completare tutti i passaggi")

if __name__ == "__main__":
    main()