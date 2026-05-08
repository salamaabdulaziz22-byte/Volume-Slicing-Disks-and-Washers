import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re

st.set_page_config(page_title="Universal Volume Solver", layout="wide")
st.title("Calculus Volume Solver")

# مدخل النص
raw_input = st.text_area("أدخلي مسألة التكامل هنا (بأي صيغة):", 
                         placeholder="مثال: y = x**2, y = 1, from x=0 to 2 about y-axis")

if st.button("تحليل وحل المسألة"):
    try:
        # 1. تنظيف وتحليل النص بشكل مرن
        clean_q = raw_input.lower().replace('^', '**').replace('√', 'sqrt')
        
        # استخراج المعادلات: يبحث عن أي شيء بعد الـ = 
        eq_found = re.findall(r'[yx]\s*=\s*([^,]+)', clean_q)
        # استخراج كافة الأرقام للفترات
        nums = [float(n) for n in re.findall(r"[-+]?\d*\.\d+|\d+", clean_q)]
        
        if not eq_found:
            st.error("لم يتم العثور على معادلات واضحة. يرجى كتابتها بصيغة y=... أو x=...")
        else:
            x, y = sp.symbols('x y')
            is_y_axis = 'y-axis' in clean_q or 'around y' in clean_q
            
            # تحديد الدوال (Disk vs Washer)
            f_expr = sp.sympify(eq_found[0].strip())
            g_expr = sp.sympify(eq_found[1].strip()) if len(eq_found) > 1 else sp.sympify(0)
            
            method = "Washer Method" if g_expr != 0 else "Disk Method"
            st.success(f"🔍 الطريقة المكتشفة: **{method}**")

            # تحديد الفترات تلقائياً (تجنب خطأ index out of range)
            a = nums[-2] if len(nums) >= 2 else 0
            b = nums[-1] if len(nums) >= 1 else 1
            
            # توحيد المتغيرات حسب محور الدوران
            var = y if is_y_axis else x
            # تحويل الدوال إذا كانت المسألة حول y-axis والدالة مكتوبة بدلالة x
            if is_y_axis and 'x' in str(f_expr):
                f_expr = sp.solve(sp.Eq(y, f_expr), x)[0]
                if g_expr != 0: g_expr = sp.solve(sp.Eq(y, g_expr), x)[0]

            # 2. الحل الرياضي
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📝 خطوات الحل")
                integrand = sp.simplify(f_expr**2 - g_expr**2)
                st.latex(rf"V = \pi \int_{{{a}}}^{{{b}}} ({sp.latex(integrand)}) \, d{var}")
                
                res = sp.integrate(integrand, (var, a, b))
                final_v = sp.pi * res
                st.latex(rf"V = {sp.latex(sp.simplify(final_v))} \approx {float(final_v.evalf()):.4f}")

            # 3. الرسم البياني 3D
            with col2:
                st.subheader("📊 المجسم الناتج")
                fig = plt.figure()
                ax = fig.add_subplot(111, projection='3d')
                u = np.linspace(float(a), float(b), 40)
                v = np.linspace(0, 2*np.pi, 40)
                U, V = np.meshgrid(u, v)
                
                f_num = sp.lambdify(var, f_expr, 'numpy')(U)
                
                if is_y_axis:
                    X, Y, Z = f_num*np.cos(V), U, f_num*np.sin(V)
                else:
                    X, Y, Z = U, f_num*np.cos(V), f_num*np.sin(V)
                
                ax.plot_surface(X, Y, Z, alpha=0.7, color='cyan', edgecolor='navy')
                st.pyplot(fig)

    except Exception as e:
        st.error(f"حدث خطأ في التحليل: {e}. حاولي كتابة المعادلات بوضوح مثل y = x**2")
