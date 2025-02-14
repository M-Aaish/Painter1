import streamlit as st
import pandas as pd
import numpy as np
from itertools import combinations

def parse_rgb(rgb):
    try:
        if isinstance(rgb, str):
            if ',' in rgb:
                parts = list(map(int, rgb.split(',')))
                if len(parts) == 3:
                    return parts
            else:
                num_str = f"{int(float(rgb)):09d}"
                return (
                    int(num_str[0:3]),
                    int(num_str[3:6]),
                    int(num_str[6:9])
                )
        elif isinstance(rgb, (int, float)):
            num_str = f"{int(rgb):09d}"
            return (
                int(num_str[0:3]),
                int(num_str[3:6]),
                int(num_str[6:9])
            )
    except:
        return None
    return None

@st.cache_data
def load_data():
    brands = {}
    xls = pd.ExcelFile('paints.xlsx')
    
    for sheet_name in xls.sheet_names:
        df = xls.parse(sheet_name)
        colors = []
        
        if 'Name' in df.columns and 'RGB' in df.columns:
            for _, row in df.iterrows():
                if pd.notna(row['RGB']):
                    rgb = parse_rgb(row['RGB'])
                    if rgb and len(rgb) == 3:
                        colors.append({
                            'name': row['Name'],
                            'rgb': rgb,
                            'original_rgb': row['RGB']
                        })
        
        if colors:
            brands[sheet_name] = colors
    
    return brands

def mix_colors(colors, target, max_colors=3):
    target = np.array(target) / 255.0
    recipes = []
    
    for n in range(1, max_colors+1):
        for combo in combinations(colors, n):
            cols = [c['rgb']/255.0 for c in combo]
            A = np.array(cols).T
            try:
                weights = np.linalg.lstsq(A, target, rcond=None)[0]
                weights = weights / weights.sum()
                if all(w >= -0.01 for w in weights):
                    valid_weights = np.clip(weights, 0, 1)
                    valid_weights /= valid_weights.sum()
                    recipe = []
                    for i, w in enumerate(valid_weights):
                        recipe.append({
                            'name': combo[i]['name'],
                            'percentage': w * 100,
                            'rgb': combo[i]['rgb']
                        })
                    recipes.append(recipe)
            except:
                continue
    
    recipes.sort(key=lambda x: np.linalg.norm(
        sum(c['percentage']/100 * np.array(c['rgb'])/255.0 for c in x) - target
    ))
    return recipes[:3]

def main():
    st.title("🎨 Paint Mixing Calculator")
    brands = load_data()
    
    brand_names = list(brands.keys())
    selected_brand = st.selectbox("Select Paint Brand", brand_names)
    
    st.subheader("Target Color")
    col1, col2, col3 = st.columns(3)
    with col1: r = st.slider("Red", 0, 255, 128)
    with col2: g = st.slider("Green", 0, 255, 128)
    with col3: b = st.slider("Blue", 0, 255, 128)
    
    if st.button("Generate Recipes"):
        brand_colors = brands[selected_brand]
        recipes = mix_colors(brand_colors, (r, g, b))
        
        st.subheader("Recommended Mixing Recipes")
        for i, recipe in enumerate(recipes, 1):
            with st.expander(f"Recipe #{i}"):
                cols = st.columns([1,3,2])
                total = 0
                for comp in recipe:
                    cols[0].color(f"rgb{tuple(comp['rgb'])}")
                    cols[1].write(f"**{comp['name']}**")
                    cols[2].write(f"{comp['percentage']:.1f}%")
                    cols = st.columns([1,3,2])  # New row
                    total += comp['percentage']
                st.caption(f"Total: {total:.1f}%")

if __name__ == "__main__":
    main()
