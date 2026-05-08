import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="Professional Volume Solver", layout="wide")
st.title("Calculus Solver")

raw_input = st.text_area("Paste your textbook question:", height=150, 
                         placeholder="e.g., y = 4 - x**2, y = 1, from x = 0 to sqrt(3) about y-axis")

if st.button("Solve Everything"):
    try:
        # 1. THE CLEANER: Fixes common textbook typos/shorthand
        text = raw_input.lower().replace('vx', 'sqrt(x)').replace('v3', 'sqrt(3)').replace('^', '**')
        
        # 2. EXTRACTION: Find equations and numbers
        eq_parts = re.findall(r'[yx]\s*=\s*([^, \n]+)', text)
        nums_only = re.findall(r"sqrt\(\d+\)|\d+\.?\d*", text) # Finds numbers or sqrt(n)
        
        x, y = sp.symbols('x y')
        is_y_axis = 'y-axis' in text or 'about y' in text
        
        # 3. MATH LOGIC: Define functions
        f_expr = sp.sympify(eq_parts[0])
        g_expr = sp.sympify(eq_parts[1]) if len(eq_parts) > 1 else sp.sympify(0)
        
        # 4. LIMITS: Convert textbook limits to actual numbers
        # If user writes 'sqrt(3)', we calculate its value for the graph
        limit_a = float(sp.sympify(nums_only[0]).evalf()) if len(nums_only) >= 1 else 0
        limit_b = float(sp.sympify(nums_only[1]).evalf()) if len(nums_only) >= 2 else 1

        # 5. REVOLUTION LOGIC: Swap variables if rotating about Y
        var = y if is_y_axis else x
        if is_y_axis and 'x' in str(f_expr):
            # Example 2.5 logic: if y = 4-x^2, solve for x -> sqrt(4-y)
            f_expr = sp.solve(sp.Eq(y, f_expr), x)[-1] # Take positive branch
            if g_expr != 0 and 'x' in str(g_expr):
                g_expr = sp.solve(sp.Eq(y, g_expr), x)[-1]
        
        # 6. DISPLAY RESULTS
        st.success(f"Method: {'Washer' if g_expr != 0 else 'Disk'}")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Calculus Steps")
            integrand = sp.simplify(f_expr**2 - g_expr**2)
            st.latex(rf"V = \pi \int_{{{limit_a}}}^{{{limit_b}}} ({sp.latex(integrand)}) \, d{var}")
            
            # Use sympify limits for exact fraction result (like 4.5pi)
            exact_a, exact_b = sp.sympify(nums_only[0]), sp.sympify(nums_only[1])
            volume_exact = sp.pi * sp.integrate(integrand, (var, exact_a, exact_b))
            
            st.write("**Final Answer:**")
            st.latex(rf"V = {sp.latex(sp.simplify(volume_exact))} \approx {float(volume_exact.evalf()):.4f}")

        with col2:
            st.subheader("📊 3D Visualization")
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            
            u = np.linspace(limit_a, limit_b, 40)
            v = np.linspace(0, 2*np.pi, 40)
            U, V = np.meshgrid(u, v)
            
            # Vectorize for numpy
            r_func = sp.lambdify(var, f_expr, 'numpy')
            R = r_func(U)
            
            if is_y_axis:
                X, Y, Z = R*np.cos(V), U, R*np.sin(V)
            else:
                X, Y, Z = U, R*np.cos(V), R*np.sin(V)
                
            ax.plot_surface(X, Y, Z, color='orchid', alpha=0.7)
            st.pyplot(fig)
            
    except Exception as e:
        st.error(f"Logic Error: {e}. Please ensure equations are clear (e.g. y = x**2).")
