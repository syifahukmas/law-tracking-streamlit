import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

# Konfigurasi halaman
st.set_page_config(
    page_title="Visualisasi Sankey Diagram",
    page_icon=":bar_chart:",
    layout="wide",
)

# Function to extract regulation number between 'Nomor' and 'tentang'
def extract_peraturan_number(text):
    if not isinstance(text, str):
        return []
    pattern = r'(Nomor|No\.)\s([\w/.]+\sTahun\s\d+|[\w/.]+)\s(?=tentang|Tentang)'
    match = re.search(pattern, text)
    return f"{match.group(1)} {match.group(2)}" if match else None

# Function to extract the first word and regulation number from the first statement
def extract_first_statement(text):
    if not isinstance(text, str):
        return []    
    first_statement = text.split(';')[0].strip()
    first_word = first_statement.split()[0]
    peraturan_number = extract_peraturan_number(first_statement)
    return [f"{first_word} - {peraturan_number}"] if peraturan_number else []

# Function to extract statements from 'Nomor' until before 'tentang'
def extract_statements_after_semicolon(text):
    if not isinstance(text, str):
        return []
    statements = [sentence.strip() for sentence in text.split(';')]
    results = []
    for statement in statements:
        peraturan_number = extract_peraturan_number(statement)
        if peraturan_number:
            first_word = statement.split()[0]
            results.append(f"{first_word} - {peraturan_number}")
    return results

# Function to create a Sankey Diagram from the 'Keterangan_status' column based on the regulation number
def sankey_from_keterangan_status(dfx, nomor_uu):
    sources = []
    targets = []
    labels = []
    unique_labels = {}  # Dictionary to map labels to their descriptions
    label_counter = 1  # Start from index 1, as 0 will be reserved for the regulation

    filtered_df = dfx[dfx['Nomor Peraturan'] == nomor_uu]

    if filtered_df.empty:
        print(f"Regulation number {nomor_uu} not found.")
        return
    
    # Get the regulation content for the first node
    isi_uu = filtered_df['Isi UU'].values[0]
    bentuk_peraturan = filtered_df['Singkatan Jenis / Bentuk Peraturan'].values[0]
    nomor_peraturan = filtered_df['Nomor Peraturan'].values[0]

    # Create the first node with index 0
    first_node = f"{bentuk_peraturan} - {nomor_peraturan}"
    unique_labels[0] = first_node  # Index 0 will hold the regulation details
    prev_node = 0  # Start from node index 0

    # Weights for the first words
    weight_dict = {
        "Diubah": 5,
        "Dicabut": 10,
        "Mencabut": 15,
        "Mengubah": 20
    }

    for changes in filtered_df['Keterangan_Status']:
        first_statements = extract_first_statement(changes)
        for statement in first_statements:
            if statement not in unique_labels.values():
                unique_labels[label_counter] = statement
                sources.append(prev_node)
                targets.append(label_counter)
                prev_node = label_counter
                label_counter += 1
        
        statements_after_semicolon = extract_statements_after_semicolon(changes)
        for statement in statements_after_semicolon:
            if statement not in unique_labels.values():
                unique_labels[label_counter] = statement
                sources.append(prev_node)
                targets.append(label_counter)
                prev_node = label_counter
                label_counter += 1

    if len(targets) == 0:
        st.write("Tidak ada perubahan yang terdaftar.")
        return

    label_list = list(unique_labels.keys())
    label_map = {label: idx for idx, label in enumerate(label_list)}
    
    source_indices = [src for src in sources]
    target_indices = [tgt for tgt in targets]

    # Get weights for each link based on the first word
    values = []
    for target in target_indices:
        statement = unique_labels[target]
        first_word = statement.split()[0]  # Use the first word for weight mapping
        values.append(weight_dict.get(first_word, 10))  # Default weight if not found

    # Define colors for node colors based on the first word
    color_mapping = {
        "Diubah": "#C76A6A",  # Red
        "Dicabut": "#D6C93A",  # Yellow
        "Mencabut": "#5DAFCE",  # Blue
        "Mengubah": "#6BBF8C",  # Green
    }

    node_colors = []
    for label in unique_labels.values():
        first_word = label.split()[0]  # Get the first word for color mapping
        node_colors.append(color_mapping.get(first_word, "grey"))  # Default color if not found

    # Define colors for links based on the first word
    link_color_mapping = {
        "Diubah": "#F5B7B1",  # Red
        "Dicabut": "#F9E79F",  # Yellow
        "Mencabut": "#85C1AE",  # Blue
        "Mengubah": "#A9DFBF"   # Green
    }

    # Create the list of link colors
    link_colors = []
    for target in target_indices:
        statement = unique_labels[target]
        first_word = statement.split()[0]
        link_colors.append(link_color_mapping.get(first_word, "grey"))

    # Create Sankey Diagram
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=30,
            line=dict(color="black", width=0.5),
            label=[str(idx) for idx in unique_labels.keys()],  # Use indices as labels
            color=node_colors  # Set node colors
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values,
            color=link_colors
        )
    ))

    # Display descriptions for each index
    descriptions = "\n".join([f"{idx}: {desc}" for idx, desc in unique_labels.items()])

    st.text("Descriptions for each index:")
    st.text(descriptions)
    
    # Display the Sankey diagram
    st.plotly_chart(fig)




