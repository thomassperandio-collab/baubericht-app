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
projekt = st.sidebar.text_input("Bauvorhaben", "Neubau Musterstrasse")
pruefer = st.sidebar.text_input("Erstellt von", "Max Mustermann")
firma = st.sidebar.text_input("Firma", "Bau GmbH")
datum_heute = datetime.now().strftime("%d.%m.%Y")
logo_file = st.sidebar.file_uploader("Firmenlogo hochladen", type=["png", "jpg", "jpeg"])

# --- HAUPTBEREICH: FOTOS ---
st.header("1. Fotos & Beschreibungen")
uploaded_files = st.file_uploader("Bilder der Baustelle auswaehlen", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

# Wir speichern jetzt Beschreibungen UND Wetter/Temperatur zusammen
foto_daten = []

if uploaded_files:
    # Formular, um alle Eingaben auf einmal zu sammeln
    with st.form("eingabe_formular"):
        for idx, file in enumerate(uploaded_files):
            cols = st.columns([1, 2])
            with cols[0]:
                st.image(file, width=200, caption=f"Bild {idx+1}")
            with cols[1]:
                msg = st.text_area(f"Beschreibung fuer Bild {idx+1}", key=f"text_{idx}", placeholder="z.B. Riss in der Bodenplatte...")
                
                # Checkboxen und Textfeld für Wetter/Temperatur
                st.markdown("**Wetterbedingungen:**")
                wetter_cols = st.columns(4)
                sonnig = wetter_cols[0].checkbox("Sonnig", key=f"sun_{idx}")
                bewoelkt = wetter_cols[1].checkbox("Bewoelkt", key=f"cloud_{idx}")
                regen = wetter_cols[2].checkbox("Regen", key=f"rain_{idx}")
                temperatur = wetter_cols[3].text_input("Temp. (°C)", key=f"temp_{idx}", value="")

                wetter_info = []
                if sonnig: wetter_info.append("Sonnig")
                if bewoelkt: wetter_info.append("Bewoelkt")
                if regen: wetter_info.append("Regen")
                if temperatur: wetter_info.append(f"{temperatur}°C")
                
                foto_daten.append({
                    'file': file,
                    'beschreibung': msg,
                    'wetter': ", ".join(wetter_info)
                })
        
        # Submit Button fuer das Formular
        submit_button = st.form_submit_button(label="📄 PDF Bericht generieren")

else:
    # Dummy Submit button, falls keine Dateien hochgeladen wurden
    submit_button = st.button("📄 PDF Bericht generieren")

# --- PDF ERSTELLUNG (Wird nur beim Klick auf Submit Button ausgefuehrt) ---
if submit_button:
    if not uploaded_files:
        st.error("Bitte lade zuerst Bilder hoch!")
    else:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        pdf_width = pdf.w - 2 * pdf.l_margin
        img_width = 80
        text_width = pdf_width - img_width - 5
        row_height = 95 # Etwas hoeher fuer mehr Platz (vorher 90)

        pdf.add_page()
        
        # --- KOPFZEILE ---
        if logo_file:
            img_logo = Image.open(logo_file)
            img_logo_path = "temp_logo_clean.png"
            img_logo.save(img_logo_path)
            pdf.image(img_logo_path, x=160, y=10, w=30)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"{firma}", ln=True)
        pdf.set_font("Arial", 'B', 20)
        pdf.cell(0, 15, f"Baustellenbericht: {projekt}", ln=True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 8, f"Datum: {datum_heute} | Ersteller: {pruefer}", ln=True)
        pdf.ln(10)

        # --- BILDER UND TEXT IM LOOP ---
        for i, data in enumerate(foto_daten):
            file = data['file']
            
            if pdf.get_y() + row_height > pdf.h - pdf.b_margin:
                pdf.add_page()
                pdf.ln(10)

            # 1. Bild vorbereiten (Rotation & Skalierung wie zuvor)
            img_data = Image.open(file)
            try:
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation]=='Orientation': break
                exif=dict(img_data._getexif().items())
                if exif[orientation] == 3: img_data=img_data.rotate(180, expand=True)
                elif exif[orientation] == 6: img_data=img_data.rotate(270, expand=True)
                elif exif[orientation] == 8: img_data=img_data.rotate(90, expand=True)
            except (AttributeError, KeyError, IndexError, TypeError):
                pass
            img_path = f"temp_clean_{file.name}"
            img_data.save(img_path)

            # 2. Positionieren von Bild (links) und Text (rechts)
            start_y = pdf.get_y()
            pdf.image(img_path, x=pdf.l_margin, y=start_y, w=img_width)
            
            pdf.set_xy(pdf.l_margin + img_width + 5, start_y)
            pdf.set_font("Arial", 'B', 11)
            pdf.multi_cell(text_width, 8, f"Bild {i+1}:", align='L') # Bezeichnung angepasst
            
            pdf.set_font("Arial", '', 10)
            pdf.set_xy(pdf.l_margin + img_width + 5, start_y + 10)
            
            # Text inkl. Wetterinformationen
            beschreibung_text = f"Befund: {data['beschreibung']}\nWetter: {data['wetter']}"
            
            # Hier zeichnen wir den Rahmen um den Text
            pdf.rect(pdf.get_x(), pdf.get_y(), text_width, 50) 
            pdf.multi_cell(text_width, 6, beschreibung_text, align='L')

            # 3. Zum Ende der Zeile springen für das nächste Element
            pdf.set_y(start_y + row_height + 5)

        # --- FUSSZEILE MIT UNTERSCHRIFT ---
        pdf.set_y(pdf.h - 30)
        pdf.line(10, pdf.get_y(), 80, pdf.get_y())
        pdf.cell(0, 10, "Unterschrift Bauleitung", ln=False)

        # PDF zum Download anbieten
        binary_pdf = pdf.output() 
        st.download_button(
            label="💾 PDF herunterladen",
            data=bytes(binary_pdf),
            file_name=f"Bericht_{projekt}_{datum_heute}.pdf",
            mime="application/pdf"
        )
        st.success("Bericht fertig erstellt!")
