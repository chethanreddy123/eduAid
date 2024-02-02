from fastapi import FastAPI
from routers import llm_routes, teacher, student
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="eduAId Backend",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(llm_routes.router)
app.include_router(teacher.router)
app.include_router(student.router)
