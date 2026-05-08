import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="Ultimate Solver", layout="wide")
st.title("Expert Calculus Solver")

question = st.text_area("Paste your textbook question here:", 
    "Find the volume... revolving y=4-x**2 and y=1 from x=0 to x=sqrt(3) about the y-axis")

if st.button("Solve & Generate Graph"):
    try:
        # 1. تنظيف النصوص وتحويل الرموز الشائعة
        q = question.lower().replace('^', '**').replace('√', 'sqrt').replace('vx', 'sqrt(3)')
        q = re.sub(r'([xy])(\d)', r'\1**\2', q) # يحول x2 إلى x**2
        
        # 2. تحديد المتغير الأساسي ومحور الدوران
        is_y_axis = 'y-axis' in q
        var = sp.Symbol('y') if is_y_axis else sp.Symbol('x')
        
        # 3. استخراج الدوال
        eqs = re.findall(r'[xy]\s*=\s*([0-9x\s\+\-\*\^/\(\)sqrt]+)', q)
        nums = re.findall(r'(\d+\.?\d*)', q)
        
        if eqs:
            # تحويل المعادلات لتكون بدلالة المتغير الصحيح
            f_expr = sp.sympify(eqs[0].strip())
            if is_y_axis and 'x' in str(f_expr):
                # إذا كان الدوران حول y والدالة معطاة كـ y=f(x)، نحولها لـ x=f(y)
                f_expr = sp.solve(sp.Eq(sp.Symbol('y'), f_expr), sp.Symbol('x'))[0]

            g_expr = sp.sympify(eqs[1].strip()) if len(eqs) > 1 else sp.sympify(0)
            
            # تحديد الفترة
            a_val = 0.0
            b_val = float(nums[-1]) if nums else 1.0
            if 'sqrt(3)' in q: b_val = float(sp.sqrt(3).evalf())

            # حساب التكامل
            integrand = sp.simplify(f_expr**2 - g_expr**2)
            volume = sp.pi * sp.integrate(integrand, (var, a_val, b_val))
            
            st.success(f"✅ Extracted: Function is now in terms of {var}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📝 Mathematical Solution")
                st.latex(rf"V = \pi \int_{{{a_val}}}^{{{b_val}}} ({sp.latex(integrand)}) \, d{var}")
                st.write("**Final Volume:**")
                st.latex(rf"V = {sp.latex(volume)} \approx {float(volume.evalf()):.4f}")

            with col2:
                st.subheader("📊 Visualization")
                # الرسم البياني باستخدام numpy
                t_vals = np.linspace(float(a_val), float(b_val), 100)
                f_func = sp.lambdify(var, f_expr, 'numpy')
                f_num = f_func(t_vals)
                
                fig, ax = plt.subplots()
                ax.plot(t_vals, f_num, color='red', label='Region Boundary')
                ax.fill_between(t_vals, f_num, alpha=0.3, color='cyan')
                ax.set_xlabel(str(var))
                st.pyplot(fig)
        else:
            st.error("Could not find equations. Example: y = 4 - x**2")
    except Exception as e:
        st.error(f"Try making the question simpler or check the math symbols.")
