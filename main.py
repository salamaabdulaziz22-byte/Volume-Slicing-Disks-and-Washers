import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re

st.set_page_config(page_title="Universal Volume Solver", layout="wide")
st.title("🚀 Universal Calculus Volume Solver")

# Flexible Text Input
raw_input = st.text_area("Paste any volume problem here:", 
                         placeholder="e.g., y = 4 - x**2, y = 1, from x=0 to sqrt(3) about y-axis")

if st.button("Analyze & Solve"):
    try:
        # 1. Flexible Extraction Logic
        # Convert visual math to python math
        clean_q = raw_input.lower().replace('^', '**').replace('√', 'sqrt').replace('vx', 'sqrt(x)')
        
        # Extract equations: Looks for anything after an '='
        eq_found = re.findall(r'[yx]\s*=\s*([^, \n]+)', clean_q)
        # Extract all numbers (integers or decimals)
        nums = [float(n) for n in re.findall(r"[-+]?\d*\.\d+|\d+", clean_q)]
        
        if not eq_found:
            st.error("No clear equations found. Use format 'y = ...' or 'x = ...'")
        else:
            x, y = sp.symbols('x y')
            is_y_axis = 'y-axis' in clean_q or 'about y' in clean_q
            
            # Identify Method
            f_expr = sp.sympify(eq_found[0].strip())
            g_expr = sp.sympify(eq_found[1].strip()) if len(eq_found) > 1 else sp.sympify(0)
            
            method = "Washer Method" if g_expr != 0 else "Disk Method"
            st.success(f"✅ Method Identified: **{method}**")

            # Limits Detection - Handles cases with fewer than 2 numbers gracefully
            a = nums[0] if len(nums) >= 1 else 0
            b = nums[1] if len(nums) >= 2 else 1
            
            # Domain Logic: Rotate about Y-axis often requires solving for X
            var = y if is_y_axis else x
            if is_y_axis and 'x' in str(f_expr):
                # Attempt to solve y = f(x) for x
                solutions = sp.solve(sp.Eq(y, f_expr), x)
                f_expr = solutions[0] # Take the positive/primary branch
                if g_expr != 0:
                    g_expr = sp.solve(sp.Eq(y, g_expr), x)[0]

            # 2. Step-by-Step Solution
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📝 Mathematical Solution")
                integrand = sp.simplify(f_expr**2 - g_expr**2)
                st.write("**1. Setup the Integral:**")
                st.latex(rf"V = \pi \int_{{{a}}}^{{{b}}} ({sp.latex(integrand)}) \, d{var}")
                
                res = sp.integrate(integrand, (var, a, b))
                final_v = sp.pi * res
                st.write("**2. Final Result:**")
                st.latex(rf"V = {sp.latex(sp.simplify(final_v))} \approx {float(final_v.evalf()):.4f}")

            # 3. 3D Visualization
            with col2:
                st.subheader("📊 3D Visualization")
                fig = plt.figure()
                ax = fig.add_subplot(111, projection='3d')
                
                # Generate mesh
                u_vals = np.linspace(float(a), float(b), 40)
                v_vals = np.linspace(0, 2*np.pi, 40)
                U, V = np.meshgrid(u_vals, v_vals)
                
                # Convert symbolic to numeric
                f_num = sp.lambdify(var, f_expr, 'numpy')(U)
                
                if is_y_axis:
                    X, Y, Z = f_num*np.cos(V), U, f_num*np.sin(V)
                else:
                    X, Y, Z = U, f_num*np.cos(V), f_num*np.sin(V)
                
                ax.plot_surface(X, Y, Z, alpha=0.8, cmap='viridis', edgecolor='none')
                st.pyplot(fig)

    except Exception as e:
        st.error(f"Analysis Error: {e}. Tip: Use 'x**2' for powers.")
