import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re

st.set_page_config(page_title="Universal Volume Solver", layout="wide")
st.title("Intelligent Volume of Revolution Solver")
st.markdown("---")

# User Input Section
raw_input = st.text_area("Paste your textbook question here:", 
                         "Find the volume of the solid resulting from revolving the region bounded by y = sqrt(x) and y = 0 from x = 0 to x = 4 about the x-axis")

if st.button("Analyze & Solve"):
    try:
        # 1. Natural Language Processing to extract Math
        # Cleans common copy-paste errors from PowerPoints/PDFs
        clean_q = raw_input.lower().replace('^', '**').replace('√', 'sqrt').replace('vx', 'sqrt(x)')
        
        # Extract equations (y=... or x=...)
        equations = re.findall(r'[xy]\s*=\s*([0-9x\s\+\-\*\^/\(\)sqrt]+)', clean_q)
        # Extract numerical intervals
        nums = re.findall(r'(\d+\.?\d*)', clean_q)
        
        if len(equations) >= 1:
            x, y = sp.symbols('x y')
            is_y_axis = 'y-axis' in clean_q
            var = y if is_y_axis else x
            
            # Define Functions
            f_expr = sp.sympify(equations[0].strip())
            g_expr = sp.sympify(equations[1].strip()) if len(equations) > 1 else sp.sympify(0)
            
            # Automatically identify the method
            method_type = "Washer Method" if g_expr != 0 else "Disk Method"
            
            # Define Integration Limits
            a_val = float(nums[0]) if len(nums) > 0 else 0.0
            b_val = float(nums[1]) if len(nums) > 1 else 1.0
            if 'sqrt(3)' in clean_q: b_val = float(sp.sqrt(3).evalf())

            st.success(f"✅ Method Detected: {method_type}")
            
            # 2. Step-by-Step Calculus Display
            st.subheader("📝 Step-by-Step Solution")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Step 1: Setup the Integral**")
                st.latex(rf"V = \pi \int_{{{a_val}}}^{{{b_val}}} [({sp.latex(f_expr)})^2 - ({sp.latex(g_expr)})^2] \, d{var}")
                
                integrand = sp.simplify(f_expr**2 - g_expr**2)
                st.write("**Step 2: Simplify the Integrand**")
                st.latex(rf"V = \pi \int_{{{a_val}}}^{{{b_val}}} ({sp.latex(integrand)}) \, d{var}")
                
                antideriv = sp.integrate(integrand, var)
                st.write("**Step 3: Find the Antiderivative**")
                st.latex(rf"V = \pi \left[ {sp.latex(antideriv)} \right]_{{{a_val}}}^{{{b_val}}}")
                
                final_vol = sp.pi * (antideriv.subs(var, b_val) - antideriv.subs(var, a_val))
                st.write("**Step 4: Evaluate and Final Result**")
                st.latex(rf"V = {sp.latex(final_vol)} \approx {float(final_vol.evalf()):.4f}")

            # 3. 3D Visualization
            with col2:
                st.subheader("📦 3D Solid Visualization")
                fig = plt.figure(figsize=(8, 6))
                ax = fig.add_subplot(111, projection='3d')
                
                # Generate points for the surface
                v_space = np.linspace(a_val, b_val, 50)
                theta = np.linspace(0, 2*np.pi, 50)
                V, THETA = np.meshgrid(v_space, theta)
                
                # Turn symbolic function into numeric for plotting
                f_num_func = sp.lambdify(var, f_expr, 'numpy')
                R = f_num_func(V)
                
                # Parametric equations for a solid of revolution
                if is_y_axis:
                    X_plot = R * np.cos(THETA)
                    Z_plot = R * np.sin(THETA)
                    Y_plot = V
                else:
                    Y_plot = R * np.cos(THETA)
                    Z_plot = R * np.sin(THETA)
                    X_plot = V
                
                ax.plot_surface(X_plot, Y_plot, Z_plot, color='orchid', alpha=0.7, edgecolor='k', lw=0.5)
                ax.set_title("3D Revolution Model")
                st.pyplot(fig)
                
        else:
            st.error("No equations detected. Please use format: 'y = ...' or 'x = ...'")
            
    except Exception as e:
        st.error(f"Processing Error: {e}. Please ensure the math syntax is correct.")
