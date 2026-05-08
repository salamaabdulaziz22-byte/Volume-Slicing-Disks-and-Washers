import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="Ultimate Math Solver", layout="wide")
st.title("Smart Calculus Solver")

# خانة السؤال
question = st.text_area("Paste your textbook question here:", 
    "Example: y = 4 - x^2 and y = 1 from x = 0 to x = sqrt(3) about the y-axis")

if st.button("Solve & Generate Graph"):
    x, y = sp.symbols('x y')
    try:
        # 1. نظام "الترجمة الذكية" لتصحيح أخطاء النسخ (Copy-Paste)
        # يحول الأسس والجذور والصيغ الشائعة لصيغة يفهمها البرنامج
        clean_q = question.lower()
        clean_q = clean_q.replace('√', 'sqrt').replace('vx', 'sqrt(x)')
        clean_q = re.sub(r'([xy])(\d)', r'\1**\2', clean_q) # يحول x2 إلى x**2
        clean_q = clean_q.replace('^', '**')
        
        # 2. تحديد المتغير والاتجاه (x-axis vs y-axis)
        var = y if 'y-axis' in clean_q else x
        
        # 3. استخراج المعادلات
        found_eqs = re.findall(r'[xy]\s*=\s*([0-9x\s\+\-\*\^/\(\)sqrt]+)', clean_q)
        # استخراج الأرقام (الفترة)
        nums = re.findall(r'(\d+\.?\d*)', clean_q)
        
        if found_eqs:
            f_expr = sp.sympify(found_eqs[0].strip())
            g_expr = sp.sympify(found_eqs[1].strip()) if len(found_eqs) > 1 else sp.sympify(0)
            
            # معالجة ذكية للجذور في الفترة (مثل sqrt(3))
            a_val = 0.0
            b_val = float(nums[-1]) if nums else 1.0
            if 'sqrt(3)' in clean_q: b_val = float(sp.sqrt(3).evalf())

            # حساب التكامل
            integrand = sp.simplify(f_expr**2 - g_expr**2)
            volume = sp.pi * sp.integrate(integrand, (var, a_val, b_val))
            
            st.success(f"✅ Extracted: f={f_expr}, g={g_expr} on [{a_val}, {b_val}]")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📝 Mathematical Solution")
                st.latex(rf"V = \pi \int_{{{a_val}}}^{{{b_val}}} ({sp.latex(integrand)}) \, d{var}")
                st.write("**Final Volume:**")
                st.latex(rf"V = {sp.latex(volume)} \approx {float(volume.evalf()):.4f}")

            with col2:
                st.subheader("📊 Visualization")
                t_vals = np.linspace(float(a_val), float(b_val), 100)
                f_n = sp.lambdify(var, f_expr, 'numpy')(t_vals)
                fig, ax = plt.subplots()
                ax.plot(t_vals, f_n, color='red', label='f(var)')
                ax.fill_between(t_vals, f_n, alpha=0.2, color='orange')
                st.pyplot(fig)
        else:
            st.error("Could not find equations. Try writing as 'y = ...'")
    except Exception as e:
        st.error(f"Analysis Error: {e}. Tip: Use '**' for power, e.g., x**2")
