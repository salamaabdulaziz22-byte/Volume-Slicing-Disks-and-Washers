import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go

# 1. Page Config
st.set_page_config(page_title="Volume Visualizer", layout="wide")

st.title("📐 Solids of Revolution: Disks & Washers")
st.write("Professional math solver for Volume by Slicing.")

# 2. Sidebar
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

# 3. Math Engine
x = sp.symbols('x')
try:
    f_expr = sp.sympify(f_text)
    g_expr = sp.sympify(g_text)
    
    R = f_expr - axis_val
    r = g_expr - axis_val
    
    if method == "Disk Method":
        integrand = sp.pi * (R**2)
    else:
        integrand = sp.pi * (R**2 - r**2)

    volume_exact = sp.integrate(integrand, (x, a_val, b_val))
    volume_numeric = float(volume_exact.evalf())

    # Step-by-step UI
    st.header("📝 Solution Steps")
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Outer Radius R(x):** ${sp.latex(R)}$")
        if method == "Washer Method":
            st.write(f"**Inner Radius r(x):** ${sp.latex(r)}$")
        st.latex(f"V = \pi \int_{{{a_val}}}^{{{b_val}}} ({sp.latex(R**2 if method=='Disk' else R**2-r**2)}) \, dx")
    with c2:
        st.success(f"**Volume:** {volume_numeric:.4f}")
        st.latex(f"V = {sp.latex(volume_exact)}")

    # 4. 3D Plotting Engine (FIXED)
    st.header("🍦 3D Visualization")
    
    x_range = np.linspace(float(a_val), float(b_val), 50)
    theta = np.linspace(0, 2 * np.pi, 50)
    X_grid, Theta_grid = np.meshgrid(x_range, theta)
    
    # Correctly lambdify with numpy and handle errors
    f_num = sp.lambdify(x, f_expr, modules=['numpy', {'pi': np.pi}])
    g_num = sp.lambdify(x, g_expr, modules=['numpy', {'pi': np.pi}])
    
    def generate_surface(func_num, axis):
        r_vals = func_num(X_grid) - axis
        # Clean data: Replace non-finite numbers (NaN/Inf) with 0 to prevent crashes
        r_vals = np.nan_to_num(r_vals.astype(float)) 
        Y = r_vals * np.cos(Theta_grid) + axis
        Z = r_vals * np.sin(Theta_grid)
        return Y, Z

    fig = go.Figure()

    # Outer surface
    Y_out, Z_out = generate_surface(f_num, axis_val)
    fig.add_trace(go.Surface(x=X_grid, y=Y_out, z=Z_out, colorscale='Viridis', opacity=0.7, showscale=False))
    
    # Inner surface
    if method == "Washer Method":
        Y_in, Z_in = generate_surface(g_num, axis_val)
        fig.add_trace(go.Surface(x=X_grid, y=Y_in, z=Z_in, colorscale='Reds', opacity=0.4, showscale=False))

    fig.update_layout(scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'))
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Computation Error: {e}")
