import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import re

# Professional UI Branding
st.set_page_config(page_title="Pro Calculus Solver", layout="wide")
st.title("Volume of Revolution Solver")
st.write("Designed for Lesson 6-2: Disks and Washers")

# User Input
raw_input = st.text_area("Paste Textbook Question:", height=100, 
                         placeholder="e.g., y = x**2, y = 4, about the y-axis")

if st.button("Generate Verified Solution"):
    try:
        # 1. PARSING & AXIS DETECTION
        text = raw_input.lower().replace('^', '**').replace('vx', 'sqrt(x)').replace('v', 'sqrt')
        x, y = sp.symbols('x y')
        
        # Determine if we integrate with dy or dx
        is_y_axis = any(word in text for word in ['y-axis', 'about y', 'vertical'])
        var = y if is_y_axis else x
        
        # 2. EQUATION TRANSFORMATION (The "Secret Sauce")
        # Extract all y=... or x=... expressions
        eqs = re.findall(r'[yx]\s*=\s*([^, \n]+)', text)
        raw_exprs = [sp.sympify(e) for e in eqs]
        
        processed_funcs = []
        for expr in raw_exprs:
            # If rotating about Y, but eq is y=x**2, we must solve for x to get sqrt(y)
            if is_y_axis and 'x' in str(expr):
                sol = sp.solve(sp.Eq(y, expr), x)
                processed_funcs.append(sol[-1]) # Pick the positive branch
            elif not is_y_axis and 'y' in str(expr):
                sol = sp.solve(sp.Eq(x, expr), y)
                processed_funcs.append(sol[-1])
            else:
                processed_funcs.append(expr)

        # 3. INTERSECTION LOGIC (Finding accurate Bounds)
        if len(processed_funcs) >= 2:
            pts = sp.solve(sp.Eq(processed_funcs[0], processed_funcs[1]), var)
        else:
            pts = sp.solve(sp.Eq(processed_funcs[0], 0), var)
            
        # Filter for real intersection points
        real_pts = [p.evalf() for p in pts if p.is_real]
        
        if real_pts:
            a, b = min(real_pts), max(real_pts)
        else:
            # Fallback to scanning text for numbers if no intersection found
            nums = re.findall(r"sqrt\(\d+\)|\d+\.?\d*", text)
            a, b = sp.sympify(nums[-2]), sp.sympify(nums[-1])

        # 4. R (Outer) vs r (Inner) IDENTIFICATION
        R = processed_funcs[0]
        r = processed_funcs[1] if len(processed_funcs) > 1 else sp.Integer(0)
        
        # Test midpoint to ensure R is the outer radius (prevents negative volume)
        mid_test = (float(a) + float(b)) / 2
        if abs(R.subs(var, mid_test)) < abs(r.subs(var, mid_test)):
            R, r = r, R

        # 5. INTEGRATION & RESULTS
        method = "Washer Method" if r != 0 else "Disk Method"
        integrand = sp.simplify(R**2 - r**2)
        volume_exact = sp.pi * sp.integrate(integrand, (var, a, b))

        # 6. UI OUTPUT
        st.success(f"Method: {method}")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Step-by-Step")
            st.write(f"**Step 1: Variables** (Rotating about {'Y' if is_y_axis else 'X'}-axis, integrating with d{var})")
            st.write("**Step 2: Setup**")
            st.latex(rf"V = \pi \int_{{{sp.latex(a)}}}^{{{sp.latex(b)}}} [({sp.latex(R)})^2 - ({sp.latex(r)})^2] \, d{var}")
            st.write("**Step 3: Evaluation**")
            st.latex(rf"V = {sp.latex(volume_exact)} \approx {float(volume_exact.evalf()):.4f}")

        with col2:
            st.subheader("📊 3D Visualization")
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            u = np.linspace(float(a), float(b), 30)
            v = np.linspace(0, 2*np.pi, 30)
            U, V = np.meshgrid(u, v)
            r_numeric = sp.lambdify(var, R, 'numpy')(U)
            
            if is_y_axis:
                X, Y, Z = r_numeric*np.cos(V), U, r_numeric*np.sin(V)
            else:
                X, Y, Z = U, r_numeric*np.cos(V), r_numeric*np.sin(V)
            
            ax.plot_surface(X, Y, Z, color='cyan', alpha=0.6, edgecolor='black', lw=0.1)
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Logic Error: {e}. Please ensure the textbook prompt is complete.")
