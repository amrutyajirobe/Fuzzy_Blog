import os
import sys
import getopt
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/blogger']
TOKEN_PICKLE = 'token.pickle'
CLIENT_SECRET_FILE = 'client_id.json'

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)
        with open(TOKEN_PICKLE, 'wb') as token:
            pickle.dump(creds, token)
    return creds

def main():
    blogId = 8609740123691510288  # put your blog ID here
    isDraft = True
    postfile = ''
    title = 'Default Title'
    labels = 'linux, rocks'

    # Argument parsing
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} -f \"Filename\" [-t \"My Title\"] [-l \"label,label\"] [--publish]")
        print("Posts are uploaded as drafts by default. Use --publish to publish immediately\n")
        sys.exit()

    myopts, args = getopt.getopt(sys.argv[1:], "f:t:l:", ['publish'])
    for o, a in myopts:
        if o == '-f':
            postfile = a
        elif o == '--publish':
            isDraft = False
        elif o == '-t':
            title = a
        elif o == '-l':
            labels = a

    if not postfile:
        print("Error: Post file must be specified with -f")
        sys.exit()

    if not isDraft and title == 'Default Title':
        print("You must provide a title if you want to publish")
        sys.exit()

    labels_list = labels.split(',')

    creds = get_credentials()
    blogger_service = build('blogger', 'v3', credentials=creds)

    # Read post content
    try:
        with open(postfile, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error opening post file: {e}")
        sys.exit()

    body = {
        "content": content,
        "title": title,
        "labels": labels_list
    }

    try:
        post = blogger_service.posts().insert(blogId=blogId, body=body, isDraft=isDraft).execute()
    except Exception as e:
        print(f"Something went wrong uploading this post: {e}")
        sys.exit()

    print(f"Title: {post['title']}")
    print(f"Is Draft: {isDraft}")
    if not isDraft:
        print(f"URL: {post['url']}")
    print(f"Labels: {post['labels']}")

if __name__ == "__main__":
    main()
