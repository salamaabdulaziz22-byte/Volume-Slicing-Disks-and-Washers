import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, integrate, pi, lambdify, sympify

# Page Config
st.set_page_config(page_title="Volume Solver", page_icon="📐")

st.title("📐 Solid of Revolution Solver")
st.write("Calculate the volume of a solid using the **Disk** or **Washer** method.")

# Sidebar for Inputs
st.sidebar.header("Input Parameters")
f_input = st.sidebar.text_input("Outer Function f(x)", "sqrt(x)")
g_input = st.sidebar.text_input("Inner Function g(x) (0 for Disk)", "0")
a_val = st.sidebar.number_input("Lower Limit (a)", value=0.0)
b_val = st.sidebar.number_input("Upper Limit (b)", value=4.0)

if st.button("Solve & Generate Steps"):
    try:
        x = symbols('x')
        f_expr = sympify(f_input)
        g_expr = sympify(g_input)

        # 1. Logical Method Identification
        if g_expr == 0:
            method = "Disk Method"
            formula_latex = r"V = \pi \int_{a}^{b} [f(x)]^2 dx"
            integrand = f_expr**2
        else:
            method = "Washer Method"
            formula_latex = r"V = \pi \int_{a}^{b} ([R(x)]^2 - [r(x)]^2) dx"
            integrand = f_expr**2 - g_expr**2

        st.subheader(f"Method Identified: {method}")
        
        # 2. Step-by-Step Breakdown
        st.markdown("### Step-by-Step Solution")
        
        st.write("**1. Identify the Formula:**")
        st.latex(formula_latex)

        st.write("**2. Set up the Integral:**")
        st.latex(f"V = \pi \int_{{{a_val}}}^{{{b_val}}} ({integrand}) dx")

        # Calculations
        antiderivative = integrate(integrand, x)
        result_exact = integrate(integrand, (x, a_val, b_val)) * pi
        result_decimal = float(result_exact.evalf())

        st.write("**3. Find the Antiderivative:**")
        st.latex(f"\pi \left[ {antiderivative} \\right]_{{{a_val}}}^{{{b_val}}}")

        st.success(f"**Final Volume:** {result_exact} ≈ {result_decimal:.4f} cubic units")

        # 3. Graphing
        st.markdown("### Visual Representation")
        x_range = np.linspace(float(a_val), float(b_val), 100)
        f_func = lambdify(x, f_expr, 'numpy')
        g_func = lambdify(x, g_expr, 'numpy')

        fig, ax = plt.subplots()
        ax.plot(x_range, f_func(x_range), 'r', label='Outer R(x)')
        if method == "Washer Method":
            ax.plot(x_range, g_func(x_range), 'b', label='Inner r(x)')
        
        ax.fill_between(x_range, f_func(x_range), g_func(x_range), color='gray', alpha=0.3)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.legend()
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error: {e}. Please ensure you use '*' for multiplication (e.g., 2*x).")
