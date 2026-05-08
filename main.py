import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re

# إعداد الصفحة
st.set_page_config(page_title="Universal Calculus Solver", layout="wide")
st.title("Smart Calculus Volume Solver")
st.markdown("هذا المحلل مصمم لفهم المسائل المكتوبة نصاً واستخراج المعادلات والحدود تلقائياً.")

# مدخلات المستخدم
raw_input = st.text_area("أدخل المسألة هنا (بالعربي أو الإنجليزي):", height=150, 
                         placeholder=" ")

def robust_solve():
    try:
        # 1. تنظيف النص وتحويله لصيغة برمجية
        text = raw_input.lower()
        # تحويل الجذور والاختصارات
        text = text.replace('^', '**').replace('√', 'sqrt').replace('vx', 'sqrt(x)')
        text = re.sub(r'[vV](\d+)', r'sqrt(\1)', text)
        
        x_sym, y_sym = sp.symbols('x y')
        
        # 2. استخراج محور الدوران
        is_about_y = "y-axis" in text or "y axis" in text or "محور الصادات" in text
        
        # 3. استخراج المعادلات (البحث عن y= أو x=)
        # نبحث عن أي شيء يبدأ بـ y= أو f(x)= ويتبعه معادلة
        eq_patterns = re.findall(r'(?:y|f\(x\)|x|g\(y\))\s*=\s*([a-z0-9\s\*\+\-\/\(\)\.\^]+)', text)
        
        found_exprs = []
        for e in eq_patterns:
            try:
                # تنظيف الجزء المستخرج من الكلمات الزائدة مثل "on" أو "about"
                clean_e = re.split(r'\s+(?:on|about|from|at|in|للغترة|حول)\s+', e)[0].strip()
                found_exprs.append(sp.sympify(clean_e))
            except:
                continue
        
        if not found_exprs:
            st.error("لم أستطع تحديد المعادلات. تأكد من كتابتها بصيغة y = ...")
            return

        f_main = found_exprs[0]
        g_second = found_exprs[1] if len(found_exprs) > 1 else sp.sympify(0)

        # 4. استخراج حدود التكامل (البحث عن أرقام داخل [] أو بعد from/to)
        # يبحث عن أرقام مفردة أو أرقام داخل فترات [0,4]
        limits = re.findall(r"(\d+\.?\d*)", text)
        if len(limits) >= 2:
            a_val, b_val = sorted([float(limits[0]), float(limits[1])])
        else:
            # إذا لم يجد حدوداً، يحاول البحث عن نقاط التقاطع
            st.info("لم يتم تحديد حدود واضحة، جاري محاولة حساب نقاط التقاطع...")
            intersection = sp.solve(f_main - g_second, x_sym)
            if len(intersection) >= 2:
                a_val, b_val = float(intersection[0]), float(intersection[1])
            else:
                a_val, b_val = 0.0, 1.0 # حدود افتراضية

        # 5. منطق الحل (القرص أو الواشر)
        st.subheader("📝 الخطوات الرياضية (Mathematical Solution)")
        col1, col2 = st.columns(2)

        with col1:
            if is_about_y:
                var = y_sym
                # تحويل الدالة لتصبح بدلالة y
                f_y = sp.solve(sp.Eq(y_sym, f_main), x_sym)[0] if 'x' in str(f_main) else f_main
                g_y = sp.solve(sp.Eq(y_sym, g_second), x_sym)[0] if 'x' in str(g_second) and g_second != 0 else g_second
                
                # حساب الحدود لـ y
                actual_a = float(f_main.subs(x_sym, a_val))
                actual_b = float(f_main.subs(x_sym, b_val))
                y_low, y_high = sorted([actual_a, actual_b])
                
                integrand = sp.simplify(f_y**2 - g_y**2)
                st.write("**طريقة الدوران حول المحور الصادي (y-axis):**")
                st.latex(rf"V = \pi \int_{{{y_low}}}^{{{y_high}}} ({sp.latex(f_y)})^2 - ({sp.latex(g_y)})^2 \, dy")
            else:
                var = x_sym
                y_low, y_high = a_val, b_val
                integrand = sp.simplify(f_main**2 - g_second**2)
                st.write("**طريقة الدوران حول المحور السيني (x-axis):**")
                st.latex(rf"V = \pi \int_{{{y_low}}}^{{{y_high}}} ({sp.latex(f_main)})^2 - ({sp.latex(g_second)})^2 \, dx")

            # التكامل
            antideriv = sp.integrate(integrand, var)
            definite = sp.integrate(integrand, (var, y_low, y_high))
            final_vol = definite * sp.pi

            st.write("**المشتقة العكسية:**")
            st.latex(rf"F({var}) = \pi \left[ {sp.latex(antideriv)} \right]")
            st.success(f"الحجم النهائي:")
            st.latex(rf"V = {sp.latex(sp.simplify(final_vol))} \approx {float(final_vol.evalf()):,.4f}")

        with col2:
            st.subheader("📊 الرسم ثلاثي الأبعاد")
            fig = plt.figure(figsize=(8,8))
            ax = fig.add_subplot(111, projection='3d')
            
            u = np.linspace(float(y_low), float(y_high), 50)
            v = np.linspace(0, 2*np.pi, 50)
            U, V = np.meshgrid(u, v)
            
            # حساب نصف القطر للرسم
            r_func = sp.lambdify(var, sp.sqrt(sp.Abs(integrand)), 'numpy')
            R = r_func(U)
            
            if is_about_y:
                X, Y, Z = R*np.cos(V), U, R*np.sin(V)
            else:
                X, Y, Z = U, R*np.cos(V), R*np.sin(V)
                
            ax.plot_surface(X, Y, Z, color='deepskyblue', alpha=0.7, edgecolor='navy', lw=0.1)
            st.pyplot(fig)

    except Exception as e:
        st.error(f"خطأ في معالجة المسألة: {e}")
        st.info("نصيحة: تأكد من كتابة الدالة بوضوح مثل y = sqrt(x) والحدود مثل [0, 4]")

if st.button("تحليل وحل المسألة"):
    if raw_input.strip():
        robust_solve()
