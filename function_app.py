import os
import azure.functions as func
import logging
from openai import AzureOpenAI

# Retrieve OpenAI API key and endpoint from environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
openai_api_endpoint = os.getenv('OPENAI_API_ENDPOINT')

client = AzureOpenAI(
    api_key=openai_api_key,  
    api_version="2024-07-01-preview",
    azure_endpoint=openai_api_endpoint
)

# System prompt for the OpenAI model
system_prompt = """
あなたはトリオ漫才のつっこみ役です。あなたと会話している人が次の2点を教えてくれます。
[Aさん] 説明したシチュエーションと話題の情報
[Bさん] Aさんのコメントを受けて解答したコメント
 
Bさんは必ずコメントでボケてきますので、あなたはそれに対してツッコミをしなければならない役目を持っています。勢いがあるwitに富んだツッコミをしてください。例えば、下記のようなコメントが求められる立場です。
[Aさん] やぁ、B君Cさん。明日から夏休みだね。私はプール行ったり海に行ったり忙しくなりそうだよ。B君はどう？
[Bさん] 僕は雪だるま作ったりスノボしたりで忙しくなりそうだよ。
 
[あなたの役割] 雪なんかあるかい！
"""

# Initialize the Function App with anonymous HTTP access level
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Function to get a response from OpenAI API
def get_openai_response(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",  # Specify the engine to use
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        max_tokens=150  # Limit the response length
    )
    return response.choices[0].message.content  # Return the response text

# Define the HTTP trigger function
@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Get 'boke' parameter from the query string or request body
    boke = req.params.get('boke')
    if not boke:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            boke = req_body.get('boke')

    # If 'boke' is provided, get response from OpenAI and return it
    if boke:
        openai_response = get_openai_response(boke)
        return func.HttpResponse(openai_response)
    else:
        # If 'boke' is not provided, return a default message
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a boke in the query string or in the request body for a personalized response.",
             status_code=200
        )