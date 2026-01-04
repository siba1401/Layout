import streamlit as st
import pandas as pd

# Set page to wide mode for a better report layout
st.set_page_config(page_title="NMIMS Supervisor Report Tool", layout="wide")

# --- PROFESSIONAL UNIVERSITY-GRADE CSS (STRICTLY PRESERVED) ---
st.markdown("""
    <style>
    @media print {
        .stButton, .stFileUploader, .stSidebar, [data-testid="stHeader"], .no-print { display: none !important; }
        .main .block-container { padding: 0 !important; margin: 0 !important; }
        body { background-color: white !important; }
        .report-page-break { page-break-after: always; }
        @page { size: A4 portrait; margin: 5mm; }
    }

    .report-wrapper { 
        font-family: 'Times New Roman', Times, serif; 
        color: #000; 
        max-width: 780px; 
        margin: auto; 
        background: white;
        padding: 5px;
        border: 1px solid #fff; /* Invisible border to maintain structure */
    }

    .header-box { text-align: center; border-bottom: 2px solid #000; padding-bottom: 3px; margin-bottom: 8px; }
    .header-box h1 { margin: 0; font-size: 20px; font-weight: bold; line-height: 1.1; }
    .header-box h2 { margin: -3px 0 0 0; font-size: 15px; line-height: 1.1; }

    .room-highlight {
        display: inline-block;
        border: 2px solid #000;
        padding: 2px 20px;
        font-size: 18px;
        font-weight: bold;
        margin: 5px 0;
    }

    .meta-table { width: 100%; border-collapse: collapse; margin-bottom: 12px; table-layout: fixed; }
    .meta-table td { 
        border: 1px solid #000; 
        padding: 5px; 
        font-weight: bold; 
        font-size: 12px; 
        vertical-align: middle; 
    }

    .row-layout { 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        margin-bottom: 4px; 
    }

    .side-container {
        width: 310px; 
        display: flex;
        gap: 4px;
    }
    .left-side { justify-content: flex-end; } 
    .right-side { justify-content: flex-start; }

    .seat-box { 
        border: 1.2px solid #000; 
        width: 50px; 
        height: 40px; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        font-size: 18px; 
        font-weight: bold; 
        background: #f2f2f2; 
    }

    .aisle-gap { 
        width: 65px; 
        text-align: center; 
        font-weight: bold; 
        font-size: 18px; 
        color: #000;
        background: #e8f0fe; 
        border-radius: 4px;
        margin: 0 5px;
    }

    .path-label { 
        width: 65px; 
        text-align: center; 
        font-weight: bold; 
        font-size: 12px; 
        border-top: 1.2px solid #000;
        margin-top: 2px;
        padding-top: 3px;
    }

    .supervisor-desk { 
        border: 1.2px dashed #000; 
        width: 220px; 
        margin: 12px auto; 
        text-align: center; 
        padding: 6px; 
        font-weight: bold; 
        font-size: 13px;
        text-transform: uppercase;
        background: #fff9c4; 
    }

    .footer-area { border-top: 2px solid #000; margin-top: 12px; padding-top: 8px; font-size: 12px; line-height: 2.0; }
    </style>
""", unsafe_allow_html=True)

# Initialize report queue
if 'report_queue' not in st.session_state:
    st.session_state.report_queue = []

# --- SIDEBAR & DYNAMIC FILTERING ---
with st.sidebar:
    st.header("MPSTME Room Layout")
    total_rows = st.number_input("Total Rows", 1, 15, 5)
    row_configs = []
    for i in range(1, total_rows + 1):
        with st.expander(f"Row {i}"):
            c1, c2 = st.columns(2)
            l = c1.number_input("Left Block", 0, 10, 3, key=f"L{i}")
            r = c2.number_input("Right Block", 0, 10, 4, key=f"R{i}")
            row_configs.append({"label": i, "left": l, "right": r})

    st.divider()
    st.header("Data Input")
    f_meta = st.file_uploader("1. Upload Metadata File", type="xlsx")

    if f_meta:
        m_df = pd.read_excel(f_meta)
        prog_col = "Programme & Stream"
        sem_col = "Sem"

        if prog_col in m_df.columns and sem_col in m_df.columns:
            # 1. Dropdown to select program
            selected_prog = st.selectbox("2. Select Programme & Stream", m_df[prog_col].unique())

            # 2. Filter semesters based on selected program
            available_sems = m_df[m_df[prog_col] == selected_prog][sem_col].unique()
            selected_sem = st.selectbox("3. Select Semester", available_sems)

            # 3. File uploader for the specific roll list
            f_roll = st.file_uploader(f"4. Upload Roll List for {selected_prog} (Sem {selected_sem})", type="xlsx")

            if st.button("➕ Add to Report List"):
                if f_roll:
                    # Capture specific metadata row using BOTH Program and Semester
                    meta_row = m_df[(m_df[prog_col] == selected_prog) & (m_df[sem_col] == selected_sem)].iloc[0]
                    roll_list = pd.read_excel(f_roll).iloc[:, 0].dropna().astype(str).tolist()

                    st.session_state.report_queue.append({
                        "meta": meta_row,
                        "rolls": roll_list
                    })
                    st.success(f"Added {selected_prog} Sem {selected_sem} to queue!")
                else:
                    st.error("Please upload the roll list for the selected program.")
        else:
            st.error(f"Required columns '{prog_col}' and '{sem_col}' not found in Metadata file.")

    if st.button("🗑️ Clear All Reports"):
        st.session_state.report_queue = []
        st.rerun()

