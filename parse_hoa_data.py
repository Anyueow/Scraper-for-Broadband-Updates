"""
Parse Neighborhoods Fill JSON, visualize HOA data, and extract HOA names.
"""

import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Streamlit will be imported only when needed in main_streamlit()

def load_json_data(file_path):
    """Load and parse the JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def extract_hoa_data(data):
    """Extract HOA information from the JSON data."""
    hoa_list = []
    
    for entry in data:
        attrs = entry.get('attributes', {})
        geometry = entry.get('geometry', {})
        
        # Extract all available attributes
        hoa_info = {
            'OBJECTID': attrs.get('OBJECTID', ''),
            'PRESIDENT': attrs.get('PRESIDENT', ''),
            'PRESIDENT_EMAIL': attrs.get('PRESIDENT_EMAIL', ''),
            'PRESIDENT_PHONE': attrs.get('PRESIDENT_PHONE', ''),
            'VICE_PRESIDENT': attrs.get('VICE_PRESIDENT', ''),
            'VP_EMAIL': attrs.get('VP_EMAIL', ''),
            'VP_PHONE': attrs.get('VP_PHONE', ''),
            'SECRETARY': attrs.get('SECRETARY', ''),
            'SECRETARY_EMAIL': attrs.get('SECRETARY_EMAIL', ''),
            'SECRETARY_PHONE': attrs.get('SECRETARY_PHONE', ''),
            'TREASURER': attrs.get('TREASURER', ''),
            'TREASURER_EMAIL': attrs.get('TREASURER_EMAIL', ''),
            'TREASURER_PHONE': attrs.get('TREASURER_PHONE', ''),
            'WARD': attrs.get('WARD', ''),
            'STATUS': attrs.get('STATUS', ''),
            'NORTH_BOUNDARY': attrs.get('NORTH_BOUNDARY', ''),
            'SOUTH_BOUNDARY': attrs.get('SOUTH_BOUNDARY', ''),
            'EAST_BOUNDARY': attrs.get('EAST_BOUNDARY', ''),
            'WEST_BOUNDARY': attrs.get('WEST_BOUNDARY', ''),
        }
        
        # Try to create a name from boundaries or other fields
        # If no explicit name field, create identifier from boundaries
        boundaries = [
            hoa_info['NORTH_BOUNDARY'],
            hoa_info['SOUTH_BOUNDARY'],
            hoa_info['EAST_BOUNDARY'],
            hoa_info['WEST_BOUNDARY']
        ]
        boundaries_str = ' / '.join([b for b in boundaries if b and b.strip()])
        hoa_info['HOA_NAME'] = boundaries_str if boundaries_str else f"HOA_{hoa_info['OBJECTID']}"
        
        hoa_list.append(hoa_info)
    
    return pd.DataFrame(hoa_list)

def create_visualizations(df):
    """Create visualizations of HOA data."""
    visualizations = {}
    
    # 1. HOA Status Distribution
    if 'STATUS' in df.columns:
        status_counts = df['STATUS'].value_counts()
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="HOA Status Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        visualizations['status'] = fig_status
    
    # 2. HOA by Ward
    if 'WARD' in df.columns:
        ward_counts = df['WARD'].value_counts().sort_index()
        fig_ward = px.bar(
            x=ward_counts.index,
            y=ward_counts.values,
            title="HOA Count by Ward",
            labels={'x': 'Ward', 'y': 'Number of HOAs'},
            color=ward_counts.values,
            color_continuous_scale='Blues'
        )
        visualizations['ward'] = fig_ward
    
    # 3. Contact Information Completeness
    contact_fields = ['PRESIDENT', 'VICE_PRESIDENT', 'SECRETARY', 'TREASURER']
    contact_completeness = {}
    for field in contact_fields:
        if field in df.columns:
            contact_completeness[field.replace('_', ' ')] = df[field].notna().sum()
    
    if contact_completeness:
        fig_contacts = px.bar(
            x=list(contact_completeness.keys()),
            y=list(contact_completeness.values()),
            title="Contact Information Completeness",
            labels={'x': 'Position', 'y': 'Number with Contact Info'},
            color=list(contact_completeness.values()),
            color_continuous_scale='Greens'
        )
        visualizations['contacts'] = fig_contacts
    
    return visualizations

def export_hoa_names(df, output_file='hoa_names.csv'):
    """Export HOA names to CSV."""
    # Create a simplified dataframe with just names and key info
    export_df = df[['HOA_NAME', 'OBJECTID', 'WARD', 'STATUS', 'PRESIDENT', 'PRESIDENT_EMAIL', 'PRESIDENT_PHONE']].copy()
    export_df.to_csv(output_file, index=False)
    return output_file

def main_streamlit():
    """Streamlit dashboard for HOA data visualization."""
    import streamlit as st
    st.set_page_config(
        page_title="HOA Data Parser & Visualizer",
        page_icon="🏘️",
        layout="wide"
    )
    
    st.title("🏘️ HOA Neighborhood Data Parser & Visualizer")
    
    # File upload
    json_file = st.file_uploader("Upload Neighborhoods Fill JSON file", type=['json'])
    
    if json_file is not None:
        # Load data
        data = json.load(json_file)
        df = extract_hoa_data(data)
        
        st.success(f"✅ Loaded {len(df)} HOA records")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total HOAs", len(df))
        with col2:
            st.metric("Active HOAs", len(df[df['STATUS'] == 'Active']) if 'STATUS' in df.columns else 'N/A')
        with col3:
            st.metric("Wards", df['WARD'].nunique() if 'WARD' in df.columns else 'N/A')
        with col4:
            st.metric("With President Info", df['PRESIDENT'].notna().sum() if 'PRESIDENT' in df.columns else 'N/A')
        
        st.markdown("---")
        
        # Visualizations
        st.subheader("📊 Visualizations")
        viz = create_visualizations(df)
        
        if 'status' in viz:
            st.plotly_chart(viz['status'], use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if 'ward' in viz:
                st.plotly_chart(viz['ward'], use_container_width=True)
        with col2:
            if 'contacts' in viz:
                st.plotly_chart(viz['contacts'], use_container_width=True)
        
        st.markdown("---")
        
        # HOA Names Table
        st.subheader("📋 HOA Names & Information")
        
        # Search/filter
        search_term = st.text_input("🔍 Search HOA names or boundaries", "")
        if search_term:
            mask = df['HOA_NAME'].str.contains(search_term, case=False, na=False)
            display_df = df[mask]
        else:
            display_df = df
        
        # Display table
        st.dataframe(
            display_df[['HOA_NAME', 'OBJECTID', 'WARD', 'STATUS', 'PRESIDENT', 'PRESIDENT_EMAIL', 'PRESIDENT_PHONE']],
            use_container_width=True,
            height=400
        )
        
        st.markdown("---")
        
        # Export
        st.subheader("📥 Export Data")
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="Download HOA Names (CSV)",
            data=csv,
            file_name="hoa_names.csv",
            mime="text/csv"
        )
        
        # Show all HOA names as a list
        with st.expander("📝 View All HOA Names (Text List)"):
            hoa_names = display_df['HOA_NAME'].tolist()
            st.text('\n'.join([f"{i+1}. {name}" for i, name in enumerate(hoa_names)]))
    
    else:
        st.info("👆 Please upload the 'Neighborhoods Fill.json' file to begin")

def main_cli():
    """Command-line interface for parsing and exporting HOA data."""
    import sys
    
    json_file = "Neighborhoods Fill.json"
    
    if not Path(json_file).exists():
        print(f"❌ Error: {json_file} not found!")
        print("Usage: python parse_hoa_data.py [json_file_path]")
        sys.exit(1)
    
    print(f"📂 Loading {json_file}...")
    data = load_json_data(json_file)
    print(f"✅ Loaded {len(data)} records")
    
    print("🔄 Extracting HOA data...")
    df = extract_hoa_data(data)
    print(f"✅ Extracted {len(df)} HOA records")
    
    print("\n📊 Summary Statistics:")
    print(f"  - Total HOAs: {len(df)}")
    if 'STATUS' in df.columns:
        print(f"  - Active HOAs: {len(df[df['STATUS'] == 'Active'])}")
    if 'WARD' in df.columns:
        print(f"  - Wards: {df['WARD'].nunique()}")
    if 'PRESIDENT' in df.columns:
        print(f"  - With President Info: {df['PRESIDENT'].notna().sum()}")
    
    # Export
    output_file = export_hoa_names(df)
    print(f"\n💾 Exported HOA names to: {output_file}")
    
    # Print first 10 HOA names
    print("\n📝 First 10 HOA Names:")
    for i, name in enumerate(df['HOA_NAME'].head(10), 1):
        print(f"  {i}. {name}")
    
    print(f"\n✅ Complete! Total HOA names extracted: {len(df)}")

if __name__ == "__main__":
    import sys
    
    # Check if running with streamlit (when called via: streamlit run parse_hoa_data.py)
    if len(sys.argv) > 0 and 'streamlit' in str(sys.argv[0]):
        # Running via streamlit
        main_streamlit()
    else:
        # Running as CLI script
        main_cli()

