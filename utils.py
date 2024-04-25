import streamlit as st
import openai
import os
import subprocess
import matplotlib.pyplot as plt
import datetime
import base64

# Import classes for data indexing and storage
from llama_index.core import SimpleDirectoryReader
from llama_index.core.tools import FunctionTool


#  Retrieve API keys from environment variables.
openai.api_key = st.secrets.openai_key

def create_bar_chart(data, title="Bar Chart", x_label="X-axis", y_label="Y-axis", color="skyblue"):
    """
    Generates and saves a bar chart based on the provided data. The data can be a dictionary,
    a list of tuples, or a simple list of values.

    Parameters:
    - data (dict, list of tuples, or list of values): The data to plot.
      - If a dictionary, expects {x_label: y_value}.
      - If a list of tuples, expects [(x_label, y_value), ...].
      - If a list of values, each value is plotted with a default x_label.
    - title (str): The title of the chart.
    - x_label (str): The label for the x-axis.
    - y_label (str): The label for the y-axis.
    - color (str): The color of the bars in the chart.
    """
    # Handle a simple list of values by assigning default x_labels
    if isinstance(data, list) and all(isinstance(item, (int, float)) for item in data):
        data = {f"Item {i+1}": val for i, val in enumerate(data)}
    # Handle a list of tuples
    elif isinstance(data, list) and all(isinstance(item, tuple) for item in data):
        data = {item[0]: item[1] for item in data}
    elif not isinstance(data, dict):
        raise ValueError("Data must be a dictionary, a list of tuples, or a list of numeric values.")

    fig, ax = plt.subplots()
    ax.bar(data.keys(), data.values(), color=color)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the figure
    directory = "temp_img"
    if not os.path.exists(directory):
        os.makedirs(directory)
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{directory}/{title.replace(' ', '_')}_{current_time}.png"
    plt.savefig(filename)
    plt.close(fig)
    print(f"Saved chart as {filename}")

def create_line_chart(data, title="Line Chart", x_label="X-axis", y_label="Y-axis", color="skyblue"):
    """
    Generates and saves a line chart based on the provided data. The data can be a dictionary,
    a list of tuples, or a simple list of values.

    Parameters:
    - data (dict, list of tuples, or list of values): The data to plot.
      - If a dictionary, expects {x_label: y_value}.
      - If a list of tuples, expects [(x_label, y_value), ...].
      - If a list of values, each value is plotted with a default x_label.
    - title (str): The title of the chart.
    - x_label (str): The label for the x-axis.
    - y_label (str): The label for the y-axis.
    - color (str): The color of the line in the chart.
    """
    # Handle a simple list of values by assigning default x_labels
    if isinstance(data, list) and all(isinstance(item, (int, float)) for item in data):
        data = {f"Item {i+1}": val for i, val in enumerate(data)}
    # Handle a list of tuples
    elif isinstance(data, list) and all(isinstance(item, tuple) for item in data):
        data = {item[0]: item[1] for item in data}
    elif not isinstance(data, dict):
        raise ValueError("Data must be a dictionary, a list of tuples, or a list of numeric values.")

    fig, ax = plt.subplots()
    
    ax.plot(list(data.keys()), list(data.values()), color=color, marker='o')  # Added a marker for better visibility
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the figure
    directory = "temp_img"
    if not os.path.exists(directory):
        os.makedirs(directory)
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{directory}/{title.replace(' ', '_')}_{current_time}.png"
    plt.savefig(filename)
    plt.close(fig)
    print(f"Saved chart as {filename}")

# Define the bar chart creation tool
bar_chart_tool = FunctionTool.from_defaults(
    fn=create_bar_chart,  
    name="bar_chart_creator",
    description="Generates a dynamic bar chart based on provided data and parameters. Do not hallucinate or make up any information."
)

# Define the bar chart creation tool
line_chart_tool = FunctionTool.from_defaults(
    fn=create_line_chart,  
    name="line_chart_creator",
    description="Generates a dynamic line chart based on provided data and parameters. Do not hallucinate or make up any information."
)

def generate_chart_data_from_pdf(pdf_file):
    print("Running inkscape to generate SVG...")

    output_svg_name = pdf_file + ".svg"
    completed = subprocess.run(["inkscape", "--export-filename=" + output_svg_name, pdf_file])
    print(completed.stdout)
    print(completed.stderr)

    print("SVG generated!")

    return generate_chart_data_from_svg(output_svg_name)

def generate_chart_data_from_svg(svg_file_name):
    svg_file = open(svg_file_name)

    line_buffer = ""
    for line in svg_file:
        line_buffer = line_buffer + line
    prompt = '''Generate a .txt file that describes the chart within the following SVG file. Label every data point. For example: 
            Title of the chart is "Apple Stock Price Over the Last 10 Years".
            • Chart type is a bar chart.
            • Chart created using matplotlib.
            • X-axis is labeled "Year".
            • Y-axis is labeled "Stock Price ($)".
            • Data points are colored in skyblue.
            • The chart measures stock price rates from 2015 to 2024.
            • Year 2015 was $27.06.
            • Year 2016 was $24.06.
            • Year 2017 was $35.29.'''
    # Use the OpenAI API for Query and Response
    openai.api_key = st.secrets.openai_key
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": line_buffer}
        ]
    )

    # Extracting text response from the OpenAI response object
    response = response.choices[0].message.content

    print(response)

    with open(svg_file_name + "chart_description.txt", "w") as f:
        f.write(response)
        print(f"{response}")
        return svg_file_name + "chart_description.txt"
    

def pdf_processing(file_path):
    print("load text and chart data from pdf")
    text_docs = SimpleDirectoryReader(
        input_files=[file_path],
        recursive=True,
    ).load_data()
    print("text_docs")
    output_text = generate_chart_data_from_pdf(file_path)
    print("output_text")
    chart_docs = SimpleDirectoryReader(
        input_files=[output_text]
    ).load_data()
    print("chart_docs")
    return text_docs, chart_docs

def process_inquiry_and_show_latest_image(question, agent):
    """
    Processes a given inquiry using an agent's chat function that might generate an image,
    prints the response, and displays the path to the newest image created in the 'temp_img'
    directory if available, along with the image itself.

    Parameters:
    - question (str): The inquiry that might lead to image creation.
    """
    inquiry_time = datetime.datetime.now()
    response = agent.chat(question)
    
    print(f"{response}")

    # Check the 'temp_img' directory for the newest file created after the inquiry
    directory = 'temp_img'
    latest_file = None
    latest_time = inquiry_time  # Start comparison from the inquiry time

    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time > latest_time:  # Compare creation time
                    latest_time = file_time
                    latest_file = file_path

    # Print the path to the latest image if available and display the image
    if latest_file:
        return latest_file  # Return the file path to be used in Streamlit
    return None  # Return None if no file was created

def display_pdf(file):
    # Opening file from file path

    # st.markdown("### PDF Preview")
    base64_pdf = base64.b64encode(file.read()).decode("utf-8")

    # Embedding PDF in HTML
    pdf_display = f"""<iframe src="data:application/pdf;base64,{base64_pdf}" width="100" height="50%" type="application/pdf"
                        style="height:50vh; width:50%"
                    >
                    </iframe>"""

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)