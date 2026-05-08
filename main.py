import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="Pro Volume Solver", layout="wide")
st.title("Expert Volume of Revolution Solver")
st.markdown("---")

# خانة السؤال
question = st.text_area("Paste your textbook question:", 
    "Find the volume of the solid resulting from revolving the region bounded by y = 4 - x**2 and y = 0 from x = 0 to x = 2 about the x-axis")

if st.button("Calculate Everything"):
    x = sp.symbols('x')
    try:
        # 1. معالجة ذكية للنص لاستخراج المعادلات
        # يبحث عن أي شيء بعد y = ويقوم بتنظيفه
        found_eqs = re.findall(r'y\s*=\s*([0-9x\s\+\-\*\^/\(\)sqrt]+)', question.replace('^', '**'))
        
        # 2. استخراج الفترة (الأرقام)
        nums = re.findall(r'(-?\d+\.?\d*)', question)
        
        if len(found_eqs) >= 1 and len(nums) >= 2:
            f_expr = sp.sympify(found_eqs[0].strip())
            # إذا كان هناك دالة ثانية (Washer) أو نعتبرها 0 (Disk)
            g_expr = sp.sympify(found_eqs[1].strip()) if len(found_eqs) > 1 else sp.sympify(0)
            
            # تحديد الفترة (آخر رقمين عادة هما حدود التكامل)
            a_val, b_val = float(nums[-2]), float(nums[-1])
            
            st.success(f"✅ Analysis Complete: Integrating from {a_val} to {b_val}")
            
            # حساب التكامل
            integrand = sp.simplify(f_expr**2 - g_expr**2)
            volume_exact = sp.pi * sp.integrate(integrand, (x, a_val, b_val))
            
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("📝 Mathematical Solution")
                st.latex(rf"V = \pi \int_{{{a_val}}}^{{{b_val}}} ({sp.latex(integrand)}) \, dx")
                st.write("**Exact Result:**")
                st.latex(rf"V = {sp.latex(volume_exact)}")
                st.write("**Decimal Approximation:**")
                st.info(f"{float(volume_exact.evalf()):.4f} cubic units")

            with c2:
                st.subheader("📊 2D Region Map")
                x_p = np.linspace(a_val, b_val, 100)
                f_p = sp.lambdify(x, f_expr, 'numpy')(x_p)
                g_p = sp.lambdify(x, g_expr, 'numpy')(x_p) if g_expr != 0 else np.zeros_like(x_p)
                
                fig, ax = plt.subplots()
                ax.plot(x_p, f_p, 'r', label='Top Curve')
                ax.plot(x_p, g_p, 'b', label='Bottom Curve')
                ax.fill_between(x_p, f_p, g_p, color='cyan', alpha=0.3)
                ax.legend()
                st.pyplot(fig)
        else:
            st.error("Format not recognized. Ensure you have 'y = ...' and numbers for the interval.")
    except Exception as e:
        st.error(f"Try writing the equation more clearly (e.g., use x**2 for x²)")
