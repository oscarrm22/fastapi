import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('GraphGeneratorTest2')


if table is not None:
    print("delete table")
    table.delete()
else:
    print("table does not exist")

table = dynamodb.create_table (
    TableName = 'GraphGeneratorTest2',
       KeySchema = [
           {
               'AttributeName': 'reqId',
               'KeyType': 'HASH'
           },
           {
               'AttributeName': 'graph',
               'KeyType': 'RANGE'
           }
           ],
           AttributeDefinitions = [
               {
                   'AttributeName': 'reqId',
                   'AttributeType': 'S'
               },
               {
                   'AttributeName':'graph',
                   'AttributeType': 'S'
               }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits':1,
                'WriteCapacityUnits':1
            }
          
    )

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