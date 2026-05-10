import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, pi, integrate, lambdify, sympify

def main():
    st.set_page_config(page_title="Math Solver", layout="centered")
    st.title("📐 Volume of Revolution Solver")
    st.write("Enter the functions from your slides (e.g., `x` and `x**2`).")

    # Input Section
    with st.expander("📝 Enter Problem Details", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            f_in = st.text_input("Outer Function f(x)", value="x")
            g_in = st.text_input("Inner Function g(x) (0 for Disk)", value="x**2")
        with col2:
            a_val = st.number_input("Lower Bound (a)", value=0.0)
            b_val = st.number_input("Upper Bound (b)", value=1.0)

    if st.button("🚀 Solve and Graph"):
        try:
            # Setup Symbols
            x = symbols('x')
            f = sympify(f_in)
            g = sympify(g_in)
            
            # Determine Method
            is_washer = g != 0
            method_name = "Washer Method" if is_washer else "Disk Method"
            
            # Calculate Volume
            # V = π ∫ (R² - r²) dx
            integrand = pi * (f**2 - g**2)
            antideriv = integrate(integrand, x)
            volume = integrate(integrand, (x, a_val, b_val))

            # --- Display Steps ---
            st.header(f"Method: {method_name}")
            
            st.subheader("Step 1: Setup")
            if is_washer:
                st.latex(rf"V = \pi \int_{{{a_val}}}^{{{b_val}}} \left( [{f_in}]^2 - [{g_in}]^2 \right) dx")
            else:
                st.latex(rf"V = \pi \int_{{{a_val}}}^{{{b_val}}} [{f_in}]^2 dx")

            st.subheader("Step 2: Integration")
            st.write("Find the antiderivative:")
            st.latex(rf"\pi \left[ {antideriv/pi} \right]_{{{a_val}}}^{{{b_val}}}")

            st.subheader("Step 3: Final Answer")
            st.success(f"Exact Volume: {volume}")
            st.write(f"Decimal Value: **{float(volume.evalf()):.4f} cubic units**")

            # --- Graphing ---
            st.subheader("Visualization")
            x_pts = np.linspace(float(a_val), float(b_val), 100)
            f_func = lambdify(x, f, 'numpy')(x_pts)
            g_func = lambdify(x, g, 'numpy')(x_pts)

            fig, ax = plt.subplots()
            ax.plot(x_pts, f_func, 'b', label=f'f(x)={f_in}')
            if is_washer:
                ax.plot(x_pts, g_func, 'r', label=f'g(x)={g_in}')
            
            ax.fill_between(x_pts, f_func, g_func, color='skyblue', alpha=0.4)
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.legend()
            ax.grid(True, linestyle='--', alpha=0.6)
            st.pyplot(fig)

        except Exception as e:
            st.error(f"Error in math: {e}. Check if you used 'x**2' for powers.")

if __name__ == "__main__":
    main()
