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
# The 'value=""' ensures there is no pre-written text inside the box.
raw_input = st.text_area("Paste your textbook question here:", value="", height=150)

if st.button("Solve & Generate Full Solution"):
    if not raw_input.strip():
        st.warning("The input is empty. Please paste your question first.")
    else:
        try:
            # 1. Smart Text Cleaning
            # Handles common copy-paste issues (x2 -> x**2, Vx -> sqrt(x), etc.)
            clean_q = raw_input.lower().replace('^', '**').replace('√', 'sqrt').replace('vx', 'sqrt(x)')
            # Automatically adds exponents if the user pastes 'x2' instead of 'x**2'
            clean_q = re.sub(r'([xy])(\d)', r'\1**\2', clean_q)
            
            # 2. Extracting Math Components
            equations = re.findall(r'[xy]\s*=\s*([0-9x\s\+\-\*\^/\(\)sqrt]+)', clean_q)
            nums = re.findall(r'(\d+\.?\d*)', clean_q)
            
            if len(equations) >= 1:
                x, y = sp.symbols('x y')
                is_y_axis = 'y-axis' in clean_q
                var = y if is_y_axis else x
                
                # Logic to handle Disk (1 function) vs Washer (2 functions)
                f_expr = sp.sympify(equations[0].strip())
                
                # Conversion logic: if revolving about y-axis but function is y=f(x), solve for x
                if is_y_axis and 'x' in str(f_expr):
                    f_expr = sp.solve(sp.Eq(y, f_expr), x)[0]

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
                    st.latex(rf"V =
