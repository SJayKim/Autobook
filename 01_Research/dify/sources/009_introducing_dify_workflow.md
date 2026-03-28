---
source_id: "009"
title: "Introducing Dify Workflow"
url: "https://dify.ai/blog/dify-ai-workflow"
type: "blog"
scraped_at: "2026-03-27"
keywords: ["Dify workflow", "Dify workflow nodes", "Dify chatflow"]
content_length: 3842
---

# Introducing Dify Workflow

Hi, Gu from Dify here. I couldn't be more excited to share with you our latest feature: Workflow.

We've all seen the huge potential of LLMs in the past year. But as many of you have experienced firsthand, harnessing that potential for robust, production-ready solutions comes with its own set of challenges. Workflow is our answer to that challenge -- it is designed to bridge the gap where single-prompt LLMs falter: generating predictable outputs with multi-step logic.

Workflow is currently accessible as a standalone app type. It can also be activated in 'Chatbot' apps for building complex conversation flows (Chatflow). We can't wait for you to start experimenting with it now.

Chatflow is set to overtake "expert mode" in current Chatbot apps. You may choose to keep editing your existing apps in "expert mode", or transform them into workflows.

## Drag, Drop, Deploy

The heart of Workflow is an intuitive, drag-and-drop interface. You build your workflow by connecting different nodes on an infinite canvas. Some nodes we think are central include:

- **LLM:** Encapsulate the power of Large Language Models within a node, with defined inputs and outputs.
- **Tools:** Utilize built-in and custom tools to extend what your workflow can achieve.
- **Question Classifier:** Automatically categorize user inputs to route conversations and processes, powered by LLM under the hood.
- **Knowledge Retrieval:** Equip your LLMs with external context from your existing knowledge bases.
- **Code:** Execute custom Python or Node.js code.
- **If/Else Block:** Define conditional logic to create branched workflows.

But this is just the beginning. We've designed Workflow to be extensible, allowing us to continually expand the types of nodes available. As we learn more about the needs and use cases of our community, we'll be introducing new nodes to support an even wider range of applications.

## Flexible Configuration

One of the key strengths of Workflow is its flexibility. Every node is configurable, allowing you to customize your workflow to your exact needs. You can define inputs and outputs for each node, ensuring that data flows seamlessly through your workflow.

For more advanced data manipulation, Workflows offers specialized node types. We designed 'Template' and 'Variable Assigner' nodes to let you reshape and reassign variables between nodes, enabling complex data transformations. The 'HTTP Request' node allows you to integrate with external services by making HTTP requests directly from your workflow. And for maximum control, the 'Code' node lets you inject your own Python or NodeJS code, so that you can implement custom logic and manipulate data in powerful ways.

## Seamless Integration with Dify Ecosystem

Workflow fits right into the Dify ecosystem. It offers native support for all built-in and custom tools, ensuring that you can leverage the full power of the Dify platform in your workflows.

Just like every other Dify feature, Workflow comes API-ready, allowing you to easily integrate your workflows into your existing applications and systems. And with built-in observability features, you can capture key usage data to monitor and optimize your workflows over time.

## Robust Debugging and Testing

We understand that building reliable LLM applications can be challenging, that's why we've integrated robust debugging and testing utilities directly into Workflow. Our tool allows you to easily test your workflows end-to-end, making sure your application behaves as expected from start to finish. You can also test individual nodes in isolation, enabling you to pinpoint issues quickly. All test runs are automatically logged, providing you with a detailed record of your workflow's behavior. If an issue arises, you can trace back through your test history, identify the problem, and take corrective action. This level of traceability is crucial when working with complex systems like LLM applications.

## Portability and Interoperability with DSL

One of the coolest features of Workflow is its support for Domain Specific Language (DSL). With DSL, you can easily export your workflows and import them into other workspaces. This provides you with a level of portability and interoperability that's unmatched in the industry. No more vendor lock-in -- you have the freedom to move your workflows between systems and customize them to your heart's content. This feature opens up a world of possibilities for collaboration, sharing, and building upon the work of others in the community.

## Forge Ahead

We're excited to see Workflow finally released into this world. Dify's mission has always been clear: to equip innovators like you with powerful tools to build with AI more effectively. Workflow is a giant leap towards this goal. We hope it can be your gateway to turning the unpredictable into the predictable, and push the envelope for deploying LLMs in the real world.
