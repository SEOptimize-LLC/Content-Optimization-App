import streamlit as st
import os
import traceback

# Diagnostic logging for imports
print("=== Starting Import Diagnostics ===")
optimize_outline = None
optimize_draft = None

try:
    from core.outline_optimizer import optimize_outline
    print("SUCCESS: Imported outline_optimizer.")
except ImportError as e:
    print(f"IMPORT ERROR in outline_optimizer: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"GENERAL ERROR in outline_optimizer: {e}")
    traceback.print_exc()

try:
    from core.draft_optimizer import optimize_draft
    print("SUCCESS: Imported draft_optimizer.")
except ImportError as e:
    print(f"IMPORT ERROR in draft_optimizer: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"GENERAL ERROR in draft_optimizer: {e}")
    traceback.print_exc()

try:
    from docx import Document
    from docx.shared import Inches
    print("SUCCESS: Imported docx.")
except ImportError as e:
    print(f"IMPORT ERROR in docx: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"GENERAL ERROR in docx: {e}")
    traceback.print_exc()

import io
print("=== All Imports Completed ===")

# Page config
st.set_page_config(page_title="Blog Optimizer", page_icon="📝", layout="wide")

# Title
st.title("📝 Blog Optimizer App")
st.markdown("Optimize your blog outlines and drafts using AI-powered NLP and ML.")

# Sidebar for instructions
with st.sidebar:
    st.header("Instructions")
    st.markdown("""
    **Outline Mode:**
    - Upload Query Fan-Out Report (Markdown/Text).
    - Upload Original Outline (Markdown).
    
    **Draft Mode:**
    - Upload Original Draft (Text/Markdown).
    - Upload Expanded Keyword List (CSV/Text).
    
    Click 'Optimize' to process. View results and export.
    """)

# Mode selection
mode = st.radio("Select Optimization Mode:", ["Outline Optimization", "Draft Optimization"])

# Session state for outputs
if 'output_md' not in st.session_state:
    st.session_state.output_md = ""
if 'metadata' not in st.session_state:
    st.session_state.metadata = {}

# File uploads based on mode
uploaded_files = {}
progress_bar = st.progress(0)

if mode == "Outline Optimization":
    st.header("Outline Optimization")
    query_report = st.file_uploader("Upload Query Fan-Out Report", type=['md', 'txt'], key="query_report")
    original_outline = st.file_uploader("Upload Original Outline", type=['md'], key="original_outline")
    
    if st.button("Optimize Outline", type="primary"):
        if query_report and original_outline:
            with st.spinner("Processing..."):
                progress_bar.progress(25)
                query_text = query_report.read().decode("utf-8")
                progress_bar.progress(50)
                outline_text = original_outline.read().decode("utf-8")
                progress_bar.progress(75)
                
                try:
                    enhanced_md, metadata = optimize_outline(query_text, outline_text)
                    st.session_state.output_md = enhanced_md
                    st.session_state.metadata = metadata
                    progress_bar.progress(100)
                    st.success("Optimization complete!")
                except NameError:
                    st.error("Optimization function not defined (import failed, likely spaCy issue). Check console logs for details.")
                    st.info("No filename matching required—uploader uses extension filters only. Fix: Downgrade spaCy to 3.7.2 in requirements.txt.")
                except Exception as e:
                    st.error(f"Error during optimization: {str(e)}")
                    st.info("Likely cause: spaCy import failure. See local console or cloud logs for details. Try downgrading spaCy to 3.7.2.")
        else:
            st.warning("Please upload both files.")

elif mode == "Draft Optimization":
    st.header("Draft Optimization")
    original_draft = st.file_uploader("Upload Original Draft", type=['txt', 'md'], key="original_draft")
    keyword_list = st.file_uploader("Upload Expanded Keyword List", type=['csv', 'txt', 'md'], key="keyword_list")
    
    if st.button("Optimize Draft", type="primary"):
        if original_draft and keyword_list:
            with st.spinner("Processing..."):
                progress_bar.progress(25)
                draft_text = original_draft.read().decode("utf-8")
                progress_bar.progress(50)
                kw_text = keyword_list.read().decode("utf-8")
                progress_bar.progress(75)
                
                try:
                    report_md, metadata = optimize_draft(draft_text, kw_text)
                    st.session_state.output_md = report_md
                    st.session_state.metadata = metadata
                    progress_bar.progress(100)
                    st.success("Optimization complete!")
                except NameError:
                    st.error("Optimization function not defined (import failed, likely spaCy issue). Check console logs for details.")
                    st.info("No filename matching required—uploader uses extension filters only. Fix: Downgrade spaCy to 3.7.2 in requirements.txt.")
                except Exception as e:
                    st.error(f"Error during optimization: {str(e)}")
                    st.info("Likely cause: spaCy import failure. See local console or cloud logs for details. Try downgrading spaCy to 3.7.2.")
        else:
            st.warning("Please upload both files.")

# Display results if available
if st.session_state.output_md:
    st.header("Optimized Output")
    
    # Metadata sidebar
    with st.sidebar:
        st.subheader("Metadata")
        for key, value in st.session_state.metadata.items():
            st.write(f"**{key}:** {value}")
    
    # Render Markdown
    st.markdown(st.session_state.output_md)
    
    # Export options
    st.header("Export")
    col1, col2 = st.columns(2)
    
    with col1:
        # Word Export
        docx_buffer = io.BytesIO()
        doc = Document()
        doc.add_heading("Blog Optimizer Output", 0)
        
        # Add metadata
        for key, value in st.session_state.metadata.items():
            doc.add_paragraph(f"{key}: {value}")
        doc.add_page_break()
        
        # Add content from Markdown (simple conversion)
        lines = st.session_state.output_md.split('\n')
        for line in lines:
            if line.startswith('# '):
                doc.add_heading(line[2:], level=1)
            elif line.startswith('## '):
                doc.add_heading(line[3:], level=2)
            elif line.startswith('### '):
                doc.add_heading(line[4:], level=3)
            elif line.startswith('- '):
                doc.add_paragraph(line[2:], style='List Bullet')
            else:
                doc.add_paragraph(line)
        
        doc.save(docx_buffer)
        docx_buffer.seek(0)
        
        st.download_button(
            label="Download as Word (.docx)",
            data=docx_buffer,
            file_name="optimized_output.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    
    with col2:
        # Google Docs note (API setup required)
        st.info("Google Docs export requires API credentials. Implement using Google Docs API in core/export.py.")
        if st.button("Setup Google Docs Export (Manual)"):
            st.markdown("""
            1. Enable Google Docs API in Google Cloud Console.
            2. Create OAuth credentials.
            3. Use google-api-python-client to create doc and insert content.
            """)

# Footer
st.markdown("---")
st.markdown("Built with Streamlit, spaCy, Transformers, and Sentence Transformers.")