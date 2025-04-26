import matplotlib.pyplot as plt
import io
import base64
from PIL import Image
import os

def execute_matplotlib_and_get_base64(code: str, image_path='chart.png'):
    """
    Executes given matplotlib code that saves a chart as a single file,
    reads the saved image as Base64, deletes it, and returns the Base64 string.
    
    Args:
        code (str): The matplotlib code to execute (must save an image like chart.png)
        image_path (str): Path of the saved image. Default is 'chart.png'.
        
    Returns:
        str: Base64 encoded image.
    """
    # 1. Execute the matplotlib code
    local_scope = {}
    exec(code, {}, local_scope)

    # 2. Check if file exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"No image saved at {image_path}")

    # 3. Read the image and encode it to base64
    with open(image_path, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read()).decode('utf-8')

    # 4. Delete the image after reading
    os.remove(image_path)

    return b64_string




def show_base64_image(base64_string: str):
    # Decode the base64 string
    img_data = base64.b64decode(base64_string)
    
    # Convert to a BytesIO stream
    buf = io.BytesIO(img_data)
    
    # Open image using PIL
    image = Image.open(buf)

    # Display the image using matplotlib
    plt.imshow(image)
    plt.axis('off')  # Hide axis
    plt.show()