# --- MAIN REPORT GENERATION ---
if st.session_state.report_queue:
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    st.info(f"Ready to generate {len(st.session_state.report_queue)} layouts.")
    if st.button("🖨️ Ready to Print All"):
        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Generate each report in the queue
    for item in st.session_state.report_queue:
        meta = item['meta']
        rolls = item['rolls']
        clean_date = str(meta.get('Date', '_______')).split(' ')[0]

        # Assignment Logic (Strictly preserved)
        roll_idx = 0
        assigned_rows = []
        for row in row_configs:
            r_data = {"label": row['label'], "left": [], "right": []}
            for _ in range(row['left']):
                r_data['left'].append(rolls[roll_idx] if roll_idx < len(rolls) else "")
                roll_idx += 1
            for _ in range(row['right']):
                r_data['right'].append(rolls[roll_idx] if roll_idx < len(rolls) else "")
                roll_idx += 1
            assigned_rows.append(r_data)

        # HTML Layout (Strictly preserved)
        st.markdown('<div class="report-wrapper report-page-break">', unsafe_allow_html=True)
        st.markdown(f"""
            <div class="header-box">
                <h1>SVKM'S NMIMS</h1>
                <h2>MPSTME, Mumbai</h2>
                <div class="room-highlight">ROOM NO : {meta.get('Room No.', '_______')}</div>
                <p style="font-size: 13px; margin: 0; font-weight: bold;">Examination Seating Arrangement / Supervisor's Report</p>
            </div>
            <table class="meta-table">
                <tr><td>Academic Year: {meta.get('Academic Year', '2025-26')}</td><td>Date: {clean_date}</td></tr>
                <tr><td>Program / Stream: {meta.get(prog_col, '_______')}</td><td>Exam Time: {meta.get('Time', '_______')}</td></tr>
                <tr><td>Subject: {meta.get('Subjects', '_______')}</td><td>Sem: {meta.get('Sem', '_______')}</td></tr>
                <tr><td>Roll No Range: {rolls[0] if rolls else 'N/A'} to {rolls[-1] if rolls else 'N/A'}</td><td>Total Students: {len(rolls)}</td></tr>
            </table>
        """, unsafe_allow_html=True)

        for row in reversed(assigned_rows):
            html = f'<div class="row-layout"><div class="side-container left-side">'
            for r_no in row['left']: html += f'<div class="seat-box">{r_no}</div>'
            html += f'</div><div class="aisle-gap">{row["label"]}</div><div class="side-container right-side">'
            for r_no in row['right']: html += f'<div class="seat-box">{r_no}</div>'
            html += '</div></div>'
            st.markdown(html, unsafe_allow_html=True)

        st.markdown('<div class="row-layout"><div class="path-label">ROW</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="supervisor-desk">Supervisor Desk Area</div>', unsafe_allow_html=True)

        footer_html = f"""
        <div class="footer-area">
            <p style="font-weight: bold; margin-bottom: 6px; font-size: 11px;">ENTRANCE &nbsp; ↑</p>
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 12px;">
                <span>Answerbooks Issued: _________</span>
                <span>Used: _________</span>
                <span>Returned: _________</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 12px;">
                <span>Supplements Issued: _________</span>
                <span>Used: _________</span>
                <span>Returned: _________</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: bold; margin-bottom: 15px; margin-top: 5px;">
                <span>TOTAL CANDIDATES PRESENT: ___________________________</span>
                <span>TOTAL CANDIDATES ABSENT: ___________________________</span>
            </div>        
            <div style="display: flex; justify-content: space-between; width: 100%; font-size: 12px;">
                <div style="width: 48%;">
                    <p style="margin: 0;"><b>Supervisor 1:</b> ___________________________</p>
                    <p style="margin: 4px 0;">Sign: ________________________________</p>
                </div>
                <div style="width: 48%;">
                    <p style="margin: 0;"><b>Supervisor 2:</b> ___________________________</p>
                    <p style="margin: 4px 0;">Sign: ________________________________</p>
                </div>
            </div>
        </div>
        """
        st.markdown(footer_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.warning("Please upload the Metadata file and add programs to the list.")

# Reminder: Students can enrol in one project only.