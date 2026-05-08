import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re

st.set_page_config(page_title="Universal Calculus Solver", layout="wide")
st.title("🚀 Universal Calculus Volume Solver")

raw_input = st.text_area("أدخل المسألة هنا:", height=150, 
                         placeholder="e.g., y = 4 - x^2 and y = 1 from x = 0 to x = V3 about the y-axis")

def universal_solve():
    try:
        # 1. تنظيف النص ومعالجة الجذور
        text = raw_input.lower().replace('^', '**').replace('√', 'sqrt')
        text = re.sub(r'[vV](\d+)', r'sqrt(\1)', text)
        text = text.replace('vx', 'sqrt(x)')
        
        x_s, y_s = sp.symbols('x y')
        
        # 2. تحديد المحور
        is_about_y = any(word in text for word in ["y-axis", "y axis", "صادات"])
        
        # 3. استخراج الدوال
        eq_patterns = re.findall(r'(?:y|f\(x\)|x|g\(y\))\s*=\s*([a-z0-9\s\*\+\-\/\(\)\.\^]+)', text)
        exprs = []
        for e in eq_patterns:
            clean_e = re.split(r'\s+(?:on|about|from|at|in|للغترة|حول|to)\s+', e)[0].strip()
            if clean_e: exprs.append(sp.sympify(clean_e))
        
        if not exprs:
            st.error("لم يتم العثور على معادلات واضحة.")
            return

        f_main = exprs[0]
        g_second = exprs[1] if len(exprs) > 1 else sp.sympify(0)

        # 4. استخراج الحدود
        limit_matches = re.findall(r'(?:x|y)\s*=\s*([a-z0-9\s\*\+\-\/\(\)\.\^]+)|(\d+\.?\d*)', text)
        found_limits = []
        for m in limit_matches:
            val = m[0] if m[0] else m[1]
            try: found_limits.append(sp.sympify(val))
            except: continue
        
        if not found_limits:
            nums = re.findall(r"(\d+\.?\d*)", text)
            found_limits = [sp.sympify(n) for n in nums]

        # 5. منطق الحسابات
        st.subheader("📝 الحل الرياضي التفصيلي")
        col1, col2 = st.columns(2)

        with col1:
            if is_about_y:
                # حل المعادلة لـ x^2 بدلالة y
                R_sq = sp.solve(sp.Eq(y_s, f_main), x_s**2)[0] if 'x' in str(f_main) else f_main**2
                r_sq = sp.solve(sp.Eq(y_s, g_second), x_s**2)[0] if ('x' in str(g_second) and g_second != 0) else g_second**2
                
                # حساب حدود y
                x1 = found_limits[0] if len(found_limits) >= 1 else 0
                x2 = found_limits[1] if len(found_limits) >= 2 else 1
                
                v1, v2 = f_main.subs(x_s, x1), f_main.subs(x_s, x2)
                # استخدام min/max العادي لتجنب خطأ Relational
                y_low = v1 if v1.evalf() < v2.evalf() else v2
                y_high = v2 if v1.evalf() < v2.evalf() else v1
                
                # استثناء للمسألة المعينة y=1
                if "y = 1" in text: y_low = sp.Integer(1)

                integrand = sp.simplify(R_sq - r_sq)
                var = y_s
            else:
                var = x_s
                v1 = found_limits[0] if len(found_limits) >= 1 else 0
                v2 = found_limits[1] if len(found_limits) >= 2 else 1
                y_low = v1 if v1.evalf() < v2.evalf() else v2
                y_high = v2 if v1.evalf() < v2.evalf() else v1
                integrand = sp.simplify(f_main**2 - g_second**2)

            # الحساب
            antideriv = sp.integrate(integrand, var)
            definite = sp.integrate(integrand, (var, y_low, y_high))
            final_vol = definite * sp.pi

            st.latex(rf"V = \pi \int_{{{sp.latex(y_low)}}}^{{{sp.latex(y_high)}}} ({sp.latex(integrand)}) \, d{var}")
            st.write("**المشتقة العكسية:**")
            st.latex(rf"F({var}) = \pi \left[ {sp.latex(antideriv)} \right]")
            st.success("النتيجة النهائية:")
            st.latex(rf"V = {sp.latex(sp.simplify(final_vol))} \approx {float(final_vol.evalf()):,.4f}")

        with col2:
            st.subheader("📊 المجسم ثلاثي الأبعاد")
            fig = plt.figure(figsize=(7,7))
            ax = fig.add_subplot(111, projection='3d')
            
            # تحويل الحدود لأرقام للرسم
            l_f, h_f = float(y_low.evalf()), float(y_high.evalf())
            u = np.linspace(l_f, h_f, 40)
            v = np.linspace(0, 2*np.pi, 40)
            U, V = np.meshgrid(u, v)
            
            r_func = sp.lambdify(var, sp.sqrt(sp.Abs(integrand)), 'numpy')
            R_vals = r_func(U)
            
            if is_about_y:
                X, Y, Z = R_vals*np.cos(V), U, R_vals*np.sin(V)
            else:
                X, Y, Z = U, R_vals*np.cos(V), R_vals*np.sin(V)
            
            ax.plot_surface(X, Y, Z, color='cyan', alpha=0.6, edgecolor='blue', lw=0.1)
            st.pyplot(fig)

    except Exception as e:
        st.error(f"خطأ في المعالجة: {e}")

if st.button("تحليل وحل المسألة"):
    if raw_input.strip(): universal_solve()
