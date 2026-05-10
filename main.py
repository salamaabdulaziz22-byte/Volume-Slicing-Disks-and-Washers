import streamlit as st
import google.generativeai as genai
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from sympy import symbols, pi, integrate, lambdify, sympify
import json
import re

# 1. API SETUP
# Get your free API key at: https://aistudio.google.com/
genai.configure(api_key="YOUR_API_KEY_HERE")
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_math_from_image(image):
    """
    Sends the image to Gemini to extract functions and bounds.
    """
    prompt = """
    Analyze this calculus problem about the volume of a solid of revolution.
    Identify:
    1. The outer function f(x).
    2. The inner function g(x) (use '0' if it is a Disk problem).
    3. The lower bound 'a' and upper bound 'b'.
    
    Return ONLY a JSON object like this:
    {"f": "x**2", "g": "0", "a": 0, "b": 2, "method": "Disk"}
    Use Python math syntax (e.g., x**2 for x squared, sqrt(x) for square root).
    """
    response = model.generate_content([prompt, image])
    # Clean the response to ensure it's valid JSON
    text = response.text
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    else:
        raise ValueError("Could not read the math from the image.")

def main():
    st.set_page_config(page_title="Volume Solver AI", layout="wide")
    st.title("📸 Image-to-Volume Calculus Solver")
    st.write("Upload a screenshot of a problem from your school files (Disks or Washers).")

    uploaded_file = st.file_uploader("Choose a math problem image...", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        
        # Display the uploaded image
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(img, caption="Your Uploaded Question", use_container_width=True)

        if st.button("✨ Solve Question"):
            try:
                with st.spinner("AI is reading the problem and calculating..."):
                    # Step 1: AI Image Recognition
                    data = extract_math_from_image(img)
                    
                    # Step 2: Math Setup
                    x = symbols('x')
                    f_sym = sympify(data['f'])
                    g_sym = sympify(data['g'])
                    a = float(data['a'])
                    b = float(data['b'])
                    
                    # Step 3: Integration Logic
                    # V = π ∫ [f(x)^2 - g(x)^2] dx
                    integrand = pi * (f_sym**2 - g_sym**2)
                    antiderivative = integrate(integrand, x)
                    volume_exact = integrate(integrand, (x, a, b))

                with col2:
                    st.header(f"Method: {data['method']}")
                    st.info(f"**Detected Functions:** f(x)={data['f']}, g(x)={data['g']} from {a} to {b}")
                    
                    # Show Steps in LaTeX
                    st.subheader("Solution Steps:")
                    st.write("**1. Setup the Integral:**")
                    if data['g'] == "0":
                        st.latex(rf"V = \pi \int_{{{a}}}^{{{b}}} ({data['f']})^2 \, dx")
                    else:
                        st.latex(rf"V = \pi \int_{{{a}}}^{{{b}}} \left[ ({data['f']})^2 - ({data['g']})^2 \right] \, dx")

                    st.write("**2. Find the Antiderivative:**")
                    # We divide by pi in the display to keep the pi symbol outside the brackets
                    st.latex(rf"V = \pi \left[ {antiderivative/pi} \right]_{{{a}}}^{{{b}}}")

                    st.write("**3. Final Result:**")
                    st.success(f"Volume = {volume_exact} units³")
                    st.write(f"Decimal Approximation: **{float(volume_exact.evalf()):.4f}**")

                    # Step 4: Generate the Graph
                    st.subheader("2D Region Visualization")
                    x_vals = np.linspace(a, b, 100)
                    f_num = lambdify(x, f_sym, 'numpy')(x_vals)
                    g_num = lambdify(x, g_sym, 'numpy')(x_vals) if data['g'] != "0" else np.zeros_like(x_vals)

                    fig, ax = plt.subplots()
                    ax.plot(x_vals, f_num, label=f"f(x)={data['f']}", color="blue")
                    if data['g'] != "0":
                        ax.plot(x_vals, g_num, label=f"g(x)={data['g']}", color="red")
                    
                    ax.fill_between(x_vals, f_num, g_num, color='gray', alpha=0.3, label="Area to rotate")
                    ax.axhline(0, color='black', linewidth=1)
                    ax.legend()
                    st.pyplot(fig)

            except Exception as e:
                st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
