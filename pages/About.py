import streamlit as st

st.set_page_config(
    layout="centered",
)
st.title("About")
st.write(
    """
    This is a Streamlit app for the Chart Question Answering Tool.
    """
)
st.markdown("Made with 🔥 by: **Bijesh Shreshta, Andrew Kerekon, and Aviv Nur**")
# profile pics
with st.sidebar:
    st.image("img/bijesh.png", width=80)
    st.markdown("Bijesh Shrestha")
    st.markdown("[GitHub](https://github.com/BijeshShrestha)")
    st.image("img/andrew.png", width=80)
    st.markdown("Andrew Kerekon")
    st.markdown("[GitHub](https://github.com/akerekon)")
    st.image("img/aviv.png", width=80)
    st.markdown("Aviv Nur")
    st.markdown("[GitHub](https://github.com/avivnur)")
st.header("How it works")
st.image("img/draft_pipeline.png", use_column_width=True)

st.header("How to use")
st.write(
    """
    1. Upload a PDF file with a chart.
    2. Ask a question about the chart.
    3. The AI will answer your question and generate a chart description.
    """
)

st.header("⚠️ Limitations")
with st.expander("Click here to see the limitations of the Chart Question Answering Tool", expanded=False):
    st.write('''
        1️⃣ The tool may not be able to answer all questions about the chart
             
        2️⃣ Hallucination: The tool may generate incorrect or misleading information
             
        3️⃣ The tool may not be able to answer questions about charts that are not in the PDF file
    '''
    )