from fastapi import FastAPI
from pydantic import BaseModel

#Import local scripts
from parserTool import *
from dbAccess import *

app = FastAPI()#to initialize our api

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
names = {}


@app.post("/createItem")
def create_item(item: Item):
    global id
    id = id + 1
    names[id] = item.namesList
    printInput(names, id)
    return "Your id is " + str(id)
# @app.post("/createItem2")
# def create_item2(item: Item):
#     printInput(item.namesList)
#     return "new name is " + item.namesList[-1]