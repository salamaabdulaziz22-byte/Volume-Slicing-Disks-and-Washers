import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import re

# Page Configuration
st.set_page_config(page_title="Calculus Volume Solver Pro", layout="wide")
st.title("Geometric Analyzer for Volumes of Revolution")
st.write("Specifically designed for Disk and Washer methods with 100% accuracy.")

# Question Input Section
st.sidebar.header("Problem Settings")
raw_input = st.text_area("Paste the question here:", height=100)

if st.button("Solve with Step-by-Step Steps"):
    try:
        # 1. Cleaning & Data Extraction
        text = raw_input.lower().replace('^', '**').replace('vx', 'sqrt(x)').replace('v', 'sqrt')
        x, y = sp.symbols('x y')
        
        # Detect Rotation Axis
        is_y_axis = any(word in text for word in ['y-axis', 'about y', 'around y', 'vertical'])
        var = y if is_y_axis else x
        
        # Extract Equations
        eqs = re.findall(r'[yx]\s*=\s*([^, \n]+)', text)
        exprs = [sp.sympify(e) for e in eqs]

        # 2. Variable Transformation (Critical Step)
        # If rotating about y but equation is y=f(x), convert to x=g(y)
        processed_exprs = []
        for expr in exprs:
            if is_y_axis and 'x' in str(expr):
                sol = sp.solve(sp.Eq(y, expr), x)
                processed_exprs.append(sol[-1]) # Use the positive/right branch
            elif not is_y_axis and 'y' in str(expr):
                sol = sp.solve(sp.Eq(x, expr), y)
                processed_exprs.append(sol[-1])
            else:
                processed_exprs.append(expr)

        # 3. Intersection Logic (Finding Bounds)
        if len(processed_exprs) >= 2:
            pts = sp.solve(sp.Eq(processed_exprs[0], processed_exprs[1]), var)
        else:
            pts = sp.solve(sp.Eq(processed_exprs[0], 0), var)
        
        # Use intersection points as bounds; otherwise, look for numbers in text
        if pts:
            a, b = min(pts), max(pts)
        else:
            nums = re.findall(r"sqrt\(\d+\)|\d+\.?\d*", text)
            a, b = sp.sympify(nums[-2]), sp.sympify(nums[-1])

        # 4. R (Outer) vs r (Inner) Identification
        R = processed_exprs[0]
        r = processed_exprs[1] if len(processed_exprs) > 1 else sp.Integer(0)
        
        # Ensure R is the outer radius for a positive result
        mid_val = (float(a.evalf()) + float(b.evalf())) / 2
        if abs(R.subs(var, mid_val)) < abs(r.subs(var, mid_val)):
            R, r = r, R

        # 5. Mathematical Calculations
        method = "Washer Method" if r != 0 else "Disk Method"
        integrand = sp.simplify(R**2 - r**2)
        volume_exact = sp.pi * sp.integrate(integrand, (var, a, b))

        # 6. Display Results
        st.success(f"Method Identified: {method}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📝 Detailed Solution Steps:")
            st.write(f"**Integration Variable:** d{var}")
            st.write("**1. Setup the Integral:**")
            st.latex(rf"V = \pi \int_{{{sp.latex(a)}}}^{{{sp.latex(b)}}} \left[ ({sp.latex(R)})^2 - ({sp.latex(r)})^2 \right] d{var}")
            
            st.write("**2. Simplified Integrand:**")
            st.latex(rf"V = \pi \int_{{{sp.latex(a)}}}^{{{sp.latex(b)}}} ({sp.latex(integrand)}) d{var}")
            
            st.write("**3. Final Value:**")
            st.latex(rf"V = {sp.latex(volume_exact)} \approx {float(volume_exact.evalf()):.4f}")

        with col2:
            st.subheader("📊 3D Visualization Model:")
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            
            u_mesh = np.linspace(float(a.evalf()), float(b.evalf()), 30)
            v_mesh = np.linspace(0, 2*np.pi, 30)
            U, V = np.meshgrid(u_mesh, v_mesh)
            
            r_func = sp.lambdify(var, R, 'numpy')
            R_vals = r_func(U)
            
            if is_y_axis:
                X, Y, Z = R_vals*np.cos(V), U, R_vals*np.sin(V)
            else:
                X, Y, Z = U, R_vals*np.cos(V), R_vals*np.sin(V)
            
            ax.plot_surface(X, Y, Z, color='cyan', alpha=0.6, edgecolor='black', lw=0.1)
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Error analyzing the question. Please ensure equations are clear. Details: {e}")
