import requests
import config

webhook_url = config.discord

def noot(message):
    main_content = {
    "content": message
    }
    requests.post(webhook_url,main_content)
