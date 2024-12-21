import re
import subprocess
import os

def extract_python_code(response):
    """Extract Python code from a response text."""
    code_match = re.search(r'```python(.*?)```', response, re.DOTALL)

    if code_match:
        return code_match.group(1).strip()
    else:
        raise ValueError("No Python code found in the response.")


def execute_code_and_generate_plot(code):
    """Execute the provided Python code and generate the plot image."""
    code_file_path = 'temp_plot_code.py'
    with open(code_file_path, 'w') as file:
        file.write(code)

    try:
        subprocess.run(['python', code_file_path], check=True)
        image_path = 'plot.png'
    except subprocess.CalledProcessError as e:
        print(f"Error executing plot code: {e}")
        image_path = None

    os.remove(code_file_path)

    return image_path