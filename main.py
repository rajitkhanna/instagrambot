import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from datetime import datetime, timedelta
import instaloader
import os

load_dotenv()
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
SES_EMAIL_SOURCE = os.getenv('SES_EMAIL_SOURCE')
AWS_REGION = os.getenv('AWS_REGION')
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD')

L = instaloader.Instaloader()
L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

def send_email(email, body):
    try:
        ses = boto3.client('ses', aws_access_key_id=AWS_ACCESS_KEY,
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                region_name=AWS_REGION)
        response = ses.send_email(
            Source=SES_EMAIL_SOURCE,
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': 'Instagram Movement Bot'},
                'Body': {
                    'Text': {'Data': body}
                }
            }
        )

    except ClientError as e:
        print(e.response['Error']['Message'])

        return False
    else:
        print("Email sent! Message ID:", response['MessageId'])
        return True


def get_posts_within_interval(username, start, end):
    posts = instaloader.Profile.from_username(L.context, username).get_posts()

    recent_posts = []
    for post in posts:
        if post.date > end:
            continue
        if post.date < start:
            break
        # L.download_post(post, username)
        recent_posts.append(post)

    return recent_posts

if __name__ == '__main__':
    creators = [
        'bamlionheart',
        'pro_golfer',
        'rishfits',
        'delallo_methods'
    ]

    end = datetime.now()
    start = end - timedelta(days=7)

    post_dict = {}
    for creator in creators:
        posts = get_posts_within_interval(creator, start, end)
        post_dict[creator] = posts

    msg = ' '
    for creator in post_dict:
        msg += f'{creator} has {len(post_dict[creator])} new post(s)\n'
        msg += '\n\n'
        msg += '\n'.join(map(lambda p: f'{p.caption}\n\n{p.video_url}\n' if p.video_url else f'{p.caption}\n\n{p.url}\n', post_dict[creator]))
        msg += '\n\n'

    send_email('rajitskhanna@gmail.com', msg)
