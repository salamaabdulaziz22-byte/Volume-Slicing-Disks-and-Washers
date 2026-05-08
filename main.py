import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

# إعداد الصفحة وتصميم الواجهة
st.set_page_config(page_title="Calculus Solver Pro", layout="wide")
st.title("Advanced Volume Analyzer")
st.write("Verified Step-by-Step Solver for Disks and Washers (Lesson 6-2)")

# منطقة المدخلات في الجانب
with st.sidebar:
    st.header("Problem Parameters")
    f_input = st.text_input("Upper Function f(x):", "sqrt(x)")
    g_input = st.text_input("Lower Function g(x):", "x**2")
    axis_val = st.text_input("Axis of Revolution (e.g., x=0 or y=2):", "x=0")

if st.button("Generate Solution"):
    try:
        # 1. تعريف الرموز والمعادلات
        x, y = sp.symbols('x y')
        f = sp.sympify(f_input)
        g = sp.sympify(g_input)
        
        # 2. إيجاد نقاط التقاطع (الحدود) تلقائياً
        intersections = sp.solve(f - g, x)
        real_pts = [p.evalf() for p in intersections if p.is_real]
        
        if not real_pts:
            st.error("No intersection found. Please check your equations.")
        else:
            a_limit, b_limit = min(real_pts), max(real_pts)
            
            # 3. تحديد نوع المحور (أفقي أم رأسي)
            axis_type = 'y' if 'x' in axis_val else 'x'
            axis_num = sp.sympify(axis_val.split('=')[1])
            
            # 4. حساب أنصاف الأقطار بناءً على اتجاه الدوران
            if axis_type == 'y':  # دوران حول محور رأسي (التكامل بالنسبة لـ y)
                # تحويل الدوال لتصبح بدلالة y
                f_inv = sp.solve(sp.Eq(y, f), x)[0]
                g_inv = sp.solve(sp.Eq(y, g), x)[0]
                
                # تحويل حدود التكامل لتناسب y
                y_a = float(f.subs(x, a_limit))
                y_b = float(f.subs(x, b_limit))
                limits = (min(y_a, y_b), max(y_a, y_b))
                
                R_radius = sp.Abs(f_inv - axis_num)
                r_radius = sp.Abs(g_inv - axis_num)
                var = y
            else:  # دوران حول محور أفقي (التكامل بالنسبة لـ x)
                R_radius = sp.Abs(f - axis_num)
                r_radius = sp.Abs(g - axis_num)
                var = x
                limits = (float(a_limit), float(b_limit))

            # 5. حساب التكامل النهائي
            integrand = sp.simplify(R_radius**2 - r_radius**2)
            volume_exact = sp.pi * sp.integrate(integrand, (var, limits[0], limits[1]))
            
            # 6. عرض النتائج بخطوات واضحة
            st.success("✅ Solution Successfully Generated")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📝 Methodology")
                st.write(f"**Integration Variable:** d{var}")
                st.write(f"**Interval:** [{limits[0]}, {limits[1]}]")
                st.write("**Washer Method Formula:**")
                st.latex(rf"V = \pi \int_{{{limits[0]}}}^{{{limits[1]}}} [({sp.latex(R_radius)})^2 - ({sp.latex(r_radius)})^2] \, d{var}")
                
                st.write("**Exact Value:**")
                st.latex(rf"V = {sp.latex(sp.simplify(volume_exact))}")
                st.info(f"Approximate Volume: {float(volume_exact.evalf()):.4f}")

            with col2:
                st.subheader("📊 2D Region Preview")
                u = np.linspace(limits[0], limits[1], 100)
                R_func = sp.lambdify(var, R_radius, 'numpy')
                r_func = sp.lambdify(var, r_radius, 'numpy')
                
                fig, ax = plt.subplots()
                ax.fill_between(u, R_func(u), r_func(u), color='orchid', alpha=0.4, label='Region')
                ax.set_title("Cross-section View")
                ax.legend()
                st.pyplot(fig)

    except Exception as e:
        st.error(f"Mathematical Error: {e}")
