---
source_id: "038"
title: "From Basic to Expert: Mastering the New Prompt Orchestration in Dify.AI"
url: "https://dify.ai/blog/mastering-new-prompt-orchestration-in-dify-ai"
type: "blog"
scraped_at: "2026-03-27"
keywords: ["Dify prompt orchestration", "Dify prompt engineering", "expert mode", "basic mode"]
content_length: 3850
---

Since its inception, Dify.AI has been on a quest to offer developers a more flexible and higher degree of control over prompt orchestration. To achieve this, they've unveiled a new orchestration mode. By simply switching from 'Basic Mode' to 'Expert Mode' on the prompt orchestration page, you embark on a fresh journey of prompt orchestration.

Discover New Ways to Explore Expert Mode in Prompt Orchestration

Mode Overview

Expert Mode is designed for professional developers and prompt engineers, providing a highly flexible customized orchestration mode. This mode assists in crafting effective prompts for robust and reliable interaction with LLMs or datasets.

From Basic to Expert

Basic Mode allows users to easily configure and create basic applications, while Expert Mode grants you more control and customization options. In Expert Mode, you are free to edit prompts including Context, User Input, Conversation History, examples, and other prompt elements, thereby guiding the model to achieve desired output results. Whether it's a conversational application or a text generation application, Expert Mode offers a plethora of options and tools to help you design more complex prompt orchestration.

Basic Mode was designed to lower the entry barrier for users to create AI applications by encapsulating some prompts, which to some extent, limits the autonomy in orchestration. If you've orchestrated prompts in 'Basic Mode' and then switch to 'Expert Mode' after uploading datasets, you can see the complete prompts encapsulated in Basic Mode, and at this point, you are free to modify any part of it. This enhances the autonomy in orchestration, allowing the LLM to output in an ideal state, and swiftly tuning the AI application to achieve optimal effects.

Functional Configuration in Expert Mode

In Expert Mode, you have the freedom to customize prompts. If you choose the CHAT model, you can write prompts for three kinds of message types: SYSTEM / USER / ASSISTANT. If you opt for the COMPLETE model, you can flexibly adjust the blocks in prompts like Context, Conversation History, Query, and Variables to make the application more in line with requirements, whereas in CHAT model, you can only adjust Context and Variables.

In the case of selecting the CHAT model, you can write prompts for the three aforementioned message types (SYSTEM / USER / ASSISTANT). By orchestrating USER and ASSISTANT interaction information in a modular manner, you can guide the model to achieve expected output.

Taking an application that helps users generate multiple QA pairs from text as an example, by providing multiple sets of USER and ASSISTANT interaction examples, you can provide clear guidance to the model, ensuring it strictly adheres to SYSTEM prompt constraints during the answering process. It's akin to setting a template, allowing the model to output results in a fixed format.

You can easily switch between CHAT and COMPLETE models to find the best application scenario. During the detailed prompt debugging process, the 'Log View' feature allows you to delve into the entire process from input to output, locating the issues. Whether it's model parsing errors or prompt quality issues, they can be discovered and adjusted in time, thereby optimizing application performance and ensuring the quality of output.

Coming Soon features mentioned: New Content Review feature (supports filtering of sensitive words in user input and model output), and External Tool API Calls (prompt orchestration now supports external tool API calls, allowing the insertion of API query results into prompts).
