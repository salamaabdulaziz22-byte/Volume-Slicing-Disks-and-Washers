import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="Smart Math Solver", layout="wide")
st.title("🤖 Smart Volume Solver (Natural Language)")
st.write("Paste your math problem below (e.g., y = x^2, interval [1, 3])")

# خانة السؤال
question = st.text_area("Enter your question here:", 
    "Revolve the region under the curve y = sqrt(x) on the interval [0, 4] about the x-axis")

if st.button("Analyze & Solve"):
    x = sp.symbols('x')
    try:
        # 1. تنظيف النص وتبسيطه للبرنامج
        clean_q = question.replace('Vx', 'sqrt(x)').replace('√x', 'sqrt(x)').replace('^', '**')
        
        # 2. البحث عن الدوال (y=...)
        functions = re.findall(r'y\s*=\s*([^\s,]+)', clean_q)
        
        # 3. البحث عن الفترة [a, b]
        interval = re.findall(r'(\d+\.?\d*)', clean_q)

        if functions and len(interval) >= 2:
            f_expr = sp.sympify(functions[0])
            g_expr = sp.sympify(functions[1]) if len(functions) > 1 else sp.sympify(0)
            
            a_val = float(interval[-2])
            b_val = float(interval[-1])
            
            st.success(f"✅ Extracted: f(x)={f_expr}, Interval=[{a_val}, {b_val}]")
            
            # حساب التكامل
            is_washer = g_expr != 0
            integrand = f_expr**2 - g_expr**2
            volume_expr = sp.pi * sp.integrate(integrand, (x, a_val, b_val))
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📝 Steps")
                st.write("**Integral Setup:**")
                st.latex(rf"\pi \int_{{{a_val}}}^{{{b_val}}} ({sp.latex(integrand)}) \, dx")
                
                st.write("**Final Result:**")
                st.latex(rf"V = {sp.latex(volume_expr)} \approx {float(volume_expr.evalf()):.4f}")

            with col2:
                st.subheader("📊 Visualization")
                x_vals = np.linspace(a_val, b_val, 100)
                # تحويل المعادلة لرقم ليقبلها الرسم
                f_num = sp.lambdify(x, f_expr, 'numpy')(x_vals)
                g_num = sp.lambdify(x, g_expr, 'numpy')(x_vals) if is_washer else np.zeros_like(x_vals)
                
                fig, ax = plt.subplots()
                ax.plot(x_vals, f_num, 'r', label='f(x)')
                if is_washer: ax.plot(x_vals, g_num, 'b', label='g(x)')
                ax.fill_between(x_vals, f_num, g_num, color='orange', alpha=0.3)
                st.pyplot(fig)
        else:
            st.error("Could not find a clear function (y=...) or interval [a, b]. Please check the format.")
    except Exception as e:
        st.error(f"Error: {e}")
