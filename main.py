import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import re

# 1. Page Configuration
st.set_page_config(page_title="Calculus Volume Solver Pro", layout="wide")
st.title("Volume of Revolution Solver")
st.write("Complete step-by-step solver for Disk and Washer methods (Lesson 6-2).")

# 2. Input Section
raw_input = st.text_area("Paste the textbook question here:", height=120, 
                         placeholder="Example: y = x**2, y = 4, about y-axis")

if st.button("Generate Solution"):
    try:
        # A. Setup Symbols and Axis Detection
        x, y = sp.symbols('x y')
        text = raw_input.lower().replace('^', '**').replace('vx', 'sqrt(x)')
        
        # Determine the Integration Variable (dx or dy)
        is_y_axis = any(word in text for word in ['y-axis', 'about y', 'vertical'])
        integration_var = y if is_y_axis else x
        
        # B. Smart Equation Extraction
        # Finds expressions like 'y = ...' or 'x = ...'
        eq_patterns = re.findall(r'[yx]\s*=\s*([^, \n]+)', text)
        if not eq_patterns:
            st.error("No equations detected. Please use format: y = x**2")
            st.stop()
            
        raw_exprs = [sp.sympify(e) for e in eq_patterns]
        
        # C. Mathematical Transformation (The Core Logic)
        # If rotating about Y, all functions must be x = f(y)
        final_funcs = []
        for expr in raw_exprs:
            if is_y_axis and 'x' in str(expr):
                # Solve y = f(x) for x to get x = g(y)
                sol = sp.solve(sp.Eq(y, expr), x)
                final_funcs.append(sol[-1]) # Uses the positive branch
            elif not is_y_axis and 'y' in str(expr):
                # Solve x = g(y) for y to get y = f(x)
                sol = sp.solve(sp.Eq(x, expr), y)
                final_funcs.append(sol[-1])
            else:
                final_funcs.append(expr)

        # D. Boundary Detection (Automatic Intersection)
        # Finds where the curves meet to define the interval [a, b]
        if len(final_funcs) >= 2:
            pts = sp.solve(sp.Eq(final_funcs[0], final_funcs[1]), integration_var)
        else:
            pts = sp.solve(sp.Eq(final_funcs[0], 0), integration_var)
            
        real_pts = [p.evalf() for p in pts if p.is_real]
        if real_pts:
            a, b = min(real_pts), max(real_pts)
        else:
            # Fallback: find explicit numbers in text (e.g., from x=0 to x=4)
            nums = re.findall(r"sqrt\(\d+\)|\d+\.?\d*", text)
            a, b = sp.sympify(nums[-2]), sp.sympify(nums[-1])

        # E. Disk vs Washer Selection
        R_outer = final_funcs[0]
        r_inner = final_funcs[1] if len(final_funcs) > 1 else sp.Integer(0)
        
        # Radius Safety: Ensure R is the outer radius at the midpoint
        test_mid = (float(a) + float(b)) / 2
        if abs(float(R_outer.subs(integration_var, test_mid))) < abs(float(r_inner.subs(integration_var, test_mid))):
            R_outer, r_inner = r_inner, R_outer

        method = "Washer Method" if r_inner != 0 else "Disk Method"

        # F. Calculus Evaluation
        integrand = sp.simplify(R_outer**2 - r_inner**2)
        volume_exact = sp.pi * sp.integrate(integrand, (integration_var, a, b))

        # G. Displaying the Result
        st.success(f"Method Identified: {method}")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Step-by-Step Logic")
            st.write(f"1. **Rotation Axis:** {'Y-axis (dy)' if is_y_axis else 'X-axis (dx)'}")
            st.write(f"2. **Interval:** from {a} to {b}")
            st.write("3. **Integral Setup:**")
            st.latex(rf"V = \pi \int_{{{sp.latex(a)}}}^{{{sp.latex(b)}}} \left( ({sp.latex(R_outer)})^2 - ({sp.latex(r_inner)})^2 \right) d{integration_var}")
            st.write("4. **Final Result:**")
            st.latex(rf"V = {sp.latex(volume_exact)} \approx {float(volume_exact.evalf()):.4f}")

        with col2:
            st.subheader("📊 3D Visual Model")
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            u = np.linspace(float(a), float(b), 40)
            v = np.linspace(0, 2*np.pi, 40)
            U, V = np.meshgrid(u, v)
            radius_func = sp.lambdify(integration_var, R_outer, 'numpy')(U)
            
            if is_y_axis:
                X, Y, Z = radius_func*np.cos(V), U, radius_func*np.sin(V)
            else:
                X, Y, Z = U, radius_func*np.cos(V), radius_func*np.sin(V)
                
            ax.plot_surface(X, Y, Z, color='cyan', alpha=0.5, edgecolor='black', lw=0.1)
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Analysis failed. Ensure you write the axis (x or y) clearly. Error: {e}")
