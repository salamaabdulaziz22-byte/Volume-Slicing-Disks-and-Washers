import streamlit as st
import numpy as np
import plotly.graph_objects as go
from sympy import symbols, integrate, pi, lambdify, sympify
import re

# 1. إعدادات الواجهة الاحترافية
st.set_page_config(page_title="Professional Calculus Solver", layout="wide")
st.title("🎓 Pro 3D Volume Solver")
st.write("Enter the full English problem. The system will extract functions and limits automatically.")

# 2. منطقة إدخال السؤال الكامل
full_question = st.text_area("Question Box:", height=120, 
                            placeholder="e.g., Find the volume of the region bounded by y=x**2 and y=x from x=0 to x=1 revolved about the x-axis.")

# دالة الاستخراج الذكي (هذا هو الحل الجذري للأخطاء)
def smart_extract(text):
    text = text.replace('^', '**') # تحويل الأسس لصيغة بايثون
    # البحث عن الدوال
    funcs = re.findall(r'[yf]\(?[xy]\)?\s*=\s*([a-zA-Z0-9\*\*\+\-\/\(\)\s\.]+(?=\s|from|bound|,|$))', text)
    # البحث عن الأرقام (الحدود)
    nums = re.findall(r'[-+]?\d*\.\d+|\d+', text)
    
    f = funcs[0].strip() if len(funcs) > 0 else "x**2"
    g = funcs[1].strip() if len(funcs) > 1 else "0"
    a = float(nums[-2]) if len(nums) >= 2 else 0.0
    b = float(nums[-1]) if len(nums) >= 1 else 1.0
    return f, g, a, b

if st.button("Generate Professional Solution"):
    try:
        # استخراج البيانات
        f_in, g_in, a, b = smart_extract(full_question)
        
        x = symbols('x')
        f_expr = sympify(f_in)
        g_expr = sympify(g_in)
        
        method = "Washer Method" if g_expr != 0 else "Disk Method"
        integrand = f_expr**2 - g_expr**2
        
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📋 Extraction & Steps")
            st.markdown(f"**Detected f(x):** `{f_in}` | **g(x):** `{g_in}`")
            st.markdown(f"**Limits:** from `{a}` to `{b}`")
            
            st.write("---")
            st.latex(r"V = \pi \int_{a}^{b} [R(x)^2 - r(x)^2] dx")
            
            # العمليات الحسابية
            antiderivative = integrate(integrand, x)
            exact_val = integrate(integrand, (x, a, b)) * pi
            
            st.write("**Antiderivative:**")
            st.latex(f"\pi \left[ {antiderivative} \\right]_{{{a}}}^{{{b}}}")
            st.success(f"**Final Result:** {float(exact_val.evalf()):.4f} units³")

        with col2:
            st.subheader("🧊 3D Visualization")
            # بناء المجسم 3D
            u_space = np.linspace(float(a), float(b), 50)
            v_rot = np.linspace(0, 2*np.pi, 50)
            U, V = np.meshgrid(u_space, v_rot)
            
            f_n = lambdify(x, f_expr, 'numpy')
            g_n = lambdify(x, g_expr, 'numpy')
            
            # إحداثيات الدوران
            X, Y, Z = U, f_n(U)*np.cos(V), f_n(U)*np.sin(V)
            
            fig = go.Figure()
            fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale='Reds', opacity=0.8, showscale=False))
            
            if g_expr != 0:
                X2, Y2, Z2 = U, g_n(U)*np.cos(V), g_n(U)*np.sin(V)
                fig.add_trace(go.Surface(x=X2, y=Y2, z=Z2, colorscale='Blues', opacity=0.9, showscale=False))
            
            fig.update_layout(scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'))
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error("I couldn't parse the question perfectly. Please try formatting functions like y=x**2.")
