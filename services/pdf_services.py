import fitz  # PyMuPDF library
from PIL import Image

def pdf_to_images(pdf_path, output_folder):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    image_path_list = []

    # Iterate through each page and convert to an image
    for page_num in range(pdf_document.page_count):
        # Get the page
        page = pdf_document[page_num]

        # Convert the page to an image
        image = page.get_pixmap()

        # Create a PIL Image from the raw image data
        pil_image = Image.frombytes("RGB", (image.width, image.height), image.samples)

        # Save the image to the output folder
        image_path = f"{output_folder}/page_{page_num + 1}.png"
        image_path_list.append(image_path)
        pil_image.save(image_path, format="PNG")

        print(f"Image saved: {image_path}")

    # Close the PDF document
    pdf_document.close()
    return image_path_list