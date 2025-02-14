import streamlit as st
import numpy as np

# New color database with density values
db_colors = {
    "Burnt Sienna": {"rgb": [58, 22, 14], "density": 1073},
    "Burnt Umber": {"rgb": [50, 27, 15], "density": 1348},
    "Cadmium Orange Hue": {"rgb": [221, 105, 3], "density": 1338},
    "Cadmium Red Deep Hue": {"rgb": [171, 1, 5], "density": 902},
    "Cadmium Red Medium": {"rgb": [221, 63, 0], "density": 1547},
    "Cadmium Red Light": {"rgb": [225, 83, 0], "density": 1573},
    "Cadmium Red Dark": {"rgb": [166, 0, 9], "density": 1055},
    "Cadmium Yellow Hue": {"rgb": [255, 193, 0], "density": 1230},
    "Cadmium Yellow Light": {"rgb": [255, 194, 0], "density": 1403},
    "Cadmium Yellow Medium": {"rgb": [255, 161, 0], "density": 1534},
    "Cerulean Blue Hue": {"rgb": [0, 74, 91], "density": 1216},
    "Cobalt Blue": {"rgb": [0, 39, 71], "density": 1317},
    "Dioxazine Purple": {"rgb": [215, 17, 115], "density": 1268},
    "French Ultramarine": {"rgb": [8, 8, 32], "density": 1277},
    "Ivory Black": {"rgb": [27, 28, 28], "density": 1228},
    "Lamp Black": {"rgb": [21, 21, 20], "density": 958},
    "Lemon Yellow": {"rgb": [239, 173, 0], "density": 1024},
    "Magenta": {"rgb": [98, 4, 32], "density": 1822},
    "Permanent Alizarin Crimson": {"rgb": [74, 16, 16], "density": 1217},
    "Permanent Rose": {"rgb": [130, 0, 24], "density": 1227},
    "Permanent Sap Green": {"rgb": [28, 42, 10], "density": 1041},
    "Phthalo Blue (Red Shade)": {"rgb": [17, 12, 37], "density": 1080},
    "Phthalo Green (Yellow Shade)": {"rgb": [0, 32, 24], "density": 1031},
    "Phthalo Green (Blue Shade)": {"rgb": [3, 26, 33], "density": 1021},
    "Prussian Blue": {"rgb": [15, 11, 11], "density": 984},
    "Raw Sienna": {"rgb": [117, 70, 17], "density": 1211},
    "Raw Umber": {"rgb": [37, 28, 20], "density": 1273},
    "Titanium White": {"rgb": [249, 245, 234], "density": 1423},
    "Viridian": {"rgb": [0, 53, 40], "density": 1149},
    "Yellow Ochre": {"rgb": [187, 128, 18], "density": 1283},
    "Zinc White (Mixing White)": {"rgb": [250, 242, 222], "density": 1687},
}

# Helper function: convert an RGB list to a hex color string
def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

# Helper function: compute Euclidean distance between two RGB colors
def color_distance(c1, c2):
    return np.linalg.norm(np.array(c1) - np.array(c2))

st.title("Painter App: Paint Recipe Generator")
st.markdown("Generate a paint recipe by matching a desired color with available paints.")

# Choose input method: Color Picker or Manual Entry
input_method = st.radio("Select color input method", ["Color Picker", "Manual Entry"])

if input_method == "Color Picker":
    desired_hex = st.color_picker("Pick the desired color", "#ffffff")
    desired_rgb = [int(desired_hex[i:i+2], 16) for i in (1, 3, 5)]
else:
    r = st.number_input("Enter Red value (0-255)", min_value=0, max_value=255, value=255)
    g = st.number_input("Enter Green value (0-255)", min_value=0, max_value=255, value=255)
    b = st.number_input("Enter Blue value (0-255)", min_value=0, max_value=255, value=255)
    desired_rgb = [r, g, b]
    desired_hex = '#{:02x}{:02x}{:02x}'.format(r, g, b)

st.write("Desired RGB:", desired_rgb)

# Build a list of paints from the new database
paints = []
for name, info in db_colors.items():
    paints.append({
        'Name': name,
        'rgb': info['rgb'],
        'density': info['density'],
        'hex': rgb_to_hex(info['rgb'])
    })

# 1. Find best match using a single paint
best_single_error = float('inf')
best_single = None
for paint in paints:
    err = color_distance(paint['rgb'], desired_rgb)
    if err < best_single_error:
        best_single_error = err
        best_single = paint

# 2. Find best two-paint mix using nested loops (analytical solution)
best_two_error = float('inf')
best_two_recipe = None
best_two_mixture = None
for i, paint1 in enumerate(paints):
    c1 = np.array(paint1['rgb'])
    for j, paint2 in enumerate(paints):
        if i == j:
            continue
        c2 = np.array(paint2['rgb'])
        diff = c1 - c2
        norm_sq = np.dot(diff, diff)
        if norm_sq == 0:
            continue  # identical colors
        desired_arr = np.array(desired_rgb)
        alpha = np.dot(desired_arr - c2, diff) / norm_sq
        alpha = max(0, min(1, alpha))  # clamp alpha to [0,1]
        mixture = alpha * c1 + (1 - alpha) * c2
        error = color_distance(mixture, desired_rgb)
        if error < best_two_error:
            best_two_error = error
            best_two_recipe = (paint1, paint2, alpha)
            best_two_mixture = mixture

