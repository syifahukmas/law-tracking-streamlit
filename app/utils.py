import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

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

    st.text("Deskripsi untuk setiap indeks:")
    st.text(descriptions)
    # Add legend for node colors
    legend_labels = list(color_mapping.keys())
    legend_colors = list(color_mapping.values())
    
    # Create a dummy scatter plot for the legend without markers
    for label, color in zip(legend_labels, legend_colors):
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='lines',  # Change to lines to avoid marker background
            line=dict(color=color, width=10),  # Set line color and width for visibility
            name=label,
            showlegend=True
        ))
    
    fig.update_layout(showlegend=True,
                      xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),  # Remove x-axis grid and ticks
                      yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),  # Remove y-axis grid and ticks
                      paper_bgcolor='rgba(0,0,0,0)',  # Make the paper background transparent
                      plot_bgcolor='rgba(0,0,0,0)'    # Make the plot background transparent
    )
    # Display the Sankey diagram
    st.plotly_chart(fig)

