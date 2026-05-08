import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re

# Page Configuration
st.set_page_config(page_title="Universal Math Solver", layout="wide")
st.title("Smart Calculus Volume Solver")
st.markdown("---")

# User Input
raw_input = st.text_area("Paste your calculus problem here:", value="", height=150, 
                         placeholder="e.g., y = sqrt(x), from x = 0 to 4 about x-axis")

if st.button("Analyze & Solve"):
    if not raw_input.strip():
        st.warning("Please paste a question first.")
    else:
        try:
            # 1. Processing Input
            clean_q = raw_input.lower().replace('^', '**').replace('√', 'sqrt').replace('vx', 'sqrt(x)')
            equations = re.findall(r'([xy])\s*=\s*([0-9x\s\+\-\*\^/\(\)sqrt]+)', clean_q)
            nums = re.findall(r'(\d+\.?\d*)', clean_q)
            
            x, y = sp.symbols('x y')
            is_y_axis = 'y-axis' in clean_q
            
            # Identify Method (Disk vs Washer)
            if len(equations) > 1:
                method_type = "Washer Method"
                f_expr = sp.sympify(equations[0][1].strip())
                g_expr = sp.sympify(equations[1][1].strip())
            else:
                method_type = "Disk Method"
                f_expr = sp.sympify(equations[0][1].strip())
                g_expr = sp.sympify(0)
            
            st.success(f"✅ Identified Method: **{method_type}**")

            # Limits Detection
            if len(nums) >= 2:
                a, b = float(nums[0]), float(nums[1])
            else:
                a, b = 0, 1 
            
            if is_y_axis and 'x' in str(f_expr):
                f_expr = sp.solve(sp.Eq(y, f_expr), x)[0]
                if g_expr != 0: g_expr = sp.solve(sp.Eq(y, g_expr), x)[0]
                var = y
            else:
                var = x

            # 2. Mathematical Steps
            st.subheader("📝 Mathematical Solution")
            col1, col2 = st.columns(2)
            
            with col1:
                integrand = sp.simplify(f_expr**2 - g_expr**2)
                st.write(f"**1. Setup the Integral ({method_type}):**")
                st.latex(rf"V = \pi \int_{{{a}}}^{{{b}}} [({sp.latex(f_expr)})^2 - ({sp.latex(g_expr)})^2] \, d{var}")
                
                antideriv = sp.integrate(integrand, var)
                st.write("**2. Anti-derivative:**")
                st.latex(rf"V = \pi \left[ {sp.latex(antideriv)} \right]_{{{a}}}^{{{b}}}")
                
                final_val = sp.pi * (antideriv.subs(var, b) - antideriv.subs(var, a))
                st.write("**3. Final Result:**")
                st.latex(rf"V = {sp.latex(sp.simplify(final_val))} \approx {float(final_val.evalf()):.4f}")

            # 3. 3D Visualization (Fixed Line 88 Logic)
            with col2:
                st.subheader("📊 3D Model")
                fig = plt.figure(figsize=(8, 6))
                ax = fig.add_subplot(111, projection='3d')
                
                v_vals = np.linspace(float(a), float(b), 50)
                theta = np.linspace(0, 2*np.pi, 50)
                V_mesh, THETA_mesh = np.meshgrid(v_vals, theta)
                
                r_num = sp.lambdify(var, f_expr, 'numpy')(V_mesh)
                
                # Correct Coordinate Mapping for Revolution
                if is_y_axis:
                    X_p = r_num * np.cos(THETA_mesh)
                    Y_p = V_mesh
                    Z_p = r_num * np.sin(THETA_mesh)
                else:
                    X_p = V_mesh
                    Y_p = r_num * np.cos(THETA_mesh)
                    Z_p = r_num * np.sin(THETA_mesh)
                
                ax.plot_surface(X_p, Y_p, Z_p, color='cyan', alpha=0.6, edgecolor='k', lw=0.1)
                st.pyplot(fig)
                
        except Exception as e:
            st.error(f"Error: {e}. Check your equations.")
