from bs4 import BeautifulSoup as bs
import requests
import re
import copy
import time
#import html2text
import unidecode
import json



#Import local scripts
from dbAccess import *

movie_sites = []
movie_soups = []
mnode_list = []
p_list = []
pnode_list = []

properties_dictionary = {
    "Protagonistas" : ["Protagonistas", "reparto", "cast-crew", "stars"],
    "Productora" : ["Produccion", "Producer"],
    "Direccion" : ["Direccion", "Director"],
    "Presupuesto" : ["Presupuesto"],
    "Año" : ["Año", "Release Date"],
    "Titulo" : ["Titulo", "Titulo original"],
    "Pais" : ["Pais", "origen"]
}

properties = list(properties_dictionary.keys())


def printInput(sitesList, id):
    global movie_sites
    print("Desde otro archivo: ", sitesList)
    movie_sites = sitesList
    start_request()



def print_sites(movies:list):
    print("Links to be parsed: ", movies)

#------------------------------------------------------
#GET HTML
def load_data(urls:list):
    global  movie_soups

    for i in urls:
        r = requests.get(i)
        movie_soups.append(bs(r.content))
    print("GETTING SOUPS", len(movie_soups))

#------------------------------------------------------
#Get texts from table
def get_text_from_table(table):
    rows = table.select("tr")#encontrar filas
    c1,c2 = [],[]
    for r in rows:
        col1 = r.select("th") # index 0 para utilizar la primer entrada 
        col2 = r.select("td")
        if col1 and col2: ##asegurar que la fila tiene tipo de dato y dato
            text1 = col1[0].get_text(" ",strip = True)
            c1.append(text1)
            #text2 =  [col2[0].get_text(strip = True)]
            text2 =  [text for text in col2[0].stripped_strings] #agregar valores como lista
            if text1 == "Presupuesto":
                for t in text2:
                    string_encode = t.encode("ascii", "ignore")
                    string_decode = string_encode.decode()
                #join all texts in one
                separator = " "
                temp = separator.join(text2)
                text2 = temp
            c2.append(text2)
            #print(f"{text1}, {text2}")
    return c1, c2


#------------------------------------------------------
#ASIGNAR PROPIEDADES

def assign_properties(texts):
    mat = [[0] * len(texts) for s in range(len(properties_dictionary))] #to register which concept refers to which text

    #text = elements[0]
    for idx_t, t in enumerate(texts):    
        for spec in properties_dictionary:
            idx_s = properties.index(spec)
            for s in properties_dictionary[spec]: # buscar valores del diccionario en los textos
                text = unidecode.unidecode(t) #quitar acentos
                sp = unidecode.unidecode(s) #quitar acentos
                #print(f"Evaluar {t} y  {s}")
                if re.search(sp.lower(), text.lower()):
                    mat[idx_s][idx_t]+=1
                    #print(f"{spec} in {idx_s}, {idx_t}")

    #REcorrer matriz para encontrar la opci[on m[as parecida
    r = {}#Diccionario para almacenar propeidades y el indice correspondiente
    for i in range(len(mat)):
        max_val = max(mat[i])
        if max_val > 0:
            max_idx = mat[i].index(max_val) 
            r[properties[i]] = max_idx

    #print(r)
    return r # regresar diccionario con propiedades y el correspondiente idx


#------------------------------------------------------
#GET TABLE

def find_table(tables):
    table_idx = 1
    count = 0
    for i, table in enumerate(tables): #recorrer todas las tablas
        c1,c2 = get_text_from_table(table)
        new_count = 0
        for c in c1:
            text = unidecode.unidecode(c) #quitar acentos
            for property in properties:
                p = unidecode.unidecode(property) #quitar acentos
                if re.search(property.lower(), text.lower()): #confirmar aserciones
                    new_count+=1
        if new_count > count:
            count = new_count
            table_idx = i

    return table_idx

#------------------------------------------------------
#ADD ROLE

def add_role(node_list, name, movie, role):
    for n in node_list:
        if name == n.name:
            n.add_link(movie, role)

num_of_nodes = 0

#------------------------------------------------------
#CREAR DICCIONARIOS DE NODOS
def mnodes_dictionary(node_list):
    global num_of_nodes
    nodes_d = []
    for i,n in enumerate(node_list):
        d = {}
        d["id"] = str(i + num_of_nodes)
        if n.title is None:
            d["username"] = n.title
        else:
            d["username"] = n.title[0]
        d["type"] = "Movie"
        # add attributes
        d["budget"] = n.budget
        d["year"] = n.year
        d["country"] = n.cntry

        nodes_d.append(d)
    num_of_nodes += len(nodes_d)

    return nodes_d

