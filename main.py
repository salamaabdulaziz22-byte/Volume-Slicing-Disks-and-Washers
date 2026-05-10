import streamlit as st
import numpy as np
import plotly.graph_objects as go
from sympy import symbols, integrate, pi, lambdify, sympify

# 1. Page Config (نفس إعداداتك)
st.set_page_config(page_title="Universal Volume Solver", page_icon="📐", layout="wide")

st.title("📐 Universal Solid of Revolution Solver")
st.write("Calculate volume and visualize the **3D Solid** by revolving around the X or Y axis.")

# 2. Sidebar for Inputs (نفس مدخلاتك بالضبط)
st.sidebar.header("Input Parameters")
axis_choice = st.sidebar.selectbox("Axis of Revolution", ["x-axis", "y-axis"])
variable = 'x' if axis_choice == "x-axis" else 'y'

f_input = st.sidebar.text_input(f"Outer Function f({variable})", "sqrt(x)" if variable == 'x' else "y**2")
g_input = st.sidebar.text_input(f"Inner Function g({variable}) (0 for Disk)", "0")
a_val = st.sidebar.number_input(f"Lower Limit ({variable} = a)", value=0.0)
b_val = st.sidebar.number_input(f"Upper Limit ({variable} = b)", value=4.0)

if st.button("Solve & Generate 3D Model"):
    try:
        v_sym = symbols(variable)
        f_expr = sympify(f_input)
        g_expr = sympify(g_input)

        # Logical Method Identification
        method = "Disk Method" if g_expr == 0 else "Washer Method"
        integrand = f_expr**2 - g_expr**2
        
        # تقسيم الشاشة لنصفين: حل ورسم
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader(f"Method: {method}")
            st.markdown("### Step-by-Step Solution")
            
            formula = r"V = \pi \int_{a}^{b} [R(x)]^2 dx" if variable == 'x' else r"V = \pi \int_{c}^{d} [R(y)]^2 dy"
            if method == "Washer Method":
                formula = r"V = \pi \int_{a}^{b} (R^2 - r^2) dx" if variable == 'x' else r"V = \pi \int_{c}^{d} (R^2 - r^2) dy"

            st.write("**1. Formula:**")
            st.latex(formula)

            st.write("**2. Set up the Integral:**")
            st.latex(f"V = \pi \int_{{{a_val}}}^{{{b_val}}} ({integrand}) d{variable}")

            # الحسابات
            antiderivative = integrate(integrand, v_sym)
            result_exact = integrate(integrand, (v_sym, a_val, b_val)) * pi
            result_decimal = float(result_exact.evalf())

            st.write("**3. Integration Result:**")
            st.latex(f"\pi \left[ {antiderivative} \\right]_{{{a_val}}}^{{{b_val}}}")
            st.success(f"**Final Volume:** {result_exact} ≈ {result_decimal:.4f} cubic units")

        with col2:
            st.subheader("Interactive 3D Visualization")
            
            # --- منطق الرسم الثلاثي الأبعاد الجديد ---
            u_vals = np.linspace(float(a_val), float(b_val), 60)
            v_rotation = np.linspace(0, 2 * np.pi, 60)
            U, V = np.meshgrid(u_vals, v_rotation)
            
            f_num = lambdify(v_sym, f_expr, 'numpy')
            g_num = lambdify(v_sym, g_expr, 'numpy')

            if variable == 'x':
                X, Y, Z = U, f_num(U) * np.cos(V), f_num(U) * np.sin(V)
                X_in, Y_in, Z_in = U, g_num(U) * np.cos(V), g_num(U) * np.sin(V)
            else:
                Y, X, Z = U, f_num(U) * np.cos(V), f_num(U) * np.sin(V)
                Y_in, X_in, Z_in = U, g_num(U) * np.cos(V), g_num(U) * np.sin(V)

            fig = go.Figure()
            # رسم السطح الخارجي (باللون البرتقالي/الأحمر المظلل)
            fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale='Oranges', opacity=0.8, showscale=False))
            
            # رسم السطح الداخلي إذا كان Washer (باللون الأزرق)
            if g_expr != 0:
                fig.add_trace(go.Surface(x=X_in, y=Y_in, z=Z_in, colorscale='Blues', opacity=0.9, showscale=False))

            fig.update_layout(scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'))
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
