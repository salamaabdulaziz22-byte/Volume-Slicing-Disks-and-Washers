import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="Smart Math Solver", layout="wide")
st.title("🤖 Smart Volume Solver (Natural Language)")
st.write("Paste your full question below, and I will extract the math!")

# خانة السؤال الكامل
question = st.text_area("Enter your question here:", 
    "Revolve the region under the curve y = sqrt(x) on the interval [0, 4] about the x-axis")

if st.button("Analyze & Solve"):
    try:
        # 1. استخراج الدالة باستخدام Regex
        func_match = re.search(r'y\s*=\s*([^on\s]+)', question)
        # 2. استخراج الفترة
        interval_match = re.findall(r'(\d+\.?\d*)', question)
        
        if func_match and len(interval_match) >= 2:
            f_expr = func_match.group(1).replace('V', 'sqrt') # تحويل V لـ sqrt إذا كتبتِها هكذا
            a_val = float(interval_match[-2])
            b_val = float(interval_match[-1])
            
            x = sp.symbols('x')
            f = sp.sympify(f_expr)
            
            # الحل
            st.success(f"Extracted: f(x) = {f_expr}, Interval = [{a_val}, {b_val}]")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📝 Steps")
                integrand = f**2
                formula = sp.pi * sp.Integral(integrand, (x, a_val, b_val))
                st.latex(sp.latex(formula))
                
                volume = sp.pi * sp.integrate(integrand, (x, a_val, b_val))
                st.write("**Final Volume:**")
                st.latex(f"V = {sp.latex(volume)} \approx {float(volume.evalf()):.4f}")

            with col2:
                st.subheader("📊 Visualization")
                x_vals = np.linspace(a_val, b_val, 100)
                f_p = sp.lambdify(x, f, 'numpy')(x_vals)
                fig, ax = plt.subplots()
                ax.plot(x_vals, f_p, color='red')
                ax.fill_between(x_vals, f_p, color='orange', alpha=0.3)
                st.pyplot(fig)
        else:
            st.warning("Could not clearly find the function or interval. Try to keep the format 'y = ...' and '[a, b]'")
    except Exception as e:
        st.error(f"Error analyzing the question: {e}")
