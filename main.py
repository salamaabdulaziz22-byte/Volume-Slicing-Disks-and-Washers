import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

# واجهة بالإنجليزية
st.set_page_config(page_title="Volume of Solids of Revolution", layout="wide")
st.title("🧮 Volume of Solids of Revolution (6.2)")

with st.sidebar:
    st.header("⚙️ Problem Input")
    f_in = st.text_input("Upper Function f(x):", "sqrt(x)")
    g_in = st.text_input("Lower Function g(x):", "x")
    a = st.number_input("Start of interval (a):", value=0.0)
    b = st.number_input("End of interval (b):", value=1.0)

if st.button("Calculate & Show Steps"):
    x = sp.symbols('x')
    try:
        f = sp.sympify(f_in)
        g = sp.sympify(g_in)
        is_washer = g != 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📝 Solution Steps:")
            method = "Washer Method" if is_washer else "Disk Method"
            st.info(f"Method: {method}")
            
            integrand = f**2 - g**2 if is_washer else f**2
            formula = sp.pi * sp.Integral(integrand, (x, a, b))
            st.write("**Step 1: Setup the Integral**")
            st.latex(sp.latex(formula))
            
            volume = sp.pi * sp.integrate(integrand, (x, a, b))
            st.write("**Step 2: Final Result**")
            st.success(f"V = {sp.latex(volume)} ≈ {float(volume.evalf()):.4f}")

        with col2:
            st.subheader("📊 Visualization:")
            x_p = np.linspace(float(a), float(b), 100)
            f_p = sp.lambdify(x, f, 'numpy')(x_p)
            g_p = sp.lambdify(x, g, 'numpy')(x_p) if is_washer else np.zeros_like(x_p)
            fig, ax = plt.subplots()
            ax.plot(x_p, f_p, label='f(x)', color='red')
            ax.plot(x_p, g_p, label='g(x)', color='blue')
            ax.fill_between(x_p, f_p, g_p, color='orange', alpha=0.3)
            ax.legend()
            st.pyplot(fig)
    except:
        st.error("Please check the function format.")
