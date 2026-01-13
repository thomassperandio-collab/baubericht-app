import streamlit as st
from fpdf import FPDF
from datetime import date

def main():
    st.set_page_config(page_title="Baubericht-Generator", page_icon="🏗️")
    st.title("🏗️ Baustellenbericht erstellen")

    # Eingabemaske
    with st.form("bericht_form"):
        col1, col2 = st.columns(2)
        with col1:
            firma = st.text_input("Firma", "Meine Baufirma GmbH")
            projekt = st.text_input("Projektname", "Neubau Wohnanlage")
        with col2:
            pruefer = st.text_input("Ersteller / Prüfer", "Max Mustermann")
            datum_heute = st.date_input("Datum", date.today())

        befund = st.text_area("Befund / Beschreibung der Arbeiten", "Heute wurden folgende Arbeiten abgeschlossen...")
        
        submitted = st.form_submit_button("PDF generieren")

    if submitted:
        # PDF Erstellung (fpdf2 Version 2.7.8+)
        pdf = FPDF()
        pdf.add_page()
        
        # Header - Schriftart 'helvetica' statt 'Arial' nutzen
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, f"{firma}", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("helvetica", 'B', 20)
        pdf.cell(0, 15, f"Baustellenbericht: {projekt}", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("helvetica", '', 10)
        pdf.cell(0, 8, f"Datum: {datum_heute} | Ersteller: {pruefer}", new_x="LMARGIN", new_y="NEXT")
        
        pdf.ln(10) # Abstand
        
        # Inhalt
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, "Befund / Beschreibung:", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("helvetica", '', 11)
        # multi_cell für Zeilenumbrüche im Textfeld
        pdf.multi_cell(0, 8, befund)
        
        pdf.ln(20)
        
        # Unterschriften-Bereich
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, "Unterschrift Bauleitung", new_x="RIGHT", new_y="TOP")
        
        # PDF Output als Bytes (Wichtig: kein .encode() mehr nötig!)
        pdf_output = pdf.output()
        
        st.success("PDF wurde erfolgreich generiert!")
        
        st.download_button(
            label="💾 PDF herunterladen",
            data=pdf_output,
            file_name=f"Baubericht_{projekt}_{datum_heute}.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    main()
