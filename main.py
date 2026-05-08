import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import re

# Page Setup
st.set_page_config(page_title="Professional Volume Solver", layout="wide")
st.title("Calculus Volume Solver")

# Input Section
raw_input = st.text_area("Paste your textbook question here:", height=150, 
                         placeholder="Example: y = 4 - x**2, y = 1, from x = 0 to x = sqrt(3) about y-axis")

if st.button("Generate Complete Solution"):
    try:
        # 1. TEXT CLEANING (Handling textbook shorthand like 'v3' or 'vx')
        # We ensure 'v' followed by a number or 'x' becomes 'sqrt'
        clean_text = raw_input.lower().replace('vx', 'sqrt(x)').replace('v', 'sqrt').replace('^', '**')
        
        # 2. EXTRACTION
        # Extract equations: y=... or x=...
        eq_found = re.findall(r'[yx]\s*=\s*([^, \n]+)', clean_text)
        # Extract limits: numbers or sqrt expressions
        limit_values = re.findall(r"sqrt\(\d+\)|\d+\.?\d*", clean_text)
        
        x, y = sp.symbols('x y')
        is_y_axis = any(word in clean_text for word in ['y-axis', 'about y', 'around y'])
        var = y if is_y_axis else x

        # 3. TRANSFORMATION (Solving for the correct variable)
        # For y-axis rotations, we need x = f(y)
        raw_exprs = [sp.sympify(e) for e in eq_found]
        final_exprs = []
        
        for expr in raw_exprs:
            if is_y_axis and 'x' in str(expr):
                # Solving y = f(x) for x
                sols = sp.solve(sp.Eq(y, expr), x)
                final_exprs.append(sols[-1]) # Selecting the outer/positive branch
            else:
                final_exprs.append(expr)

        f_expr = final_exprs[0]
        g_expr = final_exprs[1] if len(final_exprs) > 1 else sp.sympify(0)

        # 4. LIMIT IDENTIFICATION
        # Safely convert extracted strings to symbolic math
        a_sym = sp.sympify(limit_values[0]) if len(limit_values) >= 1 else sp.Integer(0)
        b_sym = sp.sympify(limit_values[1]) if len(limit_values) >= 2 else sp.Integer(1)
        
        # 5. LOGICAL ORDERING (R vs r)
        # Checking midpoint to see which curve is the 'Outer Radius'
        test_val = (float(a_sym.evalf()) + float(b_sym.evalf())) / 2
        val_f = float(f_expr.subs(var, test_val).evalf())
        val_g = float(g_expr.subs(var, test_val).evalf())
        
        R_outer, r_inner = (f_expr, g_expr) if val_f >= val_g else (g_expr, f_expr)
        method = "Washer Method" if r_inner != 0 else "Disk Method"

        # 6. CALCULATIONS
        integrand = sp.simplify(R_outer**2 - r_inner**2)
        # Volume = Pi * Integral of (R^2 - r^2)
        volume_exact = sp.pi * sp.Abs(sp.integrate(integrand, (var, a_sym, b_sym)))

        # 7. DISPLAYING THE UI
        st.success(f"✅ Identified: **{method}**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Step-by-Step Solution")
            st.write("**1. Integral Setup:**")
            st.latex(rf"V = \pi \int_{{{sp.latex(a_sym)}}}^{{{sp.latex(b_sym)}}} [({sp.latex(R_outer)})^2 - ({sp.latex(r_inner)})^2] \, d{var}")
            
            st.write("**2. Simplified Integrand:**")
            st.latex(rf"V = \pi \int ({sp.latex(integrand)}) \, d{var}")
            
            st.write("**3. Anti-derivative:**")
            antideriv = sp.integrate(integrand, var)
            st.latex(rf"V = \pi \left[ {sp.latex(antideriv)} \right]_{{{sp.latex(a_sym)}}}^{{{sp.latex(b_sym)}}}")
            
            st.write("**4. Final Exact Result:**")
            st.latex(rf"V = {sp.latex(sp.simplify(volume_exact))} \approx {float(volume_exact.evalf()):.4f}")

        with col2:
            st.subheader("📊 3D Model")
            fig = plt.figure(figsize=(8, 6))
            ax = fig.add_subplot(111, projection='3d')
            
            # Creating numeric mesh for plotting
            u = np.linspace(float(a_sym.evalf()), float(b_sym.evalf()), 50)
            v = np.linspace(0, 2*np.pi, 50)
            U, V = np.meshgrid(u, v)
            
            #
