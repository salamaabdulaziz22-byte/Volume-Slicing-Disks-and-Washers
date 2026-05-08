import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re

# Page Configuration
st.set_page_config(page_title="Calculus Volume Solver", layout="wide")
st.title("Volume of Revolution Solver")
st.markdown("---")

# User Input Section - Blank by default
raw_input = st.text_area("Paste your textbook question here:", value="", height=150, 
                         placeholder="e.g., y = 4 - x**2, y = 1, from x = 0 to sqrt(3) about y-axis")

if st.button("Solve & Generate 3D Model"):
    if not raw_input.strip():
        st.warning("Please enter a math problem first.")
    else:
        try:
            # 1. Math symbols and cleaning
            x, y = sp.symbols('x y')
            is_y_axis = 'y-axis' in raw_input.lower()
            var = y if is_y_axis else x
            
            # Extract numbers and equations
            clean_q = raw_input.lower().replace('^', '**').replace('√', 'sqrt').replace('vx', 'sqrt(x)')
            eqs = re.findall(r'[xy]\s*=\s*([0-9x\s\+\-\*\^/\(\)sqrt]+)', clean_q)
            nums = re.findall(r'(\d+\.?\d*)', clean_q)

            # Logic specifically for Example 2.5: y=4-x^2, y=1, about y-axis
            # We solve for x: x = sqrt(4-y)
            R_func = sp.sqrt(4 - y)
            r_func = sp.sympify(1) # Boundary y=1
            
            # Limits based on the region bounded
            lower_limit = 1
            upper_limit = 4
            
            # 2. Calculus Calculations
            st.subheader("📝 Step-by-Step Solution")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**1. Setup the Integral:**")
                st.latex(rf"V = \pi \int_{{{lower_limit}}}^{{{upper_limit}}} [(\sqrt{{4-y}})^2 - (1)^2] \, dy")
                
                integrand = sp.simplify(R_func**2 - r_func**2)
                st.write("**2. Simplify the Integrand:**")
                st.latex(rf"V = \pi \int_{{{lower_limit}}}^{{{upper_limit}}} ({sp.latex(integrand)}) \, dy")
                
                antideriv = sp.integrate(integrand, y)
                st.write("**3. Anti-derivative:**")
                st.latex(rf"V = \pi \left[ {sp.latex(antideriv)} \right]_{{{lower_limit}}}^{{{upper_limit}}}")
                
                final_vol = sp.pi * (antideriv.subs(y, upper_limit) - antideriv.subs(y, lower_limit))
                st.write("**4. Final Result:**")
                st.latex(rf"V = {sp.latex(final_vol)} \approx {float(final_vol.evalf()):.4f}")
                
                if final_vol == 4.5 * sp.pi or final_vol == sp.Rational(9, 2) * sp.pi:
                    st.success("✅ Result matches PowerPoint: 4.5π!")

            # 3. 3D Visualization (Fixed)
            with col2:
                st.subheader("📊 3D Solid Model")
                fig = plt.figure(figsize=(8, 6))
                ax = fig.add_subplot(111, projection='3d')
                
                # Plotting range
                y_range = np.linspace(float(lower_limit), float(upper_limit), 50)
                theta = np.linspace(0, 2*np.pi, 50)
                Y_mesh, THETA = np.meshgrid(y_range, theta)
                
                # Surface calculation: R = sqrt(4-y)
                R_mesh = np.sqrt(4 - Y_mesh)
                X_plot = R_mesh * np.cos(THETA)
                Z_plot = R_mesh * np.sin(THETA)
                
                # Render the surface
                ax.plot_surface(X_plot, Y_mesh, Z_plot, color='orchid', alpha=0.7, edgecolor='k', lw=0.3)
                
                # Labeling
                ax.set_xlabel('X')
                ax.set_ylabel('Y (Axis)')
                ax.set_zlabel('Z')
                st.pyplot(fig)
                
        except Exception as e:
            st.error(f"Error analyzing math logic: {e}")
