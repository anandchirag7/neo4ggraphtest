import streamlit as st
import os
import sys
import json
import subprocess
from pathlib import Path
import tempfile
from typing import Dict, Any, List

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.config import NEO4J_URI, NEO4J_USER, NEO4J_PASS
from neo4j import GraphDatabase

# Page configuration
st.set_page_config(
    page_title="Enterprise Knowledge Base",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'processed_docs' not in st.session_state:
    st.session_state.processed_docs = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_doc' not in st.session_state:
    st.session_state.current_doc = None

# Sidebar navigation
st.sidebar.title("📚 Enterprise KB")
page = st.sidebar.radio(
    "Navigation",
    ["📤 Upload Documents", "🕸️ Knowledge Graph", "💬 Chat with Documents"]
)

# Helper functions
def process_pdf(pdf_file, doc_id: str) -> Dict[str, Any]:
    """Process uploaded PDF through the pipeline"""
    # Save uploaded file
    upload_dir = Path("backend/uploads") / doc_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_path = upload_dir / f"{doc_id}.pdf"
    with open(pdf_path, "wb") as f:
        f.write(pdf_file.getbuffer())
    
    pipeline_dir = Path("backend/pipeline")
    
    # Step 1: Extract raw PDF
    st.info("🔍 Extracting content from PDF...")
    raw_json = pipeline_dir / f"raw_{doc_id}.json"
    assets_dir = upload_dir / "assets"
    
    result = subprocess.run([
        sys.executable,
        str(pipeline_dir / "extract_raw_pdf.py"),
        "--pdf_path", str(pdf_path),
        "--output", str(raw_json),
        "--assets_dir", str(assets_dir)
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        st.error(f"PDF extraction failed: {result.stderr}")
        return {"success": False, "error": result.stderr}
    
    # Step 2: Build RAG graph
    st.info("🏗️ Building knowledge graph...")
    enriched_json = pipeline_dir / f"enriched_{doc_id}.json"
    
    result = subprocess.run([
        sys.executable,
        str(pipeline_dir / "build_rag_graph.py"),
        "--raw_json", str(raw_json),
        "--enriched_json", str(enriched_json),
        "--neo4j_uri", NEO4J_URI,
        "--neo4j_user", NEO4J_USER,
        "--neo4j_password", NEO4J_PASS
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        st.error(f"Graph building failed: {result.stderr}")
        return {"success": False, "error": result.stderr}
    
    # Step 3: Generate ontology (optional)
    st.info("🧬 Generating ontology...")
    subprocess.run([
        sys.executable,
        str(pipeline_dir / "generate_ontology_config.py"),
        "--raw_json", str(raw_json),
        "--doc_id", doc_id
    ], capture_output=True, text=True)

    # Step 4: build ontology (optional)
    st.info("🧬 Building ontology...")
    subprocess.run([
        sys.executable,
        str(pipeline_dir / "build_ontology_layer.py"),
        "--neo4j_uri", NEO4J_URI,
        "--neo4j_user", NEO4J_USER,
        "--neo4j_password", NEO4J_PASS,
        "--doc_id", doc_id,
        "--with_spec_items"
    ], capture_output=True, text=True)
    
    # Step 5: Index chunks
    st.info("📊 Indexing chunks for search...")
    subprocess.run([
        sys.executable,
        str(pipeline_dir / "index_chunks_pgvector.py"),
        "--neo4j_uri", NEO4J_URI,
        "--neo4j_user", NEO4J_USER,
        "--neo4j_password", NEO4J_PASS,
        "--pg_host", "localhost",
        "--pg_port", "5433",
        "--pg_dbname", "postgres",
        "--pg_user", "postgres",
        "--pg_password", "522771708@Sbi",
        "--doc_id", doc_id
    ], capture_output=True, text=True)
    
    return {
        "success": True,
        "doc_id": doc_id,
        "raw_json": str(raw_json),
        "enriched_json": str(enriched_json)
    }

def get_graph_data(doc_id: str = None) -> Dict[str, Any]:
    """Fetch graph data from Neo4j"""
    from neo4j.graph import Node as Neo4jNode, Relationship as Neo4jRelationship
    
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    
    with driver.session() as session:
        if doc_id:
            query = """
            MATCH (d:Document {doc_id: $doc_id})-[r]-(n)
            RETURN d, r, n
            LIMIT 100
            """
            result = session.run(query, doc_id=doc_id)
        else:
            query = """
            MATCH (n)-[r]-(m)
            RETURN n, r, m
            LIMIT 100
            """
            result = session.run(query)
        
        nodes = []
        edges = []
        node_ids = set()
        
        for record in result:
            # Process each value in the record
            for key in record.keys():
                value = record[key]
                
                # Check if it's a Node
                if isinstance(value, Neo4jNode):
                    if value.id not in node_ids:
                        nodes.append({
                            "id": str(value.id),
                            "label": list(value.labels)[0] if value.labels else "Node",
                            "properties": dict(value)
                        })
                        node_ids.add(value.id)
                
                # Check if it's a Relationship
                elif isinstance(value, Neo4jRelationship):
                    edges.append({
                        "source": str(value.start_node.id),
                        "target": str(value.end_node.id),
                        "label": value.type
                    })
                    
                    # Also add the start and end nodes if not already added
                    if value.start_node.id not in node_ids:
                        nodes.append({
                            "id": str(value.start_node.id),
                            "label": list(value.start_node.labels)[0] if value.start_node.labels else "Node",
                            "properties": dict(value.start_node)
                        })
                        node_ids.add(value.start_node.id)
                    
                    if value.end_node.id not in node_ids:
                        nodes.append({
                            "id": str(value.end_node.id),
                            "label": list(value.end_node.labels)[0] if value.end_node.labels else "Node",
                            "properties": dict(value.end_node)
                        })
                        node_ids.add(value.end_node.id)
    
    driver.close()
    return {"nodes": nodes, "edges": edges}

def chat_with_docs(question: str, doc_id: str = None) -> Dict[str, Any]:
    """Query the RAG system"""
    import requests
    
    try:
        response = requests.post(
            "http://localhost:8000/ask",
            json={"question": question, "doc_id": doc_id},
            timeout=180  # Increased timeout to 120 seconds for LLM processing
        )
        response.raise_for_status()
        data = response.json()
        return {
            "success": True,
            "answer_text": data.get("answer_text", "No answer generated"),
            # "figures": data.get("figures", []),
            # "tables": data.get("tables", []),
            "documents": data.get("documents", [])
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "⏱️ Request timed out. The LLM is taking longer than expected. Please try a simpler question or check if the backend is running properly."
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "🔌 Cannot connect to backend server. Please ensure the FastAPI server is running on http://localhost:8000"
        }
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "error": f"❌ HTTP Error: {e.response.status_code} - {e.response.text}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"❌ Error: {str(e)}"
        }

# PAGE 1: Upload Documents
if page == "📤 Upload Documents":
    st.title("📤 Upload PDF Documents")
    st.write("Upload PDF datasheets to build your knowledge base")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload a technical datasheet or document"
        )
        
        doc_id = st.text_input(
            "Document ID",
            placeholder="e.g., rt6220, 7mm, t520",
            help="Unique identifier for this document"
        )
    
    with col2:
        st.info("📋 **Processing Steps:**\n1. Extract text & images\n2. Build knowledge graph\n3. Generate ontology\n4. Index for search")
    
    if uploaded_file and doc_id:
        if st.button("🚀 Process Document", type="primary"):
            with st.spinner("Processing document..."):
                result = process_pdf(uploaded_file, doc_id)
                
                if result.get("success"):
                    st.success(f"✅ Document '{doc_id}' processed successfully!")
                    st.session_state.processed_docs.append(doc_id)
                    st.session_state.current_doc = doc_id
                    
                    # Show summary
                    st.subheader("Processing Summary")
                    st.json(result)
                else:
                    st.error(f"❌ Processing failed: {result.get('error')}")
    
    # Show processed documents
    if st.session_state.processed_docs:
        st.subheader("📚 Processed Documents")
        for doc in st.session_state.processed_docs:
            st.badge(doc)

# PAGE 2: Knowledge Graph
elif page == "🕸️ Knowledge Graph":
    st.title("🕸️ Knowledge Graph Visualization")
    
    # Document selector
    doc_filter = st.selectbox(
        "Filter by document",
        ["All Documents"] + st.session_state.processed_docs
    )
    
    selected_doc = None if doc_filter == "All Documents" else doc_filter
    
    if st.button("🔄 Refresh Graph"):
        with st.spinner("Loading graph data..."):
            graph_data = get_graph_data(selected_doc)
            
            st.subheader("Graph Statistics")
            col1, col2, col3 = st.columns(3)
            col1.metric("Nodes", len(graph_data["nodes"]))
            col2.metric("Edges", len(graph_data["edges"]))
            col3.metric("Documents", len(st.session_state.processed_docs))
            
            # Simple visualization using streamlit-agraph
            try:
                from streamlit_agraph import agraph, Node, Edge, Config
                
                nodes = [
                    Node(
                        id=n["id"],
                        label=n["properties"].get("doc_id", n["label"]),
                        size=25,
                        color="#FF6B6B" if n["label"] == "Document" else "#4ECDC4"
                    )
                    for n in graph_data["nodes"]
                ]
                
                edges = [
                    Edge(
                        source=e["source"],
                        target=e["target"],
                        label=e["label"]
                    )
                    for e in graph_data["edges"]
                ]
                
                config = Config(
                    width=1200,
                    height=600,
                    directed=True,
                    physics=True,
                    hierarchical=False
                )
                
                agraph(nodes=nodes, edges=edges, config=config)
                
            except ImportError:
                st.warning("Install streamlit-agraph for visualization: `pip install streamlit-agraph`")
                st.json(graph_data)

# PAGE 3: Chat
elif page == "💬 Chat with Documents":
    st.title("💬 Chat with Your Documents")
    
    # Document selector for chat
    if st.session_state.processed_docs:
        chat_doc = st.selectbox(
            "Select document to chat with",
            ["All Documents"] + st.session_state.processed_docs
        )
        selected_chat_doc = None if chat_doc == "All Documents" else chat_doc
    else:
        st.warning("⚠️ No documents processed yet. Please upload a document first.")
        selected_chat_doc = None
    
    # Chat interface
    st.subheader("Ask questions about your documents")
    
    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
            # Display figures if present in history
            if msg.get("figures"):
                st.markdown("---")
                st.markdown("**📊 Relevant Figures:**")
                for fig in msg["figures"]:
                    with st.expander(f"📷 {fig.get('caption', 'Figure')} (Page {fig.get('page', 'N/A')})"):
                        st.caption(f"**Document:** {fig.get('doc_id', 'Unknown')}")
                        image_url = fig.get('image_url', '')
                        if image_url:
                            full_url = f"http://localhost:8000{image_url}"
                            try:
                                st.image(full_url, caption=fig.get('caption', ''), use_container_width=True)
                            except:
                                st.text(f"Image URL: {full_url}")
            
            # Display tables if present in history
            if msg.get("tables"):
                st.markdown("---")
                st.markdown("**📋 Relevant Tables:**")
                for tbl in msg["tables"]:
                    with st.expander(f"📊 Table from Page {tbl.get('page', 'N/A')}"):
                        st.caption(f"**Document:** {tbl.get('doc_id', 'Unknown')}")
                        table_data = tbl.get('table_data', [])
                        if table_data:
                            import pandas as pd
                            try:
                                df = pd.DataFrame(table_data)
                                st.dataframe(df, use_container_width=True)
                            except:
                                st.json(table_data)
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = chat_with_docs(prompt, selected_chat_doc)
                
                if result.get("success"):
                    # Display answer text
                    answer_text = result.get("answer_text", "")
                    st.write(answer_text)
                    
                    # Display relevant figures
                    figures = result.get("figures", [])
                    if figures:
                        st.markdown("---")
                        st.markdown("**📊 Relevant Figures:**")
                        for fig in figures:
                            with st.expander(f"📷 {fig.get('caption', 'Figure')} (Page {fig.get('page', 'N/A')})"):
                                st.caption(f"**Document:** {fig.get('doc_id', 'Unknown')}")
                                image_url = fig.get('image_url', '')
                                if image_url:
                                    # Construct full URL
                                    full_url = f"http://localhost:8000{image_url}"
                                    try:
                                        st.image(full_url, caption=fig.get('caption', ''), use_container_width=True)
                                    except Exception as e:
                                        st.error(f"Could not load image: {e}")
                                        st.text(f"Image URL: {full_url}")
                    
                    # Display relevant tables
                    tables = result.get("tables", [])
                    if tables:
                        st.markdown("---")
                        st.markdown("**📋 Relevant Tables:**")
                        for tbl in tables:
                            with st.expander(f"📊 Table from Page {tbl.get('page', 'N/A')}"):
                                st.caption(f"**Document:** {tbl.get('doc_id', 'Unknown')}")
                                table_data = tbl.get('table_data', [])
                                if table_data:
                                    import pandas as pd
                                    try:
                                        df = pd.DataFrame(table_data)
                                        st.dataframe(df, use_container_width=True)
                                    except Exception as e:
                                        st.error(f"Could not display table: {e}")
                                        st.json(table_data)
                    
                    # Store in chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer_text,
                        "figures": figures,
                        "tables": tables
                    })
                else:
                    # Display error
                    error_msg = result.get("error", "Unknown error occurred")
                    st.error(error_msg)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": error_msg
                    })
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Enterprise Knowledge Base v1.0")
st.sidebar.caption(f"Documents: {len(st.session_state.processed_docs)}")
