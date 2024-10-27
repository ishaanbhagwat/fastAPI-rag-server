# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
from fastapi.responses import JSONResponse
from fastapi import File, UploadFile, HTTPException

app = FastAPI()

# Add CORS middleware to allow your frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow your React frontend's origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")
    
    try:
        pdf_reader = PdfReader(file.file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
            
        return JSONResponse(content={"parsed_text": text})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing PDF: {str(e)}")

@app.get("/hello")
async def upload_pdf():
    return {"message": "Hello World!"}