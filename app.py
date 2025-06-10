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
    
    # Status summary con istruzioni chiare
    st.markdown("### 🎯 Prossimo Passaggio:")
    if multi_doc_mode:
        if info_extracted and manual_selection_completed:
            st.success("✅ **STEP 4: Genera il documento finale**")
            st.info("👉 Clicca sulla tab **'📝 Genera'** per creare il verbale")
        elif st.session_state.get('multi_processor') and st.session_state.multi_processor.processed_documents:
            st.warning("⏳ **STEP 3: Seleziona le informazioni da utilizzare**")
            st.info("👉 Vai alla tab **'📑 Multi-Doc'** e completa la selezione manuale")
        else:
            st.info("📤 **STEP 2: Carica i tuoi documenti**")
            st.info("👉 Vai alla tab **'📑 Multi-Doc'** per caricare più documenti")
    else:
        if info_extracted:
            st.success("✅ **STEP 3: Genera il documento finale**")
            st.info("👉 Clicca sulla tab **'📝 Genera'** per creare il verbale")
        elif document_loaded:
            st.warning("⏳ **STEP 2: Estrai le informazioni dal documento**")
            st.info("👉 Vai alla tab **'🔍 Estrai'** e clicca su 'Estrai Informazioni'")
        else:
            st.info("📤 **STEP 1: Carica il tuo documento**")
            st.info("👉 Vai alla tab **'📤 Carica'** per iniziare")
    
    st.markdown("---")

