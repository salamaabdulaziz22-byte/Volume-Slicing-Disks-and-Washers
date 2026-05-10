import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(page_title="Volume Visualizer", layout="wide")

st.title("📐 Solids of Revolution: Disks & Washers")
st.write("Calculate volumes with step-by-step solutions and 3D graphs.")

# Sidebar for User Input
with st.sidebar:
    st.header("Input Parameters")
    method = st.selectbox("Select Method:", ["Disk Method", "Washer Method"])
    
    f_text = st.text_input("Outer Function f(x):", "sqrt(x)")
    g_text = "0"
    if method == "Washer Method":
        g_text = st.text_input("Inner Function g(x):", "x**2")
    
    axis_val = st.number_input("Axis of Rotation (y = c):", value=0.0)
    
    col_a, col_b = st.columns(2)
    with col_a:
        a_val = st.number_input("Start (a):", value=0.0)
    with col_b:
        b_val = st.number_input("End (b):", value=1.0)

# Symbolic Math Processing
x = sp.symbols('x')
try:
    f_expr = sp.sympify(f_text)
    g_expr = sp.sympify(g_text)
    
    R = f_expr - axis_val
    r = g_expr - axis_val
    
    if method == "Disk Method":
        integrand = sp.pi * (R**2)
        formula_latex = r"V = \pi \int_{a}^{b} [R(x)]^2 \, dx"
    else:
        integrand = sp.pi * (R**2 - r**2)
        formula_latex = r"V = \pi \int_{a}^{b} ([R(x)]^2 - [r(x)]^2) \, dx"

    volume_exact = sp.integrate(integrand, (x, a_val, b_val))
    volume_numeric = float(volume_exact.evalf())

    # --- Display Solution ---
    st.header("📝 Step-by-Step Solution")
    col1, col2 = st.columns(2)
    with col1:
        st.latex(formula_latex)
        st.write(f"Outer Radius $R(x) = {sp.latex(R)}$")
        if method == "Washer Method":
            st.write(f"Inner Radius $r(x) = {sp.latex(r)}$")
    with col2:
        st.success("**Final Result:**")
        st.latex(f"V = {sp.latex(volume_exact)}")
        st.write(f"Numerical: {volume_numeric:.4f}")

    # --- 3D Visualization (The Fixed Part) ---
    st.header("🍦 3D Visualization")
    
    x_range = np.linspace(float(a_val), float(b_val), 60)
    theta = np.linspace(0, 2 * np.pi, 60)
    X_grid, Theta_grid = np.meshgrid(x_range, theta)
    
    # FIX: Added modules argument to handle 'pi' correctly
    f_num = sp.lambdify(x, f_expr, modules=['numpy', {'pi': np.pi}])
    g_num = sp.lambdify(x, g_expr, modules=['numpy', {'pi': np.pi}])
    
    R_vals = f_num(X_grid) - axis_val
    Y_outer = R_vals * np.cos(Theta_grid) + axis_val
    Z_outer = R_vals * np.sin(Theta_grid)
    
    fig = go.Figure()
    fig.add_trace(go.Surface(x=X_grid, y=Y_outer, z=Z_outer, colorscale='Viridis', opacity=0.7, showscale=False))
    
    if method == "Washer Method":
        r_vals = g_num(X_grid) - axis_val
        Y_inner = r_vals * np.cos(Theta_grid) + axis_val
        Z_inner = r_vals * np.sin(Theta_grid)
        fig.add_trace(go.Surface(x=X_grid, y=Y_inner, z=Z_inner, colorscale='Reds', opacity=0.4, showscale=False))

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
