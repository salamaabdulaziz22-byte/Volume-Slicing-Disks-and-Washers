import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Math Solver - Disks & Washers", layout="wide")

st.title("🧮 برنامج حساب حجوم الأجسام الدورانية")
st.markdown("---")

# مدخلات المستخدم
with st.sidebar:
    st.header("⚙️ إدخال المسألة")
    f_str = st.text_input("الدالة العلوية f(x):", "sqrt(x)")
    g_str = st.text_input("الدالة السفلية g(x) (0 للقرص):", "x")
    a = st.number_input("بداية الفترة (a):", value=0.0)
    b = st.number_input("نهاية الفترة (b):", value=1.0)
    axis = st.selectbox("الدوران حول:", ["محور x (y=0)"])

if st.button("تحليل المسألة وحلها"):
    x = sp.symbols('x')
    f = sp.sympify(f_str)
    g = sp.sympify(g_str)
    
    # 1. تحديد النوع تلقائياً
    is_washer = g != 0
    type_name = "Washer Method (طريقة الحلقات)" if is_washer else "Disk Method (طريقة الأقراص)"
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 خطوات الحل التفصيلية")
        st.info(f"**النوع المحدد:** {type_name}")
        
        st.markdown(f"**Step 1: تعريف الدوال**")
        st.latex(f"R_{{out}}(x) = {sp.latex(f)}")
        if is_washer: st.latex(f"R_{{in}}(x) = {sp.latex(g)}")
        
        st.markdown(f"**Step 2: إعداد التكامل**")
        if is_washer:
            formula = sp.pi * sp.Integral(f**2 - g**2, (x, a, b))
        else:
            formula = sp.pi * sp.Integral(f**2, (x, a, b))
        st.latex(sp.latex(formula))
        
        st.markdown(f"**Step 3: الحساب النهائي**")
        integrand = f**2 - g**2 if is_washer else f**2
        antideriv = sp.integrate(integrand, x)
        volume_exact = sp.pi * sp.integrate(integrand, (x, a, b))
        
        st.write("التكامل غير المحدود:")
        st.latex(f"\\pi \\left[ {sp.latex(antideriv)} \\right]_{{{a}}}^{{{b}}}")
        st.success(f"النتيجة النهائية: {sp.latex(volume_exact)} ≈ {float(volume_exact.evalf()):.4f}")

    with col2:
        st.subheader("📊 الرسم البياني")
        # الرسم باستخدام Matplotlib
        x_p = np.linspace(float(a), float(b), 100)
        f_p = sp.lambdify(x, f, 'numpy')(x_p)
        g_p = sp.lambdify(x, g, 'numpy')(x_p) if is_washer else np.zeros_like(x_p)
        
        fig, ax = plt.subplots()
        ax.plot(x_p, f_p, 'r', label='f(x)')
        ax.plot(x_p, g_p, 'b', label='g(x)')
        ax.fill_between(x_p, f_p, g_p, color='orange', alpha=0.3)
        ax.set_title("المنطقة المطلوب تدويرها")
        ax.legend()
        st.pyplot(fig)