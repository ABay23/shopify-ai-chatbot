from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

'''
We can allow requests from the Frontend dev server
'''
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'], #* Frontend url
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get("/ping")
def ping():
    return {"message": "Backend is running!!!"}