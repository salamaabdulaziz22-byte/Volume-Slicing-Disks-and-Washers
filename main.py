import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re

st.set_page_config(page_title="Universal Math Solver", layout="wide")
st.title("Intelligent Volume Solver (Disks & Washers)")

# خانة إدخال السؤال
raw_input = st.text_area("أدخلي السؤال هنا (مثال: y=sqrt(x), y=0, x=0 to 4 about x-axis):", 
                         "y = sqrt(x), y = 0, from x = 0 to 4 about x-axis")

if st.button("تحليل المسألة وتوليد الحل"):
    try:
        # 1. معالجة النص لاستخراج الدوال والحدود
        clean_q = raw_input.lower().replace('^', '**').replace('√', 'sqrt').replace('vx', 'sqrt(x)')
        
        # استخراج الدوال (y=...) أو (x=...)
        equations = re.findall(r'[xy]\s*=\s*([0-9x\s\+\-\*\^/\(\)sqrt]+)', clean_q)
        # استخراج الأرقام للفترة
        nums = re.findall(r'(\d+\.?\d*)', clean_q)
        
        if len(equations) >= 1:
            x, y = sp.symbols('x y')
            is_y_axis = 'y-axis' in clean_q
            var = y if is_y_axis else x
            
            # تحديد الدالة الكبرى والصغرى
            f_expr = sp.sympify(equations[0].strip())
            g_expr = sp.sympify(equations[1].strip()) if len(equations) > 1 else sp.sympify(0)
            
            # تحديد نوع الطريقة تلقائياً
            method = "Washer Method (الحلقات)" if g_expr != 0 else "Disk Method (الأقراص)"
            
            # تحديد الحدود
            a_val = float(nums[0]) if len(nums) > 0 else 0.0
            b_val = float(nums[1]) if len(nums) > 1 else 1.0
            if 'sqrt(3)' in clean_q: b_val = float(sp.sqrt(3).evalf())

            st.success(f"✅ تم اكتشاف الطريقة: {method}")
            
            # 2. عرض خطوات الحل
            st.subheader("📝 خطوات الحل بالتفصيل")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**1. إعداد التكامل:**")
                st.latex(rf"V = \pi \int_{{{a_val}}}^{{{b_val}}} [({sp.latex(f_expr)})^2 - ({sp.latex(g_expr)})^2] \, d{var}")
                
                integrand = sp.simplify(f_expr**2 - g_expr**2)
                st.write("**2. تبسيط الدالة داخل التكامل:**")
                st.latex(rf"V = \pi \int_{{{a_val}}}^{{{b_val}}} ({sp.latex(integrand)}) \, d{var}")
                
                antideriv = sp.integrate(integrand, var)
                st.write("**3. إيجاد المشتق العكسي:**")
                st.latex(rf"V = \pi \left[ {sp.latex(antideriv)} \right]_{{{a_val}}}^{{{b_val}}}")
                
                final_vol = sp.pi * (antideriv.subs(var, b_val) - antideriv.subs(var, a_val))
                st.write("**4. الناتج النهائي:**")
                st.latex(rf"V = {sp.latex(final_vol)} \approx {float(final_vol.evalf()):.4f}")

            # 3. الرسم ثلاثي الأبعاد
            with col2:
                st.subheader("📦 الرسم ثلاثي الأبعاد (3D)")
                fig = plt.figure()
                ax = fig.add_subplot(111, projection='3d')
                
                v_space = np.linspace(a_val, b_val, 50)
                theta = np.linspace(0, 2*np.pi, 50)
                V, THETA = np.meshgrid(v_space, theta)
                
                # حساب نصف القطر بناءً على الدالة المدخلة
                f_num = sp.lambdify(var, f_expr, 'numpy')(V)
                
                X = f_num * np.cos(THETA)
                Z = f_num * np.sin(THETA)
                Y = V
                
                ax.plot_surface(X, Y, Z, color='cyan', alpha=0.6)
                st.pyplot(fig)
                
        else:
            st.error("لم أتمكن من العثور على المعادلات. تأكدي من كتابتها بصيغة y = ...")
            
    except Exception as e:
        st.error(f"حدث خطأ في التحليل: {e}")
