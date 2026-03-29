import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    
    # Retrieve all instances
    response = ec2.describe_instances()
    
    instances_to_stop = []
    instances_to_start = []
    
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            state = instance['State']['Name']
            
            # Look for the 'Action' tag
            if 'Tags' in instance:
                for tag in instance['Tags']:
                    if tag['Key'] == 'Action':
                        if tag['Value'] == 'Auto-Stop' and state == 'running':
                            instances_to_stop.append(instance_id)
                        elif tag['Value'] == 'Auto-Start' and state == 'stopped':
                            instances_to_start.append(instance_id)
                            
    # Execute the actions
    if instances_to_stop:
        ec2.stop_instances(InstanceIds=instances_to_stop)
        print("Stopped instances: ", instances_to_stop)
    else:
        print("No instances to stop.")
        
    if instances_to_start:
        ec2.start_instances(InstanceIds=instances_to_start)
        print("Started instances: ", instances_to_start)
    else:
        print("No instances to start.")
        
    return {
        'statusCode': 200,
        'body': 'Execution complete'
    }
