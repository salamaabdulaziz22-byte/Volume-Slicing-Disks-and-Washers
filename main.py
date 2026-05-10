import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, integrate, pi, lambdify, sympify

# إعدادات واجهة الموقع
st.set_page_config(page_title="حاسبة حجوم الدوال الدورانية", layout="centered")

st.title("📐 حاسبة حجوم الأجسام الدورانية")
st.write("أدخلي الدوال وحدود التكامل للحصول على الحل بالخطوات والرسم البياني.")

# مدخلات المستخدم في القائمة الجانبية
st.sidebar.header("إعدادات المسألة")
f_input = st.sidebar.text_input("الدالة الأولى (f(x) - البعيدة عن المحور", "sqrt(x)")
g_input = st.sidebar.text_input("الدالة الثانية (g(x) - القريبة (0 في حال القرص)", "0")
a_val = st.sidebar.number_input("بداية التكامل (a)", value=0.0)
b_val = st.sidebar.number_input("نهاية التكامل (b)", value=4.0)

if st.button("احسب الحجم واعرض الخطوات"):
    try:
        x = symbols('x')
        f_expr = sympify(f_input)
        g_expr = sympify(g_input)

        # 1. تحديد الطريقة تلقائياً
        method = "Washer Method" if g_expr != 0 else "Disk Method"
        st.subheader(f"الطريقة المستخدمة: {method}")

        # 2. إعداد معادلة التكامل
        if method == "Disk Method":
            formula_text = r"V = \pi \int_{a}^{b} [f(x)]^2 dx"
            integrand = f_expr**2
        else:
            formula_text = r"V = \pi \int_{a}^{b} ([R(x)]^2 - [r(x)]^2) dx"
            integrand = f_expr**2 - g_expr**2

        # 3. عرض خطوات الحل
        st.write("### خطوات الحل:")
        st.write("1. إعداد التكامل المحدد:")
        st.latex(f"V = \pi \int_{{{a_val}}}^{{{b_val}}} ({integrand}) dx")

        # حساب التكامل العكسي (Antiderivative)
        antiderivative = integrate(integrand, x)
        st.write("2. إيجاد التكامل العكسي:")
        st.latex(f"\pi \left[ {antiderivative} \\right]_{{{a_val}}}^{{{b_val}}}")

        # الناتج النهائي
        result_exact = integrate(integrand, (x, a_val, b_val)) * pi
        result_decimal = float(result_exact.evalf())

        st.success(f"الناتج النهائي: {result_exact} ≈ {result_decimal:.4f} وحدة مكعبة")

        # 4. الرسم البياني
        st.write("### الرسم التوضيحي للمنطقة:")
        x_range = np.linspace(float(a_val), float(b_val), 100)
        f_func = lambdify(x, f_expr, 'numpy')
        g_func = lambdify(x, g_expr, 'numpy')

        fig, ax = plt.subplots()
        ax.plot(x_range, f_func(x_range), 'r', label='f(x)')
        if method == "Washer Method":
            ax.plot(x_range, g_func(x_range), 'b', label='g(x)')
        
        ax.fill_between(x_range, f_func(x_range), g_func(x_range), color='gray', alpha=0.3)
        ax.axhline(0, color='black', lw=1)
        ax.axvline(0, color='black', lw=1)
        ax.legend()
        st.pyplot(fig)

    except Exception as e:
        st.error(f"خطأ في إدخال الدالة: {e}. تأكدي من كتابة x بشكل صحيح واستخدام * للضرب.")
