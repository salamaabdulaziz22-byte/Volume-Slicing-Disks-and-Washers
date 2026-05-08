import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import re

# 1. UI SETUP (Professional Grade)
st.set_page_config(page_title="Calculus Volume Solver", layout="wide")
st.title("Volume of Revolution Solver")
st.markdown("---")

# 2. INPUT SECTION
raw_input = st.text_area(
    "Paste your textbook problem here:", 
    height=150, 
    placeholder="e.g., y = 4 - x**2, y = 1, from x = 0 to x = sqrt(3) about the y-axis"
)

if st.button("Generate Complete Solution"):
    if not raw_input.strip():
        st.warning("Please enter a question to analyze.")
    else:
        try:
            # A. PRE-PROCESSING (Handling textbook shorthand)
            clean_text = raw_input.lower().replace('vx', 'sqrt(x)').replace('v', 'sqrt').replace('^', '**')
            
            # B. VARIABLE & AXIS DETECTION
            x, y = sp.symbols('x y')
            is_y_axis = any(word in clean_text for word in ['y-axis', 'about y', 'around y'])
            integration_var = y if is_y_axis else x
            
            # C. EXTRACTION & TRANSFORMATION
            # Find equations (e.g., y = 4-x**2)
            eq_found = re.findall(r'[yx]\s*=\s*([^, \n]+)', clean_text)
            raw_exprs = [sp.sympify(e) for e in eq_found]
            
            # If rotating about y-axis, we MUST have x in terms of y
            final_funcs = []
            for expr in raw_exprs:
                if is_y_axis and 'x' in str(expr):
                    sol = sp.solve(sp.Eq(y, expr), x)
                    final_funcs.append(sol[-1]) # Use positive/outer branch
                else:
                    final_funcs.append(expr)
            
            # D. BOUNDARY MAPPING (The Fix for 0.0000 results)
            limits = re.findall(r"sqrt\(\d+\)|\d+\.?\d*", clean_text)
            if is_y_axis and 'x' in raw_input and len(limits) >= 2:
                # Convert X-bounds to Y-bounds for vertical integration
                x_a, x_b = sp.sympify(limits[0]), sp.sympify(limits[1])
                y_a = raw_exprs[0].subs(x, x_a)
                y_b = raw_exprs[0].subs(x, x_b)
                a, b = (y_a, y_b) if y_a < y_b else (y_b, y_a)
            else:
                a_raw = sp.sympify(limits[0]) if len(limits) >= 1 else sp.Integer(0)
                b_raw = sp.sympify(limits[1]) if len(limits) >= 2 else sp.Integer(1)
                a, b = (a_raw, b_raw) if a_raw < b_raw else (b_raw, a_raw)

            # E. DISK vs WASHER LOGIC
            f_expr = final_funcs[0]
            g_expr = final_funcs[1] if len(final_funcs) > 1 else sp.Integer(0)
            
            # Check midpoint to ensure Outer Radius R >= Inner Radius r
            mid = (float(a.evalf()) + float(b.evalf())) / 2
            val_f = float(f_expr.subs(integration_var, mid).evalf())
            val_g = float(g_expr.subs(integration_var, mid).evalf())
            
            R_outer, r_inner = (f_expr, g_expr) if abs(val_f) >= abs(val_g) else (g_expr, f_expr)
            method = "Washer Method" if r_inner != 0 else "Disk Method"

            # F. CALCULATION
            integrand = sp.simplify(R_outer**2 - r_inner**2)
            volume_exact = sp.pi * sp.Abs(sp.integrate(integrand, (integration_var, a, b)))

            # G. RESULTS UI
            st.success(f"✅ Identified: **{method}**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📝 Step-by-Step Solution")
                st.write("**1. Set up the Integral:**")
                st.latex(rf"V = \pi \int_{{{sp.latex(a)}}}^{{{sp.latex(b)}}} [({sp.latex(R_outer)})^2 - ({sp.latex(r_inner)})^2] \, d{integration_var}")
                
                st.write("**2. Simplified Integrand:**")
                st.latex(rf"V = \pi \int_{{{sp.latex(a)}}}^{{{sp.latex(b)}}} ({sp.latex(integrand)}) \, d{integration_var}")
                
                st.write("**3. Anti-derivative:**")
                anti = sp.integrate(integrand, integration_var)
                st.latex(rf"V = \pi \left[ {sp.latex(anti)} \right]_{{{sp.latex(a)}}}^{{{sp.latex(b)}}}")
                
                st.write("**4. Final Exact Volume:**")
                st.latex(rf"V = {sp.latex(sp.simplify(volume_exact))} \approx {float(volume_exact.evalf()):.4f}")

            with col2:
                st.subheader("📊 3D Visual Model")
                fig = plt.figure(figsize=(8, 6))
                ax = fig.add_subplot(111, projection='3d')
                
                u_vals = np.linspace(float(a.evalf()), float(b.evalf()), 50)
                v_vals = np.linspace(0, 2*np.pi, 50)
                U, V = np.meshgrid(u_vals, v_vals)
                
                r_num = sp.lambdify(integration_var, R_outer, 'numpy')(U)
                
                if is_y_axis:
                    X, Y, Z = r_num*np.cos(V), U, r_num*np.sin(V)
                else:
                    X, Y, Z = U, r_num*np.cos(V), r_num*np.sin(V)
                
                ax.plot_surface(X, Y, Z, color='cyan', alpha=0.6, edgecolor='k', lw=0.1)
                st.pyplot(fig)

        except Exception as e:
            st.error(f"Mathematical Parsing Error: {e}. Please check your equation formatting.")
