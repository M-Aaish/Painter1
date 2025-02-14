import streamlit as st
import pandas as pd
import numpy as np
from itertools import combinations
from sklearn.metrics import mean_squared_error

@st.cache_data
def load_and_parse_excel():
    """Load and parse the Excel database with enhanced error handling"""
    brands = {}
    try:
        xls = pd.ExcelFile('paints.xlsx')
        
        for sheet_name in xls.sheet_names:
            if sheet_name == 'Common Color Names & Values':
                continue
                
            df = pd.read_excel(xls, sheet_name=sheet_name).rename(columns=str.lower)
            
            # Handle different column name variations
            rgb_col = next((col for col in df.columns if 'rgb' in col.lower()), None)
            name_col = next((col for col in df.columns if 'name' in col.lower()), None)
            
            if not rgb_col or not name_col:
                continue
                
            # Clean and parse RGB values
            def parse_rgb(value):
                try:
                    if isinstance(value, str):
                        if ',' in value:
                            return tuple(map(int, value.split(',')))
                        else:
                            num_str = f"{int(float(value)):09d}"  # Handle float representations
                            return tuple(int(num_str[i:i+3]) for i in [0, 3, 6])
                    elif isinstance(value, (int, float)):
                        num_str = f"{int(value):09d}"
                        return tuple(int(num_str[i:i+3]) for i in [0, 3, 6])
                except:
                    return None
                
            df['parsed_rgb'] = df[rgb_col].apply(parse_rgb)
            df = df.dropna(subset=['parsed_rgb'])
            
            brands[sheet_name] = df[[name_col, 'parsed_rgb']].rename(
                columns={name_col: 'name', 'parsed_rgb': 'rgb'}
            )
            
    except Exception as e:
        st.error(f"Error loading Excel file: {str(e)}")
    
    return brands

def calculate_color_match(colors, target_rgb, max_colors=3):
    """Calculate best color matches using constrained optimization"""
    target = np.array(target_rgb)
    candidates = []
    
    # Normalize RGB values to 0-1 range
    max_val = 255.0
    target_norm = target / max_val
    color_matrix = np.array([np.array(c) / max_val for c in colors['rgb']])
    
    # Try different combinations
    for n in range(1, max_colors+1):
        for indices in combinations(range(len(colors)), n):
            try:
                # Solve for optimal weights
                A = color_matrix[list(indices)].T
                weights = np.linalg.lstsq(A, target_norm, rcond=None)[0]
                weights = np.clip(weights, 0, 1)  # No negative mixing
                total = weights.sum()
                
                if total == 0:
                    continue
                
                # Normalize weights to sum to 1
                weights /= total
                mix = A @ weights * max_val
                error = mean_squared_error(target, mix)
                
                if error < 500:  # Adjust error threshold as needed
                    candidates.append({
                        'indices': indices,
                        'weights': weights,
                        'error': error
                    })
            except:
                continue
    
    # Sort and select top candidates
    candidates.sort(key=lambda x: x['error'])
    return candidates[:3]

def main():
    st.title("Professional Paint Mixing Calculator")
    st.markdown("### Using manufacturer-provided color database")
    
    # Load data with progress indicator
    with st.spinner("Loading paint database..."):
        brands = load_and_parse_excel()
    
    if not brands:
        st.error("No valid paint data loaded. Check the Excel file format.")
        return
    
    # Brand selection
    brand_names = list(brands.keys())
    selected_brand = st.selectbox(
        "Select Paint Brand", 
        brand_names,
        help="Choose the manufacturer's product line you want to use"
    )
    
    # RGB input with validation
    target_rgb = st.text_input(
        "Target RGB Color (0-255 values, comma-separated)",
        help="Example: 128,255,0"
    )
    
    if not target_rgb:
        return
    
    try:
        target = tuple(map(int, target_rgb.split(',')))
        if len(target) != 3 or any(0 > v > 255 for v in target):
            raise ValueError
    except:
        st.error("Invalid RGB format. Please use three comma-separated values between 0-255")
        return
    
    # Get brand data
    brand_data = brands[selected_brand]
    if brand_data.empty:
        st.warning("Selected brand has no valid color data")
        return
    
    # Calculate matches
    with st.spinner(f"Calculating best mixes from {len(brand_data)} colors..."):
        results = calculate_color_match(brand_data, target)
    
    if not results:
        st.warning("No valid combinations found. Try adjusting the RGB values or select another brand.")
        return
    
    # Display results
    st.subheader("Recommended Mixing Recipes")
    
    for i, result in enumerate(results, 1):
        cols = st.columns([1, 4])
        with cols[0]:
            st.markdown(f"**Recipe #{i}**  \n"
                        f"Error: {result['error']:.1f}")
        
        with cols[1]:
            for idx, weight in zip(result['indices'], result['weights']):
                color = brand_data.iloc[idx]
                rgb = color['rgb']
                st.markdown(
                    f"- **{color['name']}**  \n"
                    f"  {weight*100:.1f}% (RGB: {rgb[0]}, {rgb[1]}, {rgb[2]})"
                )
        
        st.write("---")

if __name__ == "__main__":
    main()
