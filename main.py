import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

# 1. Page Configuration
st.set_page_config(page_title="Calculus Volume Solver", layout="wide")
st.title("Advanced Volume Analyzer")
st.write("Professional Solver for Disk & Washer methods (Lesson 6-2)")

# 2. Sidebar for Precise Inputs
with st.sidebar:
    st.header("Problem Settings")
    f_input = st.text_input("Upper Function f(x):", "sqrt(x)")
    g_input = st.text_input("Lower Function g(x):", "x**2")
    axis_val = st.text_input("Axis of Revolution (e.g., x=0 or y=2):", "x=0")

# 3. Main Calculation Logic
if st.button("Generate Verified Solution"):
    try:
        # Define Symbols
        x, y = sp.symbols('x y')
        f = sp.sympify(f_input)
        g = sp.sympify(g_input)
        
        # A. Automatic Intersection Detection (Limits)
        intersections = sp.solve(f - g, x)
        real_pts = [p.evalf() for p in intersections if p.is_real]
        
        if not real_pts:
            st.error("No intersection points found. Please check your functions.")
        else:
            a_limit, b_limit = min(real_pts), max(real_pts)
            
            # B. Axis Analysis
            axis_type = 'y' if 'x' in axis_val else 'x'
            axis_num = sp.sympify(axis_val.split('=')[1])
            
            # C. Radius and Variable Transformation
            if axis_type == 'y':  # Vertical Rotation (integrating dy)
                # Solve functions for x to get them in terms of y
                f_inv = sp.solve(sp.Eq(y, f), x)[0]
                g_inv = sp.solve(sp.Eq(y, g), x)[0]
                
                # Convert boundaries to y-limits
                y_a, y_b = float(f.subs(x, a_limit)), float(f.subs(x, b_limit))
                limits = (min(y_a, y_b), max(y_a, y_b))
                
                R_radius = sp.Abs(f_inv - axis_num)
                r_radius = sp.Abs(g_inv - axis_num)
                var = y
            else:  # Horizontal Rotation (integrating dx)
                R_radius = sp.Abs(f - axis_num)
                r_radius = sp.Abs(g - axis_num)
                var = x
                limits = (float(a_limit), float(b_limit))

            # D. Calculus Integration
            integrand = sp.simplify(R_radius**2 - r_radius**2)
            volume_exact = sp.pi * sp.integrate(integrand, (var, limits[0], limits[1]))
            
            # 4. Displaying Results
            st.success("✅ Mathematical Solution Generated")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📝 Step-by-Step Methodology")
                st.write(f"**Variable:** d{var}")
                st.write(f"**Limits:** from {limits[0]} to {limits[1]}")
                st.write("**Formula:**")
                st.latex(rf"V = \pi \int
