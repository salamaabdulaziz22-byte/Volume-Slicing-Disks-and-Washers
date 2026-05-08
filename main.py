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

# User Input - Starts empty for you to paste any question
raw_input = st.text_area("Paste your calculus problem here:", value="", height=150, 
                         placeholder="e.g., y = sqrt(x), from x = 0 to 4 about x-axis")

if st.button("Analyze & Solve"):
    if not raw_input.strip():
        st.warning("Please paste a question first.")
    else:
        try:
            # 1. Advanced Extraction Logic
            clean_q = raw_input.lower().replace('^', '**').replace('√', 'sqrt').replace('vx', 'sqrt(x)')
            
            # Find all equations like y=... or x=...
            equations = re.findall(r'([xy])\s*=\s*([0-9x\s\+\-\*\^/\(\)sqrt]+)', clean_q)
            # Find all numbers for limits
            nums = re.findall(r'(\d+\.?\d*)', clean_q)
            
            x, y = sp.symbols('x y')
            is_y_axis = 'y-axis' in clean_q
            
            # Identify functions
            f_expr = sp.sympify(equations[0][1].strip())
            g_expr = sp.sympify(equations[1][1].strip()) if len(equations) > 1 else sp.sympify(0)
            
            # Automatic Limit Detection
            if len(nums) >= 2:
                a, b = float(nums[0]), float(nums[1])
            else:
                a, b = 0, 1 # Default if not found
            
            # Handle y-axis rotation conversion (If needed)
            if is_y_axis and 'x' in str(f_expr):
                # Solving y = f(x) for x to get x = g(y)
                f_expr = sp.solve(sp.Eq(y, f_expr), x)[0]
                var = y
            else:
                var = x

            # 2. Mathematical Steps
            st.subheader("📝 Mathematical Solution")
            col1, col2 = st.columns(2)
            
            with col1:
                integrand = sp.simplify(f_expr**2 - g_expr**2)
                st.write("**1. Setup the Integral:**")
                st.latex(rf"V = \pi \int_{{{a}}}^{{{b}}} ({sp.latex(integrand)}) \, d{var}")
                
                antideriv = sp.integrate(integrand, var)
                st.write("**2. Anti-derivative:**")
                st.latex(rf"V = \pi \left[ {sp.latex(antideriv)} \right]_{{{a}}}^{{{b}}}")
                
                final_val = sp.pi * (antideriv.subs(var, b) - antideriv.subs(var, a))
                st.write("**3. Final Result:**")
                st.latex(rf"V = {sp.latex(sp.simplify(final_val))} \approx {float(final_val.evalf()):.4f}")

            # 3. Dynamic 3D Visualization
            with col2:
                st.subheader("📊 3D Model")
                fig = plt.figure(figsize=(8, 6))
                ax = fig.add_subplot(111, projection='3d')
                
                v_vals = np.linspace(float(a), float(b), 50)
                theta = np.linspace(0, 2*np.pi, 50)
                V_mesh, THETA_mesh = np.meshgrid(v_vals, theta)
                
                r_num = sp.lambdify(var, f_expr, 'numpy')(V_mesh)
                
                if is_y_axis:
                    X_p, Y_p, Z_p = r_num*np.cos(THETA_mesh), V_mesh, r_num*np.sin(THETA_mesh)
                else:
                    X_p, Y_p, Z_p = V_mesh, r_num*np.cos(THETA_mesh), r_num*np.sin(THETA_mesh)
                
                ax.plot_surface(X_p, Y_p, Z_p, color='cyan', alpha=0.6, edgecolor='k', lw=0.1)
                st.pyplot(fig)
                
        except Exception as e:
            st.error(f"Error: {e}. Please try writing the equations clearly (e.g., y = 4 - x**2).")
