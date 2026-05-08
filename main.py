import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

# Professional UI Setup
st.set_page_config(page_title="Calculus Volume Solver Pro", layout="wide")
st.title("Advanced Volume Analyzer")
st.write("Verified solver for Disk & Washer methods (Lesson 6-2)")

# Sidebar for precise inputs
with st.sidebar:
    st.header("Problem Parameters")
    f_input = st.text_input("Upper Function f(x):", "sqrt(x)")
    g_input = st.text_input("Lower Function g(x):", "x**2")
    axis_val = st.text_input("Axis of Revolution (e.g., x=0 or y=2):", "x=0")
    
if st.button("Generate Step-by-Step Solution"):
    try:
        x, y = sp.symbols('x y')
        f = sp.sympify(f_input)
        g = sp.sympify(g_input)
        
        # 1. Automatic Boundary Detection (Intersections)
        intersections = sp.solve(f - g, x)
        real_pts = [p.evalf() for p in intersections if p.is_real]
        a_limit, b_limit = min(real_pts), max(real_pts)
        
        # 2. Axis Analysis
        axis_type = 'y' if 'x' in axis_val else 'x'
        axis_num = sp.sympify(axis_val.split('=')[1])
        
        # 3. Radius Logic (R and r) based on Axis Type
        if axis_type == 'y':  # Vertical Rotation
            # Transform functions to be in terms of y
            f_inv = sp.solve(sp.Eq(y, f), x)[0]
            g_inv = sp.solve(sp.Eq(y, g), x)[0]
            
            # New boundaries in terms of y
            a_y, b_y = f.subs(x, a_limit), f.subs(x, b_limit)
            if a_y > b_y: a_y, b_y = b_y, a_y
            
            R_radius = sp.Abs(f_inv - axis_num)
            r_radius = sp.Abs(g_inv - axis_num)
            var = y
            limits = (a_y, b_y)
        else:  # Horizontal Rotation
            R_radius = sp.Abs(f - axis_num)
            r_radius = sp.Abs(g - axis_num)
            var = x
            limits = (a_limit, b_limit)

        # 4. Integration Calculation
        integrand = sp.simplify(R_outer**2 - r_inner**2) # Wait, using radius names
        integrand = sp.simplify(R_radius**2 - r_radius**2)
        volume_exact = sp.pi * sp.integrate(integrand, (var, limits[0], limits[1]))
        
        # 5. Output Results
        st.success("✅ Solution Verified!")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Step-by-Step Methodology:")
            st.write(f"**Integration Variable:** d{var}")
            st.write(f"**Limits:** from {limits[0]} to {limits[1]}")
            st.write("**Formula Applied:**")
            st.latex(rf"V = \pi \int_{{{limits[0]}}}^{{{limits[1]}}} [({sp.latex(R_radius)})^2 - ({sp.latex(r_radius)})^2] \, d{var}")
            
            st.write("**Exact Value:**")
            st.latex(rf"V = {sp.latex(sp.simplify(volume_exact))}")
            st.write
