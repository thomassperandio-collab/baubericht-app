import streamlit as st
from fpdf import FPDF
from datetime import datetime
from PIL import Image
import io

# App Titel und Layout
st.set_page_config(page_title="BauBericht Pro 2026", layout="wide")
st.title("🏗️ BauBericht Pro 2026")
st.write("Erstelle professionelle Fotodokumentationen direkt im Browser.")

# --- SEITENLEISTE: EINSTELLUNGEN ---
st.sidebar.header("Bericht-Details")
projekt = st.sidebar.text_input("Bauvorhaben", "Neubau Musterstraße")
pruefer = st.sidebar.text_input("Erstellt von", "Max Mustermann")
firma = st.sidebar.text_input("Firma", "Bau GmbH")
datum_heute = datetime.now().strftime("%d.%m.%Y")
logo_file = st.sidebar.file_uploader("Firmenlogo hochladen", type=["png", "jpg", "jpeg"])

# --- HAUPTBEREICH: FOTOS ---
st.header("1. Fotos & Beschreibungen")
uploaded_files = st.file_uploader("Bilder der Baustelle auswählen", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

beschreibungen = {}

if uploaded_files:
    cols = st.columns(2) # Bilder zweispaltig anzeigen
    for idx, file in enumerate(uploaded_files):
        with cols[idx % 2]:
            st.image(file, width=300)
            msg = st.text_area(f"Beschreibung für Bild: {file.name}", key=f"text_{idx}", placeholder="z.B. Riss in der Bodenplatte...")
            beschreibungen[file.name] = msg

# --- PDF ERSTELLUNG ---
if st.button("📄 PDF Bericht generieren"):
    if not uploaded_files:
        st.error("Bitte lade zuerst Bilder hoch!")
    else:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        for file in uploaded_files:
            pdf.add_page()
            
            # Header
            if logo_file:
                # Logo temporär speichern für PDF
                img = Image.open(logo_file)
                img.save("temp_logo.png")
                pdf.image("temp_logo.png", x=160, y=10, w=30)
            
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, f"{firma}", ln=True)
            pdf.set_font("Arial", 'B', 20)
            pdf.cell(0, 15, f"Baustellenbericht: {projekt}", ln=True)
            
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 8, f"Datum: {datum_heute} | Ersteller: {pruefer}", ln=True)
            pdf.line(10, 45, 200, 45) # Trennlinie
            
            # Bild einfügen
            img_data = Image.open(file)
            img_path = f"temp_{file.name}"
            img_data.save(img_path)
            pdf.image(img_path, x=15, y=50, w=180)
            
            # Beschreibung
            pdf.set_y(180)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Befund / Beschreibung:", ln=True)
            pdf.set_font("Arial", '', 11)
            pdf.multi_cell(0, 8, beschreibungen[file.name])
            
            # Fußzeile mit Unterschrift
            pdf.set_y(260)
            pdf.line(10, 260, 80, 260)
            pdf.cell(0, 10, "Unterschrift Bauleitung", ln=False)

        # PDF zum Download anbieten
       pdf_output = pdf.output() 
        st.download_button(
            label="💾 PDF herunterladen",
            data=pdf_output,
            file_name=f"Bericht_{projekt}_{datum_heute}.pdf",
            mime="application/pdf"
        )
        st.success("Bericht fertig erstellt!")
