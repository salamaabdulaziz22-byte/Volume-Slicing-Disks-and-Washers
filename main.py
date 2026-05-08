import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re

# Page Configuration
st.set_page_config(page_title="Universal Math Solver", layout="wide")
st.title("Dynamic Volume of Revolution Solver")
st.markdown("---")

# User Input Section - This is now empty by default for you to type any question
raw_input = st.text_area("Enter your calculus problem below:", 
                         placeholder="e.g., y = 4 - x**2, y = 1, from x = 0 to sqrt(3) about y-axis")

if st.button("Solve & Visualize"):
    if not raw_input:
        st.warning("Please enter a question first!")
    else:
        try:
            # 1. Smart Text Cleaning (Data Pre-processing)
            # This handles common copy-paste issues like 'vx' or '^'
            clean_q = raw_input.lower().replace('^', '**').replace('√', 'sqrt').replace('vx', 'sqrt(x)')
            clean_q = re.sub(r'([xy])(\d)', r'\1**\2', clean_q)
            
            # 2. Extracting Math Components
            equations = re.findall(r'[xy]\s*=\s*([0-9x\s\+\-\*\^/\(\)sqrt]+)', clean_q)
            nums = re.findall(r'(\d+\.?\d*)', clean_q)
            
            if len(equations) >= 1:
                x, y = sp.symbols('x y')
                is_y_axis = 'y-axis' in clean_q
                var = y if is_y_axis else x
                
                # Logic to convert y=f(x) to x=f(y) if revolving about y-axis
                f_expr = sp.sympify(equations[0].strip())
                if is_y_axis and 'x' in str(f_expr):
                    f_expr = sp.solve(sp.Eq(y, f_expr), x)[0]

                g_expr = sp.sympify(equations[1].strip()) if len(equations) > 1 else sp.sympify(0)
                
                # Detect Method (Disk vs Washer)
                method_name = "Washer Method" if g_expr != 0 else "Disk Method"
                
                # Handling limits (e.g., 0 to sqrt(3))
                a_val = 0.0
                b_val = float(nums[-1]) if nums else 1.0
                if 'sqrt(3)' in clean_q: b_val = float(sp.sqrt(3).evalf())

                st.success(f"✅ Method Identified: {method_name}")
                
                # 3. Generating Step-by-Step UI
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📝 Step-by-Step Solution")
                    st.write("**1. Setup the Integral:**")
                    st.latex(rf"V = \pi \int_{{{a_val}}}^{{{b_val}}} [({sp.latex(f_expr)})^2 - ({sp.latex(g_expr)})^2] \, d{var}")
                    
                    integrand = sp.simplify(f_expr**2 - g_expr**2)
                    st.write("**2. Simplify:**")
                    st.latex(rf"V = \pi \int_{{{a_val}}}^{{{b_val}}} ({sp.latex(integrand)}) \, d{var}")
                    
                    antideriv = sp
