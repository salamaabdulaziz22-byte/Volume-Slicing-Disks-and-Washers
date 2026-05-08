import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re

# Page Configuration
st.set_page_config(page_title="Math Solver Pro", layout="wide")
st.title("Advanced Calculus Volume Solver")

# User Input
raw_input = st.text_area("Paste your calculus problem here:", height=150, 
                         placeholder=" ")

def solve_calculus():
    try:
        text = raw_input.lower()
        x_sym, y_sym = sp.symbols('x y')
        
        # 1. Detection of Rotation Axis (Crucial Fix)
        is_about_y = "y-axis" in text or "y axis" in text
        
        # 2. Extract Equations
        eq_patterns = re.findall(r'(?:y|x|f\(x\)|g\(y\))\s*=\s*([^,; \n\t\r]+(?:(?!\band\b|\bfrom\b|\bto\b|\babout\b).)*)', text)
        cleaned_exprs = [sp.sympify(e.replace('^', '**').replace('v', 'sqrt').replace('√', 'sqrt')) for e in eq_patterns]
        
        if not cleaned_exprs:
            st.error("Equations not found.")
            return

        f_expr = cleaned_exprs[0]
        g_expr = cleaned_exprs[1] if len(cleaned_exprs) > 1 else sp.sympify(0)

        # 3. Handle Limits and Variables
        num_matches = re.findall(r"(?:sqrt\(\d+\)|\d+\.?\d*)", text.replace('v', 'sqrt'))
        limits = [sp.sympify(n) for n in num_matches]
        
        st.subheader("📝 Mathematical Solution (Step-by-Step)")
        col1, col2 = st.columns([1, 1])

        with col1:
            if is_about_y:
                st.write("**Method:** Disk/Washer Method (Rotating about **y-axis**)")
                # Convert y = f(x) -> x = f(y)
                # For y = 4 - x^2 -> x = sqrt(4 - y)
                f_y = sp.solve(sp.Eq(y_sym, f_expr), x_sym)[0] if 'x' in str(f_expr) else f_expr
                g_y = sp.solve(sp.Eq(y_sym, g_expr), x_sym)[0] if 'x' in str(g_expr) and g_expr != 0 else g_expr
                
                # Determine y-limits
                # If x is 0 to sqrt(3), then y is 4-0=4 and 4-(sqrt(3))^2=1
                # We prioritize explicit numbers found in the text for limits
                a_val, b_val = (1, 4) if not limits else (min(limits), max(limits))
                # Auto-correction: if limits are x-limits, calculate y-limits
                if float(b_val) < 2: # Likely x-limits like sqrt(3) ~ 1.73
                    a_val = float(f_expr.subs(x_sym, b_val))
                    b_val = float(f_expr.subs(x_sym, a_val))

                integrand = sp.simplify(f_y**2 - g_y**2)
                var = y_sym
                st.write(f"**1. Transform to y-variable:** $x = {sp.latex(f_y)}$")
                st.latex(rf"V = \pi \int_{{{a_val}}}^{{{b_val}}} \left( {sp.latex(f_y)} \right)^2 dy")
            else:
                st.write("**Method:** Disk/Washer Method (Rotating about **x-axis**)")
                var = x_sym
                a_val, b_val = (0, 1) if not limits else (limits[0], limits[1])
                integrand = sp.simplify(f_expr**2 - g_expr**2)
                st.latex(rf"V = \pi \int_{{{a_val}}}^{{{b_val}}} ({sp.latex(f_expr)})^2 dx")

            # Final Calculation
            antideriv = sp.integrate(integrand, var)
            definite = sp.integrate(integrand, (var, a_val, b_val))
            final_vol = definite * sp.pi

            st.write("**2. Anti-derivative:**")
            st.latex(rf"F({var}) = \pi \left[ {sp.latex(antideriv)} \right]")
            st.write("**3. Final Result:**")
            st.success(f"Volume = {final_vol}")
            st.latex(rf"V = {sp.latex(sp.simplify(final_vol))} \approx {float(final_vol.evalf()):,.4f}")

        with col2:
            st.subheader("📊 3D Model")
            fig = plt.figure(figsize=(7, 7))
            ax = fig.add_subplot(111, projection='3d')
            u = np.linspace(float(a_val), float(b_val), 50)
            v = np.linspace(0, 2*np.pi, 50)
            U, V = np.meshgrid(u, v)
            
            radius_func = sp.lambdify(var, f_y if is_about_y else f_expr, 'numpy')
            R = radius_func(U)
            
            if is_about_y:
                X, Y, Z = R*np.cos(V), U, R*np.sin(V)
            else:
                X, Y, Z = U, R*np.cos(V), R*np.sin(V)
                
            ax.plot_surface(X, Y, Z, color='magenta', alpha=0.6)
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Error: {e}")

if st.button("Analyze & Solve"):
    solve_calculus()
