import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go

# إعدادات واجهة الموقع
st.set_page_config(page_title="Volume Solver", layout="wide")
st.title("🎓 Quick Volume Solver (Disks & Washers)")

# القائمة الجانبية للمدخلات
with st.sidebar:
    st.header("Enter Problem Details")
    method = st.selectbox("Select Method", ["Disk", "Washer"])
    f_input = st.text_input("Top Function f(x)", "sqrt(x)")
    g_input = "0"
    if method == "Washer":
        g_input = st.text_input("Bottom Function g(x)", "x**2")
    
    a_val = st.number_input("Start (a)", value=0.0)
    b_val = st.number_input("End (b)", value=1.0)
    axis = st.number_input("Axis of Rotation y =", value=0.0)

# محرك الحل الرياضي
x = sp.symbols('x')
try:
    # تحويل النصوص إلى معادلات
    f = sp.sympify(f_input)
    g = sp.sympify(g_input)
    
    # تحديد انصاف الأقطار
    R = f - axis
    r = g - axis
    
    # قانون التكامل
    integrand = sp.pi * (R**2 - r**2)
    volume_step = sp.integrate(integrand, x) # التكامل غير المحدود للخطوات
    volume_final = sp.integrate(integrand, (x, a_val, b_val))
    
    # عرض الحل والخطوات
    st.subheader("📝 Solution Steps")
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Selected:** {method} Method")
        st.write(f"**Outer Radius R(x):** ${sp.latex(R)}$")
        if method == "Washer":
            st.write(f"**Inner Radius r(x):** ${sp.latex(r)}$")
    
    with col2:
        st.latex(f"V = \pi \int_{{{a_val}}}^{{{b_val}}} ({sp.latex(R**2 - r**2)}) \, dx")
        st.success(f"**Final Volume:** {float(volume_final.evalf()):.4f}")
        st.latex(f"V = {sp.latex(volume_final)}")

    # محرك الرسم ثلاثي الأبعاد (نسخة سريعة ومستقرة)
    st.subheader("📊 3D Visualization")
    
    u = np.linspace(float(a_val), float(b_val), 40)
    v = np.linspace(0, 2*np.pi, 40)
    U, V = np.meshgrid(u, v)

    # تحويل المعادلات لقيم عددية مع الحماية من الأخطاء
    f_num = sp.lambdify(x, f, modules=['numpy', {'pi': np.pi}])
    g_num = sp.lambdify(x, g, modules=['numpy', {'pi': np.pi}])

    def create_surface(func_num, color, name):
        r_vals = func_num(U) - axis
        # استبدال القيم غير المنطقية بصفر لضمان عدم توقف الرسم
        r_vals = np.nan_to_num(r_vals.astype(float))
        Y = r_vals * np.cos(V) + axis
        Z = r_vals * np.sin(V)
        return go.Surface(x=U, y=Y, z=Z, colorscale=color, opacity=0.7, showscale=False, name=name)

    fig = go.Figure()
    fig.add_trace(create_surface(f_num, 'Viridis', 'Outer'))
    if method == "Washer":
        fig.add_trace(create_surface(g_num, 'Reds', 'Inner'))

    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0), scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'))
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Waiting for correct math input... Error: {e}")
