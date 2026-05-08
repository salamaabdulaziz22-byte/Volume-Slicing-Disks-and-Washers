import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re

# إعدادات الصفحة
st.set_page_config(page_title="Math Solver Pro", layout="wide")
st.title("📐 Advanced Calculus Volume Solver")
st.markdown("قم بلصق المسألة وسأقوم بتحليلها، حلها خطوة بخطوة، ورسمها 3D.")

# مدخلات المستخدم
raw_input = st.text_area("Paste your calculus problem here:", height=150, 
                         placeholder="مثال: y = sqrt(x), from x = 0 to 4 about x-axis")

def solve_calculus():
    try:
        # 1. تنظيف النص وتحليله
        text = raw_input.lower()
        x, y, z = sp.symbols('x y z')
        
        # استخراج الأرقام (الحدود)
        numbers = [float(n) for n in re.findall(r"[-+]?\d*\.\d+|\d+", text)]
        
        # تحديد نوع المسألة
        is_about_y = "about y-axis" in text or "about the y axis" in text
        is_pyramid = "pyramid" in text
        
        st.subheader("📝 الخطوات الرياضية (Step-by-Step)")
        col1, col2 = st.columns([1, 1])

        with col1:
            if is_pyramid:
                # حل مسألة الهرم (مثل المثال 2.1 في الصور)
                side = max(numbers) # 180
                height = min([n for n in numbers if n != side and n != 0] + [100]) # 100
                
                st.write(f"**1. تحديد دالة طول الضلع:**")
                st.write(f"بما أن القاعدة مربعة والضلع يقل تدريجياً:")
                f_x = (side/height) * (height - x)
                st.latex(rf"f(x) = {sp.latex(f_x)}")
                
                st.write("**2. دالة المساحة A(x):**")
                a_x = f_x**2
                st.latex(rf"A(x) = ({sp.latex(f_x)})^2")
                
                a, b = 0, height
                integrand = a_x
                var = x
                final_multiplier = 1 # لا يوجد pi في الهرم المربع

            else:
                # حل مسائل الدوران (Disks/Washers)
                # استخراج الدوال (يبحث عن y=... أو f(x)=...)
                func_matches = re.findall(r"(?:y|f\(x\)|x|g\(y\))\s*=\s*([^,]+)", text)
                exprs = [sp.sympify(m.replace('^', '**').replace('√', 'sqrt').strip()) for m in func_matches]
                
                if not exprs:
                    st.error("لم أستطع التعرف على الدوال. حاول كتابتها بصيغة y = x**2")
                    return

                f_expr = exprs[0]
                g_expr = exprs[1] if len(exprs) > 1 else sp.sympify(0)
                
                # تحديد الحدود تلقائياً إذا لم توجد
                a = min(numbers) if len(numbers) >= 2 else 0
                b = max(numbers) if len(numbers) >= 2 else 1
                
                if is_about_y:
                    st.write("**نوع المسألة:** دوران حول المحور الصادي (y-axis)")
                    var = y
                    # إذا كانت الدالة تحتوي x، نحاول حلها بالنسبة لـ y
                    if 'x' in str(f_expr):
                        f_expr = sp.solve(sp.Eq(y, f_expr), x)[0]
                else:
                    st.write("**نوع المسألة:** دوران حول المحور السيني (x-axis)")
                    var = x

                integrand = sp.simplify(f_expr**2 - g_expr**2)
                final_multiplier = sp.pi
                
                st.write("**1. إعداد التكامل:**")
                st.latex(rf"V = \pi \int_{{{a}}}^{{{b}}} \left( {sp.latex(f_expr)}^2 - {sp.latex(g_expr)}^2 \right) d{var}")

            # حساب التكامل
            antideriv = sp.integrate(integrand, var)
            result = sp.integrate(integrand, (var, a, b)) * final_multiplier
            
            st.write("**2. المشتقة العكسية:**")
            st.latex(rf"{sp.latex(antideriv)}")
            
            st.write("**3. النتيجة النهائية:**")
            st.success(f"النتيجة: {result}")
            st.latex(rf"V = {sp.latex(sp.simplify(result))} \approx {float(result.evalf()):,.2f}")

        # 3. الرسم البياني 3D
        with col2:
            st.subheader("📊 المجسم الناتج (3D View)")
            fig = plt.figure(figsize=(8, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            u = np.linspace(float(a), float(b), 60)
            v = np.linspace(0, 2 * np.pi, 60)
            U, V = np.meshgrid(u, v)
            
            # تحويل الدالة لرقمية للرسم
            f_num = sp.lambdify(var, f_expr if not is_pyramid else sp.sqrt(a_x), 'numpy')
            R = f_num(U)
            
            if is_about_y or is_pyramid: # في الهرم والرسم الرأسي
                X_p = R * np.cos(V)
                Z_p = R * np.sin(V)
                Y_p = U
            else:
                X_p = U
                Y_p = R * np.cos(V)
                Z_p = R * np.sin(V)
                
            surf = ax.plot_surface(X_p, Y_p, Z_p, cmap='viridis', alpha=0.7, edgecolor='none')
            ax.set_title("Solid of Revolution / Volume Shape")
            st.pyplot(fig)

    except Exception as e:
        st.error(f"حدث خطأ أثناء التحليل: {e}")
        st.info("نصيحة: تأكد من كتابة الدالة بوضوح مثل y = sqrt(x) والحدود من 0 إلى 4.")

if st.button("تحليل وحل المسألة"):
    if raw_input:
        solve_calculus()
    else:
        st.warning("الرجاء إدخال نص المسألة أولاً.")
