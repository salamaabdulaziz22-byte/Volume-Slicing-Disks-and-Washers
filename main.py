import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

# --- إعدادات الصفحة الرسمية ---
st.set_page_config(page_title="Volume Solver - Al Shawamekh School", layout="wide")

# تصميم بسيط وراقي
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .main-title { color: #2E4053; font-family: 'Segoe UI'; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>📐 Solid of Revolution Calculator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Designed for Grade 12 Advanced Math - Term 3</p>", unsafe_allow_html=True)
st.divider()

# --- مدخلات المستخدم (تبدأ فارغة) ---
col_in1, col_in2 = st.columns(2)

with col_in1:
    f_input = st.text_input("Enter Outer Function f(x):", placeholder="e.g., x")
    g_input = st.text_input("Enter Inner Function g(x):", placeholder="Leave empty for Disk Method")

with col_in2:
    a = st.text_input("Lower Bound (a):", placeholder="0")
    b = st.text_input("Upper Bound (b):", placeholder="1")

# زر التشغيل
solve_btn = st.button("✨ Calculate Volume")

# --- منطق الحل (لا يظهر إلا عند الضغط وكتابة بيانات) ---
if solve_btn:
    if not f_input:
        st.warning("Please enter at least the outer function f(x) to start.")
    else:
        try:
            # تحويل المدخلات إلى رموز رياضية
            x = sp.symbols('x')
            f_expr = sp.sympify(f_input)
            g_expr = sp.sympify(g_input) if g_input else sp.sympify(0)
            
            # تحويل الحدود إلى أرقام
            a_val = float(a) if a else 0.0
            b_val = float(b) if b else 1.0
            
            # تحديد الطريقة
            method = "Disk Method" if g_expr == 0 else "Washer Method"
            
            # حساب التكامل
            integrand = sp.pi * (f_expr**2 - g_expr**2)
            volume = sp.integrate(integrand, (x, a_val, b_val))
            
            # --- عرض النتائج (تظهر الآن فقط) ---
            st.divider()
            res_col1, res_col2 = st.columns([1, 1])
            
            with res_col1:
                st.subheader(f"Method: {method}")
                st.write("**Integration Setup:**")
                st.latex(rf"V = \pi \int_{{{a_val}}}^{{{b_val}}} \left( {sp.latex(f_expr**2 - g_expr**2)} \right) \, dx")
                
                st.write("**Final Result:**")
                st.success(f"Final Volume: {volume} cubic units")
                st.write(f"Approximate Value: **{float(volume.evalf()):.4f}**")

            with res_col2:
                st.subheader("Region Visualization")
                t = np.linspace(a_val, b_val, 100)
                f_num = sp.lambdify(x, f_expr, 'numpy')(t)
                g_num = sp.lambdify(x, g_expr, 'numpy')(t)
                
                fig, ax = plt.subplots(figsize=(5, 3))
                ax.plot(t, f_num, label='f(x)', color='blue')
                if g_input:
                    ax.plot(t, g_num, label='g(x)', color='red')
                
                ax.fill_between(t, f_num, g_num, color='skyblue', alpha=0.4)
                ax.grid(True, linestyle='--', alpha=0.6)
                ax.legend()
                st.pyplot(fig)
                
        except Exception as e:
            st.error(f"Error: Could not solve. Please check your math syntax (use x**2 for x²).")
