import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import io
from gc_content import read_sequences, gc_content

# --- Page config ---
st.set_page_config(page_title="GC Content Analyzer", layout="wide")
st.title("🧬 GC Content Analysis Tool")


# --- Hide anchor link icons beside headers ---
st.markdown("""
    <style>
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Theme Selector ---
theme_option = st.sidebar.selectbox("Choose Theme", ["Light", "Dark"])

# --- Theme colors ---
if theme_option == "Light":
    metric_bg = "#F0F2F6"
    text_color = "#000000"
    chart_colors = ["#2E86C1", "#FFBB33"]
    desc_bg = "#f0f2f6"
    desc_text = "#333333"
    highlight = "#2E86C1"
else:
    metric_bg = "#262730"
    text_color = "#FAFAFA"
    chart_colors = ["#4CAF50", "#FF9999"]
    desc_bg = "#1e1e1e"
    desc_text = "#f5f5f5"
    highlight = "#4FC3F7"

# --- About Section ---
st.markdown(f"""
<div style='background-color:{desc_bg}; padding:22px; border-radius:12px; margin-bottom:20px;'>
<h3 style='color:{highlight}; margin-top:0;'>About This Tool</h3>

<p style='font-size:16px; color:{desc_text};'>
The <b>GC Content Analysis Tool</b> helps you explore DNA composition by calculating
the <b>GC content</b>  (the proportion of guanine (G) and cytosine (C) bases in your DNA sequences).
</p>

<ul style='font-size:16px; color:{desc_text}; margin-left:25px;'>
<li><b>GC-rich DNA</b> is more stable and melts at higher temperatures.</li>
<li><b>AT-rich regions</b> are generally more flexible and easier to separate.</li>
<li>GC content patterns can reflect gene function, species variation, or genome structure.</li>
</ul>

<p style='font-size:16px; color:{desc_text};'>
This tool lets you upload or paste sequences, visualize GC distribution through charts,
and download results instantly for further analysis.
</p>

<hr style='border:0.5px solid #888888; margin:15px 0;'>
<p style='font-size:15px; color:{desc_text};'>
<i>Quick takeaway:</i> GC content offers a clear, powerful look into DNA stability.
</div>
""", unsafe_allow_html=True)

# --- Highlight Cards ---
st.markdown(f"""
<div style='display:flex; gap:20px; flex-wrap:wrap; margin-top:20px;'>

<div style='flex:1; min-width:280px; background-color:{desc_bg}; padding:15px; border-radius:12px; text-align:center; box-shadow: 0px 3px 8px rgba(0,0,0,0.1);'>
<h4 style='color:{highlight};'>Easy Input</h4>
<p style='color:{desc_text};'>Upload a FASTA file or paste sequences directly. No formatting headaches.</p>
</div>

<div style='flex:1; min-width:280px; background-color:{desc_bg}; padding:15px; border-radius:12px; text-align:center; box-shadow: 0px 3px 8px rgba(0,0,0,0.1);'>
<h4 style='color:{highlight};'>Instant Analysis</h4>
<p style='color:{desc_text};'>Get GC% stats, charts, and downloadable reports in one click.</p>
</div>


</div>
""", unsafe_allow_html=True)

# --- Fun non-bio explanation ---
st.markdown(f"""
<div style='background-color:{desc_bg}; padding:20px; border-radius:12px; margin-top:20px;'>
<h3 style='color:{highlight}; margin-top:0;'> For Non-biologists:</h3>
<p style='font-size:16px; color:{desc_text};'>
Think of your DNA like a recipe written in four letters: A, T, G, and C. 
This app checks how much of your recipe is made up of the 'stronger ingredients' - G and C. 
The more GC you’ve got, the tougher your DNA tends to be. It’s that simple!
</p>
</div>
""", unsafe_allow_html=True)

# === Sidebar Inputs ===
st.sidebar.header("Input Options")
option = st.sidebar.radio(
    "How do you want to input sequences?",
    ("Upload FASTA File", "Paste Sequence Directly")
)

# --- Initialize session state ---
if "seq_input" not in st.session_state:
    st.session_state.seq_input = ""
if "sequences" not in st.session_state:
    st.session_state.sequences = []

# --- Helper to clean header ---
def clean_header(header: str) -> str:
    """Return only the first word of the FASTA header (after '>')."""
    if not header:
        return header
    return header.split()[0].strip()

# --- FASTA parser ---
def parse_fasta(text):
    fasta_seqs = []
    lines = text.strip().splitlines()
    header = None
    seq_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header and seq_lines:
                fasta_seqs.append((clean_header(header), "".join(seq_lines).upper()))
            header = line[1:].strip()
            seq_lines = []
        else:
            seq_lines.append(line)
    if header and seq_lines:
        fasta_seqs.append((clean_header(header), "".join(seq_lines).upper()))
    return fasta_seqs

# --- File upload ---
if option == "Upload FASTA File":
    uploaded_file = st.sidebar.file_uploader("Upload your FASTA file", type=["fasta", "fa", "txt"])
    if uploaded_file is not None:
        with open("temp.fasta", "wb") as f:
            f.write(uploaded_file.getbuffer())
        try:
            st.session_state.sequences = read_sequences("temp.fasta")
            st.session_state.sequences = [
                (clean_header(h), s) if isinstance(h, str) else (h, s)
                for (h, s) in st.session_state.sequences
            ]
            if not st.session_state.sequences:
                st.error("❌ No valid DNA sequences found in the uploaded file.")
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")

# --- Pasted sequences ---
elif option == "Paste Sequence Directly":
    st.sidebar.markdown("Note: For multiple sequences, separate each sequence by a comma.")
    st.session_state.seq_input = st.sidebar.text_area(
        "Paste your DNA sequence(s) in plain sequence format (ATGC only)",
        value=st.session_state.seq_input,
        height=200
    )

    def submit_sequences():
        text = st.session_state.seq_input.strip().upper()
        valid_seqs = []
        if text.startswith(">"):
            fasta_seqs = parse_fasta(text)
            for header, seq in fasta_seqs:
                if all(base in "ATGC" for base in seq):
                    valid_seqs.append((clean_header(header), seq))
                else:
                    st.error(f"❌ Invalid characters in sequence '{header}'. Only A, T, G, C are allowed.")
        else:
            sequences_list = [seq.strip().replace(" ", "").replace("\n", "") for seq in text.split(",") if seq.strip()]
            for i, seq in enumerate(sequences_list, start=1):
                if all(base in "ATGC" for base in seq):
                    valid_seqs.append((f"Sequence_{i}", seq))
                else:
                    st.error(f"❌ Invalid characters in Sequence {i}. Only A, T, G, C are allowed.")
        st.session_state.sequences = valid_seqs

    st.sidebar.button("Submit Sequences", on_click=submit_sequences)

# --- Use sequences from session_state ---
sequences = st.session_state.sequences

# === Process sequences ===
if sequences:
    st.subheader("Results")

    results, gc_values, names = [], [], []

    for i, item in enumerate(sequences, start=1):
        if isinstance(item, tuple):
            header, seq = item
        else:
            header, seq = None, item

        gc = gc_content(seq)
        name = header if header else f"Sequence_{i}"
        results.append((name, len(seq), gc))
        gc_values.append(gc)
        names.append(name)

    # === Tabs ===
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Graphs", "📋 Results Table", "⬇️ Downloads"])

    # --- Overview Tab ---
    with tab1:
        st.subheader("Summary Statistics")
        col1, col2, col3 = st.columns(3)
        min_gc, max_gc, avg_gc = min(gc_values), max(gc_values), sum(gc_values)/len(gc_values)

        for col, title, value in zip(
            [col1, col2, col3],
            ["Minimum GC%", "Maximum GC%", "Average GC%"],
            [min_gc, max_gc, avg_gc]
        ):
            col.markdown(f"""
            <div style='background-color:{metric_bg}; color:{text_color}; padding:20px; border-radius:10px; text-align:center; box-shadow:0px 3px 8px rgba(0,0,0,0.1);'>
                <h4>{title}</h4>
                <h3>{value:.2f}</h3>
            </div>
            """, unsafe_allow_html=True)

    # --- Graphs Tab ---
    with tab2:
        fig, ax = plt.subplots(1, 2, figsize=(10, 4))
        ax[0].hist(gc_values, bins=10, color=chart_colors[0], edgecolor="black")
        ax[0].set_xlabel("GC%")
        ax[0].set_ylabel("Frequency")
        ax[0].set_title("GC Content Distribution")

        ax[1].bar(names, gc_values, color=chart_colors[0], edgecolor="black")
        ax[1].set_xlabel("Sequences")
        ax[1].set_ylabel("GC%")
        ax[1].set_title("GC% per Sequence")
        plt.setp(ax[1].xaxis.get_majorticklabels(), rotation=0, ha="center")
        ax[1].tick_params(axis="x", pad=10)
        ax[1].xaxis.labelpad = 20
        plt.subplots_adjust(bottom=0.25)
        plt.tight_layout()
        st.pyplot(fig)

        # Pie charts
        st.subheader("GC vs AT Composition")
        num_per_row = 2
        for row_start in range(0, len(results), num_per_row):
            cols = st.columns(num_per_row)
            for i, (name, length, gc) in enumerate(results[row_start:row_start+num_per_row]):
                at = 100 - gc
                fig, ax = plt.subplots(figsize=(3, 3))
                ax.pie([gc, at], labels=None, autopct="%.1f%%", colors=chart_colors, textprops={"fontsize": 10})
                ax.set_title(name, fontsize=10, pad=6)
                ax.legend(["GC%", "AT%"], loc="center left", bbox_to_anchor=(1, 0.5), fontsize=8, frameon=False)
                cols[i].pyplot(fig)

    # --- Results Table Tab ---
    with tab3:
        df = pd.DataFrame(results, columns=["Sequence Name", "Length", "GC%"])
        st.dataframe(df)

    # --- Downloads Tab ---
    with tab4:
        df = pd.DataFrame(results, columns=["Sequence Name", "Length", "GC%"])
        st.markdown("⬇️ *Click below to grab your results — instant and tidy!*")
        st.download_button(
            "📥 Download Results as CSV",
            df.to_csv(index=False).encode("utf-8"),
            "gc_content_results.csv",
            "text/csv",
            key="csv_download"
        )
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, engine="openpyxl")
        st.download_button(
            "📊 Download Results as Excel",
            excel_buffer.getvalue(),
            "gc_content_results.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="excel_download"
        )

# --- Footer ---

