import streamlit as st
import numpy as np
import plotly.graph_objects as go
from sympy import symbols, integrate, pi, lambdify, sympify
import re

# 1. إعداد الصفحة
st.set_page_config(page_title="Professional 3D Calculus Solver", layout="wide")

st.title("📐 3D Solid of Revolution Solver")
st.markdown("---")

# 2. منطقة إدخال السؤال كاملاً
st.subheader("Step 1: Enter your Word Problem")
full_question = st.text_area("Paste the full question from your worksheet:", 
                            height=100, 
                            placeholder="e.g., Find the volume of the region bounded by y=sqrt(x) and y=x from x=0 to x=1 about the x-axis.")

# دالة ذكية لاستخراج المعطيات (لتجنب الأخطاء البرمجية)
def extract_parameters(text):
    text = text.lower().replace('^', '**')
    # البحث عن الدوال y=...
    funcs = re.findall(r'y\s*=\s*([a-z0-9\*\+\-\/\(\)\s\.]+)(?=\s|from|bound|,|$)', text)
    # البحث عن الأرقام (الحدود)
    nums = re.findall(r'[-+]?\d*\.\d+|\d+', text)
    
    f_str = funcs[0].strip() if len(funcs) > 0 else "x"
    g_str = funcs[1].strip() if len(funcs) > 1 else "0"
    a = float(nums[-2]) if len(nums) >= 2 else 0.0
    b = float(nums[-1]) if len(nums) >= 1 else 1.0
    return f_str, g_str, a, b

if st.button("Generate Solution & 3D Model"):
    try:
        # استخراج البيانات تلقائياً
        f_in, g_in, a, b = extract_parameters(full_question)
        
        x_sym = symbols('x')
        f_expr = sympify(f_in)
        g_expr = sympify(g_in)
        
        # الحسابات الرياضية
        method = "Washer Method" if g_expr != 0 else "Disk Method"
        integrand = f_expr**2 - g_expr**2
        antiderivative = integrate(integrand, x_sym)
        exact_val = integrate(integrand, (x_sym, a, b)) * pi
        
        # عرض النتائج في عمودين
        col1, col2 = st.columns([1, 1.2])

        with col1:
            st.subheader("📝 Detailed Solution")
            st.write(f"**Detected Method:** {method}")
            st.write(f"**Interval:** [{a}, {b}]")
            st.write("---")
            st.write("**1. Integral Setup:**")
            st.latex(f"V = \pi \int_{{{a}}}^{{{b}}} ({integrand}) dx")
            st.write("**2. Antiderivative:**")
            st.latex(f"\pi \left[ {antiderivative} \\right]_{{{a}}}^{{{b}}}")
            st.success(f"**Final Volume:** {float(exact_val.evalf()):.4f} units³")

        with col2:
            st.subheader("🧊 Interactive 3D Model")
            # توليد نقاط الرسم 3D
            u = np.linspace(float(a), float(b), 60)
            v = np.linspace(0, 2*np.pi, 60)
            U, V = np.meshgrid(u, v)
            f_n, g_n = lambdify(x_sym, f_expr, 'numpy'), lambdify(x_sym, g_expr, 'numpy')
            
            # السطح الخارجي
            X, Y, Z = U, f_n(U)*np.cos(V), f_n(U)*np.sin(V)
            fig = go.Figure()
            fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale='Reds', opacity=0.8, showscale=False))
            
            # السطح الداخلي (Washer)
            if g_expr != 0:
                X2, Y2, Z2 = U, g_n(U)*np.cos(V), g_n(U)*np.sin(V)
                fig.add_trace(go.Surface(x=X2, y=Y2, z=Z2, colorscale='Blues', opacity=0.9, showscale=False))
            
            fig.update_layout(scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z', aspectmode='data'))
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error: Please ensure the functions are written clearly (e.g., y=x**2). Detail: {e}")
