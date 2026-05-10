import streamlit as st
import numpy as np
import plotly.graph_objects as go
from sympy import symbols, integrate, pi, lambdify, sympify

# Page Layout
st.set_page_config(page_title="3D Volume Solver", layout="wide")
st.title("📐 3D Solid of Revolution Visualizer")

# Sidebar Inputs
st.sidebar.header("Parameters")
axis_choice = st.sidebar.selectbox("Rotate around:", ["x-axis", "y-axis"])
var_name = 'x' if axis_choice == "x-axis" else 'y'

f_in = st.sidebar.text_input(f"Outer Function f({var_name})", "sqrt(x)" if var_name == 'x' else "y**2")
g_in = st.sidebar.text_input(f"Inner Function g({var_name}) (0 for Disk)", "0")
a = st.sidebar.number_input("Start", value=0.0)
b = st.sidebar.number_input("End", value=2.0)

if st.button("Generate 3D Solid"):
    v_sym = symbols(var_name)
    f_expr = sympify(f_in)
    g_expr = sympify(g_in)
    
    # 1. Math Solution
    integrand = f_expr**2 - g_expr**2
    volume_exact = integrate(integrand, (v_sym, a, b)) * pi
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Solution Steps")
        st.write(f"**Method:** {'Disk' if g_expr == 0 else 'Washer'}")
        st.latex(f"V = \pi \int_{{{a}}}^{{{b}}} ({integrand}) d{var_name}")
        st.success(f"Volume ≈ {float(volume_exact.evalf()):.4f}")

    with col2:
        # 2. 3D Visualization Logic
        st.subheader("3D Interactive Model")
        
        # Create points for rotation
        u = np.linspace(float(a), float(b), 50)
        v = np.linspace(0, 2 * np.pi, 50)
        U, V = np.meshgrid(u, v)
        
        f_num = lambdify(v_sym, f_expr, 'numpy')
        g_num = lambdify(v_sym, g_expr, 'numpy')
        
        # Generate coordinates for Outer Surface
        if axis_choice == "x-axis":
            X = U
            Y = f_num(U) * np.cos(V)
            Z = f_num(U) * np.sin(V)
            # Inner Surface
            Y_in = g_num(U) * np.cos(V)
            Z_in = g_num(U) * np.sin(V)
        else:
            Y = U
            X = f_num(U) * np.cos(V)
            Z = f_num(U) * np.sin(V)
            # Inner Surface
            X_in = g_num(U) * np.cos(V)
            Z_in = g_num(U) * np.sin(V)

        fig = go.Figure()
        # Add Outer Surface
        fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale='Reds', opacity=0.7, showscale=False, name="Outer"))
        # Add Inner Surface if Washer
        if g_expr != 0:
            fig.add_trace(go.Surface(x=X_in, y=Y_in, z=Z_in, colorscale='Blues', opacity=0.8, showscale=False, name="Inner"))

        fig.update_layout(scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'))
        st.plotly_chart(fig, use_container_width=True)
