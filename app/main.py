import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
from utils import sankey_from_keterangan_status

# Konfigurasi halaman
st.set_page_config(
    page_title="Visualisasi Sankey Diagram",
    page_icon=":bar_chart:",
    layout="wide",
)

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
