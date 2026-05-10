import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, integrate, pi, lambdify, sympify
import openai

# إعداد مفتاح OpenAI
# openai.api_key = "ضع_مفتاحك_هنا"

# إعدادات واجهة المستخدم
st.set_page_config(page_title="Math Solver: Disks & Washers", layout="wide")
st.title("📐 Automated Calculus Volume Solver")
st.write("Enter your English word problem, and I will identify the method, solve it, and draw the solid.")

# منطقة إدخال السؤال الكلامي
user_query = st.text_area("Enter your word problem in English:", 
                          placeholder="e.g., Find the volume of the region bounded by y=sqrt(x) and y=x rotated about the x-axis from x=0 to x=1")

# دالة ذكاء اصطناعي لاستخراج المعطيات من النص
def extract_math_params(text):
    # ملاحظة: في النسخة التجريبية، سنقوم بمحاكاة رد الذكاء الاصطناعي
    # ليعمل الكود، يجب تفعيل الربط مع OpenAI API
    try:
        # هذا "البرومبت" يوجه الذكاء الاصطناعي لاستخراج البيانات فقط
        prompt = f"Analyze: {text}. Extract f(x), g(x), lower_limit, upper_limit. Return ONLY as python dict."
        # رد افتراضي للمثال المذكور
        return {"f": "sqrt(x)", "g": "x", "a": 0, "b": 1}
    except:
        return None

if st.button("Solve My Problem"):
    if user_query:
        # 1. تحليل السؤال (Extraction)
        params = extract_math_params(user_query)
        
        if params:
            f_text = params['f']
            g_text = params['g']
            a_val = params['a']
            b_val = params['b']

            x = symbols('x')
            f_expr = sympify(f_text)
            g_expr = sympify(g_text)

            # 2. تحديد الطريقة (Method Identification)
            method = "Washer Method" if g_expr != 0 else "Disk Method"
            
            col1, col2 = st.columns(2)

            with col1:
                st.subheader(f"Step-by-Step Solution ({method})")
                
                # إعداد التكامل
                if method == "Disk Method":
                    formula = r"V = \pi \int_{a}^{b} [f(x)]^2 dx"
                    integrand = f_expr**2
                else:
                    formula = r"V = \pi \int_{a}^{b} ([R(x)]^2 - [r(x)]^2) dx"
                    integrand = f_expr**2 - g_expr**2

                st.write("**1. The Formula:**")
                st.latex(formula)

                st.write("**2. Setup Integral:**")
                st.latex(f"V = \pi \int_{{{a_val}}}^{{{b_val}}} ({integrand}) dx")

                # الحساب
                antiderivative = integrate(integrand, x)
                result = integrate(integrand, (x, a_val, b_val)) * pi
                
                st.write("**3. Antiderivative:**")
                st.latex(f"\pi \left[ {antiderivative} \\right]_{{{a_val}}}^{{{b_val}}}")

                st.success(f"Final Volume: {result} \approx {float(result.evalf()):.4f} \text{{ units}}^3")

            with col2:
                st.subheader("Visual Representation")
                # الرسم البياني
                x_vals = np.linspace(float(a_val), float(b_val), 100)
                f_num = lambdify(x, f_expr, 'numpy')
                g_num = lambdify(x, g_expr, 'numpy')

                fig, ax = plt.subplots()
                ax.plot(x_vals, f_num(x_vals), 'r', label=f'R(x)={f_text}')
                if method == "Washer Method":
                    ax.plot(x_vals, g_num(x_vals), 'b', label=f'r(x)={g_text}')
                
                ax.fill_between(x_vals, f_num(x_vals), g_num(x_vals), color='gray', alpha=0.3)
                ax.set_title("2D Area before rotation")
                ax.legend()
                st.pyplot(fig)
                
                st.info(f"The logic detected a {'gap' if method == 'Washer' else 'solid contact'} with the axis, hence using {method}.")
    else:
        st.warning
