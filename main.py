import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import re

# 1. UI Configuration
st.set_page_config(page_title="STEM Volume Solver", layout="wide")
st.title("Volume of Revolution Solver")
st.write("Professional Tool for Disks and Washers Method (Lesson 6-2)")

# 2. Input Area
raw_input = st.text_area("Enter problem text:", height=100, 
                         placeholder="Example: y = x**2, y = 4, about y-axis")

if st.button("Solve Step-by-Step"):
    try:
        # A. Symbols and Axis Detection
        x, y = sp.symbols('x y')
        text = raw_input.lower().replace('^', '**').replace('vx', 'sqrt(x)')
        
        # Determine Axis of Revolution
        is_y_axis = any(word in text for word in ['y-axis', 'about y', 'vertical'])
        var = y if is_y_axis else x
        
        # B. Smart Equation Extraction
        # Find all parts like 'y = ...' or 'x = ...'
        found_eqs = re.findall(r'[yx]\s*=\s*([^, \n]+)', text)
        raw_exprs = [sp.sympify(e) for e in found_eqs]
        
        # C. Variable Transformation (Crucial for y-axis rotation)
        # If axis is Y, we need x = f(y). If axis is X, we need y = f(x).
        final_funcs = []
        for expr in raw_exprs:
            if is_y_axis and 'x' in str(expr):
                # Solve y = f(x) for x
                sol = sp.solve(sp.Eq(y, expr), x)
                final_funcs.append(sol[-1]) # Use positive/right-hand branch
            elif not is_y_axis and 'y' in str(expr):
                # Solve x = f(y) for y
                sol = sp.solve(sp.Eq(x, expr), y)
                final_funcs.append(sol[-1])
            else:
                final_funcs.append(expr)

        # D. Dynamic Boundary Detection (Intersections)
        # Find where the curves meet to set the limits of integration
        if len(final_funcs) >= 2:
            pts = sp.solve(sp.Eq(final_funcs[0], final_funcs[1]), var)
        else:
            pts = sp.solve(sp.Eq(final_funcs[0], 0), var)
        
        # Clean points to get real numerical limits
        real_pts = [p.evalf() for p in pts if p.is_real]
        if real_pts:
            a, b = min(real_pts), max(real_pts)
        else:
            # Fallback to scanning text for explicit limits (from x=0 to x=2)
            nums = re.findall(r"sqrt\(\d+\)|\d+\.?\d*", text)
            a, b = sp.sympify(nums[-2]), sp.sympify(nums[-1])

        # E. Radius Logic (R vs r)
        R_outer = final_funcs[0]
        r_inner = final_funcs[1] if len(final_funcs) > 1 else sp.Integer(0)
        
        # Ensure R is the larger radius at midpoint
        mid = (float(a) + float(b)) / 2
        if abs(float(R_outer.subs(var, mid))) < abs(float(r_inner.subs(var, mid))):
            R_outer, r_inner = r_inner, R_outer

        # F. Calculus Calculation
        method = "Washer Method" if r_inner != 0 else "Disk Method"
        integrand = sp.simplify(R_outer**2 - r_inner**2)
        volume_exact = sp.pi * sp.integrate(integrand, (var, a, b))

        # G. Professional Output
        st.success(f"Method Identified: {method}")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Solution Steps")
            st.write(f"**Variable:** Integrating with respect to d{var}")
            st.write("**Integral Setup:**")
            st.latex(rf"V = \pi \int_{{{sp.latex(a)}}}^{{{sp.latex(b)}}} [({sp.latex(R_outer)})^2 - ({sp.latex(r_inner)})^2] \, d{var}")
            st.write("**Simplified Result:**")
            st.latex(rf"V = {sp.latex(volume_exact)} \approx {float(volume_exact.evalf()):.4f}")

        with col2:
            st.subheader("📊 3D Geometric Model")
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            u = np.linspace(float(a), float(b), 40)
            v = np.linspace(0, 2*np.pi, 40)
            U, V = np.meshgrid(u, v)
            radius_vals = sp.lambdify(var, R_outer, 'numpy')(U)
            
            if is_y_axis:
                X, Y, Z = radius_vals*np.cos(V), U, radius_vals*np.sin(V)
            else:
                X, Y, Z = U, radius_vals*np.cos(V), radius_vals*np.sin(V)
            
            ax.plot_surface(X, Y, Z, color='cyan', alpha=0.5, edgecolor='k', lw=0.1)
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Mathematical Error: {e}. Ensure you include the equations and the axis (x or y).")
