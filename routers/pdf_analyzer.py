from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import os
import fitz
from PIL import Image
from services.llm import LLM
from fastapi import APIRouter, HTTPException, Query
from services.pdf_services import pdf_to_images
from markdown_pdf import Section, MarkdownPdf


router = APIRouter(
    prefix='/pdf_analyzer',
    tags=['PDF Analyzer'],
)


UPLOAD_FOLDER = "uploads"



@router.post("/generate_notes/")
async def generate_notes(file: UploadFile = File(...)):
    try:
        # Save the uploaded PDF file
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        # Convert PDF to images
        output_folder = os.path.join(UPLOAD_FOLDER, "images")
        os.makedirs(output_folder, exist_ok=True)
        output_paths = pdf_to_images(file_path, output_folder)

        # Initialize LLM
        llm = LLM()

        # Process images and generate notes
        image_text = []
        page_count = 1
        for path_image in output_paths:
            image = Image.open(path_image)
            model_image = llm.get_image_model()
            prompt = "You are tasked with interpreting handwritten notes from a programming instructor. The notes are presented in the form of an image. Your goal is to analyze and comprehend the content of these handwritten notes, focusing on extracting key information related to programming concepts. Provide a detailed and crisp understanding and summary  in well structured format of the instructor's notes based on the presented image."

            response = model_image.generate_content([prompt, image])
            response.resolve()
            image_text.append(response.text)

        # Create a PDF with the generated notes
        pdf = MarkdownPdf(toc_level=2)
        for i in image_text:
            pdf.add_section(Section(f"# Instructor Notes Description for Page {page_count}\n" + i))

        pdf_path = os.path.join(UPLOAD_FOLDER, "notes.pdf")
        pdf.save(pdf_path)
        page_count += 1

        # Return the generated notes PDF
        return StreamingResponse(open(pdf_path, "rb"), media_type="application/pdf")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
