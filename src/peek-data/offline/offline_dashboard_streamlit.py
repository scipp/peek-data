# streamlit run offline_dashboard_streamlit.py

import base64
import streamlit as st
import mpld3
from base_setup import sample, reference, binned, get_sample_plot
st.set_page_config(layout="wide")
fig = get_sample_plot()
st.markdown(
    """<style>
    button[title="View fullscreen"] {
        left: 0;
        height: 15px;
    }
    </styles>"
    """,
    unsafe_allow_html=True,
)

st.header("Offline Divergent data reduction for Amor")

## Buttons
if st.session_state.get('stop', False):
    st.session_state.processing = False
elif st.session_state.get('resume', True):
    st.session_state.processing = True

grid01_01, grid01_02, grid01_03, _ = st.columns([0.13, 0.13, 0.1, 1], gap="small")
with grid01_01:
    stop_button = st.button(label="Stop Refreshing", disabled=(not st.session_state.processing), key='stop')
with grid01_02:
    refresh_button = st.button(label="Resume Refreshing", disabled=st.session_state.processing, key='resume')
with grid01_03:
    if not st.session_state.processing:
        st.write('stop!')
    if st.session_state.processing:
        file = open("assets/processing.gif", 'rb')
        contents = file.read()
        data_url = base64.b64encode(contents).decode('utf-8')
        file.close()
        st.markdown(f'<img src="data:image/gif;base64,{data_url}" width=25px>', unsafe_allow_html = True)

## Dashboards
col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("Interactive Plot")
    st.plotly_chart(fig, height=450, scrolling=True)
    st.subheader("Reduction Result")
    st.image('assets/binned.png')
    st.components.v1.html(binned._repr_html_(), height=450, scrolling=True)
    st.subheader("Offline Data")
    st.image('assets/sample_raw_2d.png')
    st.components.v1.html(sample._repr_html_(), width=1000, height=450, scrolling=True)
    st.components.v1.html(reference._repr_html_(), width=1000, height=450, scrolling=True)

with col2:
    st.subheader("Workflow")
    st.image('assets/workflow_graph.png')
    st.subheader("Reference Calibration Result")
    st.image('assets/calibration_result.png')
    st.subheader("Normalization Result")
    st.image('assets/normalized_2d_scatter.png')
    st.image('assets/normalized_mean.png')