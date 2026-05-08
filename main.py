import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re

# Page Configuration
st.set_page_config(page_title="Math Solver", layout="wide")
st.title("Dynamic Volume of Revolution Solver")
st.markdown("---")

# User Input Section - Completely empty start
raw_input = st.text_area("Paste your textbook question here:", value="", height=150)

if st.button("Solve & Generate Full Solution"):
    if not raw_input.strip():
        st.warning("The input is empty. Please paste your question first.")
    else:
        try:
            # 1. Smart Text Cleaning
            # Handles common copy-paste issues (x2 -> x**2, Vx -> sqrt(x), etc.)
            clean_q = raw_input.lower().replace('^', '**').replace('√', 'sqrt').replace('vx', 'sqrt(x)')
            clean_q = re.sub(r'([xy])(\d)', r'\1**\2', clean_q)
            
            # 2. Extracting Math Components
            equations = re.findall(r'[xy]\s*=\s*([0-9x\s\+\-\*\^/\(\)sqrt]+)', clean_q)
            nums = re.findall(r'(\d+\.?\d*)', clean_q)
            
            if len(equations) >= 1:
                x, y = sp.symbols('x y')
                is_y_axis = 'y-axis' in clean_q
                var = y if is_y_axis else x
                
                # Primary function
                f_expr = sp.sympify(equations[0].strip())
                
                # Conversion logic: if revolving about y-axis but function is y=f(x), solve for x
                if is_y_axis and 'x' in str(f_expr):
                    f_expr = sp.solve(sp.Eq(y, f_expr), x)[0]

                # Secondary function for Washer Method
                g_expr = sp.sympify(equations[1].strip()) if len(equations) > 1 else sp.sympify(0)
                
                # Identify Method
                method_name = "Washer Method" if g_expr != 0 else "Disk Method"
                
                # Determine limits
                a_val = float(nums[0]) if len(nums) > 1 else 0.0
                b_val = float(nums[-1]) if nums else 1.0
                if 'sqrt(3)' in clean_q: b_val = float(sp.sqrt(3).evalf())

                st.success(f"✅ {method_name} Identified")
                
                # 3. UI Layout for Results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📝 Step-by-Step Solution")
                    st.write("**1. Setup the Integral:**")
                    st.latex(rf"V = \pi \int_{{{a_val}}}^{{{b_val}}} [({sp.latex(f_expr)})^2 - ({sp.latex(g_expr)})^2] \, d{var}")
                    
                    integrand = sp.simplify(f_expr**2 - g_expr**2)
                    st.write("**2. Simplified Integrand:**")
                    st.latex(rf"V = \pi \int_{{{a_val}}}^{{{b_val}}} ({sp.latex(integrand)}) \, d{var}")
                    
                    antideriv = sp.integrate(integrand, var)
                    st.write("**3. Anti-derivative:**")
                    st.latex(rf"V = \pi \left[ {sp.latex(antideriv)} \right]_{{{a_val}}}^{{{b_val}}}")
                    
                    final_vol = sp.pi * (antideriv.subs(var, b_val) - antideriv.subs(var, a_val))
                    st.write("**4. Final Answer:**")
                    st.latex(rf"V = {sp.latex(final_vol)} \approx {float(final_vol.evalf()):.4f}")

                with col2:
                    st.subheader("📊 3D Solid Model")
                    fig = plt.figure(figsize=(8, 6))
                    ax = fig.add_subplot(111, projection='3d')
                    
                    v_space = np.linspace(a_val, b_val, 50)
                    theta = np.linspace(0, 2*np.pi, 50)
                    V_mesh, THETA = np.meshgrid(v_space, theta)
                    
                    f_num = sp.lambdify(var, f_expr, 'numpy')(V_mesh)
                    
                    X_surf = f_num * np.cos(THETA)
                    Z_surf = f_num * np.sin(THETA)
                    Y_surf = V_mesh
                    
                    ax.plot_surface(X_surf, Y_surf, Z_surf, color='springgreen', alpha=0.6, edgecolor='k')
                    st.pyplot(fig)
            else:
                st.error("Format Error: Ensure equations are written as 'y = ...' or 'x = ...'")
        except Exception as e:
            st.error(f"Could not parse problem: {e}")
