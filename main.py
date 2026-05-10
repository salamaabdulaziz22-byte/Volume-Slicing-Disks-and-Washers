import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, pi, integrate, lambdify, sympify, solve

def main():
    st.title("Volume Solver: Disks & Washers")
    st.write("Enter your functions and bounds to calculate the volume of a solid of revolution.")

    # User Inputs
    col1, col2 = st.columns(2)
    with col1:
        f_input = st.text_input("Enter f(x) (Outer Radius)", "x**2")
        g_input = st.text_input("Enter g(x) (Inner Radius - leave 0 for Disk)", "0")
    with col2:
        a = st.number_input("Lower Bound (a)", value=0.0)
        b = st.number_input("Upper Bound (b)", value=1.0)

    if st.button("Solve"):
        try:
            x = symbols('x')
            f = sympify(f_input)
            g = sympify(g_input)

            # Determine Method [cite: 1, 29]
            method = "Disk Method" if g == 0 else "Washer Method"
            st.subheader(f"Method: {method}")

            # Formula and Setup [cite: 10, 294]
            if g == 0:
                integrand = pi * f**2
                formula_latex = r"V = \pi \int_{a}^{b} [f(x)]^2 dx"
            else:
                integrand = pi * (f**2 - g**2)
                formula_latex = r"V = \pi \int_{a}^{b} ([f(x)]^2 - [g(x)]^2) dx"

            st.latex(formula_latex)

            # Step-by-Step Solving 
            st.write("**Step 1: Setup the Integral**")
            st.latex(rf"V = \pi \int_{{{a}}}^{{{b}}} ({integrand/pi}) dx")

            antiderivative = integrate(integrand, x)
            result = integrate(integrand, (x, a, b))

            st.write("**Step 2: Find the Antiderivative**")
            st.latex(rf"\pi \left[ {antiderivative/pi} \right]")

            st.write("**Step 3: Final Result**")
            st.success(f"The Volume is: {result.evalf():.4f} cubic units")
            st.latex(rf"V = {result} \approx {result.evalf():.4f}")

            # Graphing the Region [cite: 9]
            st.write("**Visualising the Region:**")
            x_vals = np.linspace(float(a), float(b), 100)
            f_num = lambdify(x, f, 'numpy')(x_vals)
            g_num = lambdify(x, g, 'numpy')(x_vals) if g != 0 else np.zeros_like(x_vals)

            fig, ax = plt.subplots()
            ax.plot(x_vals, f_num, label=f'f(x)={f_input}', color='blue')
            if g != 0:
                ax.plot(x_vals, g_num, label=f'g(x)={g_input}', color='red')
            
            ax.fill_between(x_vals, f_num, g_num, color='gray', alpha=0.3, label='Area to Rotate')
            ax.axhline(0, color='black', linewidth=1)
            ax.legend()
            st.pyplot(fig)

        except Exception as e:
            st.error(f"Error: {e}. Please ensure your math syntax is correct (e.g., use 'x**2' for x²).")

if __name__ == "__main__":
    main()