# Load the data
@st.cache_data
def load_data():
    return pd.read_csv('data/jdih_data_cleaning.csv')

data = load_data()

st.title("Pemantauan Perubahan Hukum: Analisis Data dari JDIH KESDM")
st.write("""Dashboard ini memvisualisasikan perubahan regulasi di sektor energi dan 
         sumber daya mineral berdasarkan data dari JDIH KESDM. Melalui visualisasi 
         yang disediakan, dapat memudahkan dalam melihat alur perubahan pada 
         peraturan, termasuk penghapusan, revisi, atau adopsi regulasi baru. Filter 
         interaktif membantu eksplorasi berdasarkan Bentuk Peraturan dan Nomor Undang-undang.""")

tipe_dokumen = st.selectbox('Pilih Bentuk Peraturan', ['Semua'] + data['Singkatan Jenis / Bentuk Peraturan'].unique().tolist())
if tipe_dokumen == 'Semua':
    filtered_data = data 
else:
    filtered_data = data[data['Singkatan Jenis / Bentuk Peraturan'] == tipe_dokumen]

nomor_uu = st.selectbox('Pilih Nomor UU', filtered_data['Nomor Peraturan'].unique().tolist())

# diubah
# Sidebar for filter
st.sidebar.title("Navigasi Menu")

menu = st.sidebar.radio("Pilih Halaman:", 
                        ["📊 Data Tabel", "📉 Sankey Diagram", "📈 Deskripsi Data"])
if menu == "📊 Data Tabel":
    filtered_data = filtered_data.reset_index(drop=True)
    filtered_data.index += 1
    if tipe_dokumen == 'Tampilkan Semua':
        st.write(f"### Semua Data")
    else:
        st.write(f"### Data {tipe_dokumen}")
    st.write(filtered_data)

elif menu == "📉 Sankey Diagram":
    selected_data = data[data['Nomor Peraturan'] == nomor_uu]
    if 'Singkatan Jenis / Bentuk Peraturan' in selected_data.columns and 'Nomor Peraturan' in selected_data.columns:
        bentuk_peraturan = selected_data['Singkatan Jenis / Bentuk Peraturan'].iloc[0]
        nomor_peraturan = selected_data['Nomor Peraturan'].iloc[0]
        peraturan_info = f"{bentuk_peraturan} Nomor {nomor_peraturan}"
    else:
        peraturan_info = "Informasi peraturan tidak tersedia."
    
    st.write(f"### Sankey Diagram untuk {peraturan_info}")
    # Calculating total revision
    if 'Keterangan_Status' in selected_data.columns:
        total_revisi = len(selected_data[selected_data['Keterangan_Status'].notna() & selected_data['Keterangan_Status'].str.contains("Diubah", na=False)])
    else:
        total_revisi = 0
    # Calculating total revocations
    if 'Keterangan_Status' in selected_data.columns:
        total_pencabutan = len(selected_data[selected_data['Keterangan_Status'].notna() & selected_data['Keterangan_Status'].str.contains("Dicabut", na=False)])
    else:
        total_pencabutan = 0 
    st.write(f"**Total Revisi**: {total_revisi}")
    st.write(f"**Total Pencabutan**: {total_pencabutan}")
    sankey_from_keterangan_status(data, nomor_uu)
    st.write(f"### Isi dari {peraturan_info} adalah:")
    isi_uu = selected_data['Isi UU'].iloc[0] if 'Isi UU' in selected_data.columns else "Isi UU tidak tersedia."
    st.write(isi_uu)
    st.write("") 
    st.write(f"\n### Perubahan dari {peraturan_info} mencakup:")
    # Obtaining the content of changes
    if 'Keterangan_Status' in selected_data.columns:
        isi_perubahan = selected_data['Keterangan_Status'].iloc[0] if selected_data['Keterangan_Status'].notna().any() else "Tidak ada perubahan yang terdaftar."
        # Ensuring that isi_perubahan is a string
        if isinstance(isi_perubahan, str):
            perubahan_list = isi_perubahan.split(";") 
            for perubahan in perubahan_list:
                perubahan = perubahan.strip()  
                if perubahan: 
                    st.write(f"- {perubahan}")
        else:
            st.write("Tidak ada perubahan yang terdaftar.")
    else:
        st.write("Keterangan status tidak tersedia.")

elif menu == "📈 Deskripsi Data":
    st.write("### Deskripsi Data")
    # st.write(data.describe())
    st.write("Tabel data terdiri dari:")
    for column in data.columns:
        st.write(f"- {column}")