def pnodes_dictionary(node_list):
    global num_of_nodes
    nodes_d = []
    for i,n in enumerate(node_list):
        d = {}
        d["id"] = str(i + num_of_nodes)
        d["username"] = n.name
        d["type"] = "Person"
        nodes_d.append(d)
    num_of_nodes += len(nodes_d)
    return nodes_d  

def get_node_id(nodes_list, name):
    id = -1
    for n in nodes_list:
        if n["username"] == name:
            id = n["id"]
    return id

def get_node_by_name(nodes_list, name):
    node:MNode = None
    for n in nodes_list:
        if n.name == name:
            node = n
    return node
        
def get_node_by_mname(nodes_list, name):
    node:MNode = None
    for n in nodes_list:
        if n.title[0] == name:
            node = n
    return node    


def create_links_dictionary(pnode_list, nodes_to_display):
    links_d = []
    link_id = 0
    for node in nodes_to_display:
        
        
        if node["username"] in p_list: #si es una persona   
            pnode = get_node_by_name(pnode_list, node["username"]) #obtener el nodo corresponidente
            for l in pnode.links:
                d = {}
                d["source"] = node["id"]
                d["target"] = get_node_id(nodes_to_display,l[0])
                d["type"] = l[1]
                d["id"] = str(link_id)
                link_id = link_id +1
                links_d.append(d)

    return links_d

#------------------------------------------------------
#CLASS MOVIE
class MNode:
    def __init__(self, cst, prd, dr, bdgt, yr, ttl, cntry):
        self.cast = cst
        self.producer = prd
        self.director = dr
        self.budget= bdgt
        self.year= yr
        self.title= ttl
        self.cntry= cntry

#------------------------------------------------------
#CLASS PERSON
class PNode:

    movies = []
    roles = []
    links = []

    def __init__(self, nm, mv, rl):
        self.name = nm
        #print("create ",mv)
        self.movies = [mv]
        self.roles= [rl]
        self.links = [[mv, rl]]
        
    def add_link(self, mv, rl):
        link = [mv, rl]
        if mv not in self.movies:
            self.movies.append(mv)
        if rl not in self.roles:
            self.roles.append(rl)
        if link not in self.links:
            self.links.append(link)

#**************************************************************************************************************************************
def start_request():
    global mnode_list, p_list, pnode_list, num_of_nodes, movie_sites
    movie_soups = []
    mnode_list = []
    p_list = []
    pnode_list = []
    print_sites(movie_sites)

    #obtener HTML
    load_data(movie_sites)

    #PRocesar Informacion de Wikipedia
    ## DE wikipedia
    wiki_idx = 0
    print("DBG 3, ",len(movie_soups))
    tables = movie_soups[wiki_idx].select("table")
    table_idx = find_table(tables)
    c1,c2 = get_text_from_table(tables[table_idx])

    #Recorrer todas las p[aginas
    for m in range(len(movie_soups)):
        tables = movie_soups[m].select("table")
        table_idx = find_table(tables)
        c1,c2 = get_text_from_table(tables[table_idx])

        r = assign_properties(c1)
        # print(f"----------MOVIE {m}----------")
        
        att = []
        for p in properties:
            if p in r:
                value = c2[r[p]]
            else:
                value = "None"
            # print(f"{p}: {value}")
            att.append(value)
        n = MNode(att[0],att[1],att[2],att[3],att[4],att[5],att[6])
        mnode_list.append(n)

    #Crear lista de personas

    for movie in mnode_list:
        for p in movie.producer:
            if p not in p_list:
                p_list.append(p)
                n = PNode(p, movie.title[0], "Producer")
                pnode_list.append(n)
            else:
                add_role(pnode_list, p, movie.title[0], "Producer")
        for p in movie.director:
            if p not in p_list:
                p_list.append(p)
                n = PNode(p, movie.title[0], "Director")
                pnode_list.append(n)
            else:
                add_role(pnode_list,p, movie.title[0], "Director")
        for p in movie.cast:
            if p not in p_list:
                p_list.append(p)
                n = PNode(p, movie.title[0], "Cast")
                pnode_list.append(n)
            else:
                add_role(pnode_list,p, movie.title[0], "Cast")

    #Crear diccionario de nodos
    nodes = mnodes_dictionary(mnode_list)
    nodes.extend(pnodes_dictionary(pnode_list))

    #crear links
    links_dic = create_links_dictionary(pnode_list, nodes)

    #Crear json
    toGraph = {"nodes":nodes, "links":links_dic}
    jsonString = json.dumps(toGraph)
    jsonFile = open("dataToGraph2.json", "w")
    jsonFile.write(jsonString)
    jsonFile.close()
    
    #add graph dictionary to DB
    addItemToTable(jsonString)





