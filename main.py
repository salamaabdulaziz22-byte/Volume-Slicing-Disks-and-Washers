import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import re

# Professional Layout
st.set_page_config(page_title="Ultimate Calculus Solver", layout="wide")
st.title("Volume of Revolution Solver")

raw_input = st.text_area("Paste your textbook question here:", height=150, 
                         placeholder="e.g., y = 4 - x**2, y = 1, from x = 0 to sqrt(3) about y-axis")

if st.button("Solve with 100% Precision"):
    if not raw_input.strip():
        st.warning("Please enter a question.")
    else:
        try:
            # 1. ADVANCED PRE-PROCESSING
            # Handles textbook shorthand like 'vx' (sqrt x) or 'v3' (sqrt 3)
            clean_text = raw_input.lower().replace('vx', 'sqrt(x)').replace('v', 'sqrt').replace('^', '**')
            
            # 2. FEATURE EXTRACTION
            eq_found = re.findall(r'[yx]\s*=\s*([^, \n]+)', clean_text)
            limits = re.findall(r"sqrt\(\d+\)|\d+\.?\d*", clean_text)
            is_y_axis = any(word in clean_text for word in ['y-axis', 'about y', 'around y'])
            
            x, y = sp.symbols('x y')
            
            # 3. BOUNDARY INTELLIGENCE
            # If rotating about y, we MUST solve for x and find y-bounds
            exprs = [sp.sympify(e) for e in eq_found]
            final_funcs = []
            
            for expr in exprs:
                if is_y_axis and 'x' in str(expr):
                    # Solve y = f(x) for x to get x = g(y)
                    sol = sp.solve(sp.Eq(y, expr), x)
                    final_funcs.append(sol[-1]) # Use the positive/right-hand branch
                else:
                    final_funcs.append(expr)

            # Assign Outer (R) and Inner (r) radii
            R_expr = final_funcs[0]
            r_expr = final_funcs[1] if len(final_funcs) > 1 else sp.Integer(0)
            
            # Determine correct integration variable
            var = y if is_y_axis else x
            
            # 4. LIMIT NORMALIZATION
            # Convert text limits (like 0 and sqrt(3)) into the correct integration variable
            # For Example 2.5: x=0 becomes y=4, and x=sqrt(3) becomes y=1
            if is_y_axis and 'x' in raw_input:
                raw_lim_a = sp.sympify(limits[0])
                raw_lim_b = sp.sympify(limits[1])
                # Find corresponding y-values for the given x-bounds
                y_a = exprs[0].subs(x, raw_lim_a)
                y_b = exprs[0].subs(x, raw_lim_b)
                a, b = (y_a, y_b) if y_a < y_b else (y_b, y_a)
            else:
                a = sp.sympify(limits[0]) if len(limits) >= 1 else 0
                b = sp.sympify(limits[1]) if len(limits) >= 2 else 1

            # 5. PHYSICAL VALIDITY CHECK (No negative volumes)
            mid = (float(a.evalf()) + float(b.evalf())) / 2
            val_R = float(R_expr.subs(var, mid).evalf())
            val_r = float(r_expr.subs(var, mid).evalf())
            
            if val_r > val_R:
                R_expr, r_expr = r_expr, R_expr # Swap to ensure R is Outer

            # 6. CALCULATIONS
            integrand = sp.simplify(R_expr**2 - r_expr**2)
            volume_exact = sp.pi * sp.integrate(integrand, (var, a, b))
            
            # 7. OUTPUT
            st.success(f"Method: {'Washer' if r_expr != 0 else 'Disk'}")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📝 Step-by-Step Solution")
                st.write("**1. Setup the Integral:**")
                st.latex(rf"V = \pi \int_{{{sp.latex(a)}}}^{{{sp.latex(b)}}} [({sp.latex(R_expr)})^2 - ({sp.latex(r_expr)})^2] \, d{var}")
                
                st.write("**2. Final Exact Result:**")
                st.latex(rf"V = {sp.latex(sp.simplify(volume_exact))} \approx {float(volume_exact.evalf()):.4f}")

            with col2:
                st.subheader("📊 Accurate 3D Visualization")
                fig = plt.figure()
                ax = fig.add_subplot(111, projection='3d')
                
                u = np.linspace(float(a.evalf()), float(b.evalf()), 50)
                v = np.linspace(0, 2*np.pi, 50)
                U, V = np.meshgrid(u, v)
                
                r_num = sp.lambdify(var, R_expr, 'numpy')(U)
                
                if is_y_axis:
                    X, Y, Z = r_num*np.cos(V), U, r_num*np.sin(V)
                else:
                    X, Y, Z = U, r_num*np.cos(V), r_num*np.sin(V)
                
                ax.plot_surface(X, Y, Z, color='cyan', alpha=0.7, edgecolor='k', lw=0.1)
                st.pyplot(fig)

        except Exception as e:
            st.error(f"Analysis failed: {e}. Please ensure equations like 'y = x**2' are clear.")
