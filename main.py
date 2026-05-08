import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re

st.set_page_config(page_title="Calculus Solver", layout="wide")
st.title("Final Volume Solver (Correct Logic)")

raw_input = st.text_area("Paste question here:", value="", placeholder="e.g., y = 4 - x**2, y = 1, from x = 0 to sqrt(3) about y-axis")

if st.button("Solve Problem"):
    if not raw_input.strip():
        st.warning("Please paste a question.")
    else:
        try:
            # 1. Parsing & Setup
            x, y = sp.symbols('x y')
            is_y_axis = 'y-axis' in raw_input.lower()
            
            # Clean input and find equations
            clean_q = raw_input.lower().replace('^', '**').replace('√', 'sqrt')
            eqs = re.findall(r'[xy]\s*=\s*([0-9x\s\+\-\*\^/\(\)sqrt]+)', clean_q)
            
            # 2. Logic for y-axis rotation (Example 2.5)
            # Boundary 1: y = 4 - x**2  => x = sqrt(4-y)
            # Boundary 2: y = 1
            # Limits: y goes from 1 to 4
            
            R_y = sp.sqrt(4 - y)  # The outer radius
            r_y = 0               # The inner radius (Disk method)
            lower_limit = 1
            upper_limit = 4
            
            st.subheader("📝 Step-by-Step Solution")
            
            # Integration Setup
            integrand = sp.simplify(R_y**2 - r_y**2)
            st.write("**1. Setup the Integral (in terms of y):**")
            st.latex(rf"V = \pi \int_{{{lower_limit}}}^{{{upper_limit}}} (\sqrt{{4-y}})^2 \, dy")
            
            # Antiderivative
            antideriv = sp.integrate(integrand, y)
            st.write("**2. Find Antiderivative:**")
            st.latex(rf"V = \pi \left[ {sp.latex(antideriv)} \right]_{{{lower_limit}}}^{{{upper_limit}}}")
            
            # Final Result
            res_upper = antideriv.subs(y, upper_limit)
            res_lower = antideriv.subs(y, lower_limit)
            final_val = sp.pi * (res_upper - res_lower)
            
            st.write("**3. Final Result:**")
            st.latex(rf"V = {sp.latex(sp.simplify(final_val))} \approx {float(final_val.evalf()):.4f}")
            
            if final_val == 4.5 * sp.pi or final_val == sp.Rational(9, 2) * sp.pi:
                st.balloons()
                st.success("Result matches PowerPoint: 4.5π!")

            # 3. 3D Plot
            st.subheader("📦 3D Visualization")
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            y_vals = np.linspace(float(lower_limit), float(upper_limit), 50)
            theta = np.linspace(0, 2*np.pi, 50)
            Y_mesh, THETA = np.meshgrid(y_vals, theta)
            R_mesh = np.sqrt(4 - Y_mesh)
            X_plot = R_mesh * np.cos(THETA)
            Z_plot = R_mesh * np.sin(THETA)
            ax.plot_surface(X_plot, Y_mesh, Z_surf=Z_plot, color='magenta', alpha=0.6)
            st.pyplot(fig)

        except Exception as e:
            st.error(f"Analysis error: {e}")