# 3. Find best three-paint mix using grid search
best_three_error = float('inf')
best_three_recipe = None
best_three_mixture = None
step = 0.1  # grid resolution
n_paints = len(paints)
for i in range(n_paints):
    c1 = np.array(paints[i]['rgb'])
    for j in range(i+1, n_paints):
        c2 = np.array(paints[j]['rgb'])
        for k in range(j+1, n_paints):
            c3 = np.array(paints[k]['rgb'])
            # Search over coefficients a and b; let c = 1 - a - b
            for a in np.arange(0, 1+step, step):
                for b in np.arange(0, 1+step, step):
                    if a + b > 1:
                        continue
                    c_val = 1 - a - b
                    mixture = a * c1 + b * c2 + c_val * c3
                    error = color_distance(mixture, desired_rgb)
                    if error < best_three_error:
                        best_three_error = error
                        best_three_recipe = (paints[i], paints[j], paints[k], a, b, c_val)
                        best_three_mixture = mixture

# Determine the best overall option among single, two-paint, and three-paint mixtures
best_option = None
min_error = min(best_single_error, best_two_error, best_three_error)

if best_single_error == min_error:
    best_option = 'single'
elif best_two_error == min_error:
    best_option = 'two'
else:
    best_option = 'three'

st.header("Best Recipe Found")
if best_option == 'single':
    st.subheader("Use a Single Paint")
    st.write("Paint Name:", best_single['Name'])
    st.write("RGB:", best_single['rgb'])
    st.write("Density:", best_single['density'])
    st.write("Error (Euclidean distance):", round(best_single_error, 2))
    result_hex = best_single['hex']
    st.markdown(
        f"<div style='width:150px; height:150px; background-color:{result_hex}; border:1px solid black;'></div>",
        unsafe_allow_html=True,
    )
elif best_option == 'two':
    paint1, paint2, alpha = best_two_recipe
    pct1 = round(alpha * 100, 1)
    pct2 = round((1 - alpha) * 100, 1)
    st.subheader("Mix Two Paints")
    st.write("**Paint 1:**", paint1['Name'], "RGB:", paint1['rgb'], f"({pct1}%)", "Density:", paint1['density'])
    st.write("**Paint 2:**", paint2['Name'], "RGB:", paint2['rgb'], f"({pct2}%)", "Density:", paint2['density'])
    mixture_rgb = tuple(map(lambda x: int(round(x)), best_two_mixture))
    st.write("Resulting Mixture RGB:", mixture_rgb)
    st.write("Error (Euclidean distance):", round(best_two_error, 2))
    result_hex = '#{:02x}{:02x}{:02x}'.format(*mixture_rgb)
    st.markdown(
        f"<div style='width:150px; height:150px; background-color:{result_hex}; border:1px solid black;'></div>",
        unsafe_allow_html=True,
    )
else:
    paint1, paint2, paint3, a, b, c_val = best_three_recipe
    pct1 = round(a * 100, 1)
    pct2 = round(b * 100, 1)
    pct3 = round(c_val * 100, 1)
    st.subheader("Mix Three Paints")
    st.write("**Paint 1:**", paint1['Name'], "RGB:", paint1['rgb'], f"({pct1}%)", "Density:", paint1['density'])
    st.write("**Paint 2:**", paint2['Name'], "RGB:", paint2['rgb'], f"({pct2}%)", "Density:", paint2['density'])
    st.write("**Paint 3:**", paint3['Name'], "RGB:", paint3['rgb'], f"({pct3}%)", "Density:", paint3['density'])
    mixture_rgb = tuple(map(lambda x: int(round(x)), best_three_mixture))
    st.write("Resulting Mixture RGB:", mixture_rgb)
    st.write("Error (Euclidean distance):", round(best_three_error, 2))
    result_hex = '#{:02x}{:02x}{:02x}'.format(*mixture_rgb)
    st.markdown(
        f"<div style='width:150px; height:150px; background-color:{result_hex}; border:1px solid black;'></div>",
        unsafe_allow_html=True,
    )

# Side-by-side display of Desired vs. Result
col1, col2 = st.columns(2)
with col1:
    st.markdown("### Desired Color")
    st.markdown(
        f"<div style='width:150px; height:150px; background-color:{desired_hex}; border:1px solid black;'></div>",
        unsafe_allow_html=True,
    )
with col2:
    st.markdown("### Resulting Color")
    st.markdown(
        f"<div style='width:150px; height:150px; background-color:{result_hex}; border:1px solid black;'></div>",
        unsafe_allow_html=True,
    )

st.markdown("---")
st.info("Note: The three-paint mixing uses a grid search with a 0.1 resolution. Adjust the step size for a finer search (at the cost of speed).")
