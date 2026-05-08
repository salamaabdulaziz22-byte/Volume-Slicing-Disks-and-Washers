import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="Ultimate Volume Solver", layout="wide")
st.title("Calculus Volume Solver")

# Input field
raw_input = st.text_area("Paste textbook question here:", height=150, 
                         placeholder="e.g., y = 4 - x**2, y = 1, from x = 0 to x = sqrt(3) about y-axis")

if st.button("Generate Full Accurate Solution"):
    try:
        # 1. TEXT PRE-PROCESSING (Handling textbook shorthand)
        # Replaces 'vx' or 'v3' with 'sqrt' for the math engine
        clean_text = raw_input.lower().replace('vx', 'sqrt(x)').replace('v', 'sqrt').replace('^', '**')
        
        # 2. DATA EXTRACTION
        # Finds equations (y=... or x=...) and all numbers/sqrt limits
        eq_found = re.findall(r'[yx]\s*=\s*([^, \n]+)', clean_text)
        limit_values = re.findall(r"sqrt\(\d+\)|\d+\.?\d*", clean_text)
        
        x, y = sp.symbols('x y')
        is_y_axis = any(word in clean_text for word in ['y-axis', 'about y', 'around y'])
        integration_var = y if is_y_axis else x

        # 3. FUNCTION TRANSFORMATION
        # If rotating about y, we MUST have functions in terms of y (x = f(y))
        raw_exprs = [sp.sympify(e) for e in eq_found]
        processed_exprs = []
        
        for expr in raw_exprs:
            if is_y_axis and 'x' in str(expr):
                # Solve y = f(x) for x to get the required f(y)
                sol = sp.solve(sp.Eq(y, expr), x)
                processed_exprs.append(sol[-1]) # Use positive/outer branch
            else:
                processed_exprs.append(expr)

        f_expr = processed_exprs[0]
        g_expr = processed_exprs[1] if len(processed_exprs) > 1 else sp.sympify(0)

        # 4. LIMIT IDENTIFICATION
        # Safely convert extracted strings to symbolic numbers
        a_sym = sp.sympify(limit_values[0]) if len(limit_values) >= 1 else sp.Integer(0)
        b_sym = sp.sympify(limit_values[1]) if len(limit_values) >= 2 else sp.Integer(1)
        
        # 5. R vs r LOGIC (Washer vs Disk)
        # Compare functions at the midpoint to ensure R >= r
        mid =
