import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import re

# =====================================================
# STEM Volume Solver
# Volume: Disks and Washers
# =====================================================

st.set_page_config(page_title="Volume Solver", layout="wide")

st.title("STEM Volume Solver")
st.subheader("Volume: Disks and Washers Method")

st.write("""
Enter a problem like:

• y = x^2 , y = 4 about x-axis  
• y = x^2 , y = 0 about x-axis  
• x = y^2 , x = 4 about y-axis
""")

# =====================================================
# USER INPUT
# =====================================================

problem = st.text_area(
    "Enter Problem:",
    height=120,
    placeholder="Example: y = x^2 , y = 4 about x-axis"
)

solve = st.button("Solve Step-by-Step")

# =====================================================
# MAIN PROGRAM
# =====================================================

if solve:

    try:

        # =====================================================
        # SYMBOLS
        # =====================================================

        x, y = sp.symbols('x y')

        text = problem.lower()

        # Clean input
        text = text.replace("^", "**")
        text = text.replace("√x", "sqrt(x)")

        # =====================================================
        # DETECT AXIS OF ROTATION
        # =====================================================

        axis = ""

        if "x-axis" in text or "about x" in text:
            axis = "x-axis"

        elif "y-axis" in text or "about y" in text:
            axis = "y-axis"

        else:
            st.error("Please specify axis of rotation.")
            st.stop()

        # =====================================================
        # EXTRACT EQUATIONS
        # =====================================================

        equations = re.findall(r'[yx]\s*=\s*[^,]+', text)

        if len(equations) < 2:
            st.error("Please enter two equations.")
            st.stop()

        eq1 = equations[0].strip()
        eq2 = equations[1].strip()

        # =====================================================
        # PARSE EQUATIONS
        # =====================================================

        def parse_equation(eq):

            left, right = eq.split("=")

            left = left.strip()
            right = right.strip()

            expr = sp.sympify(right)

            return left, expr

        var1, expr1 = parse_equation(eq1)
        var2, expr2 = parse_equation(eq2)

        # =====================================================
        # DETERMINE METHOD
        # =====================================================

        method = ""

        # Disk if one curve is axis
        if expr1 == 0 or expr2 == 0:
            method = "Disk Method"
        else:
            method = "Washer Method"

        # =====================================================
        # DISPLAY BASIC INFO
        # =====================================================

        st.header("Problem Analysis")

        st.success(f"Axis of Rotation: {axis}")
        st.success(f"Method: {method}")

        # =====================================================
        # CASE 1 : ROTATION ABOUT X-AXIS
        # =====================================================

        if axis == "x-axis":

            # Need y functions
            if var1 != 'y' or var2 != 'y':
                st.error("For x-axis rotation, equations must be in y = form.")
                st.stop()

            outer = sp.Max(expr1, expr2)
            inner = sp.Min(expr1, expr2)

            # Find intersection points
            intersections = sp.solve(sp.Eq(expr1, expr2), x)

            real_points = []

            for val in intersections:
                if val.is_real:
                    real_points.append(val)

            if len(real_points) < 2:

                if len(real_points) == 1:
                    a = 0
                    b = real_points[0]
                else:
                    st.error("Could not determine bounds.")
                    st.stop()

            else:
                a = min(real_points)
                b = max(real_points)

            # =====================================================
            # SHOW STEPS
            # =====================================================

            st.header("Step-by-Step Solution")

            st.subheader("Step 1: Determine Radius")

            st.latex(f"R(x) = {sp.latex(outer)}")
            st.latex(f"r(x) = {sp.latex(inner)}")

            st.subheader("Step 2: Volume Formula")

            if method == "Disk Method":

                formula = sp.pi * (outer**2)

                st.latex(
                    rf"V = \pi \int_{{{a}}}^{{{b}}} ({sp.latex(outer)})^2 \, dx"
                )

            else:

                formula = sp.pi * (outer**2 - inner**2)

                st.latex(
                    rf"V = \pi \int_{{{a}}}^{{{b}}}"
                    rf"\left(({sp.latex(outer)})^2 - ({sp.latex(inner)})^2\right)dx"
                )

            # =====================================================
            # INTEGRATION
            # =====================================================

            st.subheader("Step 3: Integrate")

            volume = sp.integrate(formula, (x, a, b))

            integral_expr = sp.integrate(formula, x)

            st.latex(
                rf"V = {sp.latex(volume)}"
            )

            # =====================================================
            # GRAPH
            # =====================================================

            st.header("Graph")

            x_vals = np.linspace(float(a)-1, float(b)+1, 400)

            f1 = sp.lambdify(x, expr1, 'numpy')
            f2 = sp.lambdify(x, expr2, 'numpy')

            y1_vals = f1(x_vals)
            y2_vals = f2(x_vals)

            fig, ax = plt.subplots(figsize=(8,5))

            ax.plot(x_vals, y1_vals, label=f"y = {expr1}")
            ax.plot(x_vals, y2_vals, label=f"y = {expr2}")

            ax.fill_between(
                x_vals,
                y1_vals,
                y2_vals,
                alpha=0.3
            )

            ax.axhline(0)

            ax.set_title(f"{method} around {axis}")

            ax.legend()

            st.pyplot(fig)

        # =====================================================
        # CASE 2 : ROTATION ABOUT Y-AXIS
        # =====================================================

        elif axis == "y-axis":

            # Need x functions
            if var1 != 'x' or var2 != 'x':
                st.error("For y-axis rotation, equations must be in x = form.")
                st.stop()

            outer = sp.Max(expr1, expr2)
            inner = sp.Min(expr1, expr2)

            # Find intersections
            intersections = sp.solve(sp.Eq(expr1, expr2), y)

            real_points = []

            for val in intersections:
                if val.is_real:
                    real_points.append(val)

            if len(real_points) < 2:

                if len(real_points) == 1:
                    a = 0
                    b = real_points[0]
                else:
                    st.error("Could not determine bounds.")
                    st.stop()

            else:
                a = min(real_points)
                b = max(real_points)

            # =====================================================
            # SHOW STEPS
            # =====================================================

            st.header("Step-by-Step Solution")

            st.subheader("Step 1: Determine Radius")

            st.latex(f"R(y) = {sp.latex(outer)}")
            st.latex(f"r(y) = {sp.latex(inner)}")

            st.subheader("Step 2: Volume Formula")

            if method == "Disk Method":

                formula = sp.pi * (outer**2)

                st.latex(
                    rf"V = \pi \int_{{{a}}}^{{{b}}} ({sp.latex(outer)})^2 \, dy"
                )

            else:

                formula = sp.pi * (outer**2 - inner**2)

                st.latex(
                    rf"V = \pi \int_{{{a}}}^{{{b}}}"
                    rf"\left(({sp.latex(outer)})^2 - ({sp.latex(inner)})^2\right)dy"
                )

            # =====================================================
            # INTEGRATION
            # =====================================================

            st.subheader("Step 3: Integrate")

            volume = sp.integrate(formula, (y, a, b))

            st.latex(
                rf"V = {sp.latex(volume)}"
            )

            # =====================================================
            # GRAPH
            # =====================================================

            st.header("Graph")

            y_vals = np.linspace(float(a)-1, float(b)+1, 400)

            f1 = sp.lambdify(y, expr1, 'numpy')
            f2 = sp.lambdify(y, expr2, 'numpy')

            x1_vals = f1(y_vals)
            x2_vals = f2(y_vals)

            fig, ax = plt.subplots(figsize=(8,5))

            ax.plot(x1_vals, y_vals, label=f"x = {expr1}")
            ax.plot(x2_vals, y_vals, label=f"x = {expr2}")

            ax.fill_betweenx(
                y_vals,
                x1_vals,
                x2_vals,
                alpha=0.3
            )

            ax.axvline(0)

            ax.set_title(f"{method} around {axis}")

            ax.legend()

            st.pyplot(fig)

        # =====================================================
        # FINAL ANSWER
        # =====================================================

        st.header("Final Answer")

        st.success(f"Volume = {sp.simplify(volume)}")

    except Exception as e:

        st.error("Error while solving the problem.")
        st.code(str(e))
