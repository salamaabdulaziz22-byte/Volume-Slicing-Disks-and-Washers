import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re

# Page Configuration
st.set_page_config(page_title="Math Solver Pro", layout="wide")
st.title("Advanced Calculus Volume Solver")
st.markdown("Paste your problem below, and I will analyze, solve, and visualize it in 3D.")

# User Input
raw_input = st.text_area("Paste your calculus problem here:", height=150, 
                         placeholder="e.g., y = 4 - x^2 and y = 1 from x = 0 to x = sqrt(3) about y-axis")

def clean_math_string(s):
    """Converts common textbook shorthand to SymPy readable math."""
    s = s.lower()
    # Replace V3 with sqrt(3), Vx with sqrt(x)
    s = re.sub(r'[vV](\d+)', r'sqrt(\1)', s)
    s = re.sub(r'[vV][xX]', 'sqrt(x)', s)
    s = s.replace('^', '**').replace('√', 'sqrt')
    return s

def solve_calculus():
    try:
        text = raw_input.lower()
        x_sym, y_sym = sp.symbols('x y')
        
        # 1. Identify Rotation Axis
        is_about_y = "about y-axis" in text or "about the y axis" in text
        
        # 2. Extract Equations (Split by 'and', 'from', or commas)
        # This regex looks for y=... or x=... patterns
        raw_equations = re.findall(r'(?:y|f\(x\)|x|g\(y\))\s*=\s*([^,; \n\t\r]+(?:(?!\band\b|\bfrom\b|\bto\b|\babout\b).)*)', text)
        
        cleaned_exprs = []
        for eq in raw_equations:
            clean_eq = clean_math_string(eq)
            try:
                cleaned_exprs.append(sp.sympify(clean_eq))
            except:
                continue

        if not cleaned_exprs:
            st.error("Could not parse equations. Try writing them as y = 4 - x**2.")
            return

        # Assign f(x) and g(x)
        f_expr = cleaned_exprs[0]
        g_expr = cleaned_exprs[1] if len(cleaned_exprs) > 1 else sp.sympify(0)

        # 3. Extract Limits (Numbers or sqrt expressions)
        # We look for numbers or patterns like sqrt(3)
        limit_matches = re.findall(r"(?:sqrt\(\d+\)|\d+\.?\d*)", clean_math_string(text))
        nums = [sp.sympify(n) for n in limit_matches]
        
        # Usually, the first two numbers found after 'from' or 'x=' are the limits
        a = nums[-2] if len(nums) >= 2 else 0
        b = nums[-1] if len(nums) >= 2 else 1

        st.subheader("📝 Mathematical Solution (Step-by-Step)")
        col1, col2 = st.columns([1, 1])

        with col1:
            if is_about_y:
                st.write("**Method:** Washer Method (Rotating about y-axis)")
                var = y_sym
                # If equations are in terms of x, solve for x
                f_in_y = sp.solve(sp.Eq(y_sym, f_expr), x_sym)[0] if 'x' in str(f_expr) else f_expr
                g_in_y = sp.solve(sp.Eq(y_sym, g_expr), x_sym)[0] if 'x' in str(g_expr) and g_expr != 0 else g_expr
                
                # Note: In Example 2.5, boundaries are often given in y. 
                # If the user says from x=0 to x=V3, we might need the y-limits
                # Let's calculate y-limits based on the functions if they aren't clear
                y_start = float(min(f_expr.subs(x_sym, float(a)), f_expr.subs(x_sym, float(b))))
                y_end = float(max(f_expr.subs(x_sym, float(a)), f_expr.subs(x_sym, float(b))))
                
                # Check if user provided y-limits directly
                limit_a, limit_b = float(a), float(b) 
                # (Logic adjustment for Example 2.5: y goes from 1 to 4)
                if limit_a == 0: # Common for x-limits, but we need y-limits
                    limit_a, limit_b = y_start, y_end

                integrand = sp.simplify(f_in_y**2 - g_in_y**2)
                st.write("**1. Setup Integral (in terms of y):**")
                st.latex(rf"V = \pi \int_{{{limit_a}}}^{{{limit_b}}} \left( {sp.latex(f_in_y)} \right)^2 - \left( {sp.latex(g_in_y)} \right)^2 \, dy")
            else:
                st.write("**Method:** Disk/Washer Method (Rotating about x-axis)")
                var = x_sym
                limit_a, limit_b = float(a), float(b)
                integrand = sp.simplify(f_expr**2 - g_expr**2)
                st.write("**1. Setup Integral:**")
                st.latex(rf"V = \pi \int_{{{limit_a}}}^{{{limit_b}}} ({sp.latex(f_expr)})^2 - ({sp.latex(g_expr)})^2 \, dx")

            # Integration steps
            antideriv = sp.integrate(integrand, var)
            definite = sp.integrate(integrand, (var, limit_a, limit_b))
            final_vol = definite * sp.pi

            st.write("**2. Anti-derivative:**")
            st.latex(rf"F({var}) = \pi \left( {sp.latex(antideriv)} \right)")
            
            st.write("**3. Final Result:**")
            st.success(f"Volume Calculated")
            st.latex(rf"V = {sp.latex(sp.simplify(final_vol))} \approx {float(final_vol.evalf()):,.4f}")

        # 4. 3D Visualization
        with col2:
            st.subheader("📊 3D Model")
            fig = plt.figure(figsize=(8, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            u = np.linspace(float(limit_a), float(limit_b), 50)
            v = np.linspace(0, 2*np.pi, 50)
            U, V = np.meshgrid(u, v)
            
            # Radii for outer and inner surfaces
            r_outer = sp.lambdify(var, f_in_y if is_about_y else f_expr, 'numpy')(U)
            r_inner = sp.lambdify(var, g_in_y if is_about_y else g_expr, 'numpy')(U)
            
            if is_about_y:
                X_o, Y_o, Z_o = r_outer*np.cos(V), U, r_outer*np.sin(V)
                X_i, Y_i, Z_i = r_inner*np.cos(V), U, r_inner*np.sin(V)
            else:
                X_o, Y_o, Z_o = U, r_outer*np.cos(V), r_outer*np.sin(V)
                X_i, Y_i, Z_i = U, r_inner*np.cos(V), r_inner*np.sin(V)

            ax.plot_surface(X_o, Y_o, Z_o, color='cyan', alpha=0.6, label='Outer')
            if g_expr != 0:
                ax.plot_surface(X_i, Y_i, Z_i, color='red', alpha=0.3, label='Inner')
            
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Error analyzing: {e}")

if st.button("Analyze & Solve"):
    if raw_input.strip():
        solve_calculus()
