import streamlit as st
import google.generativeai as genai
import matplotlib.pyplot as plt
import numpy as np
from sympy import symbols, pi, integrate, lambdify, sympify, solve
import re

# 1. Setup API Key (Get one for free at aistudio.google.com)
GOOGLE_API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def parse_question_with_ai(question_text):
    """Uses AI to extract f(x), g(x), and bounds from raw text."""
    prompt = f"""
    Extract the mathematical components for a volume of revolution problem:
    Question: "{question_text}"
    Return ONLY a python dictionary like this:
    {{"f": "outer_function", "g": "inner_function_or_0", "a": start_bound, "b": end_bound}}
    Use python syntax (e.g., x**2, sqrt(x)).
    """
    response = model.generate_content(prompt)
    return eval(response.text.strip())

def main():
    st.title("Smart Volume Solver")
    st.write("Paste your full question below (e.g., 'Find the volume of the region bounded by y=x and y=x^2 rotated around the x-axis from 0 to 1')")

    user_query = st.text_area("Enter the question text:")

    if st.button("Solve Everything"):
        if not user_query:
            st.warning("Please enter a question first.")
            return

        with st.spinner("Analyzing question..."):
            data = parse_question_with_ai(user_query)
            f_str, g_str = data['f'], data['g']
            a, b = float(data['a']), float(data['b'])

        # Logic for Disk vs Washer
        x = symbols('x')
        f_sym = sympify(f_str)
        g_sym = sympify(g_str)
        method = "Washer Method" if g_sym != 0 else "Disk Method"

        # --- Display Results ---
        st.header(f"Detected Method: {method}")
        st.info(f"Functions identified: f(x) = {f_str}, g(x) = {g_str} on interval [{a}, {b}]")

        # Step 1: Integral Setup
        st.subheader("Step 1: Setup")
        integrand = pi * (f_sym**2 - g_sym**2)
        st.latex(rf"V = \pi \int_{{{a}}}^{{{b}}} \left( ({f_str})^2 - ({g_str})^2 \right) dx")

        # Step 2: Integration
        st.subheader("Step 2: Integration Steps")
        antiderivative = integrate(integrand, x)
        result = integrate(integrand, (x, a, b))
        
        st.write("The antiderivative is:")
        st.latex(rf"\pi \left[ {antiderivative/pi} \right]")

        # Step 3: Result
        st.subheader("Step 3: Final Answer")
        st.success(rf"Final Volume: {result} \approx {result.evalf():.4f}")

        # --- Graphing ---
        st.subheader("Visual Representation")
        x_plot = np.linspace(a, b, 100)
        f_func = lambdify(x, f_sym, 'numpy')
        g_func = lambdify(x, g_sym, 'numpy')

        fig, ax = plt.subplots()
        ax.plot(x_plot, f_func(x_plot), label=f"f(x)={f_str}")
        if g_sym != 0:
            ax.plot(x_plot, g_func(x_plot), label=f"g(x)={g_str}")
        
        ax.fill_between(x_plot, f_func(x_plot), g_func(x_plot), color='cyan', alpha=0.3)
        ax.set_title("Region to be Rotated")
        ax.legend()
        st.pyplot(fig)

if __name__ == "__main__":
    main()
