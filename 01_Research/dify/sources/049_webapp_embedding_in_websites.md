---
source_id: "049"
title: "Embedding Your Web App - Dify Docs"
url: "https://docs.dify.ai/en/use-dify/publish/webapp/embedding-in-websites"
type: "documentation"
scraped_at: "2026-03-27"
keywords: ["Dify application publishing", "Dify web app embed", "Dify iframe"]
content_length: 5420
---

# Embedding Your Web App - Dify Docs

Your published web app can be embedded directly into any website. This isn't a separate publishing method -- it's how you deploy the same web app you've already created, just presented within your existing website instead of as a standalone page.

## How Web App Embedding Works

When you publish an app in Dify, you get a web app URL. You can share this URL directly, or embed the same app into your website using these methods:

- **Chat Bubble Widget**: Your web app as a floating button -- visitors click to open the full interface
- **Iframe Integration**: Your web app embedded directly in page content -- always visible and ready
- **JavaScript Control**: Advanced embedding with custom styling and behavior control
- **Responsive Design**: Same web app adapts automatically to any presentation format

All embedding methods use your published web app. Changes to your app configuration automatically apply everywhere it's embedded.

## Chat Bubble Widget

The chat bubble presents your web app as a floating button. Visitors click it to open your app in an overlay -- keeping them on your page while accessing your AI features.

### Configuration Options

The chat bubble can be customized through the `difyChatbotConfig` object:

```javascript
window.difyChatbotConfig = {
    // Required: Your app's token from Dify
    token: 'YOUR_TOKEN',

    // Optional: Environment settings
    isDev: false,
    baseUrl: 'https://udify.app',

    // Optional: Visual customization
    containerProps: {
        style: { right: '20px', bottom: '20px' },
        className: 'custom-chat-button'
    },

    // Optional: Interactive behavior
    draggable: false,
    dragAxis: 'both',

    // Optional: Pre-fill user context
    inputs: { name: "John Doe", department: "Support" },

    // Optional: System variables for tracking
    systemVariables: { user_id: 'USER_123', conversation_id: 'CONV_456' },

    // Optional: User profile information
    userVariables: { avatar_url: 'https://example.com/avatar.jpg', name: 'John Doe' }
}
```

Steps to embed:
1. Get your embed token: In your Dify app, go to Publish > Embed to find your unique token.
2. Add the script: Include the configuration and Dify's embed script in your website's HTML.
3. Customize appearance: Adjust the containerProps to match your website's design.
4. Test functionality: Open your website and try the chat button.

## Iframe Integration

Embed your web app directly into your page content:

```html
<iframe
  src="https://udify.app/chatbot/YOUR_APP_TOKEN"
  width="100%"
  height="600"
  frameborder="0">
</iframe>
```

### Why Use Iframe Embedding

- **Always visible** - Your web app is immediately accessible, not hidden behind a button
- **Full functionality** - Everything from your web app works identically in the iframe
- **Page integration** - Appears as native content, not an overlay
- **Simple setup** - Just HTML, no JavaScript configuration needed

Responsive Design example:

```html
<div style="position: relative; width: 100%; height: 0; padding-bottom: 75%;">
  <iframe
    src="https://udify.app/chatbot/YOUR_APP_TOKEN"
    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
    frameborder="0">
  </iframe>
</div>
```

## Choosing Your Embedding Method

- **Customer Support Apps**: Chat bubble works best -- stays out of the way until needed.
- **Form & Workflow Apps**: Iframe embed for dedicated pages where the app is the main content.
- **Product Demonstrations**: Iframe embed on landing pages for instant try-out.
- **Multi-page Integration**: Chat bubble when you want the same app accessible across your entire site.

## CSS Customization Variables

The following CSS variables are supported for the chat bubble button:

- `--dify-chatbot-bubble-button-bottom` (default: 1rem)
- `--dify-chatbot-bubble-button-right` (default: 1rem)
- `--dify-chatbot-bubble-button-left` (default: unset)
- `--dify-chatbot-bubble-button-top` (default: unset)
- `--dify-chatbot-bubble-button-bg-color` (default: #155EEF)
- `--dify-chatbot-bubble-button-width` (default: 50px)
- `--dify-chatbot-bubble-button-height` (default: 50px)
- `--dify-chatbot-bubble-button-border-radius` (default: 25px)
- `--dify-chatbot-bubble-button-box-shadow` (default: rgba(0, 0, 0, 0.2) 0px 4px 8px 0px)
- `--dify-chatbot-bubble-button-hover-transform` (default: scale(1.1))

## Input Passing

Four types of inputs are supported: text-input, paragraph, number, and options. When using embed.js, each input value is compressed using GZIP and encoded in base64 before being appended to the URL.

Your web app must be published before embedding. If you update your app configuration, republish to see changes in embedded versions.
