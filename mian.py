from fastapi import FastAPI
from pydantic import BaseModel

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
id = 1
names = {
    id : "Alonso"
}

@app.post("/createItem")
def create_item(item: Item):
    global id
    id = id + 1
    # names[id] = item.namesList
    print(item.namesList)
    return "new name is " + item.namesList[1]

@app.get("/createItem")
def show_item():
    return "Latest name is " + names[id]


@app.post("/createItem2")
def create_item2(item: Item):
    return "new name is " + item.namesList