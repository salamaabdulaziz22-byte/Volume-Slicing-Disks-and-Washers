import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go

# إعدادات الصفحة
st.set_page_config(page_title="Volume Solver", layout="wide")
st.title("📐 Volume of Revolution Solver")

# الجانب الأيسر للمدخلات
with st.sidebar:
    st.header("Settings")
    method = st.selectbox("Method", ["Disk", "Washer"])
    f_text = st.text_input("Outer Function f(x)", "sqrt(x)")
    g_text = st.text_input("Inner Function g(x)", "0") if method == "Washer" else "0"
    a = st.number_input("Start (a)", value=0.0)
    b = st.number_input("End (b)", value=1.0)
    axis = st.number_input("Rotation Axis (y=c)", value=0.0)

# المحرك الرياضي
x = sp.symbols('x')
try:
    # تحويل النص إلى معادلة رياضية
    f_expr = sp.simplify(f_text)
    g_expr = sp.simplify(g_text)
    
    # حساب أنصاف الأقطار
    R = f_expr - axis
    r = g_expr - axis
    
    # معادلة التكامل
    integrand = sp.pi * (R**2 - r**2)
    volume = sp.integrate(integrand, (x, a, b))
    
    # عرض النتائج
    st.header("📝 Steps & Results")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Method:** {method}")
        st.latex(r"V = \pi \int_{a}^{b} [R(x)^2 - r(x)^2] dx")
        st.write(f"**Radius R(x):** ${sp.latex(R)}$")
    with col2:
        st.success(f"**Final Volume:** {float(volume.evalf()):.4f}")
        st.latex(f"V = {sp.latex(volume)}")

    # الرسم ثلاثي الأبعاد (محمي من الأخطاء)
    st.header("🍦 3D Visualization")
    u_vals = np.linspace(float(a), float(b), 40)
    v_vals = np.linspace(0, 2*np.pi, 40)
    U, V = np.meshgrid(u_vals, v_vals)

    # تحويل المعادلات لقيم عددية (Numpy)
    f_num = sp.lambdify(x, f_expr, 'numpy')
    g_num = sp.lambdify(x, g_expr, 'numpy')

    def get_surface(func):
        radius = func(U) - axis
        # حماية: تحويل أي أخطاء (مثل جذر سالب) إلى صفر لكي لا ينهار الرسم
        radius = np.nan_to_num(radius.astype(float))
        Y = radius * np.cos(V) + axis
        Z = radius * np.sin(V)
        return Y, Z

    fig = go.Figure()
    # السطح الخارجي
    Y1, Z1 = get_surface(f_num)
    fig.add_trace(go.Surface(x=U, y=Y1, z=Z1, colorscale='Viridis', showscale=False))
    
    # السطح الداخلي (Washer فقط)
    if method == "Washer":
        Y2, Z2 = get_surface(g_num)
        fig.add_trace(go.Surface(x=U, y=Y2, z=Z2, colorscale='Reds', opacity=0.5, showscale=False))

    fig.update_layout(scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'))
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.warning("Enter valid functions to see the solution and 3D graph.")
