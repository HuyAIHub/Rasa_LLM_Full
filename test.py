import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi import FastAPI, UploadFile, Form, File


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


uvicorn.run(app, host="0.0.0.0", port=1234)