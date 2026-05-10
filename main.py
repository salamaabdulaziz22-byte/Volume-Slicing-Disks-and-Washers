import streamlit as st
import google.generativeai as genai
import matplotlib.pyplot as plt
import numpy as np
from sympy import symbols, pi, integrate, lambdify, sympify
from PIL import Image
import json

# 1. API Configuration (Get your key at aistudio.google.com)
genai.configure(api_key="YOUR_API_KEY_HERE")
model = genai.GenerativeModel('gemini-2.0-flash')

def analyze_image_with_ai(image):
    """Uses AI to 'read' the screenshot and extract math data."""
    prompt = """
    Look at this math problem regarding the volume of a solid of revolution.
    Identify:
    1. The outer function f(x)
    2. The inner function g(x) (set to 0 if it's a Disk problem)
    3. The lower bound 'a' and upper bound 'b'.
    
    Return ONLY a JSON object:
    {"f": "function_text", "g": "function_text", "a": value, "b": value, "method": "Disk or Washer"}
    Use python math syntax (e.g., x**2 for x²).
    """
    response = model.generate_content([prompt, image])
    # Clean the response text to ensure it's valid JSON
    clean_text = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_text)

def main():
    st.set_page_config(page_title="Math Vision Solver", layout="wide")
    st.title("📸 Image-to-Volume Solver")
    st.write("Upload a screenshot of a problem from your PDF or PPT.")

    uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Question", width=400)

        if st.button("Extract and Solve"):
            try:
                with st.spinner("AI is reading the problem..."):
                    data = analyze_image_with_ai(img)
                
                # Setup math variables
                x = symbols('x')
                f_sym = sympify(data['f'])
                g_sym = sympify(data['g'])
                a, b = float(data['a']), float(data['b'])

                # Display Results
                st.header(f"Detected Method: {data['method']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Step-by-Step Solution")
                    st.write(f"**Interval:** $[{a}, {b}]$")
                    
                    # Setup Integral
                    integrand = pi * (f_sym**2 - g_sym**2)
                    st.latex(rf"V = \pi \int_{{{a}}}^{{{b}}} \left( ({data['f']})^2 - ({data['g']})^2 \right) dx")
                    
                    # Integration
                    antiderivative = integrate(integrand, x)
                    result = integrate(integrand, (x, a, b))
                    
                    st.write("**Antiderivative:**")
                    st.latex(rf"\pi \left[ {antiderivative/pi} \right]")
                    
                    st.success(f"**Final Volume:** {result} or ≈ {result.evalf():.4f}")

                with col2:
                    st.subheader("Graph of the Region")
                    x_plot = np.linspace(a, b, 100)
                    f_func = lambdify(x, f_sym, 'numpy')
                    g_func = lambdify(x, g_sym, 'numpy')

                    fig, ax = plt.subplots()
                    ax.plot(x_plot, f_func(x_plot), label=f"f(x)")
                    if data['g'] != "0":
                        ax.plot(x_plot, g_func(x_plot), label=f"g(x)")
                    
                    ax.fill_between(x_plot, f_func(x_plot), g_func(x_plot), color='orange', alpha=0.3)
                    ax.set_title("Area to Rotate")
                    ax.grid(True, linestyle='--', alpha=0.6)
                    st.pyplot(fig)

            except Exception as e:
                st.error(f"Could not solve. Ensure the image is clear. Error: {e}")

if __name__ == "__main__":
    main()
