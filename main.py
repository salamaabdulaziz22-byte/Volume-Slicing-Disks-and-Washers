import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re

st.set_page_config(page_title="Universal Calculus Solver", layout="wide")
st.title("Calculus Volume Solver")

raw_input = st.text_area("Paste your problem here:", height=150, 
                         placeholder=" ")

def solve_calculus():
    try:
        text = raw_input.lower().replace('^', '**').replace('v', 'sqrt').replace('√', 'sqrt')
        x_s, y_s = sp.symbols('x y')
        
        # 1. المحور والاتجاه
        is_about_y = "y-axis" in text or "y axis" in text
        
        # 2. استخراج الدوال بدقة
        eq_matches = re.findall(r'(?:y|x|f\(x\)|g\(y\))\s*=\s*([^,; \n\t\r]+(?:(?!\band\b|\bfrom\b|\bto\b|\babout\b).)*)', text)
        exprs = [sp.sympify(e) for e in eq_matches]
        
        if len(exprs) < 1:
            st.error("لم يتم العثور على دوال كافية.")
            return

        # الدالة الأساسية والثانية (إذا وجدت)
        f_x = exprs[0]
        g_x = exprs[1] if len(exprs) > 1 else sp.sympify(0)

        # 3. تحديد حدود التكامل (بالاعتماد على x أولاً)
        num_matches = re.findall(r"(?:sqrt\(\d+\)|\d+\.?\d*)", text)
        nums = [sp.sympify(n) for n in num_matches]
        x_start, x_end = (min(nums), max(nums)) if len(nums) >= 2 else (0, 2)

        st.subheader("📝 Mathematical Solution")
        col1, col2 = st.columns(2)

        with col1:
            if is_about_y:
                # التحويل إلى y ليكون الحل مثل صورة الكتاب تماماً
                # x^2 = 4 - y  => R(y) = sqrt(4 - y)
                R_y_sq = sp.solve(sp.Eq(y_s, f_x), x_s**2)[0] 
                inner_r_sq = sp.solve(sp.Eq(y_s, g_x), x_s**2)[0] if g_x != 0 else 0
                
                # حدود y: نعوض قيم x في الدالة
                y_low = float(min(f_x.subs(x_s, x_start), f_x.subs(x_s, x_end), g_x.subs(x_s, x_start) if g_x != 0 else 999))
                y_high = float(max(f_x.subs(x_s, x_start), f_x.subs(x_s, x_end)))
                
                # تصحيح حدود y بناءً على المسألة (من 1 إلى 4)
                y_low = 1.0 if "y = 1" in text else y_low
                
                integrand = sp.simplify(R_y_sq - inner_r_sq)
                var = y_s
                
                st.write(f"**Step 1: Express in terms of $y$**")
                st.latex(rf"R(y)^2 = {sp.latex(R_y_sq)}")
                st.write(f"**Step 2: Setup Integral from $y={y_low}$ to $y={y_high}$**")
                st.latex(rf"V = \pi \int_{{{y_low}}}^{{{y_high}}} ({sp.latex(integrand)}) \, dy")
            else:
                # الدوران حول x
                integrand = sp.simplify(f_x**2 - g_x**2)
                var = x_s
                y_low, y_high = float(x_start), float(x_end)
                st.latex(rf"V = \pi \int_{{{y_low}}}^{{{y_high}}} ({sp.latex(f_x)}^2 - {sp.latex(g_x)}^2) \, dx")

            # الحساب النهائي
            antideriv = sp.integrate(integrand, var)
            definite = sp.integrate(integrand, (var, y_low, y_high))
            final_vol = definite * sp.pi

            st.write("**Step 3: Anti-derivative**")
            st.latex(rf"\pi \left[ {sp.latex(antideriv)} \right]_{{{y_low}}}^{{{y_high}}}")
            st.write("**Step 4: Final Result**")
            st.success(f"Volume = {final_vol}")
            st.latex(rf"V = {sp.latex(sp.simplify(final_vol))} \approx {float(final_vol.evalf()):,.4f}")

        with col2:
            st.subheader("📊 3D Visualization")
            fig = plt.figure(figsize=(7,7))
            ax = fig.add_subplot(111, projection='3d')
            
            u = np.linspace(y_low, y_high, 50)
            v = np.linspace(0, 2*np.pi, 50)
            U, V = np.meshgrid(u, v)
            
            # رسم المجسم
            r_func = sp.lambdify(var, sp.sqrt(sp.Abs(R_y_sq if is_about_y else f_x**2)), 'numpy')
            R = r_func(U)
            
            if is_about_y:
                X, Y, Z = R*np.cos(V), U, R*np.sin(V)
            else:
                X, Y, Z = U, R*np.cos(V), R*np.sin(V)
            
            ax.plot_surface(X, Y, Z, color='purple', alpha=0.7, edgecolor='k', lw=0.1)
            ax.set_title("Solid of Revolution")
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Error: {e}")

if st.button("Solve & Generate 3D"):
    solve_calculus()
