import os
import uuid
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported.")
    
    # Generate unique ID for dataset
    dataset_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename)[1]
    save_path = os.path.join(DATA_DIR, f"{dataset_id}{file_ext}")
    
    try:
        # Save file to disk
        contents = await file.read()
        with open(save_path, "wb") as f:
            f.write(contents)
            
        # Parse with pandas
        if file_ext == '.csv':
            df = pd.read_csv(save_path)
        else:
            df = pd.read_excel(save_path)
            
        # Extract metadata
        metadata = {
            "dataset_id": dataset_id,
            "filename": file.filename,
            "rows": len(df),
            "columns": len(df.columns),
            "columns_list": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict()
        }
        
        return JSONResponse(content={"status": "success", "metadata": metadata})
        
    except Exception as e:
        # Cleanup if parsing fails
        if os.path.exists(save_path):
            os.remove(save_path)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
