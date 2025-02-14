import streamlit as st
import numpy as np

# In-code color database
color_db = {
    "Aquamarine": {"hex": "#7fffd4", "rgb": [127, 255, 212]},
    "Antiquewhite": {"hex": "#faebd7", "rgb": [250, 235, 215]},
    "Beige": {"hex": "#f5f5dc", "rgb": [245, 245, 220]},
    "Cadetblue": {"hex": "#5f9ea0", "rgb": [95, 158, 160]},
    "Coral": {"hex": "#ff7f50", "rgb": [255, 127, 80]},
    "Cornflowerblue": {"hex": "#6495ed", "rgb": [100, 149, 237]},
    "Cornsilk": {"hex": "#fff8dc", "rgb": [255, 248, 220]},
    "Firebrick": {"hex": "#b22222", "rgb": [178, 34, 34]},
    "Forestgreen": {"hex": "#228b22", "rgb": [34, 139, 34]},
    "Gainsboro": {"hex": "#dcdcdc", "rgb": [220, 220, 220]},
    "Gold": {"hex": "#ffd700", "rgb": [255, 215, 0]},
    "Honeydew": {"hex": "#f0fff0", "rgb": [240, 255, 240]},
    "Khaki": {"hex": "#f0e68c", "rgb": [240, 230, 140]},
    "Lavender": {"hex": "#e6e6fa", "rgb": [230, 230, 250]},
    "Lavenderblush": {"hex": "#fff0f5", "rgb": [255, 240, 245]},
    "Lawngreen": {"hex": "#7cfc00", "rgb": [124, 252, 0]},
    "Lemonchiffon": {"hex": "#fffacd", "rgb": [255, 250, 205]},
    "Lightsalmon": {"hex": "#ffa07a", "rgb": [255, 160, 122]},
    "Linen": {"hex": "#faf0e6", "rgb": [250, 240, 230]},
    "Maroon": {"hex": "#800000", "rgb": [128, 0, 0]},
    "Midnightblue": {"hex": "#191970", "rgb": [25, 25, 112]},
    "Mintcream": {"hex": "#f5fffa", "rgb": [240, 255, 250]},
    "Mistyrose": {"hex": "#ffe4e1", "rgb": [255, 228, 225]},
    "Moccasin": {"hex": "#ffe4b5", "rgb": [255, 228, 181]},
    "Navy": {"hex": "#000080", "rgb": [0, 0, 128]},
    "Oldlace": {"hex": "#fdf5e6", "rgb": [253, 245, 230]},
    "Olive": {"hex": "#808000", "rgb": [128, 128, 0]},
    "Olivedrab": {"hex": "#6b8e23", "rgb": [107, 142, 35]},
    "Orchid": {"hex": "#da70d6", "rgb": [218, 112, 214]},
    "Palegoldenrod": {"hex": "#eee8aa", "rgb": [238, 232, 170]},
    "Palegreen": {"hex": "#98fb98", "rgb": [152, 251, 152]},
    "Peachpuff": {"hex": "#ffdab9", "rgb": [255, 218, 185]},
    "Peru": {"hex": "#cd853f", "rgb": [205, 133, 63]},
    "Pink": {"hex": "#ffc0cb", "rgb": [255, 192, 203]},
    "Plum": {"hex": "#dda0dd", "rgb": [221, 160, 221]},
    "Royalblue": {"hex": "#4169e1", "rgb": [65, 105, 225]},
    "Saddlebrown": {"hex": "#8b4513", "rgb": [139, 69, 19]},
    "Salmon": {"hex": "#fa8072", "rgb": [250, 128, 114]},
    "Seagreen": {"hex": "#2e8b57", "rgb": [46, 139, 87]},
    "Seashell": {"hex": "#fff5ee", "rgb": [255, 245, 238]},
    "Slategray": {"hex": "#708090", "rgb": [112, 128, 144]},
}

# Helper function: convert hex to RGB tuple
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Helper function: compute Euclidean distance between two RGB colors
def color_distance(c1, c2):
    return np.linalg.norm(np.array(c1) - np.array(c2))

st.title("Painter App: Paint Recipe Generator")
st.markdown("Select your desired color using the color picker below. The app will generate a paint recipe using the available colors.")

# Desired color input via color picker
desired_hex = st.color_picker("Pick the desired color", "#ffffff")
desired_rgb = hex_to_rgb(desired_hex)
st.write("Desired RGB:", desired_rgb)

# Build a list of paints from the color_db
paints = []
for name, info in color_db.items():
    paints.append({
        'Name': name,
        'hex': info['hex'],
        'rgb': info['rgb'],
        'R': info['rgb'][0],
        'G': info['rgb'][1],
        'B': info['rgb'][2],
    })

# Find best match with a single paint
best_error = float('inf')
best_single = None
for paint in paints:
    err = color_distance(paint['rgb'], desired_rgb)
    if err < best_error:
        best_error = err
        best_single = paint

# Try to find a better two-paint mix using nested loops
best_two_error = float('inf')
best_two_recipe = None
best_two_mixture = None

for i, paint1 in enumerate(paints):
    color1 = np.array(paint1['rgb'])
    for j, paint2 in enumerate(paints):
        if i == j:
            continue
        color2 = np.array(paint2['rgb'])
        diff = color1 - color2
        norm_sq = np.dot(diff, diff)
        if norm_sq == 0:
            continue  # avoid division by zero if colors are identical
        desired_arr = np.array(desired_rgb)
        alpha = np.dot(desired_arr - color2, diff) / norm_sq
        alpha = max(0, min(1, alpha))  # ensure alpha is between 0 and 1
        mixture = alpha * color1 + (1 - alpha) * color2
        error = color_distance(mixture, desired_rgb)
        if error < best_two_error:
            best_two_error = error
            best_two_recipe = (paint1, paint2, alpha)
            best_two_mixture = mixture

st.header("Best Recipe Found")

# Compare the best single paint with the best two-paint mix
if best_error <= best_two_error:
    st.markdown("### Use a Single Paint")
    st.write("Paint Name:", best_single['Name'])
    st.write("RGB:", best_single['rgb'])
    st.write("Error (Euclidean distance):", round(best_error, 2))
    st.markdown(f"<div style='width:100px; height:100px; background-color:{desired_hex}; border:1px solid black;'></div>", unsafe_allow_html=True)
    st.info("The desired color is very close to one of the available paints!")
else:
    paint1, paint2, alpha = best_two_recipe
    pct1 = round(alpha * 100, 1)
    pct2 = round((1 - alpha) * 100, 1)
    st.markdown("### Mix Two Paints")
    st.write("**Paint 1:**", paint1['Name'], "RGB:", paint1['rgb'], f"({pct1}%)")
    st.write("**Paint 2:**", paint2['Name'], "RGB:", paint2['rgb'], f"({pct2}%)")
    st.write("Resulting Mixture RGB:", tuple(map(lambda x: int(round(x)), best_two_mixture)))
    st.write("Error (Euclidean distance):", round(best_two_error, 2))
    mixture_hex = '#{:02x}{:02x}{:02x}'.format(*tuple(map(lambda x: int(round(x)), best_two_mixture)))
    st.markdown(f"<div style='width:100px; height:100px; background-color:{mixture_hex}; border:1px solid black;'></div>", unsafe_allow_html=True)

st.markdown("---")
st.info("Note: This app currently supports mixing two paints. For more complex recipes, consider using optimization techniques to handle mixtures of three or more paints.")
