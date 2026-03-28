---
source_id: "048"
title: "API - Dify Docs"
url: "https://docs.dify.ai/en/use-dify/publish/developing-with-apis"
type: "documentation"
scraped_at: "2026-03-27"
keywords: ["Dify API", "Dify backend-as-a-service", "Dify RESTful endpoints"]
content_length: 3850
---

# API - Dify Docs

You can use your Dify app as a backend API service out-of-box.

## How API Integration Works

1. **Build your app** in Dify Studio with the AI capabilities you need
2. **Generate API credentials** to securely access your app's functionality
3. **Call the API** from your application to get AI-powered responses
4. **Users interact** with your custom interface while Dify handles the AI processing

## Getting Started

1. Access API settings: In your app, navigate to **API Access** in the left sidebar.
2. Create API credentials: Generate new credentials for your integration. You can create multiple keys for different environments or users.
3. Review documentation: Dify generates complete API documentation specific to your app's configuration.
4. Implement in your app: Use the provided examples to integrate API calls into your application.

Never expose API keys in frontend code or client-side requests. Always call Dify APIs from your backend to prevent abuse and maintain security.

### Text-generation application

These applications are used to generate high-quality text, such as articles, summaries, translations, etc., by calling the completion-messages API and sending user input to obtain generated text results. The model parameters and prompt templates used for generating text depend on the developer's settings in the Dify Prompt Arrangement page.

Example cURL call:

```
curl --location --request POST 'https://api.dify.ai/v1/completion-messages' \
--header 'Authorization: Bearer ENTER-YOUR-SECRET-KEY' \
--header 'Content-Type: application/json' \
--data-raw '{
"inputs": {},
"response_mode": "streaming",
"user": "abc-123"
}'
```

Example Python call:

```python
import requests
import json

url = "https://api.dify.ai/v1/completion-messages"

headers = {
'Authorization': 'Bearer ENTER-YOUR-SECRET-KEY',
'Content-Type': 'application/json',
}

data = {
"inputs": {"text": 'Hello, how are you?'},
"response_mode": "streaming",
"user": "abc-123"
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.text)
```

### Conversational Applications

Conversational applications facilitate ongoing dialogue with users through a question-and-answer format. To initiate a conversation, you will call the `chat-messages` API. A `conversation_id` is generated for each session and must be included in subsequent API calls to maintain the conversation flow.

Important Note: The Service API does not share conversations created by the WebApp. Conversations created through the API are isolated from those created in the WebApp interface.

#### Key Considerations for conversation_id:

- **Generating the conversation_id:** When starting a new conversation, leave the conversation_id field empty. The system will generate and return a new conversation_id, which you will use in future interactions to continue the dialogue.
- **Handling conversation_id in Existing Sessions:** Once a conversation_id is generated, future calls to the API should include this conversation_id to ensure the conversation continuity with the Dify bot. When a previous conversation_id is passed, any new inputs will be ignored. Only the query is processed for the ongoing conversation.
- **Managing Dynamic Variables:** If there is a need to modify logic or variables during the session, you can use conversation variables (session-specific variables) to adjust the bot's behavior or responses.

Example cURL call for chat-messages:

```
curl --location --request POST 'https://api.dify.ai/v1/chat-messages' \
--header 'Authorization: Bearer ENTER-YOUR-SECRET-KEY' \
--header 'Content-Type: application/json' \
--data-raw '{
"inputs": {},
"query": "eh",
"response_mode": "streaming",
"conversation_id": "1c7e55fb-1ba2-4e10-81b5-30addcea2276",
"user": "abc-123"
}'
```
