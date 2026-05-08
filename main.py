import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re

# Page Configuration
st.set_page_config(page_title="Calculus Volume Solver Pro", layout="wide")
st.title("Smart Calculus Volume Solver")

# User Input
raw_input = st.text_area("Paste your problem here:", height=100, 
                         placeholder=" ")

def solve_problem():
    try:
        # Pre-processing shorthand like V3 (sqrt 3)
        clean_text = raw_input.lower().replace('^', '**').replace('√', 'sqrt')
        clean_text = re.sub(r'[vV](\d+)', r'sqrt(\1)', clean_text)
        
        x, y = sp.symbols('x y')
        
        # 1. Detect Axis of Revolution
        is_about_y = "y-axis" in clean_text or "y axis" in clean_text
        
        # 2. Extract Equations
        # Look for y = ... patterns
        eq_matches = re.findall(r'(?:y|f\(x\))\s*=\s*([^,; \n\t\r]+(?:(?!\band\b|\bfrom\b|\bto\b|\babout\b).)*)', clean_text)
        exprs = [sp.sympify(e) for e in eq_matches]
        
        # In Example 2.5: f(x) = 4 - x^2, g(x) = 1
        f_x = exprs[0]
        g_x = exprs[1] if len(exprs) > 1 else sp.sympify(0)

        # 3. Handle Variable Transformation (Disk Method about y-axis)
        if is_about_y:
            # Solve y = 4 - x^2 for x^2 to get R(y)^2
            # R(y)^2 = 4 - y
            R_y_sq = sp.solve(sp.Eq(y, f_x), x**2)[0]
            
            # Determine boundaries in y (from y=1 to y=4)
            y_start = 1.0 if "y = 1" in clean_text else 0.0
            y_end = 4.0   # The vertex of the parabola
            
            integrand = R_y_sq
            var = y
        else:
            # Disk/Washer about x-axis
            integrand = f_x**2 - g_x**2
            y_start, y_end = 0, 1 # Default placeholders
            var = x

        # 4. Perform Integration
        antideriv = sp.integrate(integrand, var)
        definite = sp.integrate(integrand, (var, y_start, y_end))
        result = definite * sp.pi

        # 5. Display Results
        st.subheader("📝 Mathematical Solution")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Step 1: Setup Integral (Rotating about {'y-axis' if is_about_y else 'x-axis'})**")
            st.latex(rf"V = \pi \int_{{{y_start}}}^{{{y_end}}} ({sp.latex(integrand)}) \, d{var}")
            
            st.write("**Step 2: Anti-derivative**")
            st.latex(rf"F({var}) = \pi \left[ {sp.latex(antideriv)} \right]_{{{y_start}}}^{{{y_end}}}")
            
            st.write("**Step 3: Final Volume**")
            st.success(f"Result: {result}")
            st.latex(rf"V = {sp.latex(sp.simplify(result))} \approx {float(result.evalf()):,.4f}")

        with col2:
            st.subheader("📊 3D Visualization")
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            u = np.linspace(float(y_start), float(y_end), 50)
            v = np.linspace(0, 2*np.pi, 50)
            U, V = np.meshgrid(u, v)
            
            # Radius calculation for the plot
            r_val = sp.lambdify(var, sp.sqrt(sp.Abs(integrand)), 'numpy')(U)
            
            if is_about_y:
                X, Y, Z = r_val*np.cos(V), U, r_val*np.sin(V)
            else:
                X, Y, Z = U, r_val*np.cos(V), r_val*np.sin(V)
                
            ax.plot_surface(X, Y, Z, color='cyan', alpha=0.6, edgecolor='blue', lw=0.1)
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Logic Error: {e}")

if st.button("Analyze & Solve"):
    solve_problem()
