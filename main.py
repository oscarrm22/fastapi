from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

#Import local scripts
from parserTool import *
from dbAccess import *

app = FastAPI()#to initialize our api


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):  
    namesList = []

@app.get("/") # con esto hacemos un get del endpoint /
def home(): #esta funcion se triggerea cuando se hace un get
    return {"Data": 'Testing'} # por estandar, el return siempre es en JSON format

#otro endpoint
@app.get("/about")
def about():
    return {"Data" : "about"}


id = 0
newId = 0
# names = {}


@app.post("/createItem")
def create_item(item: Item):
    global id, newId
    # names = {}
    id = newId
    # names[id] = item.namesList
    printInput(item.namesList, id)
    newId = id + 1
    return "Your id is " + str(id)

@app.post("/getItem")
def create_item(key: str):
    return getItemFromTable(key)

urls = []

@app.post("/setURL")
def set_url(url: str):
    global urls
    urls.append(url)
    return "Last URL added: " + urls[-1]

@app.post("/useURLS")
def use_urls():
    global urls, id, newId
    printInput(urls, id)
    num_of_urls = len(urls)
    urls = []
    id = newId
    newId = id + 1
    return "Number of URLs: " + str(num_of_urls) + ", Your ID is " + str(id)
