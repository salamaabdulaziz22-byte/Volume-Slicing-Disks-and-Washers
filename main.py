import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go

# إعدادات واجهة الموقع
st.set_page_config(page_title="Math Solver", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("📐 Volume of Revolution Solver")
st.write("أداة حل مسائل الحجوم الدورانية بالخطوات والرسم ثلاثي الأبعاد")

# تقسيم الصفحة لخانة معطيات وخانة حل
col_input, col_solution = st.columns([1, 2])

with col_input:
    st.header("📥 المعطيات")
    with st.container():
        method = st.selectbox("اختر الطريقة:", ["Disk Method", "Washer Method"])
        f_txt = st.text_input("الدالة الخارجية f(x):", "sqrt(x)")
        g_txt = "0"
        if method == "Washer Method":
            g_txt = st.text_input("الدالة الداخلية g(x):", "x**2")
        
        col_range = st.columns(2)
        with col_range[0]:
            a_val = st.number_input("بداية الفترة (a):", value=0.0)
        with col_range[1]:
            b_val = st.number_input("نهاية الفترة (b):", value=1.0)
            
        axis_val = st.number_input("محور الدوران y =", value=0.0)
        solve_btn = st.button("احسب الحل")

# محرك الحل الرياضي والرسم
x = sp.symbols('x')
if solve_btn:
    try:
        f_expr = sp.sympify(f_txt)
        g_expr = sp.sympify(g_txt)
        
        R = f_expr - axis_val
        r = g_expr - axis_val
        
        # صيغة التكامل
        integrand = sp.pi * (R**2 - r**2)
        volume_exact = sp.integrate(integrand, (x, a_val, b_val))
        volume_numeric = float(volume_exact.evalf())

        with col_solution:
            st.header("📝 خطوات الحل")
            st.info(f"تم استخدام طريقة: **{method}**")
            
            # عرض الخطوات الرياضية
            st.write("**1. تحديد أنصاف الأقطار:**")
            st.latex(f"R(x) = {sp.latex(R)}")
            if method == "Washer Method":
                st.latex(f"r(x) = {sp.latex(r)}")
            
            st.write("**2. إعداد التكامل:**")
            st.latex(f"V = \pi \int_{{{a_val}}}^{{{b_val}}} ({sp.latex(R**2 - r**2)}) \, dx")
            
            st.write("**3. النتيجة النهائية:**")
            st.success(f"الحجم = {volume_numeric:.4f} وحدة مكعبة")
            st.latex(f"V = {sp.latex(volume_exact)}")

            # الرسم ثلاثي الأبعاد
            st.header("🍦 الرسم ثلاثي الأبعاد")
            u = np.linspace(float(a_val), float(b_val), 40)
            v = np.linspace(0, 2*np.pi, 40)
            U, V = np.meshgrid(u, v)

            f_num = sp.lambdify(x, f_expr, 'numpy')
            g_num = sp.lambdify(x, g_expr, 'numpy')

            def get_coords(func_num):
                # حماية من القيم غير المعرفة (NaN)
                rad = np.nan_to_num(func_num(U).astype(float)) - axis_val
                Y = rad * np.cos(V) + axis_val
                Z = rad * np.sin(V)
                return Y, Z

            fig = go.Figure()
            Y1, Z1 = get_coords(f_num)
            fig.add_trace(go.Surface(x=U, y=Y1, z=Z1, colorscale='Viridis', opacity=0.8, showscale=False))
            
            if method == "Washer Method":
                Y2, Z2 = get_coords(g_num)
                fig.add_trace(go.Surface(x=U, y=Y2, z=Z2, colorscale='Reds', opacity=0.5, showscale=False))

            fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"تأكد من كتابة الدالة بشكل صحيح. مثال: x**2 أو sqrt(x)")
