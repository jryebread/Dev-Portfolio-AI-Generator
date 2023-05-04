import os
import subprocess

import openai
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
# Load environment variables from the .env file
load_dotenv()

VERCEL_TOKEN = os.environ.get("VERCEL_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_KEY")

vercel_website_name = "developerportfolio"

import requests
import tempfile
from pathlib import Path
import json

def deployVercel(html_content: str, project_name: str, vercel_token: str):
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = Path(temp_dir) / project_name
        os.makedirs(project_dir)

        # Write the HTML content to the index.html file
        with open(project_dir / "index.html", "w") as f:
            f.write(html_content)

        # Write the vercel.json configuration file
        vercel_config = {
            "name": project_name,
            "version": 2,
            "builds": [{"src": "index.html", "use": "@vercel/static"}],
        }

        with open(project_dir / "vercel.json", "w") as f:
            json.dump(vercel_config, f)

        # Deploy to Vercel using the CLI
        cmd = ["vercel", "--token", vercel_token, "-y", "--prod"]

        result = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True)

        if result.returncode == 0:
            print("Deployment READY!!")
            print(f"Final URL: {result.stdout.strip()}")
        else:
            print("Deployment failed:")
            print(result.stderr)

def create_website(github_json):
    prompt = f"""Make a beautiful website. Your code should not only be visually stunning, but also intuitive and mobile friendly. Include some animations where appropriate. 
             Remember to prioritize readability and organization, and to create a polished final product. Include the following information from this json in the website, 
             but skip the ones that end in url: 
            ---
            {github_json}"""

    chat = ChatOpenAI(temperature=0.2, max_tokens=2500)

    messages = [
        SystemMessage(content="You are a senior frontend designer. Generate HTML that is colorful and well designed. Use gradient and animations where applicable."),
        HumanMessage(content=prompt),
    ]

    response = chat(messages)

    reply = response.content
    return reply

def createPortfolio(user):
    response = requests.get(f"https://api.github.com/users/{user}")
    if response.status_code != 200:
        print(f"Error: Unable to fetch the page. Status code: {response.status_code}")
        return
    print(response.json())

    html_content = create_website(response.json())
    deployVercel(html_content, vercel_website_name, VERCEL_TOKEN)

# user = input("What developer github ID to make personal website for?")
user = "yoheinakajima"
createPortfolio(user)
