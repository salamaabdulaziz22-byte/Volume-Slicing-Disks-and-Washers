import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re

# Page Configuration
st.set_page_config(page_title="Universal Calculus Solver", layout="wide")
st.title("Calculus Volume Solver")

raw_input = st.text_area("Paste your problem here:", height=150, 
                         placeholder="e.g., y = 4 - x^2 and y = 1 from x = 0 to x = V3 about the y-axis")

def solve_calculus():
    try:
        # Pre-process text to handle math shorthand like V3 or Vx
        processed_text = raw_input.lower()
        processed_text = re.sub(r'[vV](\d+)', r'sqrt(\1)', processed_text)
        processed_text = re.sub(r'[vV][xX]', 'sqrt(x)', processed_text)
        processed_text = processed_text.replace('^', '**').replace('√', 'sqrt')

        x_s, y_s = sp.symbols('x y')
        
        # 1. Detection of Axis
        is_about_y = "y-axis" in processed_text or "y axis" in processed_text
        
        # 2. Advanced Equation Extraction
        # Finds patterns like y=..., x=..., f(x)=...
        eq_matches = re.findall(r'(?:y|x|f\(x\)|g\(y\))\s*=\s*([^,; \n\t\r]+(?:(?!\band\b|\bfrom\b|\bto\b|\babout\b).)*)', processed_text)
        exprs = [sp.sympify(e) for e in eq_matches]
        
        if len(exprs) < 1:
            st.error("No equations found. Please use the format 'y = 4 - x^2'.")
            return

        f_x = exprs[0]
        g_x = exprs[1] if len(exprs) > 1 else sp.sympify(0)

        # 3. Dynamic Limit Detection
        # Looks for numbers or sqrt expressions
        limit_finds = re.findall(r"(?:sqrt\(\d+\)|\d+\.?\d*)", processed_text)
        limit_vals = [sp.sympify(l) for l in limit_finds]
        
        # If text says from x=0 to x=V3, we take the last two numbers found
        a_limit = limit_vals[-2] if len(limit_vals) >= 2 else sp.Integer(0)
        b_limit = limit_vals[-1] if len(limit_vals) >= 2 else sp.Integer(1)

        st.subheader("📝 Mathematical Solution")
        col1, col2 = st.columns(2)

        with col1:
            if is_about_y:
                # Washer Method (Rotating about y-axis)
                # Solve for x: x^2 = 4 - y
                f_y_sq = sp.solve(sp.Eq(y_s, f_x), x_s**2)[0] if 'x' in str(f_x) else f_x**2
                g_y_sq = sp.solve(sp.Eq(y_s, g_x), x_s**2)[0] if 'x' in str(g_x) and g_x != 0 else g_x**2
                
                # Determine Y-limits from the bounding functions
                # If y = 4-x^2 and y=1, boundaries are 1 and 4
                y_bounds = [float(f_x.subs(x_s, a_limit)), float(f_x.subs(x_s, b_limit))]
                if g_x != 0:
                    y_bounds.append(float(g_x.subs(x_s, a_limit)))
                
                y_low, y_high = min(y_bounds), max(y_bounds)
                
                # Check if the user mentioned "y = 1" specifically
                if "y = 1" in processed_text: y_low = 1.0

                integrand = sp.simplify(f_y_sq - g_y_sq)
                var = y_s
                
                st.write("**Step 1: Express functions in terms of $y$**")
                st.latex(rf"R(y)^2 = {sp.latex(f_y_sq)}")
                st.write(f"**Step 2: Setup Integral from $y={y_low}$ to $y={y_high}$**")
                st.latex(rf"V = \pi \int_{{{y_low}}}^{{{y_high}}} ({sp.latex(integrand)}) \, dy")
            else:
                # Disk Method (Rotating about x-axis)
                integrand = sp.simplify(f_x**2 - g_x**2)
                var = x_s
                y_low, y_high = float(a_limit), float(b_limit)
                st.latex(rf"V = \pi \int_{{{y_low}}}^{{{y_high}}} ({sp.latex(f_x)}^2 - {sp.latex(g_x)}^2) \, dx")

            # Final Integration
            antideriv = sp.integrate(integrand, var)
            definite_integral = sp.integrate(integrand, (var, y_low, y_high))
            final_volume = definite_integral * sp.pi

            st.write("**Step 3: Evaluate Integral**")
            st.latex(rf"V = \pi \left[ {sp.latex(antideriv)} \right]_{{{y_low}}}^{{{y_high}}}")
            st.write("**Step 4: Final Result**")
            st.success(f"Calculated Volume: {final_volume}")
            st.latex(rf"V = {sp.latex(sp.simplify(final_volume))} \approx {float(final_volume.evalf()):,.4f}")

        with col2:
            st.subheader("📊 3D Visualization")
            fig = plt.figure(figsize=(7,7))
            ax = fig.add_subplot(111, projection='3d')
            
            u_space = np.linspace(float(y_low), float(y_high), 40)
            v_space = np.linspace(0, 2*np.pi, 40)
            U, V = np.meshgrid(u_space, v_space)
            
            # Surface calculation
            r_sq_val = sp.lambdify(var, f_y_sq if is_about_y else f_x**2, 'numpy')
            R = np.sqrt(np.abs(r_sq_val(U)))
            
            if is_about_y:
                X, Y, Z = R*np.cos(V), U, R*np.sin(V)
            else:
                X, Y, Z = U, R*np.cos(V), R*np.sin(V)
            
            ax.plot_surface(X, Y, Z, color='orchid', alpha=0.7, edgecolor='k', lw=0.1)
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Error: {e}")

if st.button("Solve & Generate 3D"):
    if raw_input:
        solve_calculus()
    else:
        st.warning("Please enter a math problem first.")
