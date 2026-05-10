import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from sympy import symbols, pi, integrate, lambdify, sympify
import easyocr
from PIL import Image

# Initialize the OCR reader (This reads the text from your screenshot)
reader = easyocr.Reader(['en'])

def solve_volume(f_text, g_text, a, b):
    x = symbols('x')
    f = sympify(f_text)
    g = sympify(g_text)
    
    # Check if Disk or Washer
    method = "Disk" if g == 0 else "Washer"
    
    # Formula setup
    integrand = pi * (f**2 - g**2)
    antiderivative = integrate(integrand, x)
    result = integrate(integrand, (x, a, b))
    
    return method, f, g, antiderivative, result

def main():
    st.set_page_config(page_title="Math Homework Solver", layout="wide")
    st.title("Step-by-Step Volume Solver")
    st.write("Upload your problem image. I will try to read the functions for you.")

    uploaded_file = st.file_uploader("Upload Problem Image", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, width=400)
        
        # 1. READ TEXT FROM IMAGE
        with st.spinner("Reading math from image..."):
            img_np = np.array(img)
            text_results = reader.readtext(img_np, detail=0)
            detected_text = " ".join(text_results)
            st.info(f"Detected Text: {detected_text}")

        # 2. MANUAL OVERRIDE (In case OCR makes a mistake)
        st.subheader("Confirm Details")
        col1, col2, col3, col4 = st.columns(4)
        with col1: f_in = st.text_input("Outer Function f(x)", "x")
        with col2: g_in = st.text_input("Inner Function g(x)", "x**2")
        with col3: a_in = st.number_input("Start Bound (a)", value=0.0)
        with col4: b_in = st.number_input("End Bound (b)", value=1.0)

        if st.button("Calculate Everything"):
            try:
                method, f, g, anti, res = solve_volume(f_in, g_in, a_in, b_in)
                
                st.divider()
                st.header(f"Method Identified: {method}")
                
                # Step 1: Integral Setup
                st.write("### Step 1: Setup the Integral")
                if method == "Disk":
                    st.latex(rf"V = \pi \int_{{{a_in}}}^{{{b_in}}} ({f_in})^2 dx")
                else:
                    st.latex(rf"V = \pi \int_{{{a_in}}}^{{{b_in}}} [({f_in})^2 - ({g_in})^2] dx")

                # Step 2: Show Anti-derivative
                st.write("### Step 2: Find the Antiderivative")
                st.latex(rf"\pi \left[ {anti/pi} \right]_{{{a_in}}}^{{{b_in}}}")

                # Step 3: Final Answer
                st.write("### Step 3: Final Calculation")
                st.success(f"Volume = {res} ≈ {float(res.evalf()):.4f}")

                # Graphing
                st.write("### Visualization")
                t = np.linspace(float(a_in), float(b_in), 100)
                f_func = lambdify(symbols('x'), f, 'numpy')(t)
                g_func = lambdify(symbols('x'), g, 'numpy')(t)
                
                fig, ax = plt.subplots()
                ax.plot(t, f_func, label='f(x)')
                if method == "Washer":
                    ax.plot(t, g_func, label='g(x)')
                ax.fill_between(t, f_func, g_func, color='cyan', alpha=0.3)
                ax.set_title(f"{method} Method Region")
                st.pyplot(fig)

            except Exception as e:
                st.error(f"Error processing math: {e}")

if __name__ == "__main__":
    main()
