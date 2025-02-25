import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
from sklearn.metrics.pairwise import euclidean_distances

# Provided base color database
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

# Function to calculate closest color mix using Euclidean Distance
def find_closest_colors(target_rgb):
    colors = np.array([color["rgb"] for color in db_colors.values()])
    color_names = list(db_colors.keys())

    distances = euclidean_distances([target_rgb], colors)[0]
    closest_indices = np.argsort(distances)[:5]  # Take top 5 closest colors
    
    return [(color_names[i], db_colors[color_names[i]]) for i in closest_indices]

# Function to generate 3 recipes using color mixing
def generate_paint_recipes(target_rgb):
    closest_colors = find_closest_colors(target_rgb)
    possible_combinations = list(combinations(closest_colors, 3))

    best_recipes = []
    for combo in possible_combinations:
        total_density = sum(color[1]["density"] for color in combo)
        weighted_rgb = np.array([0, 0, 0], dtype=float)
        percentages = []

        for name, color in combo:
            weight = color["density"] / total_density
            percentages.append(round(weight * 100, 1))
            weighted_rgb += np.array(color["rgb"]) * weight

        error = np.linalg.norm(np.array(target_rgb) - weighted_rgb)

        best_recipes.append({"colors": combo, "percentages": percentages, "mixed_rgb": weighted_rgb.astype(int), "error": error})

    best_recipes = sorted(best_recipes, key=lambda x: x["error"])[:3]
    return best_recipes

# Function to display colors in a grid
def display_color(color_name, rgb):
    st.markdown(f"<div style='width:100px; height:50px; background-color:rgb({rgb[0]},{rgb[1]},{rgb[2]});'></div>", unsafe_allow_html=True)
    st.write(f"**{color_name}** (RGB: {rgb})")

# Streamlit UI
st.title("🎨 Paint Recipe Generator")
st.markdown("Enter an RGB value and get three possible paint recipes using base colors.")

# User Input
r = st.slider("Red", 0, 255, 128)
g = st.slider("Green", 0, 255, 128)
b = st.slider("Blue", 0, 255, 128)
target_color = (r, g, b)

# Display Desired Color
st.subheader("🎨 Desired Color")
st.markdown(f"<div style='width:150px; height:75px; background-color:rgb({r},{g},{b});'></div>", unsafe_allow_html=True)
st.write(f"RGB: ({r}, {g}, {b})")

if st.button("Generate Recipe"):
    recipes = generate_paint_recipes(target_color)
    
    st.subheader("🎨 Generated Paint Recipes")
    for idx, recipe in enumerate(recipes, start=1):
        st.markdown(f"### Recipe {idx}")

        # Display individual colors with percentages
        cols = st.columns(len(recipe["colors"]))
        for i, (color_name, color_data) in enumerate(recipe["colors"]):
            with cols[i]:
                display_color(color_name, color_data["rgb"])
                st.write(f"{recipe['percentages'][i]}%")

        # Display mixed color result
        st.markdown("##### Mixed Color Result")
        mixed_rgb = recipe["mixed_rgb"]
        st.markdown(f"<div style='width:150px; height:75px; background-color:rgb({mixed_rgb[0]},{mixed_rgb[1]},{mixed_rgb[2]});'></div>", unsafe_allow_html=True)
        st.write(f"Mixed RGB: {tuple(mixed_rgb)}")

        # Comparison with Desired Color
        fig, ax = plt.subplots(1, 2, figsize=(5, 2))
        ax[0].imshow([[target_color]], aspect="auto")
        ax[0].set_title("Desired Color")
        ax[0].axis("off")

        ax[1].imshow([[tuple(mixed_rgb)]], aspect="auto")
        ax[1].set_title("Mixed Color")
        ax[1].axis("off")

        st.pyplot(fig)
