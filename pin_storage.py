import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timezone

# Initialize the DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('c22-fysh-user-pins')


def add_pin(user_id: str,
            lat: float,
            lng: float,
            label: str,
            features: dict = None) -> str:
    """
    Adds a pin with an optional 'features' dictionary for flexibility.
    'features' can contain anything: { 'color': 'red', 'rating': 5, 'visited': True }
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    # Initialize the item with core required fields
    item = {
        'user_id': user_id,
        'created_at': timestamp,
        'latitude': str(lat),
        'longitude': str(lng),
        'label': label
    }

    # If features are provided, merge them into the item
    # This allows you to store flexible attributes at the top level
    if features and isinstance(features, dict):
        item.update(features)

    table.put_item(Item=item)
    return timestamp


def delete_pin(user_id: str, created_at: str) -> None:
    """
    Deletes a specific pin.
    Requires both Partition Key and Sort Key.
    """
    table.delete_item(
        Key={
            'user_id': user_id,
            'created_at': created_at
        }
    )


def get_user_pins(user_id: str, ascending: bool = True) -> list:
    """
    Fetches all pins for a specific user.
    ScanIndexForward controls the sort order of the Sort Key.
    """
    response = table.query(
        KeyConditionExpression=Key('user_id').eq(user_id),
        ScanIndexForward=ascending  # True for oldest first, False for newest first
    )
    return response.get('Items', [])
