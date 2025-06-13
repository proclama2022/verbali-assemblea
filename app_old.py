import streamlit as st
import os
from dotenv import load_dotenv
from mistralai import Mistral
from datetime import date
import sys
import PyPDF2

# Add src directory to path for imports
sys.path.append('src')

from document_processors import DocumentProcessorFactory
from document_templates import DocumentTemplateFactory
from load_templates import load_all_templates

# Load environment variables
load_dotenv()
api_key = os.environ.get("MISTRAL_API_KEY")

# Verify API key is configured
if not api_key:
    st.error("⚠️ MISTRAL_API_KEY non configurata. Controlla il file .env")
    st.stop()

# Initialize Mistral client
try:
    client = Mistral(api_key=api_key)
except Exception as e:
    st.error(f"❌ Errore nell'inizializzazione del client Mistral: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Generatore Verbali d'Assemblea",
    page_icon="📄",
    layout="wide"
)

def load_templates():
    """Load templates and return status"""
    try:
        loaded = load_all_templates()
        available = DocumentTemplateFactory.get_available_templates()
        return len(loaded), available
    except Exception as e:
        st.error(f"Errore nel caricamento template: {e}")
        return 0, []

def main():
    st.title("📄 Generatore Verbali d'Assemblea")
    st.markdown("**Sistema semplificato per la creazione di verbali professionali**")
    
    # Load templates at startup
    loaded_count, available_templates = load_templates()
    
    if loaded_count == 0:
        st.error("❌ Nessun template trovato. Verifica la configurazione.")
        return
    
    st.success(f"✅ {loaded_count} template disponibili")
    
    # Progress indicator
    col1, col2, col3 = st.columns(3)
    
    template_selected = st.session_state.get('selected_template') is not None
    document_processed = st.session_state.get('extracted_info') is not None
    
    with col1:
        if template_selected:
            st.success("✅ **1. Template Selezionato**")
        else:
            st.info("🔄 **1. Seleziona Template**")
    
    with col2:
        if document_processed:
            st.success("✅ **2. Documento Elaborato**")
        elif template_selected:
            st.warning("⏳ **2. Carica Documento**")
        else:
            st.info("⏸️ **2. Carica Documento**")
    
    with col3:
        if document_processed:
            st.warning("⏳ **3. Genera Verbale**")
        else:
            st.info("⏸️ **3. Genera Verbale**")
    
    st.markdown("---")
    
    # STEP 1: Template Selection
    st.header("📋 Passo 1: Seleziona il Tipo di Verbale")
    
    if available_templates:
        # Template mapping for user-friendly names - TUTTI I TEMPLATE
        template_names = {
            'verbale_standard': '📊 Verbale Standard - Approvazione Bilancio',
            'verbale_assemblea_template': '📋 Verbale Assemblea - Approvazione Bilancio',
            'verbale_assemblea_completo': '📄 Verbale Completo',
            'verbale_assemblea_nomina_amministratori': '👨‍💼 Nomina Amministratori',
            'verbale_assemblea_revoca_nomina': '🔄 Revoca e Nomina',
            'nomina_collegio_sindacale': '👥 Nomina Collegio Sindacale',
            'nomina_revisore': '🔍 Nomina Revisore',
            'verbale_assemblea_ratifica_operato': '✅ Ratifica Operato',
            'verbale_assemblea_revoca_sindaci': '❌ Revoca Sindaci',
            'dividendi': '💰 Distribuzione Dividendi',
            'verbale_assemblea_rimborsi_spese': '💸 Rimborsi Spese',
            'verbale_assemblea_irregolare': '⚠️ Assemblea Irregolare',
            'correzioni': '✏️ Correzioni',
            'verbale_assemblea_generico': '📝 Verbale Generico',
            'verbale_assemblea_amministratore_unico': '👤 Amministratore Unico',
            'verbale_assemblea_consiglio_amministrazione': '🏛️ Consiglio Amministrazione'
        }
        
        # Filter available templates to only show those we have names for
        available_named_templates = [t for t in available_templates if t in template_names]
        
        if available_named_templates:
            selected_template = st.selectbox(
                "Scegli il tipo di verbale da generare:",
                available_named_templates,
                format_func=lambda x: template_names.get(x, x),
                index=None,
                placeholder="Seleziona un template..."
            )
            
            if selected_template:
                st.session_state.selected_template = selected_template
                st.success(f"✅ Template selezionato: {template_names.get(selected_template, selected_template)}")
        else:
            st.warning("⚠️ Nessun template configurato correttamente")
            return
    else:
        st.error("❌ Nessun template disponibile")
        return
    
    # STEP 2: Document Upload and Processing
    if st.session_state.get('selected_template'):
        st.markdown("---")
        st.header("📤 Passo 2: Carica il Documento")
        
        # Document type selection
        document_types = DocumentProcessorFactory.get_available_types()
        document_type = st.selectbox(
            "Tipo di documento da elaborare:",
            document_types,
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        # File upload
        uploaded_file = st.file_uploader(
            "Carica il documento da cui estrarre le informazioni:",
            type=['pdf', 'txt', 'docx'],
            help="Carica un documento contenente le informazioni per il verbale"
        )
        
        if uploaded_file:
            st.success(f"✅ File caricato: {uploaded_file.name}")
            
            # Extract text from file
            if st.button("🔍 Elabora Documento", type="primary"):
                with st.spinner("Estrazione testo in corso..."):
                    try:
                        # Extract text based on file type
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
                        
                        # Process with AI
                        with st.spinner("🤖 Estrazione informazioni con AI..."):
                            processor = DocumentProcessorFactory.create_processor(document_type, client)
                            extracted_info = processor.extract_information(text)
                            st.session_state.extracted_info = extracted_info
                        
                        st.success("✅ Documento elaborato con successo!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Errore nell'elaborazione: {str(e)}")
        
        # Show extracted text preview if available
        if st.session_state.get('document_text'):
            with st.expander("📄 Testo Estratto", expanded=False):
                st.text_area(
                    "Contenuto del documento:",
                    st.session_state.document_text[:1000] + "..." if len(st.session_state.document_text) > 1000 else st.session_state.document_text,
                    height=150,
                    disabled=True
                )
    
    # STEP 3: Generate Document
    if st.session_state.get('extracted_info'):
        st.markdown("---")
        st.header("📝 Passo 3: Genera il Verbale")
        
        try:
            template_type = st.session_state.selected_template
            template = DocumentTemplateFactory.create_template(template_type)
            
            st.info(f"📄 Generazione: **{template.get_template_name()}**")
            
            # Create form fields
            with st.form("verbale_form"):
                st.markdown("### ✏️ Configura i Dati del Verbale")
                
                # Get form fields from template
                form_data = template.get_form_fields(st.session_state.extracted_info)
                
                # Generate button
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    generate_button = st.form_submit_button("📝 Genera Verbale", type="primary", use_container_width=True)
                
                if generate_button:
                    with st.spinner("🔄 Generazione documento in corso..."):
                        try:
                            # Generate document
                            doc = template.generate_document(form_data)
                            
                            # Save document
                            output_path = f"output/{template_type}_generated.docx"
                            os.makedirs("output", exist_ok=True)
                            doc.save(output_path)
                            
                            # Store in session state for download
                            st.session_state.generated_document_path = output_path
                            st.session_state.generated_document_name = f"{template_type}_{date.today().strftime('%Y%m%d')}.docx"
                            
                            st.success("✅ Documento generato con successo!")
                            
                        except Exception as e:
                            st.error(f"❌ Errore durante la generazione: {str(e)}")
                            st.exception(e)
            
            # Show preview outside form
            if form_data:
                template.show_preview(form_data)
            
            # Download button outside form
            if st.session_state.get('generated_document_path') and os.path.exists(st.session_state.generated_document_path):
                st.markdown("---")
                st.success("📄 **Documento pronto per il download!**")
                
                with open(st.session_state.generated_document_path, "rb") as file:
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        st.download_button(
                            label="⬇️ Scarica Verbale",
                            data=file,
                            file_name=st.session_state.generated_document_name,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            type="primary",
                            use_container_width=True
                        )
                
                # Clear generated document after showing download
                if st.button("🔄 Genera Nuovo Verbale", help="Pulisce la sessione per iniziare un nuovo verbale"):
                    for key in ['selected_template', 'document_text', 'extracted_info', 'generated_document_path', 'generated_document_name']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
                    
        except Exception as e:
            st.error(f"❌ Errore nel template: {str(e)}")
    
    # Sidebar with info
    with st.sidebar:
        st.header("ℹ️ Informazioni")
        st.markdown("""
        **Come usare il sistema:**
        
        1. **Seleziona** il tipo di verbale
        2. **Carica** un documento con le informazioni
        3. **Configura** i dati estratti
        4. **Genera** il verbale finale
        
        **Formati supportati:**
        - PDF
        - TXT
        - DOCX (limitato)
        
        **Template disponibili:**
        - Approvazione Bilancio
        - Verbale Completo
        - Nomina Amministratori
        - Revoca e Nomina
        - Nomina Collegio Sindacale
        - Nomina Revisore
        - Ratifica Operato
        - Revoca Sindaci
        - Distribuzione Dividendi
        - Rimborsi Spese
        - Assemblea Irregolare
        - Correzioni
        - Verbale Generico
        - Amministratore Unico
        - Consiglio Amministrazione
        """)
        
        if st.button("🔄 Reset Completo"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()
