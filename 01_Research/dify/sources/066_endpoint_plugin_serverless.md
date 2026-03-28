---
source_id: "066"
title: "Extension Plugin Endpoint: Bringing Serverless Flexibility to Dify"
url: "https://dify.ai/blog/extension-plugin-endpoint-bringing-serverless-flexibility-to-dify"
type: "blog"
scraped_at: "2026-03-27"
keywords: ["Dify endpoint plugin", "Dify plugin system", "Dify plugin development"]
content_length: 7850
---

# Extension Plugin Endpoint: Bringing Serverless Flexibility to Dify

Introducing Dify's new Endpoint, which lets Extension plugins handle custom HTTP requests and leverage reverse calls for greater flexibility. It enables features like custom web interfaces, OpenAI-compatible APIs, and asynchronous event triggers.

## About Endpoint

The Endpoint is a new, extensible type introduced in Dify's v1.0.0 plugin system, providing a new API entry point for Dify. Plugins can define the logic of these APIs through code. From the developer's perspective, this is akin to running an HTTP server within Dify, with the server implementation entirely determined by the developer.

The specific logic of an Endpoint is implemented within the Extension Plugin. When the user activates the Endpoint, Dify generates a random URL formatted as https://abcdefg.dify.ai. When Dify receives a request to this URL, the original HTTP message is forwarded to the plugin, and the plugin behaves similarly to a serverless function -- receiving and processing the request.

To allow the plugin to call apps within Dify, a reverse call feature has been introduced.

## Examining the Core Capabilities

Originally, Endpoint was designed as a module to handle Webhooks, intended to abstract complex low-code/no-code workflows into reusable code implementations via plugin logic. As usage deepened, Endpoint was found to have broader applications. At its core, it is a serverless HTTP server. While it doesn't support long connection protocols like WebSockets, it can perform most of the functions of an HTTP server.

## WebApp Templates

Currently, Dify's WebApp is still fairly basic, and customization options for styling are limited. Since it's difficult to fine-tune every specific scenario, Endpoint can implement these requirements. Imagine a plugin that includes several Endpoints, each with a different template style -- minimalistic, anime-cute, Korean, or Western styles. Behind these different Endpoint styles is the same Chatbot, only with a different skin. This naturally forms a template marketplace.

### Implementation

A simple version includes two Endpoints: one for displaying a page and another for calling Dify APIs. The page Endpoint serves HTML:

```python
class NekoEndpoint(Endpoint):
    def _invoke(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        with open(os.path.join(os.path.dirname(__file__), "girls.html"), "r") as f:
            return Response(
                f.read().replace("{{ bot_name }}", settings.get("bot_name", "Candy")),
                status=200, content_type="text/html",
            )
```

The talk Endpoint uses reverse calls to invoke Dify apps:

```python
class GirlsTalk(Endpoint):
    def _invoke(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        app = settings.get("app")
        data = r.get_json()
        query = data.get("query")
        conversation_id = data.get("conversation_id")

        def generator():
            response = self.session.app.chat.invoke(
                app_id=app.get("app_id"),
                query=query, inputs={},
                conversation_id=conversation_id,
                response_mode="streaming",
            )
            for chunk in response:
                yield json.dumps(chunk) + "\n\n"

        return Response(generator(), status=200, content_type="text/event-stream")
```

## OpenAI-Compatible Interface

Users have asked: Why not use Dify as an API gateway? Why can't Dify's apps return in OpenAI-compatible formats?

Dify's API is stateful (controlling conversations via conversation_id), whereas OpenAI's stateless API must carry the full context each time. With the introduction of Endpoints and reverse calls, these functionalities are now plugins. By developing plugins that call Dify's LLM, we can meet the need to transform models into OpenAI format.

### Implementation

Set up an Endpoint group with model-selector settings for LLM and text_embedding. The endpoint receives OpenAI-format requests, transforms messages to Dify's prompt format, invokes the model via `self.session.model.llm.invoke()`, and returns responses in OpenAI-compatible format (both streaming and non-streaming).

## Asynchronous Event Trigger

The community has frequently requested workflows based on event triggers, especially for asynchronous events. With Endpoints, this can be achieved by splitting into two workflows: the first initiates the task and exits, the second receives the Webhook signal via Endpoint to continue. For example, posting AI-generated content for review, with user acceptance triggering an event that returns to Dify to complete publishing. Direct event-trigger capabilities for workflows will be introduced in coming months.

## Runtime Architecture

The SaaS version was designed with a serverless architecture that can scale elastically based on usage. AWS Lambda was chosen as the solution, as AWS supports Dify's existing SaaS business, and Dify communicates with Lambda over the network.
