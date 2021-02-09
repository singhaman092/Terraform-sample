import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal

ec2 = boto3.client('ec2')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('tag') #get from terraform
indextable = dynamodb.Table('tagindex') #get from terraform

def lambda_handler(event, context):
    
    newevent = json.loads(event['Records'][0]['Sns']['Message'])
    instanceid = newevent["EC2InstanceId"]
    eresponse = ec2.describe_instances(
        InstanceIds = [instanceid]
        )
    #get from ec2 instance
    tagarr = eresponse['Reservations'][0]['Instances'][0]['Tags']
    
    for i in tagarr:
        if i['Key'] == "Hostname":
            tag = i['Value']
    print(tag)   
    
    try:
        response = table.get_item(Key={
        'InstanceId': instanceid,
        })
        print(response['Item'])
    except:
        if tag.startswith('tsui'):
            tagToPass = 'tsui'
        elif tag.startswith('tshead'):
            tagToPass = 'tshead'
        elif tag.startswith('tsdb'):
            tagToPass = 'tsdb'
        elif tag.startswith('tsapp'):
            tagToPass = 'tsapp'
        elif tag.startswith('tshpc'):
            tagToPass = 'tshpc'
        elif tag.startswith('tsmodel'):
            tagToPass = 'tsmodel'
        else:
            print("Wrong tag given to hostname: tag must start with tsui,tshead,tsmodel,tshpc,tsdb,tsapp")
            tagToPass = 'none'
        
        indextopass = 0
        #getting the current index
        
        indexresponse = indextable.get_item(
            Key={'tag': tagToPass })
        currentindex = indexresponse['Item']['indexo']
        indextopass = currentindex+1
        tag = tag+str(indextopass)
        tresponse = ec2.create_tags(
            Resources = [instanceid],
            Tags = [{
                'Key' : 'Hostname',
                'Value': tag
            }])
        print(tresponse)
        res = indextable.update_item(
            Key = {
                'tag' : tagToPass
            },
            UpdateExpression = "SET indexo = :indextopass",
            ExpressionAttributeValues={ ':indextopass': Decimal(indextopass)},
            ReturnValues="UPDATED_NEW"
            )
        print(res)
        tres = table.put_item(
            Item = {
                'InstanceId': instanceid
            })
        print(res)
        
        
        # try:
        #     res = table.put_item(
        #         Item = {
        #             'InstanceId' : instanceid,
        #             'Tag': tag
        #         })
        # except:
        #     pass

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
