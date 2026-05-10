import streamlit as st
import numpy as np
import plotly.graph_objects as go
from sympy import symbols, integrate, pi, lambdify, sympify

# Page Config
st.set_page_config(page_title="Universal Volume Solver", page_icon="📐", layout="wide")

st.title("📐 Universal 3D Solid of Revolution Solver")
st.write("Calculate volume and visualize the 3D solid by revolving around the **X-axis** or **Y-axis**.")

# Sidebar for Inputs
st.sidebar.header("Input Parameters")
axis_choice = st.sidebar.selectbox("Axis of Revolution", ["x-axis", "y-axis"])
variable = 'x' if axis_choice == "x-axis" else 'y'

f_input = st.sidebar.text_input(f"Outer Function f({variable})", "sqrt(x)" if variable == 'x' else "y**2")
g_input = st.sidebar.text_input(f"Inner Function g({variable}) (0 for Disk)", "0")
a_val = st.sidebar.number_input(f"Lower Limit ({variable} = a)", value=0.0)
b_val = st.sidebar.number_input(f"Upper Limit ({variable} = b)", value=4.0)

if st.button("Solve & Generate 3D Solid"):
    try:
        v_sym = symbols(variable)
        f_expr = sympify(f_input)
        g_expr = sympify(g_input)

        # 1. Method Identification
        method = "Disk Method" if g_expr == 0 else "Washer Method"
        integrand = f_expr**2 - g_expr**2
        
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader(f"Method: {method}")

            # 2. Step-by-Step Breakdown
            st.markdown("### Step-by-Step Solution")
            
            formula = r"V = \pi \int_{a}^{b} [R(x)]^2 dx" if variable == 'x' else r"V = \pi \int_{c}^{d} [R(y)]^2 dy"
            if method == "Washer Method":
                formula = r"V = \pi \int_{a}^{b} (R^2 - r^2) dx" if variable == 'x' else r"V = \pi \int_{c}^{d} (R^2 - r^2) dy"

            st.write("**1. Formula:**")
            st.latex(formula)

            st.write("**2. Set up the Integral:**")
            st.latex(f"V = \pi \int_{{{a_val}}}^{{{b_val}}} ({integrand}) d{variable}")

            # Calculations
            antiderivative = integrate(integrand, v_sym)
            result_exact = integrate(integrand, (v_sym, a_val, b_val)) * pi
            result_decimal = float(result_exact.evalf())

            st.write("**3. Integration Result:**")
            st.latex(f"\pi \left[ {antiderivative} \\right]_{{{a_val}}}^{{{b_val}}}")

            st.success(f"**Final Volume:** {result_exact} ≈ {result_decimal:.4f} cubic units")

        with col2:
            st.subheader("3D Interactive Visualization")
            
            # 3. 3D Plotting Logic
            u_vals = np.linspace(float(a_val), float(b_val), 60)
            v_rotation = np.linspace(0, 2 * np.pi, 60)
            U, V = np.meshgrid(u_vals, v_rotation)
            
            f_num = lambdify(v_sym, f_expr, 'numpy')
            g_num = lambdify(v_sym, g_expr, 'numpy')

            # Coordinate transformation based on the chosen axis
            if variable == 'x':
                X = U
                Y = f_num(U) * np.cos(V)
                Z = f_num(U) * np.sin(V)
                X_in = U
                Y_in = g_num(U) * np.cos(V)
                Z_in = g_num(U) * np.sin(V)
            else:
                Y = U
                X = f_num(U) * np.cos(V)
                Z = f_num(U) * np.sin(V)
                Y_in = U
                X_in = g_num(U) * np.cos(V)
                Z_in = g_num(U) * np.sin(V)

            fig = go.Figure()
            
            # Outer Surface
            fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale='Reds', opacity=0.7, name="Outer Surface", showscale=False))
            
            # Inner Surface (only for Washer)
            if g_expr != 0:
                fig.add_trace(go.Surface(x=X_in, y=Y_in, z=Z_in, colorscale='Blues', opacity=0.8, name="Inner Surface", showscale=False))

            fig.update_layout(
                scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'),
                margin=dict(l=0, r=0, b=0, t=0)
            )
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}. Check your function syntax.")
