import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import re

# Page Setup
st.set_page_config(page_title="Professional Volume Solver", layout="wide")
st.title("Calculus Volume Solver")

# Input Section - Starts blank as requested
raw_input = st.text_area("Paste your textbook question here:", height=150, value="",
                         placeholder="Example: y = 4 - x**2, y = 1, from x = 0 to x = sqrt(3) about y-axis")

if st.button("Generate Complete Solution"):
    if not raw_input.strip():
        st.warning("Please enter a question first.")
    else:
        try:
            # 1. TEXT CLEANING
            # Standardize notation: 'vx' -> 'sqrt(x)', '^' -> '**'
            clean_text = raw_input.lower().replace('vx', 'sqrt(x)').replace('v', 'sqrt').replace('^', '**')
            
            # 2. EXTRACTION
            # Find equations (y=... or x=...)
            eq_found = re.findall(r'[yx]\s*=\s*([^, \n]+)', clean_text)
            # Find numerical limits or sqrt expressions
            limit_strings = re.findall(r"sqrt\(\d+\)|\d+\.?\d*", clean_text)
            
            x, y = sp.symbols('x y')
            is_y_axis = any(word in clean_text for word in ['y-axis', 'about y', 'around y'])
            var = y if is_y_axis else x

            # 3. TRANSFORMATION (Variable Logic)
            raw_exprs = [sp.sympify(e) for e in eq_found]
            final_exprs = []
            
            for expr in raw_exprs:
                if is_y_axis and 'x' in str(expr):
                    # Rotate about Y-axis requires x = f(y)
                    sols = sp.solve(sp.Eq(y, expr), x)
                    final_exprs.append(sols[-1]) # Usually the positive/outer branch
                else:
                    final_exprs.append(expr)

            f_expr = final_exprs[0]
            g_expr = final_exprs[1] if len(final_exprs) > 1 else sp.sympify(0)

            # 4. LIMIT IDENTIFICATION
            a_sym = sp.sympify(limit_strings[0]) if len(limit_strings) >= 1 else sp.Integer(0)
            b_sym = sp.sympify(limit_strings[1]) if len(limit_strings) >= 2 else sp.Integer(1)
            
            # 5. R vs r LOGIC (Precision Check)
            # Compare values at midpoint to ensure the outer radius is R
            test_val = (float(a_sym.evalf()) + float(b_sym.evalf())) / 2
            val_f = float(f_expr.subs(var, test_val).evalf())
            val_g = float(g_expr.subs(var, test_val).evalf())
            
            R_outer, r_inner = (f_expr, g_expr) if val_f >= val_g else (g_expr, f_expr)
            method = "Washer Method" if r_inner != 0 else "Disk Method"

            # 6. INTEGRATION MATH
            integrand = sp.simplify(R_outer**2 - r_inner**2)
            antideriv = sp.integrate(integrand, var)
            # Final result wrapped in Abs() for physical accuracy
            volume_exact = sp.pi * sp.Abs(sp.integrate(integrand, (var, a_sym, b_sym)))

            # 7. DISPLAY RESULTS
            st.success(f"✅ Identified: **{method}**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📝 Step-by-Step Solution")
                st.write("**1. Integral Setup:**")
                st.latex(rf"V = \pi \int_{{{sp.latex(a_sym)}}}^{{{sp.latex(b_sym)}}} [({sp.latex(R_outer)})^2 - ({sp.latex(r_inner)})^2] \, d{var}")
                
                st.write("**2. Simplified Integrand:**")
                st.latex(rf"V = \pi \int ({sp.latex(integrand)}) \, d{var}")
                
                st.write("**3. Anti-derivative Result:**")
                st.latex(rf"V = \pi \left[ {sp.latex(antideriv)} \right]_{{{sp.latex(a_sym)}}}^{{{sp.latex(b_sym)}}}")
                
                st.write("**4. Final Exact Volume:**")
                st.latex(rf"V = {sp.latex(sp.simplify(volume_exact))} \approx {float(volume_exact.evalf()):.4f}")

            with col2:
                st.subheader("📊 3D Visualization")
                fig = plt.figure(figsize=(8, 6))
                ax = fig.add_subplot(111, projection='3d')
                
                # Mesh for Plotting
                u = np.linspace(float(a_sym.evalf()), float(b_sym.evalf()), 50)
                v = np.linspace(0, 2*np.pi, 50)
                U_mesh, V_mesh = np.meshgrid(u, v)
                
                # Outer Radius surface
                r_vals = sp.lambdify(var, R_outer, 'numpy')(U_mesh)
                
                if is_y_axis:
                    X_plot, Y_plot, Z_plot = r_vals*np.cos(V_mesh), U_mesh, r_vals*np.sin(V_mesh)
                else:
                    X_plot, Y_plot, Z_plot = U_mesh, r_vals*np.cos(V_mesh), r_vals*np.sin(V_mesh)
                    
                ax.plot_surface(X_plot, Y_plot, Z_plot, color='cyan', alpha=0.6, edgecolor='k', lw=0.1)
                st.pyplot(fig)

        except Exception as e:
            st.error(f"Error Analyzing Problem: {e}")
