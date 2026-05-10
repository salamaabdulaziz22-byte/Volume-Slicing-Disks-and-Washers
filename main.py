import streamlit as st
import numpy as np
import plotly.graph_objects as go
from sympy import symbols, integrate, pi, lambdify, sympify

# إعدادات الصفحة
st.set_page_config(page_title="3D Volume Solver", layout="wide")

st.title("📐 3D Solid of Revolution Solver")
st.write("Enter your functions and limits to see the step-by-step solution and the 3D solid.")

# المدخلات في القائمة الجانبية
st.sidebar.header("Input Parameters")
axis_choice = st.sidebar.selectbox("Rotation Axis", ["x-axis", "y-axis"])
var_name = 'x' if axis_choice == "x-axis" else 'y'

f_input = st.sidebar.text_input(f"Outer Function f({var_name})", "sqrt(x)" if var_name == 'x' else "y**2")
g_input = st.sidebar.text_input(f"Inner Function g({var_name}) (0 for Disk)", "0")
a_val = st.sidebar.number_input("Lower Limit (Start)", value=0.0)
b_val = st.sidebar.number_input("Upper Limit (End)", value=4.0)

if st.button("Solve & Generate 3D Solid"):
    try:
        v_sym = symbols(var_name)
        f_expr = sympify(f_input)
        g_expr = sympify(g_input)

        # 1. تحديد الطريقة والحسابات
        method = "Disk Method" if g_expr == 0 else "Washer Method"
        integrand = f_expr**2 - g_expr**2
        
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader(f"Step-by-Step Solution ({method})")
            
            # عرض القوانين والخطوات
            formula = r"V = \pi \int_{a}^{b} [R(x)]^2 dx" if var_name == 'x' else r"V = \pi \int_{c}^{d} [R(y)]^2 dy"
            if method == "Washer Method":
                formula = r"V = \pi \int_{a}^{b} (R^2 - r^2) dx" if var_name == 'x' else r"V = \pi \int_{c}^{d} (R^2 - r^2) dy"

            st.write("**1. Formula:**")
            st.latex(formula)

            st.write("**2. Integral Setup:**")
            st.latex(f"V = \pi \int_{{{a_val}}}^{{{b_val}}} ({integrand}) d{var_name}")

            # التكامل الحسابي
            antiderivative = integrate(integrand, v_sym)
            result_exact = integrate(integrand, (v_sym, a_val, b_val)) * pi
            
            st.write("**3. Antiderivative:**")
            st.latex(f"\pi \left[ {antiderivative} \\right]_{{{a_val}}}^{{{b_val}}}")
            st.success(f"Final Volume ≈ {float(result_exact.evalf()):.4f} units³")

        with col2:
            st.subheader("3. Interactive 3D Solid")
            
            # توليد نقاط الرسم ثلاثي الأبعاد
            u = np.linspace(float(a_val), float(b_val), 50)
            v = np.linspace(0, 2 * np.pi, 50)
            U, V = np.meshgrid(u, v)
            
            f_num = lambdify(v_sym, f_expr, 'numpy')
            g_num = lambdify(v_sym, g_expr, 'numpy')
            
            # تحويل المعادلات ثنائية الأبعاد إلى إحداثيات ثلاثية الأبعاد
            if axis_choice == "x-axis":
                X, Y, Z = U, f_num(U) * np.cos(V), f_num(U) * np.sin(V)
                X_in, Y_in, Z_in = U, g_num(U) * np.cos(V), g_num(U) * np.sin(V)
            else:
                Y, X, Z = U, f_num(U) * np.cos(V), f_num(U) * np.sin(V)
                Y_in, X_in, Z_in = U, g_num(U) * np.cos(V), g_num(U) * np.sin(V)

            fig = go.Figure()
            # إضافة السطح الخارجي
            fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale='Reds', opacity=0.7, showscale=False))
            # إضافة السطح الداخلي في حال كانت Washer
            if g_expr != 0:
                fig.add_trace(go.Surface(x=X_in, y=Y_in, z=Z_in, colorscale='Blues', opacity=0.8, showscale=False))

            fig.update_layout(scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'), margin=dict(l=0, r=0, b=0, t=0))
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error in calculation: {e}")
