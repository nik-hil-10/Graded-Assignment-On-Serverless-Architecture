import boto3
from datetime import datetime

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    
    # get instance id directly from the EventBridge state-change event payload
    instance_id = event.get('detail', {}).get('instance-id')
    
    if not instance_id:
        print("no instance ID found in event details, maybe triggered manually without a real event?")
        return
        
    print(f"preparing to auto-tag new instance: {instance_id}")
    
    # generate current date string as required by the assignment
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # tag the newly launched instance with the date and my custom tag
        ec2.create_tags(
            Resources=[instance_id],
            Tags=[
                {'Key': 'LaunchDate', 'Value': current_date},
                {'Key': 'Environment', 'Value': 'Testing'}
            ]
        )
        print(f"successfully auto-tagged {instance_id}")
    except Exception as e:
        print(f"could not tag instance {instance_id} - {str(e)}")
        
    return {
        'statusCode': 200,
        'body': 'auto-tagging complete'
    }
