import boto3
import os

# the SNS topic to publish alerts to
SNS_TOPIC_ARN = 'arn:aws:sns:ap-south-1:791358130074:EC2StateAlerts'

def lambda_handler(event, context):
    sns_client = boto3.client('sns')
    
    # pull info from the cloudwatch event payload
    detail = event.get('detail', {})
    instance_id = detail.get('instance-id', 'Unknown-Instance')
    state = detail.get('state', 'Unknown-State')
    
    # format a clean, human-readable message for the email alert
    email_subject = f"EC2 Alert: State Change detected ({state})"
    email_message = f"Attention,\n\nThe EC2 Instance {instance_id} has just changed its state to: {state.upper()}.\n\nAutomatically sent from AWS Lambda."
    
    print(f"preparing to send alert for instance {instance_id} moving to {state}...")
    
    try:
        # publish the notification to our sns topic
        response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=email_subject,
            Message=email_message
        )
        print(f"alert email successfully dispatched via SNS. message ID: {response.get('MessageId')}")
        
    except Exception as e:
        print(f"failed to send SNS alert: {str(e)}")
        
    return {
        'statusCode': 200,
        'body': 'sns alert process executed'
    }
