import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

st.set_page_config(page_title="Calculus Companion", layout="wide")

st.title("Volumes of Revolution: Disk & Washer Methods")
st.write("استكشف أحجام الأجسام الدورانية بسهولة!")

# المدخلات
col1, col2 = st.columns([1, 1])

with col1:
    st.header("إدخال الدوال")
    f_input = st.text_input("الدالة العلوية f(x):", "x**2")
    g_input = st.text_input("الدالة السفلية g(x) (اختياري للـ Washer):", "0")
    a = st.number_input("بداية الفترة (a):", value=0.0)
    b = st.number_input("نهاية الفترة (b):", value=2.0)
    axis = st.number_input("محور الدوران (y = ):", value=0.0)

# الحسابات
try:
    f = lambda x: eval(f_input)
    g = lambda x: eval(g_input)
    
    # تحديد الطريقة تلقائياً
    method = "Disk Method" if g_input == "0" else "Washer Method"
    
    # تكامل الحجم
    integrand = lambda x: np.pi * (abs(f(x) - axis)**2 - abs(g(x) - axis)**2)
    volume, error = quad(integrand, a, b)

    with col2:
        st.header("الرسم البياني")
        x_vals = np.linspace(a, b, 100)
        plt.figure(figsize=(8, 4))
        plt.plot(x_vals, [f(x) for x in x_vals], label=f"f(x)={f_input}")
        if g_input != "0":
            plt.plot(x_vals, [g(x) for x in x_vals], label=f"g(x)={g_input}")
        plt.fill_between(x_vals, [f(x) for x in x_vals], [g(x) for x in x_vals], alpha=0.3)
        plt.axhline(y=axis, color='r', linestyle='--', label=f"Axis y={axis}")
        plt.legend()
        st.pyplot(plt)

    st.divider()
    st.header("خطوات الحل والنتيجة")
    st.write(f"**الطريقة المستخدمة:** {method}")
    st.latex(r"V = \pi \int_{a}^{b} [R(x)^2 - r(x)^2] dx")
    st.success(f"الحجم النهائي التقريبي هو: {volume:.4f}")
    
except Exception as e:
    st.error(f"خطأ في إدخال الدوال: {e}")
