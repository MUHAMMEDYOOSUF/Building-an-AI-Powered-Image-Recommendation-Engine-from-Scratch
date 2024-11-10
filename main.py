# main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from io import BytesIO
from PIL import Image
import base64
from image_search import ImageSearch
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)
image_searcher = ImageSearch()

class QueryRequest(BaseModel):
    query: str

def image_to_base64(image: Image.Image) -> str:
    """Converts an image to a base64 string."""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

@app.post("/search_by_image/")
async def search_by_image(file: UploadFile = File(...)):
    file_location = f"temp_images/{file.filename}"
    
    try:
        # Save the uploaded file temporarily
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Perform image search
        image_results = image_searcher.search_by_image(uri=file_location, k=5)
        
        # Prepare the response
        results = []
        for idx, (img, meta_df) in enumerate(image_results):
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            out_dict = {"image": img_str}
            out_dict.update(meta_df.to_dict()['Values'])
            results.append(out_dict)
        
        return JSONResponse(content={"results": results})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
    finally:
        # Clean up the temp file
        if os.path.exists(file_location):
            os.remove(file_location)


@app.post("/search_by_query/")
async def search_by_query(query_request: QueryRequest):
    try:
        # Get the query from the request
        query = query_request.query

        # Perform query search
        image_results = image_searcher.search_by_query(query=query)
        
        # Prepare the response
        results = []
        for idx, (img, meta_df) in enumerate(image_results):
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            out_dict={"image": img_str}
            out_dict.update(meta_df.to_dict()['Values'])
            results.append(out_dict)
        
        return JSONResponse(content={"results": results})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
