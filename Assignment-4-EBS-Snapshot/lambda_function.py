import boto3
from datetime import datetime, timedelta, timezone

# target volume for assignment
VOLUME_ID = 'vol-055d84aa7e05362ec' 
RETENTION_DAYS = 30 # delete backups after a month

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    
    # take backup of the volume
    print(f"Creating snapshot for volume: {VOLUME_ID}...")
    try:
        new_snapshot = ec2.create_snapshot(
            VolumeId=VOLUME_ID,
            Description=f"Automated backup snapshot created by Lambda for {VOLUME_ID}"
        )
        print(f"Successfully created Snapshot ID: {new_snapshot['SnapshotId']}")
    except Exception as e:
        print(f"Error creating snapshot for volume {VOLUME_ID}: {str(e)}")
        # catch error if volume doesn't exist
        
    # calculate cutoff date for strict rotation
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    
    # only get my own snapshots
    snapshots_response = ec2.describe_snapshots(OwnerIds=['self'])
    
    deleted_snapshots = []
    
    for snapshot in snapshots_response['Snapshots']:
        snapshot_id = snapshot['SnapshotId']
        start_time = snapshot['StartTime']
        
        # delete if it matches volume and is too old
        if snapshot.get('VolumeId') == VOLUME_ID and start_time < cutoff_date:
            try:
                ec2.delete_snapshot(SnapshotId=snapshot_id)
                deleted_snapshots.append(snapshot_id)
            except Exception as e:
                print(f"Could not delete snapshot {snapshot_id}: {str(e)}")
                
    if deleted_snapshots:
        print(f"Deleted old snapshots: {deleted_snapshots}")
    else:
        print("No snapshots older than 30 days found for deletion.")
        
    return {
        'statusCode': 200,
        'body': 'EBS Backup and Cleanup executed successfully'
    }
