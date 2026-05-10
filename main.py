import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(page_title="Volume of Revolution Calc", layout="wide")

st.title("📐 Solids of Revolution: Disks & Washers")
st.write("Calculate volumes with step-by-step solutions and interactive 3D visualizations.")

# Sidebar for User Input
with st.sidebar:
    st.header("Input Parameters")
    method = st.selectbox("Select Method:", ["Disk Method", "Washer Method"])
    
    f_text = st.text_input("Outer Function f(x) (Upper):", "sqrt(x)")
    
    g_text = "0"
    if method == "Washer Method":
        g_text = st.text_input("Inner Function g(x) (Lower):", "x**2")
    
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
    
    # Define Radii
    R = f_expr - axis_val
    r = g_expr - axis_val
    
    # Define Integrand based on method
    if method == "Disk Method":
        integrand = sp.pi * (R**2)
        formula_latex = r"V = \pi \int_{a}^{b} [R(x)]^2 \, dx"
    else:
        integrand = sp.pi * (R**2 - r**2)
        formula_latex = r"V = \pi \int_{a}^{b} ([R(x)]^2 - [r(x)]^2) \, dx"

    # Calculate Integral
    volume_exact = sp.integrate(integrand, (x, a_val, b_val))
    volume_numeric = float(volume_exact.evalf())

    # --- Display Solution Steps ---
    st.header("📝 Step-by-Step Solution")
    step_col1, step_col2 = st.columns(2)
    
    with step_col1:
        st.markdown(f"**1. Formula used:**")
        st.latex(formula_latex)
        
        st.markdown(f"**2. Identify Radii:**")
        st.write(f"Outer Radius $R(x) = {sp.latex(R)}$")
        if method == "Washer Method":
            st.write(f"Inner Radius $r(x) = {sp.latex(r)}$")
            
    with step_col2:
        st.markdown("**3. Setup Integral:**")
        st.latex(f"V = \int_{{{a_val}}}^{{{b_val}}} {sp.latex(integrand)} \, dx")
        
        st.success(f"**Result:**")
        st.latex(f"V = {sp.latex(volume_exact)}")
        st.write(f"Numerical Value: **{volume_numeric:.4f}** cubic units")

    # --- 3.D Visualization ---
    st.header("🍦 3D Visualization")
    
    # Generate data for plotting
    x_range = np.linspace(float(a_val), float(b_val), 60)
    theta = np.linspace(0, 2 * np.pi, 60)
    X_grid, Theta_grid = np.meshgrid(x_range, theta)
    
    f_num = sp.lambdify(x, f_expr, 'numpy')
    g_num = sp.lambdify(x, g_expr, 'numpy')
    
    # Outer Surface
    R_vals = f_num(X_grid) - axis_val
    Y_outer = R_vals * np.cos(Theta_grid) + axis_val
    Z_outer = R_vals * np.sin(Theta_grid)
    
    fig = go.Figure()
    fig.add_trace(go.Surface(x=X_grid, y=Y_outer, z=Z_outer, 
                             colorscale='Viridis', opacity=0.7, 
                             showscale=False, name='Outer Surface'))
    
    # Inner Surface (for Washers)
    if method == "Washer Method":
        r_vals = g_num(X_grid) - axis_val
        Y_inner = r_vals * np.cos(Theta_grid) + axis_val
        Z_inner = r_vals * np.sin(Theta_grid)
        fig.add_trace(go.Surface(x=X_grid, y=Y_inner, z=Z_inner, 
                                 colorscale='Reds', opacity=0.4, 
                                 showscale=False, name='Inner Surface'))

    fig.update_layout(
        scene=dict(xaxis_title='x-axis', yaxis_title='y-axis', zaxis_title='z-axis'),
        margin=dict(l=0, r=0, b=0, t=0)
    )
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error in mathematical expression: {e}")
    st.info("Tip: Use '*' for multiplication and '**' for powers (e.g., x**2).")
