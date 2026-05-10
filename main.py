import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, integrate, pi, lambdify, sympify

# Page Config
st.set_page_config(page_title="Universal Volume Solver", page_icon="📐")

st.title("📐 Universal Solid of Revolution Solver")
st.write("Calculate volume by revolving around the **X-axis** or **Y-axis**.")

# Sidebar for Inputs
st.sidebar.header("Input Parameters")
axis_choice = st.sidebar.selectbox("Axis of Revolution", ["x-axis", "y-axis"])
variable = 'x' if axis_choice == "x-axis" else 'y'

f_input = st.sidebar.text_input(f"Outer Function f({variable})", "sqrt(x)" if variable == 'x' else "y**2")
g_input = st.sidebar.text_input(f"Inner Function g({variable}) (0 for Disk)", "0")
a_val = st.sidebar.number_input(f"Lower Limit ({variable} = a)", value=0.0)
b_val = st.sidebar.number_input(f"Upper Limit ({variable} = b)", value=0.0)

if st.button("Solve & Generate Steps"):
    try:
        v_sym = symbols(variable)
        f_expr = sympify(f_input)
        g_expr = sympify(g_input)

        # 1. Method Identification
        method = "Disk Method" if g_expr == 0 else "Washer Method"
        integrand = f_expr**2 - g_expr**2
        
        st.subheader(f"Method: {method} (About {axis_choice})")

        # 2. Step-by-Step Breakdown
        st.markdown("### Step-by-Step Solution")
        
        formula = r"V = \pi \int_{a}^{b} [R(x)]^2 dx" if variable == 'x' else r"V = \pi \int_{c}^{d} [R(y)]^2 dy"
        if method == "Washer Method":
            formula = r"V = \pi \int_{a}^{b} (R^2 - r^2) dx" if variable == 'x' else r"V = \pi \int_{c}^{d} (R^2 - r^2) dy"

        st.write("**1. Formula:**")
        st.latex(formula)

        st.write("**2. Set up the Integral:**")
        st.latex(f"V = \pi \int_{{{a_val}}}^{{{b_val}}} ({integrand}) d{variable}")

        # Calculations
        antiderivative = integrate(integrand, v_sym)
        result_exact = integrate(integrand, (v_sym, a_val, b_val)) * pi
        result_decimal = float(result_exact.evalf())

        st.write("**3. Integration Result:**")
        st.latex(f"\pi \left[ {antiderivative} \\right]_{{{a_val}}}^{{{b_val}}}")

        st.success(f"**Final Volume:** {result_exact} ≈ {result_decimal:.4f} cubic units")

        # 3. Visual Representation
        st.markdown("### Visual Representation (2D Area)")
        vals = np.linspace(float(a_val), float(b_val), 100)
        f_func = lambdify(v_sym, f_expr, 'numpy')
        g_func = lambdify(v_sym, g_expr, 'numpy')

        fig, ax = plt.subplots()
        if variable == 'x':
            ax.plot(vals, f_func(vals), 'r', label='f(x)')
            ax.fill_between(vals, f_func(vals), g_func(vals), color='gray', alpha=0.3)
            ax.set_xlabel('x')
            ax.set_ylabel('y')
        else:
            # For y-axis, we plot x as a function of y
            ax.plot(f_func(vals), vals, 'r', label='f(y)')
            ax.fill_betweenx(vals, f_func(vals), g_func(vals), color='gray', alpha=0.3)
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            
        ax.axhline(0, color='black', lw=0.5)
        ax.axvline(0, color='black', lw=0.5)
        ax.legend()
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error: {e}. Check your function syntax.")
