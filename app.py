import streamlit as st
from fpdf import FPDF
from datetime import datetime
from PIL import Image, ExifTags
import io
import os

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
    cols = st.columns(2)
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
        
        # Einstellungen für das Layout
        pdf_width = pdf.w - 2 * pdf.l_margin
        img_width = 80
        text_width = pdf_width - img_width - 5 # 5mm Abstand
        row_height = 90 # Höhe einer Zeile im Dokument

        pdf.add_page()
        
        # --- KOPFZEILE (Einmalig pro Dokument) ---
        if logo_file:
            img_logo = Image.open(logo_file)
            img_logo_path = "temp_logo.png"
            img_logo.save(img_logo_path)
            pdf.image(img_logo_path, x=160, y=10, w=30)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"{firma}", ln=True)
        pdf.set_font("Arial", 'B', 20)
        pdf.cell(0, 15, f"Baustellenbericht: {projekt}", ln=True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 8, f"Datum: {datum_heute} | Ersteller: {pruefer}", ln=True)
        pdf.ln(10) # Abstand nach Header

        # --- BILDER UND TEXT IM LOOP ---
        for i, file in enumerate(uploaded_files):
            
            # Prüfen ob neue Seite benötigt wird
            if pdf.get_y() + row_height > pdf.h - pdf.b_margin:
                pdf.add_page()
                pdf.ln(10) # Kleiner Abstand auf neuer Seite

            # 1. Bild vorbereiten (Rotation & Skalierung wie zuvor)
            img_data = Image.open(file)
            try:
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation]=='Orientation': break
                exif=dict(img_data._getexif().items())
                if exif[orientation] == 3: img_data=img_data.rotate(180, expand=True)
                elif exif[orientation] == 6: img_data=img_data.rotate(270, expand=True)
                elif exif[orientation] == 8: img_data=img_data.rotate(90, expand=True)
            except (AttributeError, KeyError, IndexError):
                pass
            img_path = f"temp_{file.name}"
            img_data.save(img_path)

            # 2. Positionieren von Bild (links) und Text (rechts)
            start_y = pdf.get_y()
            pdf.image(img_path, x=pdf.l_margin, y=start_y, w=img_width)
            
            pdf.set_xy(pdf.l_margin + img_width + 5, start_y)
            pdf.set_font("Arial", 'B', 11)
            pdf.multi_cell(text_width, 8, f"Mangel/Befund ({file.name}):", align='L')
            
            pdf.set_font("Arial", '', 10)
            pdf.set_xy(pdf.l_margin + img_width + 5, start_y + 10)
            pdf.multi_cell(text_width, 6, beschreibungen[file.name], align='L')

            # 3. Zum Ende der Zeile springen für das nächste Element
            pdf.set_y(start_y + row_height + 5) # 5mm Abstand zur nächsten Zeile

        # --- FUSSZEILE MIT UNTERSCHRIFT (am Ende des Dokuments) ---
        pdf.set_y(pdf.h - 30) # 3 cm von unten
        pdf.line(10, pdf.get_y(), 80, pdf.get_y())
        pdf.cell(0, 10, "Unterschrift Bauleitung", ln=False)

        # PDF zum Download anbieten
        pdf_buffer = io.BytesIO()
        pdf.output(dest=pdf_buffer) 
        st.download_button(
            label="💾 PDF herunterladen",
            data=pdf_buffer.getvalue(),
            file_name=f"Bericht_{projekt}_{datum_heute}.pdf",
            mime="application/pdf"
        )
        st.success("Bericht fertig erstellt!")
