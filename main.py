import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Math Solver", layout="wide")
st.title("📐 Volume of Revolution Solver")

# 1. مدخلات بسيطة
with st.sidebar:
    method = st.selectbox("Method", ["Disk", "Washer"])
    f_in = st.text_input("Outer Function f(x)", "sqrt(x)")
    g_in = st.text_input("Inner Function g(x)", "0") if method == "Washer" else "0"
    a = st.number_input("Start x", value=0.0)
    b = st.number_input("End x", value=1.0)
    axis = st.number_input("Rotate around y =", value=0.0)

x = sp.symbols('x')
try:
    # 2. الحسابات الرياضية
    f = sp.sympify(f_in)
    g = sp.sympify(g_in)
    R = f - axis
    r = g - axis
    
    integrand = sp.pi * (R**2 - r**2)
    volume = sp.integrate(integrand, (x, a, b))
    
    # عرض الحل
    st.success(f"Final Volume: {float(volume.evalf()):.4f}")
    st.latex(f"V = {sp.latex(volume)}")

    # 3. الرسم (نسخة مبسطة جداً)
    st.subheader("3D Preview")
    u = np.linspace(float(a), float(b), 40)
    v = np.linspace(0, 2*np.pi, 40)
    U, V = np.meshgrid(u, v)

    # تحويل المعادلات لرسم
    f_num = sp.lambdify(x, f, 'numpy')
    g_num = sp.lambdify(x, g, 'numpy')

    def get_coords(func_num):
        radius = func_num(U) - axis
        # تنظيف البيانات من أي أخطاء رياضية (NaN)
        radius = np.where(np.isnan(radius), 0, radius)
        Y = radius * np.cos(V) + axis
        Z = radius * np.sin(V)
        return Y, Z

    fig = go.Figure()
    # رسم السطح الخارجي
    Y1, Z1 = get_coords(f_num)
    fig.add_trace(go.Surface(x=U, y=Y1, z=Z1, colorscale='Viridis', showscale=False))
    
    # رسم السطح الداخلي إذا كان Washer
    if method == "Washer":
        Y2, Z2 = get_coords(g_num)
        fig.add_trace(go.Surface(x=U, y=Y2, z=Z2, colorscale='Reds', opacity=0.5, showscale=False))

    fig.update_layout(scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'))
    st.plotly_chart(fig)

except Exception as e:
    st.error(f"Please check your math: {e}")
