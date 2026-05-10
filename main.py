import streamlit as st
import google.generativeai as genai
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import json
import re

# --- 1. CONFIGURATION & API SETUP ---
# Securely configure your Gemini API Key
# Get a free key at: https://aistudio.google.com/
GOOGLE_API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=GOOGLE_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

# Page UI Configuration
st.set_page_config(page_title="AI Calculus Volume Solver", layout="wide")

# Custom CSS for a professional "Academic" look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .stTextArea>div>div>textarea { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Smart Calculus Volume Solver")
st.markdown("---")

def extract_parameters(question_text):
    """Uses Generative AI to parse any natural language math problem."""
    prompt = f"""
    Act as a calculus expert. Extract the parameters for a 'volume of a solid of revolution' problem.
    Input Text: "{question_text}"
    
    Instructions:
    1. Identify the Outer Function f(x) or f(y).
    2. Identify the Inner Function g(x) or g(y) (return '0' if it is a Disk problem).
    3. Identify the Lower Bound 'a' and Upper Bound 'b'.
    4. Determine the rotation axis ('x' or 'y').
    5. Determine the method ('Disk' or 'Washer').
    
    Return ONLY a valid JSON object:
    {{
        "f": "python_expression",
        "g": "python_expression",
        "a": number,
        "b": number,
        "axis": "x_or_y",
        "method": "Disk_or_Washer"
    }}
    Use Python math syntax (e.g., x**2, sqrt(x), exp(x)).
    """
    response = ai_model.generate_content(prompt)
    # Extract JSON using regex to avoid extra text from AI
    json_str = re.search(r'\{.*\}', response.text, re.DOTALL).group()
    return json.loads(json_str)

# --- 2. USER INTERFACE ---
st.sidebar.header("Instructions")
st.sidebar.write("""
1. Paste your full math question in the text area.
2. The AI will automatically detect functions, bounds, and the rotation axis.
3. Review the steps and the 2D visual representation.
""")

raw_input = st.text_area("Paste your calculus problem here:", height=150, 
                         placeholder="e.g., Find the volume of the region bounded by y=x and y=x^2 rotated about the x-axis from x=0 to x=1")

if st.button("Analyze & Solve Problem"):
    if not raw_input.strip():
        st.warning("Please provide a question to proceed.")
    else:
        try:
            with st.spinner("AI is interpreting the problem and calculating..."):
                # AI Extraction
                data = extract_parameters(raw_input)
                
                f_str, g_str = data['f'], data['g']
                a, b = float(data['a']), float(data['b'])
                axis = data['axis']
                
                # Math Engine Setup
                var = sp.symbols('x') if axis == 'x' else sp.symbols('y')
                f_sym = sp.sympify(f_str)
                g_sym = sp.sympify(g_str)

                # Calculus Calculations
                # Formula: V = π ∫ [f(var)^2 - g(var)^2] d(var)
                integrand = sp.pi * (f_sym**2 - g_sym**2)
                antideriv = sp.integrate(integrand, var)
                final_volume = sp.integrate(integrand, (var, a, b))

            # --- 3. OUTPUT RENDERING ---
            st.divider()
            col1, col2 = st.columns([1, 1])

            with col1:
                st.header(f"Method: {data['method']} Method")
                st.subheader("Step-by-Step Solution")
                
                # 1. Setup
                st.write("**1. Set up the Definite Integral:**")
                st.latex(rf"V = \pi \int_{{{a}}}^{{{b}}} \left( {sp.latex(f_sym**2 - g_sym**2)} \right) \, d{axis}")
                
                # 2. Antiderivative
                st.write("**2. Find the Antiderivative:**")
                st.latex(rf"V = \pi \left[ {sp.latex(antideriv/sp.pi)} \right]_{{{a}}}^{{{b}}}")
                
                # 3. Final Answer
                st.write("**3. Evaluate and Simplify:**")
                st.success(f"Exact Volume: {final_volume} cubic units")
                st.metric("Decimal Approximation", f"{float(final_volume.evalf()):.4f}")

            with col2:
                st.subheader("2D Region Visualization")
                # Plotting logic
                t_vals = np.linspace(a, b, 100)
                f_num = sp.lambdify(var, f_sym, 'numpy')(t_vals)
                g_num = sp.lambdify(var, g_sym, 'numpy')(t_vals) if g_str != "0" else np.zeros_like(t_vals)

                fig, ax = plt.subplots()
                ax.plot(t_vals, f_num, label=f'f({axis})', color='#007bff', linewidth=2)
                if g_str != "0":
                    ax.plot(t_vals, g_num, label=f'g({axis})', color='#dc3545', linewidth=2)
                
                ax.fill_between(t_vals, f_num, g_num, color='#17a2b8', alpha=0.3, label='Area to Rotate')
                ax.set_title(f"Region bounded on [{a}, {b}]")
                ax.set_xlabel(axis)
                ax.set_ylabel('Value')
                ax.legend()
                ax.grid(True, linestyle='--', alpha=0.5)
                st.pyplot(fig)

        except Exception as e:
            st.error(f"Analysis Error: {e}. Please ensure the question text is clear.")