def main():
    st.title("📄 Generatore Verbali d'Assemblea")
    st.markdown("**Crea verbali professionali in 3 semplici passaggi**")
    
    # Load templates at startup
    loaded_count, available_templates = load_templates()
    
    if loaded_count > 0:
        st.info(f"✅ **{loaded_count} tipi di verbale disponibili**")
    else:
        st.error("❌ Errore: nessun template trovato")
    
    # Simplified progress indicator
    col1, col2, col3 = st.columns(3)
    
    template_selected = st.session_state.get('template_locked', False)
    info_extracted = st.session_state.get('extracted_info') is not None
    
    with col1:
        if template_selected:
            st.success("✅ **1. Template Scelto**")
        else:
            st.info("🔄 **1. Scegli Template**")
    
    with col2:
        if info_extracted:
            st.success("✅ **2. Dati Estratti**")
        elif template_selected:
            st.warning("⏳ **2. Carica Documento**")
        else:
            st.info("⏸️ **2. Carica Documento**")
    
    with col3:
        if info_extracted:
            st.warning("⏳ **3. Genera Verbale**")
        else:
            st.info("⏸️ **3. Genera Verbale**")
    
    # SIDEBAR SEMPLIFICATA
    with st.sidebar:
        st.header("🎯 Scegli Template")
        
        if available_templates:
            # Mapping semplificato
            template_names = {
                'verbale_assemblea_template': 'Verbale Standard',
                'verbale_assemblea_nomina_amministratori_template': 'Nomina Amministratori',
                'verbale_assemblea_revoca_nomina_template': 'Revoca e Nomina',
                'verbale_assemblea_nomina_collegio_sindacale_template': 'Nomina Collegio Sindacale',
                'verbale_assemblea_nomina_revisore_template': 'Nomina Revisore',
                'verbale_assemblea_ratifica_operato_template': 'Ratifica Operato',
                'verbale_assemblea_revoca_sindaci_template': 'Revoca Sindaci',
                'verbale_assemblea_dividendi_template': 'Distribuzione Dividendi',
                'verbale_assemblea_rimborsi_spese_template': 'Rimborsi Spese',
                'verbale_assemblea_irregolare_template': 'Assemblea Irregolare',
                'verbale_assemblea_completo_template': 'Verbale Completo',
                'verbale_assemblea_generico_template': 'Verbale Generico',
                'verbale_assemblea_amministratore_unico_template': 'Amministratore Unico',
                'verbale_assemblea_correzioni_template': 'Correzioni',
                'verbale_assemblea_consiglio_amministrazione_template': 'Consiglio Amministrazione'
            }
            
            if not st.session_state.get('template_locked', False):
                # Selezione template
                template_options = [(t, template_names.get(t, t)) for t in available_templates]
                
                selected = st.selectbox(
                    "Tipo di verbale:",
                    template_options,
                    format_func=lambda x: x[1],
                    index=None,
                    placeholder="Seleziona..."
                )
                
                if selected and st.button("✅ Conferma", type="primary", use_container_width=True):
                    st.session_state.selected_template_type = selected[0]
                    st.session_state.template_locked = True
                    st.rerun()
                    
            else:
                # Template confermato
                template_type = st.session_state.selected_template_type
                st.success(f"✅ {template_names.get(template_type, template_type)}")
                
                if st.button("🔄 Cambia Template", use_container_width=True):
                    for key in ['selected_template_type', 'template_locked', 'document_text', 'extracted_info']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
        
        st.markdown("---")
        
        # Tipo documento
        available_document_types = DocumentProcessorFactory.get_available_types()
        document_type = st.selectbox(
            "Tipo documento da caricare:",
            available_document_types,
            format_func=lambda x: x.replace('_', ' ').title()
        )

    # Controlla che il template sia selezionato
    if not st.session_state.get('template_locked', False):
        st.info("👈 Seleziona un template nella sidebar per iniziare")
        return
        
    # Usa il template selezionato e bloccato
    template_type = st.session_state.selected_template_type
    
    # AREA PRINCIPALE SEMPLIFICATA
    if template_type:
        # Passo 1: Carica Documento
        st.markdown("### 📤 Passo 1: Carica il Documento")
        
        uploaded_file = st.file_uploader(
            "Carica il documento da cui estrarre le informazioni:",
            type=['pdf', 'txt', 'docx'],
            key="file_uploader"
        )
        
        if uploaded_file:
            st.success(f"✅ File caricato: {uploaded_file.name}")
            
            # Estrazione automatica del testo
            if st.button("🔍 Estrai Testo", type="primary"):
                with st.spinner("Estrazione testo in corso..."):
                    try:
                        file_extension = uploaded_file.name.split('.')[-1].lower()
                        
                        if file_extension == 'pdf':
                            pdf_reader = PyPDF2.PdfReader(uploaded_file)
                            text = ""
                            for page in pdf_reader.pages:
                                text += page.extract_text() + "\n"
                        elif file_extension == 'txt':
                            text = str(uploaded_file.read(), "utf-8")
                        else:
                            text = "[Formato non supportato completamente]"
                        
                        st.session_state.document_text = text
                        st.success("✅ Testo estratto!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Errore: {str(e)}")
        
        # Passo 2: Estrai Informazioni
        if st.session_state.get('document_text'):
            st.markdown("---")
            st.markdown("### 🔍 Passo 2: Estrai Informazioni")
            
            with st.expander("📄 Testo Estratto", expanded=False):
                st.text_area(
                    "Contenuto:",
                    st.session_state.document_text[:1000] + "..." if len(st.session_state.document_text) > 1000 else st.session_state.document_text,
                    height=150,
                    disabled=True
                )
            
            if st.button("🤖 Estrai Informazioni", type="primary"):
                with st.spinner("Estrazione informazioni..."):
                    try:
                        processor = DocumentProcessorFactory.create_processor(document_type)
                        extracted_info = processor.extract_information(
                            st.session_state.document_text,
                            template_type
                        )
                        st.session_state.extracted_info = extracted_info
                        st.success("✅ Informazioni estratte!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Errore: {str(e)}")
        
        # Passo 3: Modifica e Genera
        if st.session_state.get('extracted_info'):
            st.markdown("---")
            st.markdown("### ✏️ Passo 3: Modifica e Genera")
            
            # Form per modificare le informazioni
            with st.form("edit_info"):
                st.markdown("**Modifica le informazioni estratte:**")
                
                edited_info = {}
                for key, value in st.session_state.extracted_info.items():
                    if isinstance(value, list):
                        # Handle both string lists and dictionary lists
                        if value and isinstance(value[0], dict):
                            list_text = '\n'.join(
                                ', '.join(f"{k_item}: {v_item}" for k_item, v_item in item.items())
                                for item in value
                            )
                        else: # For inner if
                            list_text = '\n'.join(str(item) for item in value) if value else ''

                        current_text_value = st.text_area(
                            label=key.replace('_', ' ').title(),
                            value=list_text,
                            height=80,
                            key=f"text_area_{key}" 
                        )
                        edited_info[key] = [line.strip() for line in current_text_value.split('\n') if line.strip()]
                    else: # For outer if isinstance(value, list)
                        edited_info[key] = st.text_input(
                            label=key.replace('_', ' ').title(),
                            value=str(value) if value else "",
                            key=f"text_input_{key}"
                        )
                
                if st.form_submit_button("💾 Salva Modifiche"):
                    st.session_state.extracted_info = edited_info
                    st.success("✅ Modifiche salvate!")
                    st.rerun()
            
            # Generazione documento
            st.markdown("**Genera il documento finale:**")
            
            if st.button("📝 Genera Verbale", type="primary", use_container_width=True):
                with st.spinner("Generazione documento..."):
                    try:
                        generator = DocumentGenerator('templates')
                        output_path = generator.generate_document(
                            template_type,
                            st.session_state.extracted_info
                        )
                        
                        st.session_state.generated_document_path = output_path
                        st.session_state.generated_document_name = os.path.basename(output_path)
                        
                        st.success(f"✅ Documento generato!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Errore: {str(e)}")
            
            # Download
            if st.session_state.get('generated_document_path'):
                if os.path.exists(st.session_state.generated_document_path):
                    with open(st.session_state.generated_document_path, 'rb') as file:
                        st.download_button(
                            label="📥 Scarica Documento",
                            data=file.read(),
                            file_name=st.session_state.generated_document_name,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            type="primary",
                            use_container_width=True
                        )
    else:
        st.info("👈 Seleziona prima un template dalla sidebar per iniziare")
        return

