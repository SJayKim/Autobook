---
source_id: "026"
title: "Manage Document Metadata - Dify Docs"
url: "https://docs.dify.ai/en/use-dify/knowledge/metadata"
type: "documentation"
scraped_at: "2026-03-27"
keywords: ["Dify metadata filtering", "Dify knowledge base"]
content_length: 5920
---

## What is Metadata?

### Overview

Metadata is information that describes your data - essentially "data about data". Just as a book has a table of contents to help you understand its structure, metadata provides context about your data's content, origin, purpose, etc., making it easier for you to find and manage information in your knowledge base.

### Core Concepts

- **Field**: The label of a metadata field (e.g., "author", "language").
- **Value**: The information stored in a metadata field (e.g., "Jack", "English").
- **Value Count**: The number of values contained in a metadata field, including duplicates (e.g., "3").
- **Value Type**: The type of value a field can contain. Dify supports three value types:
  - String: For text-based information
  - Number: For numerical data
  - Time: For dates/timestamps

## How to Manage Metadata

### Manage Metadata Fields in the Knowledge Base

You can create, modify, and delete metadata fields in the knowledge base. Any changes you make to metadata fields here affect your knowledge base globally.

**Built-in vs Custom Metadata**

| | Built-in Metadata | Custom Metadata |
| --- | --- | --- |
| Location | Lower section of the Metadata panel | Upper section of the Metadata panel |
| Activation | Disabled by default; requires manual activation | Add as needed |
| Generation | System automatically extracts and generates field values | User-defined and manually added |
| Editing | Fields and values cannot be modified once generated | Fields and values can be edited or deleted |
| Scope | Applies to all existing and new documents when enabled | Stored in metadata list; requires manual assignment to documents |
| Fields | System-defined fields include: document_name (string), uploader (string), upload_date (time), last_update_date (time), source (string) | No default fields; all fields must be manually created |
| Value Types | String, Number, Time | String, Number, Time |

**Create New Metadata Fields**:
1. Click +Add Metadata to open the New Metadata dialog.
2. Choose the value type.
3. Name the field. Naming rules: Use lowercase letters, numbers, and underscores only.
4. Click Save to apply changes.

**Edit Metadata Fields**: Click the edit icon next to a field to rename it. Note: You can only modify the field name, not the value type. Field changes update across all related documents.

**Delete Metadata Fields**: Click the delete icon. Note: Deleting a field deletes it and all its values from all documents.

### Edit Metadata

**Bulk Edit Metadata in the Metadata Editor**:
1. In the knowledge base, select documents using the checkboxes.
2. Click Metadata in the bottom action bar to open the Metadata Editor.
3. Click +Add Metadata to add existing fields or create new ones.
4. Enter values for fields. The date picker is available for time-type fields.
5. Click Save to apply changes.

**Set Update Scope**: Use "Apply to All Documents" to control changes:
- Unchecked (Default): Updates only documents that already have the field.
- Checked: Adds or updates fields across all selected documents.

**Edit Metadata on the Document Details Page**:
1. On the document details page, click "Start labeling" to begin editing.
2. Click +Add Metadata to create new fields or add existing ones.
3. Enter values and click Save.

### How to Filter Documents with Metadata

See Metadata Filtering in Integrate Knowledge Base within Application documentation.

### FAQ

**What can I do with metadata?**
- Find information faster with smart filtering.
- Control access to sensitive content.
- Organize data more effectively.
- Automate workflows based on metadata rules.

**How do different delete options work?**

| Action | Impact | Outcome |
| --- | --- | --- |
| Delete field in the Metadata Panel | Global - affects all documents | Field and all values permanently deleted from the knowledge base |
| Delete field in the Metadata Editor | Selected documents only | Field deleted from selected documents; remains in the knowledge base |
| Delete field on the document detail page | Current document only | Field deleted from current document; remains in the knowledge base |
