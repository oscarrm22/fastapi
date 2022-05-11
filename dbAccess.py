import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('GraphGeneratorTest2')
# print(table)

# test_graph = {"nodoId" : 10, "nodoName": "oscar"}

element_id = 0

def addItemToTable(nodesDic):
    global element_id
    response = table.put_item(
    Item = { 
        'reqId': str(element_id),
        'graph': str(1),
        'graphDic': nodesDic
        }
    )

    element_id = element_id + 1

def getItemFromTable(key1):
    response = table.get_item(
        Key={
            'reqId': key1,
            'graph': '1',
        }
    )
    print(response['Item'])
    return response['Item']