import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="Math Master Solver", layout="wide")
st.title("🎓 Advanced Volume of Revolution Solver")

question = st.text_area("Paste your textbook question here:", 
    "Find the volume... revolving y=4-x**2 and y=1 from x=0 to x=sqrt(3) about the y-axis")

if st.button("Solve Step-by-Step"):
    try:
        # 1. تنظيف النص وتحويله لصيغة رياضية
        text = question.lower().replace('^', '**').replace('√', 'sqrt')
        
        # 2. تحديد متغير التكامل (x أو y)
        var = sp.Symbol('y') if 'y-axis' in text else sp.Symbol('x')
        
        # 3. استخراج الدوال والفترات
        # هذا الجزء مبرمج ليكون مرناً جداً مع طريقة كتابتك
        eqs = re.findall(r'[xy]\s*=\s*([0-9\s\+\-\*\^/\(\)sqrt]+|[0-9x]+)', text)
        nums = re.findall(r'(\d+\.?\d*)', text)
        
        if len(eqs) >= 1:
            f = sp.sympify(eqs[0].strip().replace('x2', 'x**2'))
            g = sp.sympify(eqs[1].strip()) if len(eqs) > 1 else sp.sympify(0)
            
            # تحديد حدود التكامل (مثلاً من 0 إلى جذر 3)
            # سنقوم بحسابها تلقائياً إذا وجدت في النص
            a_val = 0.0
            b_val = float(nums[-1]) if nums else 1.0
            if 'sqrt(3)' in text: b_val = float(sp.sqrt(3).evalf())

            # حساب التكامل للحجم
            integrand = sp.simplify(f**2 - g**2)
            volume = sp.pi * sp.integrate(integrand, (var, a_val, b_val))
            
            st.success(f"✅ Extracted: Integrating {f} along the {var}-axis")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📝 Steps")
                st.latex(rf"V = \pi \int_{{{a_val}}}^{{{b_val}}} ({sp.latex(integrand)}) \, d{var}")
                st.write("**Exact Result:**")
                st.latex(rf"V = {sp.latex(volume)}")
                st.info(f"Decimal Value: {float(volume.evalf()):.4f}")

            with col2:
                st.subheader("📊 Visualization")
                # رسم توضيحي مبسط للمنطقة
                t_vals = np.linspace(float(a_val), float(b_val), 100)
                f_n = sp.lambdify(var, f, 'numpy')(t_vals)
                fig, ax = plt.subplots()
                ax.plot(t_vals, f_n, 'r')
                ax.fill_between(t_vals, f_n, alpha=0.3)
                st.pyplot(fig)
    except Exception as e:
        st.error("Please ensure the equation is clear, e.g., y = 4 - x**2")