# Passo 3: Genera il Documento
if selected_template and st.session_state.get('extracted_data'):
    with st.expander("📄 Passo 3: Genera il Documento", expanded=True):
        if st.button("🚀 Genera Verbale", type="primary", use_container_width=True):
            try:
                # Get the template processor
                template_processor = get_template_processor(selected_template)
                
                # Use edited data if available, otherwise use extracted data
                data_to_use = st.session_state.get('edited_data', st.session_state['extracted_data'])
                
                # Generate document
                output_path = template_processor.generate_document(data_to_use)
                
                # Read and offer download
                with open(output_path, 'rb') as file:
                    st.download_button(
                        label="📥 Scarica Verbale Generato",
                        data=file.read(),
                        file_name=f"verbale_{selected_template.lower().replace(' ', '_')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                
                st.success("✅ Verbale generato con successo!")
                
            except Exception as e:
                st.error(f"❌ Errore nella generazione: {str(e)}")

# Advanced Multi-Document Section
if st.session_state.get('show_advanced', False):
    st.markdown("---")
    st.markdown("### 🔧 Sezione Avanzata - Multi-Documento")
    
    # Multi-document upload
    uploaded_files = st.file_uploader(
        "Carica più documenti per elaborazione batch",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        key="multi_upload"
    )
    
    if uploaded_files and selected_template:
        if st.button("🔄 Elabora Tutti i Documenti", type="secondary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            for i, file in enumerate(uploaded_files):
                status_text.text(f"Elaborando {file.name}...")
                progress_bar.progress((i + 1) / len(uploaded_files))
                
                try:
                    # Extract text
                    text = extract_text_from_file(file)
                    
                    # Process with template
                    template_processor = get_template_processor(selected_template)
                    extracted_data = template_processor.extract_data(text)
                    
                    # Generate document
                    output_path = template_processor.generate_document(extracted_data)
                    
                    results.append({
                        'file': file.name,
                        'status': 'success',
                        'output': output_path
                    })
                    
                except Exception as e:
                    results.append({
                        'file': file.name,
                        'status': 'error',
                        'error': str(e)
                    })
            
            # Show results
            st.markdown("### 📊 Risultati Elaborazione")
            for result in results:
                if result['status'] == 'success':
                    st.success(f"✅ {result['file']} - Elaborato con successo")
                else:
                    st.error(f"❌ {result['file']} - Errore: {result['error']}")


    
    # Step 3: Generate Document
    st.markdown("---")
    st.header("📝 Passo 3: Genera il Documento")
    
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
        st.warning("⚠️ Estrai prima le informazioni nel Passo 2")
        st.info("👆 Completa i passaggi precedenti per procedere")
        
        # Show what's missing
        if 'document_text' not in st.session_state or not st.session_state.document_text:
            st.error("❌ **Manca:** Documento caricato")
        else:
            st.success("✅ **Disponibile:** Documento caricato")
            
        st.error("❌ **Manca:** Informazioni estratte")
        
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
    
    # Advanced Multi-Document Section
    st.markdown("---")
    with st.expander("🔧 Modalità Avanzata: Multi-Documenti", expanded=False):
        st.subheader("📑 Estrazione Multi-Documenti")
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
                        final_data = {k: v for k, v in selected_data.items() if v is not None and v != ""}
                        
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