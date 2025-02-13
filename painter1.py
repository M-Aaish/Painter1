import streamlit as st
import json
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

def mix_colors(colors, ratios):
    total = sum(ratios)
    if total == 0:
        return "#FFFFFF"
    
    r = sum(c[0] * ratio for c, ratio in zip(colors, ratios)) / total
    g = sum(c[1] * ratio for c, ratio in zip(colors, ratios)) / total
    b = sum(c[2] * ratio for c, ratio in zip(colors, ratios)) / total
    
    return f"#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}"

def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % tuple(int(255 * x) for x in rgb)

def main():
    st.set_page_config(page_title="Paint Mixer", page_icon="🎨")
    st.title("🎨 Paint Mixer")
    st.write("Create custom paint colors by mixing different base colors")

    if 'num_colors' not in st.session_state:
        st.session_state.num_colors = 2

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("➕ Add Color"):
            st.session_state.num_colors += 1
        if st.button("➖ Remove Color") and st.session_state.num_colors > 1:
            st.session_state.num_colors -= 1

    colors = []
    ratios = []
    ratio_total = 0

    for i in range(st.session_state.num_colors):
        cols = st.columns(2)
        with cols[0]:
            color = st.color_picker(f"Color {i+1}", "#FF0000", key=f"color_{i}")
            colors.append([int(color.lstrip('#')[j:j+2], 16)/255 for j in (0, 2, 4)])
        with cols[1]:
            ratio = st.slider(f"Ratio {i+1}", 0, 100, 50 if i == 0 else 25, key=f"ratio_{i}")
            ratios.append(ratio)
            ratio_total += ratio

    if ratio_total == 0:
        st.warning("Total ratio cannot be zero!")
        return

    mixed_color = mix_colors(colors, ratios)
    
    st.markdown("---")
    st.subheader("Mixed Color Result")
    st.markdown(f'<div style="background-color:{mixed_color}; height:100px; border-radius:10px"></div>', 
                unsafe_allow_html=True)
    
    rgb = [int(x*255) for x in colors[0]] if len(colors) == 1 else [
        int(sum(c[0] * r for c, r in zip(colors, ratios))/sum(ratios)*255),
        int(sum(c[1] * r for c, r in zip(colors, ratios))/sum(ratios)*255),
        int(sum(c[2] * r for c, r in zip(colors, ratios))/sum(ratios)*255)
    ]
    
    st.write(f"**HEX:** {mixed_color}")
    st.write(f"**RGB:** {rgb[0]}, {rgb[1]}, {rgb[2]}")
    
    st.markdown("---")
    st.subheader("Paint Recipe")
    recipe = []
    for i in range(len(ratios)):
        percentage = (ratios[i] / ratio_total) * 100
        recipe.append({
            "Color": colors[i],
            "Percentage": round(percentage, 2),
            "HEX": rgb_to_hex(colors[i])
        })
        st.write(f"- Color {i+1}: {round(percentage, 2)}% ({rgb_to_hex(colors[i])})")
    
    recipe_json = json.dumps(recipe, indent=2)
    st.download_button(
        label="📥 Download Recipe",
        data=recipe_json,
        file_name="paint_recipe.json",
        mime="application/json"
    )

if __name__ == "__main__":
    main()
