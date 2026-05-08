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
                         placeholder="e.g., y = sqrt(x), from x = 0 to 4 about x-axis")

def clean_expression(expr_str):
    """Clean the extracted string to make it SymPy compatible."""
    # Handle 'Vx' or 'vx' as sqrt(x)
    expr_str = re.sub(r'[vV][xX]', 'sqrt(x)', expr_str)
    # Basic cleanup
    expr_str = expr_str.replace('^', '**').replace('√', 'sqrt')
    # Remove common words that might get caught in the regex
    stop_words = ['on', 'the', 'interval', 'between', 'from', 'to', 'about']
    for word in stop_words:
        expr_str = re.sub(rf'\b{word}\b', '', expr_str)
    return expr_str.strip()

def solve_calculus():
    try:
        # 1. Text Pre-processing
        text = raw_input.lower()
        x_sym, y_sym = sp.symbols('x y')
        
        # Extract numbers (limits)
        numbers = [float(n) for n in re.findall(r"[-+]?\d*\.\d+|\d+", text)]
        
        # Identify Problem Type
        is_about_y = "about y-axis" in text or "about the y axis" in text
        is_pyramid = "pyramid" in text
        
        st.subheader("📝 Mathematical Solution (Step-by-Step)")
        col1, col2 = st.columns([1, 1])

        with col1:
            if is_pyramid:
                # Pyramid Logic (Example 2.1)
                side = max(numbers) if numbers else 180
                height = min([n for n in numbers if n != side and n != 0] + [100])
                
                st.write("**1. Define the Side Length Function:**")
                f_x = (side/height) * (height - x_sym)
                st.latex(rf"f(x) = {sp.latex(f_x)}")
                
                a, b = 0, height
                integrand = f_x**2
                var = x_sym
                final_multiplier = 1 
            else:
                # Disk/Washer Method Logic
                # Improved Regex: Look for y=... or x=... and stop at comma or common words
                func_matches = re.findall(r"(?:y|x|f\(x\)|g\(y\))\s*=\s*([^,; \n]+(?:(?!\bon\b|\bthe\b|\binterval\b).)*)", text)
                
                if not func_matches:
                    st.error("Could not find an equation (e.g., y = ...).")
                    return

                # Clean the first expression found
                expr_cleaned = clean_expression(func_matches[0])
                f_expr = sp.sympify(expr_cleaned)
                g_expr = sp.sympify(0) # Default second function
                
                # Determine Limits
                a = min(numbers) if len(numbers) >= 2 else 0
                b = max(numbers) if len(numbers) >= 2 else 1
                
                if is_about_y:
                    st.write("**Type:** Rotation about the **y-axis**")
                    var = y_sym
                    if 'x' in str(f_expr):
                        # Solve y = f(x) for x to get x = g(y)
                        f_expr = sp.solve(sp.Eq(y_sym, f_expr), x_sym)[0]
                else:
                    st.write("**Type:** Rotation about the **x-axis**")
                    var = x_sym

                integrand = sp.simplify(f_expr**2 - g_expr**2)
                final_multiplier = sp.pi
                
                st.write("**1. Setup the Integral:**")
                st.latex(rf"V = \pi \int_{{{a}}}^{{{b}}} \left( {sp.latex(f_expr)} \right)^2 d{var}")

            # Calculations
            antideriv = sp.integrate(integrand, var)
            definite_val = sp.integrate(integrand, (var, a, b))
            final_vol = definite_val * final_multiplier
            
            st.write("**2. Anti-derivative:**")
            st.latex(rf"F({var}) = {sp.latex(antideriv)}")
            
            st.write("**3. Evaluate and Result:**")
            st.latex(rf"V = {sp.latex(sp.simplify(final_vol))} \approx {float(final_vol.evalf()):,.4f}")

        # 3. 3D Visualization
        with col2:
            st.subheader("📊 3D Model")
            fig = plt.figure(figsize=(8, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            u_vals = np.linspace(float(a), float(b), 50)
            v_vals = np.linspace(0, 2*np.pi, 50)
            U, V = np.meshgrid(u_vals, v_vals)
            
            f_num = sp.lambdify(var, f_expr if not is_pyramid else sp.sqrt(integrand), 'numpy')
            R = f_num(U)
            
            if is_about_y or is_pyramid:
                X_p, Y_p, Z_p = R*np.cos(V), U, R*np.sin(V)
            else:
                X_p, Y_p, Z_p = U, R*np.cos(V), R*np.sin(V)
                
            ax.plot_surface(X_p, Y_p, Z_p, cmap='winter', alpha=0.7)
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Error: {e}")

if st.button("Analyze & Solve"):
    if raw_input.strip():
        solve_calculus()
    else:
        st.warning("Please enter a question.")
