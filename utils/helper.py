import cv2
import os
import base64
from io import BytesIO

def create_blog_post(title, images, texts, output_dir="blog_post"):
    # Create the output directory if it does not exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize HTML content with title and intro
    html_content = f"""
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; text-align: center; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #2980b9; margin-top: 20px; }}
            img {{ max-width: 80%; height: auto; border-radius: 8px; margin-top: 10px; }}
            p {{ text-align: center; margin-top: 10px; }}
            .section {{ margin-bottom: 40px; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <p>Welcome to this detailed post on {title.lower()}. Below, you will find an in-depth discussion, complete with visual examples to enhance your understanding.</p>
    """
    
    # Function to convert OpenCV image to base64
    def convert_image_to_base64(image):
        _, buffer = cv2.imencode('.png', image)
        img_base64 = base64.b64encode(buffer).decode("utf-8")
        return f"data:image/png;base64,{img_base64}"
    
    # Loop through each image and text snippet
    for idx, (image, text) in enumerate(zip(images, texts)):

        if texts:
            # Convert the image to base64
            image_base64 = convert_image_to_base64(image)
            
            # Append each section with an image and its corresponding text
            html_content += f"""
            <div class="section">
                <img src="{image_base64}" alt="Image {idx + 1}">
                <p>{text}</p>
            </div>
            """
        
        # Closing HTML tags
        html_content += """
        </body>
        </html>
        """
    
    # Save HTML content to a file
    html_file_path = os.path.join(output_dir, "centered_blog_post.html")
    with open(html_file_path, "w", encoding="utf-8") as file:
        file.write(html_content)
    
    print(f"Blog post saved at: {html_file_path}")
    return html_file_path
