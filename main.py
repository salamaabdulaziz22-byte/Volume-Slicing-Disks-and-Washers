import streamlit as st
import numpy as np
import plotly.graph_objects as go
from sympy import symbols, integrate, pi, lambdify, sympify

# Website Layout
st.set_page_config(page_title="3D Calculus Visualizer", layout="wide")
st.title("📐 3D Solid of Revolution Interactive Solver")

# Sidebar
st.sidebar.header("Input Settings")
axis_choice = st.sidebar.selectbox("Rotation Axis", ["x-axis", "y-axis"])
variable = 'x' if axis_choice == "x-axis" else 'y'

f_input = st.sidebar.text_input(f"Outer Function f({variable})", "x")
g_input = st.sidebar.text_input(f"Inner Function g({variable}) (0 for Disk)", "0")
start = st.sidebar.number_input("Start Point", value=0.0)
end = st.sidebar.number_input("End Point", value=2.0)

if st.button("Calculate & Visualize 3D"):
    v_sym = symbols(variable)
    f_expr = sympify(f_input)
    g_expr = sympify(g_input)
    
    # 1. Math Solution
    integrand = f_expr**2 - g_expr**2
    volume_exact = integrate(integrand, (v_sym, start, end)) * pi
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Calculation Details")
        method = "Disk Method" if g_expr == 0 else "Washer Method"
        st.info(f"Method: {method}")
        st.latex(f"V = \pi \int_{{{start}}}^{{{end}}} ({integrand}) d{variable}")
        st.success(f"Final Volume ≈ {float(volume_exact.evalf()):.4f}")

    with col2:
        st.subheader("3D Solid Model")
        
        # 3. Generating the 3D Geometry
        # 'u' is the position along the axis, 'v' is the rotation angle
        u = np.linspace(float(start), float(end), 60)
        v = np.linspace(0, 2 * np.pi, 60)
        U, V = np.meshgrid(u, v)
        
        f_num = lambdify(v_sym, f_expr, 'numpy')
        g_num = lambdify(v_sym, g_expr, 'numpy')
        
        # Mapping 2D functions to 3D Space
        if axis_choice == "x-axis":
            # Outer Surface
            X, Y, Z = U, f_num(U) * np.cos(V), f_num(U) * np.sin(V)
            # Inner Surface (for Washers)
            X_in, Y_in, Z_in = U, g_num(U) * np.cos(V), g_num(U) * np.sin(V)
        else:
            # Outer Surface
            Y, X, Z = U, f_num(U) * np.cos(V), f_num(U) * np.sin(V)
            # Inner Surface
            Y_in, X_in, Z_in = U, g_num(U) * np.cos(V), g_num(U) * np.sin(V)

        fig = go.Figure()

        # Add the Outer Surface (Red/Orange)
        fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale='Oranges', opacity=0.8, name="Outer Surface", showscale=False))
        
        # Add the Inner Surface (Blue) if it's a Washer
        if g_expr != 0:
            fig.add_trace(go.Surface(x=X_in, y=Y_in, z=Z_in, colorscale='Blues', opacity=0.9, name="Inner Surface", showscale=False))

        fig.update_layout(
            scene=dict(
                xaxis_title='X Axis',
                yaxis_title='Y Axis',
                zaxis_title='Z Axis',
                aspectmode='data'
            ),
            margin=dict(l=0, r=0, b=0, t=0)
        )
        st.plotly_chart(fig, use_container_width=True)
