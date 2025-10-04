import streamlit as st
from step_solver import StepByStepper

st.title("🧮 Step-by-Step Solution Test")

# Test input
test_expr = st.text_input("Enter math expression:", value="2+3*4")

if st.button("Generate Steps"):
    solver = StepByStepper()
    steps = solver.solve_step_by_step(test_expr)
    
    st.markdown("---")
    with st.expander("📝 **Step-by-Step Solution**", expanded=True):
        for step in steps:
            st.write(step)
    
    st.success("✅ Step-by-step solution generated successfully!")