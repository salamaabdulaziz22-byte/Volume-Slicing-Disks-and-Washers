import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

st.set_page_config(page_title="Step-by-Step Solver", layout="wide")
st.title("💡 Professional Volume Solver (3D & Steps)")

question = st.text_area("Paste question:", "y = 4 - x**2, y = 1, x = 0 to sqrt(3) about y-axis")

if st.button("Generate Full Solution"):
    try:
        # 1. إعداد الرموز
        y = sp.Symbol('y')
        # السؤال يتطلب التكامل بالنسبة لـ y (الدوران حول y-axis)
        # من البوربوينت: R(y) = sqrt(4-y), r(y) = 0 (disk method)
        # الحدود من y=1 إلى y=4
        
        R_y = sp.sqrt(4 - y)
        a, b = 1, 4
        
        st.subheader("📝 Step-by-Step Integration")
        
        # الخطوة 1: كتابة القانون
        st.write("**1. Setup the Integral:**")
        st.latex(rf"V = \pi \int_{{{a}}}^{{{b}}} [R(y)]^2 \, dy")
        
        # الخطوة 2: التعويض وتبسيط الدالة
        integrand = R_y**2
        st.write("**2. Substitute and Simplify:**")
        st.latex(rf"V = \pi \int_{{{a}}}^{{{b}}} (\sqrt{{4-y}})^2 \, dy = \pi \int_{{{a}}}^{{{b}}} (4-y) \, dy")
        
        # الخطوة 3: إيجاد المشتق العكسي (Antiderivative)
        antideriv = sp.integrate(integrand, y)
        st.write("**3. Find the Antiderivative:**")
        st.latex(rf"V = \pi \left[ {sp.latex(antideriv)} \right]_{{{a}}}^{{{b}}}")
        
        # الخطوة 4: التعويض بالحدود والناتج النهائي
        result = sp.pi * (antideriv.subs(y, b) - antideriv.subs(y, a))
        st.write("**4. Evaluate the Limits:**")
        st.latex(rf"V = \pi [ (4(4) - \frac{{4^2}}{{2}}) - (4(1) - \frac{{1^2}}{{2}}) ] = {sp.latex(result)}")
        st.info(f"Final Volume ≈ {float(result.evalf()):.4f}")

        # --- رسم المجسم ثلاثي الأبعاد 3D ---
        st.subheader("📦 3D Visualization")
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')
        
        # توليد بيانات الرسم
        y_vals = np.linspace(a, b, 50)
        theta = np.linspace(0, 2*np.pi, 50)
        Y, THETA = np.meshgrid(y_vals, theta)
        
        # نصف القطر R = sqrt(4-y)
        R = np.sqrt(4 - Y)
        X = R * np.cos(THETA)
        Z = R * np.sin(THETA)
        
        ax.plot_surface(X, Y, Z, color='magenta', alpha=0.6, edgecolor='k')
        ax.set_title("3D Solid of Revolution")
        st.pyplot(fig)
        
    except Exception as e:
        st.error(f"Error: {e}")
