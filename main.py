import streamlit as st
import google.generativeai as genai
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from sympy import symbols, pi, integrate, lambdify, sympify
import json

# Configuration - Replace with your API Key from aistudio.google.com
genai.configure(api_key="YOUR_API_KEY_HERE")
model = genai.GenerativeModel('gemini-2.0-flash')

def get_math_data(image):
    """Parses the image to extract the functions and rotation axis."""
    prompt = """
    Extract the volume of revolution problem from this image.
    Identify the outer function f(x), inner function g(x) (use 0 if none), 
    and the interval [a, b]. 
    Return ONLY a JSON object:
    {"f": "expression", "g": "expression", "a": start, "b": end, "method": "Disk or Washer"}
    """
    response = model.generate_content([prompt, image])
    clean_json = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_json)

def main():
    st.title("Calculus Volume Solver (Image Upload)")
    uploaded_file = st.file_uploader("Upload your math problem image", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Detected Question", width=300)
        
        if st.button("Solve with Steps"):
            data = get_math_data(img)
            x = symbols('x')
            f_sym = sympify(data['f'])
            g_sym = sympify(data['g'])
            a, b = float(data['a']), float(data['b'])

            # Header
            st.header(f"Method: {data['method']}")
            
            # Step 1: Setup
            st.subheader("Step 1: The Integral Setup")
            if data['method'] == "Disk":
                integrand = pi * f_sym**2
                st.latex(rf"V = \pi \int_{{{a}}}^{{{b}}} ({data['f']})^2 \, dx")
            else:
                integrand = pi * (f_sym**2 - g_sym**2)
                st.latex(rf"V = \pi \int_{{{a}}}^{{{b}}} \left[ ({data['f']})^2 - ({data['g']})^2 \right] \, dx")

            # Step 2: Anti-derivative
            st.subheader("Step 2: Integration")
            antideriv = integrate(integrand, x)
            st.write("The antiderivative is:")
            st.latex(rf"\pi \left[ {antideriv/pi} \right]_{{{a}}}^{{{b}}}")

            # Step 3: Final Answer
            result = integrate(integrand, (x, a, b))
            st.subheader("Step 3: Final Result")
            st.success(f"Volume = {result} units³ (≈ {result.evalf():.4f})")

            # Graphing
            st.subheader("Graph of the Region")
            x_vals = np.linspace(a, b, 100)
            f_num = lambdify(x, f_sym, 'numpy')(x_vals)
            g_num = lambdify(x, g_sym, 'numpy')(x_vals) if data['g'] != "0" else np.zeros_like(x_vals)
            
            fig, ax = plt.subplots()
            ax.plot(x_vals, f_num, label="f(x)")
            if data['g'] != "0": ax.plot(x_vals, g_num, label="g(x)")
            ax.fill_between(x_vals, f_num, g_num, color='skyblue', alpha=0.4)
            ax.set_title("Region to be Rotated")
            st.pyplot(fig)

if __name__ == "__main__":
    main()
