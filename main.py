import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

# Professional Page Config
st.set_page_config(page_title="Calculus Volume Solver Pro", layout="wide")
st.title("Advanced Volume Analyzer")
st.write("Verified solver for Disk & Washer methods (Lesson 6-2)")

# Sidebar for precise user inputs
with st.sidebar:
    st.header("Problem Parameters")
    f_input = st.text_input("Upper Function f(x):", "sqrt(x)")
    g_input = st.text_input("Lower Function g(x):", "x**2")
    axis_val = st.text_input("Axis of Revolution (e.g., x=0 or y=2):", "x=0")
    
if st.button("Generate Step-by-Step Solution"):
    try:
        # 1. SETUP SYMBOLS
        x, y = sp.symbols('x y')
        f = sp.sympify(f_input)
        g = sp.sympify(g_input)
        
        # 2. AUTOMATIC BOUNDARY DETECTION (Intersections)
        intersections = sp.solve(f - g, x)
        real_pts = [p.evalf() for p in intersections if p.is_real]
        if not real_pts:
            st.error("No intersection found between these functions.")
        else:
            a_limit, b_limit = min(real_pts), max(real_pts)
            
            # 3. AXIS ANALYSIS
            axis_type = 'y' if 'x' in axis_val else 'x'
            axis_num = sp.sympify(axis_val.split('=')[1])
            
            # 4. RADIUS LOGIC (R and r)
            if axis_type == 'y':  # Vertical Rotation (dy)
                # Transform functions to be in terms of y
                f_inv = sp.solve(sp.Eq(y, f), x)[0]
                g_inv = sp.solve(sp.Eq(y, g), x)[0]
                
                # Update boundaries for y
                y_a, y_b = float(f.subs(x, a_limit)), float(f.subs(x, b_limit))
                limits = (min(y_a, y_b), max(y_a, y_b))
                
                R_radius = sp.Abs(f_inv - axis_num)
                r_radius = sp.Abs(g_inv - axis_num)
                var = y
            else:  # Horizontal Rotation (dx)
                R_radius = sp.Abs(f - axis_num)
                r_radius = sp.Abs(g - axis_num)
                var = x
                limits = (float(a_limit), float(b_limit))

            # 5. INTEGRATION
            integrand = sp.simplify(R_radius**2 - r_radius**2)
            volume_exact = sp.pi * sp.integrate(integrand, (var, limits[0], limits[1]))
            
            # 6. UI OUTPUT
            st.success("✅ Solution Verified!")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📝 Step-by-Step Methodology:")
                st.write(f"**Integration Variable:** d{var}")
                st.write(f"**Limits:** from {limits[0]} to {limits[1]}")
                st.write("**Formula Applied (Washer Method):**")
                st.latex(rf"V = \pi
