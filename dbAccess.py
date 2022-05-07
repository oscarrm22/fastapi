import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('GraphGeneratorTest2')
# print(table)

# test_graph = {"nodoId" : 10, "nodoName": "oscar"}

def addItemToTable(nodesDic):
    response = table.put_item(
    Item = { 
        'reqId': str(0),
        'graph': str(1),
        'graphDic': nodesDic
        }
    )

# addItemToTable(test_graph)