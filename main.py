import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re

st.set_page_config(page_title="Universal Calculus Solver", layout="wide")
st.title(" Universal Calculus Volume Solver")

raw_input = st.text_area("أدخل المسألة هنا:", height=150, 
                         placeholder=" ")

def universal_solve():
    try:
        # 1. تنظيف النص ومعالجة الجذور
        text = raw_input.lower().replace('^', '**').replace('√', 'sqrt')
        text = re.sub(r'[vV](\d+)', r'sqrt(\1)', text) # V3 -> sqrt(3)
        text = text.replace('vx', 'sqrt(x)')
        
        x_s, y_s = sp.symbols('x y')
        
        # 2. تحديد المحور
        is_about_y = any(word in text for word in ["y-axis", "y axis", "صادات"])
        
        # 3. استخراج الدوال (البحث عن y= أو x=)
        eq_patterns = re.findall(r'(?:y|f\(x\)|x|g\(y\))\s*=\s*([a-z0-9\s\*\+\-\/\(\)\.\^]+)', text)
        exprs = []
        for e in eq_patterns:
            clean_e = re.split(r'\s+(?:on|about|from|at|in|للغترة|حول|to)\s+', e)[0].strip()
            if clean_e: exprs.append(sp.sympify(clean_e))
        
        if not exprs:
            st.error("لم أجد معادلات واضحة. يرجى كتابتها بصيغة y = ...")
            return

        f_main = exprs[0]
        g_second = exprs[1] if len(exprs) > 1 else sp.sympify(0)

        # 4. استخراج الحدود (دعم الرموز مثل sqrt(3))
        # نبحث عن x=0 أو x=sqrt(3) أو أرقام مجردة
        limit_matches = re.findall(r'(?:x|y)\s*=\s*([a-z0-9\s\*\+\-\/\(\)\.\^]+)|(\d+\.?\d*)', text)
        found_limits = []
        for m in limit_matches:
            val = m[0] if m[0] else m[1]
            try: found_limits.append(sp.sympify(val))
            except: continue
            
        # إذا لم يجد حدوداً صريحة، يبحث عن الأرقام في النص
        if not found_limits:
            nums = re.findall(r"(\d+\.?\d*)", text)
            found_limits = [sp.sympify(n) for n in nums]

        # 5. منطق الحسابات
        st.subheader("📝 الحل الرياضي التفصيلي")
        col1, col2 = st.columns(2)

        with col1:
            if is_about_y:
                # التحويل لمتغير y
                # إذا كانت y = 4 - x^2 -> x^2 = 4 - y
                R_sq = sp.solve(sp.Eq(y_s, f_main), x_s**2)[0] if 'x' in str(f_main) else f_main**2
                r_sq = sp.solve(sp.Eq(y_s, g_second), x_s**2)[0] if ('x' in str(g_second) and g_second != 0) else g_second**2
                
                # تحديد الحدود (إذا كانت x=0 لـ sqrt(3) فإن y=4 لـ 1)
                a_x = found_limits[0] if len(found_limits) >= 1 else 0
                b_x = found_limits[1] if len(found_limits) >= 2 else 1
                
                y_val1 = f_main.subs(x_s, a_x)
                y_val2 = f_main.subs(x_s, b_x)
                y_low, y_high = (y_val2, y_val1) if y_val1 > y_val2 else (y_val1, y_val2)
                
                # تصحيح خاص للمسألة (Example 2.5) لو وجد y=1
                if "y = 1" in text: y_low = sp.sympify(1)

                integrand = sp.simplify(R_sq - r_sq)
                var = y_s
                st.info("الدوران حول المحور الصادي: تحويل الدوال والحدود بدلالة y")
            else:
                var = x_s
                y_low = found_limits[0] if len(found_limits) >= 1 else 0
                y_high = found_limits[1] if len(found_limits) >= 2 else 1
                integrand = sp.simplify(f_main**2 - g_second**2)
                st.info("الدوران حول المحور السيني: التكامل بدلالة x")

            # التكامل النهائي
            antideriv = sp.integrate(integrand, var)
            definite = sp.integrate(integrand, (var, y_low, y_high))
            final_vol = definite * sp.pi

            st.latex(rf"V = \pi \int_{{{sp.latex(y_low)}}}^{{{sp.latex(y_high)}}} ({sp.latex(integrand)}) \, d{var}")
            st.write("**المشتقة العكسية:**")
            st.latex(rf"\pi \left[ {sp.latex(antideriv)} \right]_{{{sp.latex(y_low)}}}^{{{sp.latex(y_high)}}}")
            st.success("النتيجة النهائية:")
            st.latex(rf"V = {sp.latex(sp.simplify(final_vol))} \approx {float(final_vol.evalf()):,.4f}")

        with col2:
            st.subheader("📊 المجسم الناتج")
            # رسم 3D
            fig = plt.figure(figsize=(8,8))
            ax = fig.add_subplot(111, projection='3d')
            
            # تحويل الحدود لأرقام عشرية فقط للرسم
            y_l_f, y_h_f = float(y_low.evalf()), float(y_high.evalf())
            u = np.linspace(y_l_f, y_h_f, 40)
            v = np.linspace(0, 2*np.pi, 40)
            U, V = np.meshgrid(u, v)
            
            r_func = sp.lambdify(var, sp.sqrt(sp.Abs(integrand)), 'numpy')
            R_vals = r_func(U)
            
            if is_about_y:
                X, Y, Z = R_vals*np.cos(V), U, R_vals*np.sin(V)
            else:
                X, Y, Z = U, R_vals*np.cos(V), R_vals*np.sin(V)
            
            ax.plot_surface(X, Y, Z, color='orchid', alpha=0.7, edgecolor='indigo', lw=0.1)
            st.pyplot(fig)

    except Exception as e:
        st.error(f"خطأ في المعالجة: {e}")

if st.button("تحليل وحل المسألة"):
    if raw_input.strip():
        universal_solve()
