import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import re

# Professional Header for your STEM Portfolio
st.set_page_config(page_title="Volume Solver Pro", layout="wide")
st.title("Volume of Revolution Solver")
st.write("Step-by-step solution for Disks and Washers (Lesson 6-2)")

# Input Section
raw_input = st.text_area("Enter your problem here:", height=120, 
                         placeholder="e.g., y=x**2, y=4, about y-axis")

if st.button("Calculate Final Solution"):
    try:
        # --- 1. INITIALIZATION ---
        x, y = sp.symbols('x y')
        text = raw_input.lower().replace('^', '**').replace('vx', 'sqrt(x)')
        
        # Determine Axis
        is_y_axis = any(word in text for word in ['y-axis', 'about y', 'vertical'])
        var = y if is_y_axis else x
        
        # --- 2. EXTRACT & TRANSFORM EQUATIONS ---
        # Find everything that looks like an equation
        eq_patterns = re.findall(r'[yx]\s*=\s*([^, \n]+)', text)
        if not eq_patterns:
            st.error("Error: No equations found. Please use y=... or x=...")
            st.stop()
            
        raw_exprs = [sp.sympify(e) for e in eq_patterns]
        
        # Convert functions to match the axis of rotation
        final_funcs = []
        for expr in raw_exprs:
            if is_y_axis and 'x' in str(expr):
                # Solving y = f(x) for x to get x = g(y)
                sol = sp.solve(sp.Eq(y, expr), x)
                final_funcs.append(sol[-1]) # Take the right-side branch
            elif not is_y_axis and 'y' in str(expr):
                # Solving x = g(y) for y to get y = f(x)
                sol = sp.solve(sp.Eq(x, expr), y)
                final_funcs.append(sol[-1])
            else:
                final_funcs.append(expr)

        # --- 3. FIND BOUNDARIES (INTERSECTIONS) ---
        if len(final_funcs) >= 2:
            pts = sp.solve(sp.Eq(final_funcs[0], final_funcs[1]), var)
        else:
            pts = sp.solve(sp.Eq(final_funcs[0], 0), var)
            
        # Get real numerical values for the limits
        real_pts = [p.evalf() for p in pts if p.is_real]
        if real_pts:
            a, b = min(real_pts), max(real_pts)
        else:
            # Look for explicit numbers in text as a backup
            nums = re.findall(r"sqrt\(\d+\)|\d+\.?\d*", text)
            a, b = sp.sympify(nums[-2]), sp.sympify(nums[-1])

        # --- 4. DETERMINE R AND r ---
        R_outer = final_funcs[0]
        r_inner = final_funcs[1] if len(final_funcs) > 1 else sp.Integer(0)
        
        # Test which is bigger at the midpoint to prevent negative volume
        mid = (float(a) + float(b)) / 2
        if abs(float(R_outer.subs(var, mid))) < abs(float(r_inner.subs(var, mid))):
            R_outer, r_inner = r_inner, R_outer

        # --- 5. CALCULUS & OUTPUT ---
        method = "Washer Method" if r_inner != 0 else "Disk Method"
        integrand = sp.simplify(R_outer**2 - r_inner**2)
        volume_exact = sp.pi * sp.integrate(integrand, (var, a, b))

        st.success(f"Successfully identified the **{method}**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📝 Step-by-Step Steps")
            st.write(f"**Integration Variable:** d{var}")
            st.write(f"**Limits of Integration:** from {a} to {b}")
            
            st.write("**1. Setup:**")
            st.latex(rf"V = \pi \int_{{{sp.latex(a)}}}^{{{sp.latex(b)}}} [({sp.latex(R_outer)})^2 - ({sp.latex(r_inner)})^2] \, d{var}")
            
            st.write("**2. Integrated Value:**")
            st.latex(rf"V = {sp.latex(volume_exact)}")
            
            st.write("**3. Decimal Approximation:**")
            st.info(f"Volume ≈ {float(volume_exact.evalf()):.4f}")

        with col2:
            st.subheader("📊 3D Visual Result")
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            u_vals = np.linspace(float(a), float(b), 40)
            v_vals = np.linspace(0, 2*np.pi, 40)
            U, V = np.meshgrid(u_vals, v_vals)
            
            # Numeric conversion for plotting
            rad_func = sp.lambdify(var, R_outer, 'numpy')(U)
            
            if is_y_axis:
                X, Y, Z = rad_func*np.cos(V), U, rad_func*np.sin(V)
            else:
                X, Y, Z = U, rad_func*np.cos(V), rad_func*np.sin(V)
            
            ax.plot_surface(X, Y, Z, color='orchid', alpha=0.6, edgecolor='k', lw=0.1)
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Analysis Failed: {e}. Try entering the equations more clearly.")
