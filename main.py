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

def solve_calculus():
    try:
        # 1. Text Pre-processing
        text = raw_input.lower()
        x, y, z = sp.symbols('x y z')
        
        # Extract numbers (limits/dimensions)
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
                
                st.write(f"**1. Define the Side Length Function:**")
                st.write(f"Since the base is square and tapers linearly to the height:")
                f_x = (side/height) * (height - x)
                st.latex(rf"f(x) = {sp.latex(f_x)}")
                
                st.write("**2. Area Function A(x):**")
                a_x = f_x**2
                st.latex(rf"A(x) = [f(x)]^2 = ({sp.latex(f_x)})^2")
                
                a, b = 0, height
                integrand = a_x
                var = x
                final_multiplier = 1 # No Pi for square pyramids

            else:
                # Disk/Washer Method Logic (Example 2.4 & 2.5)
                # Extracting equations (looks for y=... or x=...)
                func_matches = re.findall(r"(?:y|f\(x\)|x|g\(y\))\s*=\s*([^,]+)", text)
                exprs = [sp.sympify(m.replace('^', '**').replace('√', 'sqrt').strip()) for m in func_matches]
                
                if not exprs:
                    st.error("Could not identify functions. Please use format 'y = x**2'.")
                    return

                f_expr = exprs[0]
                g_expr = exprs[1] if len(exprs) > 1 else sp.sympify(0)
                
                # Default limits if not clearly found
                a = min(numbers) if len(numbers) >= 2 else 0
                b = max(numbers) if len(numbers) >= 2 else 1
                
                if is_about_y:
                    st.write("**Type:** Rotation about the **y-axis**")
                    var = y
                    # Convert f(x) to f(y) if necessary
                    if 'x' in str(f_expr):
                        f_expr = sp.solve(sp.Eq(y, f_expr), x)[0]
                else:
                    st.write("**Type:** Rotation about the **x-axis**")
                    var = x

                integrand = sp.simplify(f_expr**2 - g_expr**2)
                final_multiplier = sp.pi
                
                st.write("**1. Setup the Integral:**")
                st.latex(rf"V = \pi \int_{{{a}}}^{{{b}}} \left( [{sp.latex(f_expr)}]^2 - [{sp.latex(g_expr)}]^2 \right) d{var}")

            # Perform Integration
            antideriv = sp.integrate(integrand, var)
            definite_integral = sp.integrate(integrand, (var, a, b))
            result = definite_integral * final_multiplier
            
            st.write("**2. Anti-derivative:**")
            st.latex(rf"{sp.latex(antideriv)}")
            
            st.write("**3. Final Volume:**")
            st.success(f"Calculation Complete")
            st.latex(rf"V = {sp.latex(sp.simplify(result))} \approx {float(result.evalf()):,.2f}")

        # 3. 3D Visualization
        with col2:
            st.subheader("📊 3D Visualization")
            fig = plt.figure(figsize=(8, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            u_vals = np.linspace(float(a), float(b), 60)
            v_vals = np.linspace(0, 2 * np.pi, 60)
            U, V = np.meshgrid(u_vals, v_vals)
            
            # Lambdify for plotting
            f_num = sp.lambdify(var, f_expr if not is_pyramid else sp.sqrt(integrand), 'numpy')
            R = f_num(U)
            
            if is_about_y or is_pyramid:
                X_p = R * np.cos(V)
                Z_p = R * np.sin(V)
                Y_p = U
            else:
                X_p = U
                Y_p = R * np.cos(V)
                Z_p = R * np.sin(V)
                
            ax.plot_surface(X_p, Y_p, Z_p, cmap='viridis', alpha=0.8, edgecolor='none')
            ax.set_title("Generated 3D Solid")
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Analysis Error: {e}")
        st.info("Tip: Ensure your equation is clear, e.g., 'y = x**2' or 'y = 4 - x**2'.")

if st.button("Analyze & Solve"):
    if raw_input:
        solve_calculus()
    else:
        st.warning("Please enter a problem description first.")
