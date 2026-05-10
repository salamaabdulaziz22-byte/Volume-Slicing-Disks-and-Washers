import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

# إعدادات واجهة الموقع
st.set_page_config(page_title="Volume Solver Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stTitle { color: #1E3A8A; font-family: 'Arial'; }
    </style>
    """, unsafe_allow_html=True)

st.title("📐 Volume of Revolution Calculator")
st.subheader("Grade 12 Math Project - Term 3")

# منطقة إدخال البيانات
with st.sidebar:
    st.header("Input Parameters")
    f_input = st.text_input("Outer Function f(x)", "x")
    g_input = st.text_input("Inner Function g(x) (0 for Disk)", "x**2")
    a = st.number_input("Lower Bound (a)", value=0.0)
    b = st.number_input("Upper Bound (b)", value=1.0)
    axis = st.selectbox("Axis of Rotation", ["x-axis", "y-axis"])

# معالجة المسألة رياضياً
try:
    x = sp.symbols('x')
    f_expr = sp.sympify(f_input)
    g_expr = sp.sympify(g_input)
    
    # تحديد الطريقة
    method = "Disk Method" if g_expr == 0 else "Washer Method"
    
    # حساب التكامل
    # Formula: V = π ∫ (f^2 - g^2) dx
    integrand = sp.pi * (f_expr**2 - g_expr**2)
    volume_integral = sp.integrate(integrand, (x, a, b))
    
    # العرض في الموقع
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"### Detected Method: {method}")
        st.write("#### Step 1: Setup the Integral")
        if g_expr == 0:
            st.latex(rf"V = \pi \int_{{{a}}}^{{{b}}} ({sp.latex(f_expr)})^2 \, dx")
        else:
            st.latex(rf"V = \pi \int_{{{a}}}^{{{b}}} \left[ ({sp.latex(f_expr)})^2 - ({sp.latex(g_expr)})^2 \right] \, dx")
            
        st.write("#### Step 2: Final Result")
        st.success(f"The Volume is: **{volume_integral}**")
        st.write(f"Approximate Value: **{float(volume_integral.evalf()):.4f} cubic units**")

    with col2:
        st.write("#### Visualization")
        # الرسم البياني
        t = np.linspace(float(a), float(b), 100)
        f_num = sp.lambdify(x, f_expr, 'numpy')(t)
        g_num = sp.lambdify(x, g_expr, 'numpy')(t) if g_expr != 0 else np.zeros_like(t)
        
        fig, ax = plt.subplots()
        ax.plot(t, f_num, label='f(x)')
        if g_expr != 0:
            ax.plot(t, g_num, label='g(x)')
        ax.fill_between(t, f_num, g_num, color='skyblue', alpha=0.5)
        ax.set_title("Region to Rotate")
        ax.legend()
        st.pyplot(fig)

except Exception as e:
    st.error("Please enter valid mathematical expressions (e.g., x**2 for x²)")
