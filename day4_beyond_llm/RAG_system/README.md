# What problem does the LLM has?

Traditional LLMs:
- Have fixed knowledge
- Cannot access latest company data
- May hallucinate answers
- Cannot perform actions independently
- Cannot remember long workflows properly

Example:
If you ask:
> “Summarize my company policy PDF”

A normal LLM:
- Has never seen your PDF
- May generate fake answers

## Why RAG Is Needed

RAG helps AI:
- Read external documents
- Retrieve relevant information
- Generate grounded responses

Instead of:
- “Guessing”

It:
- “Searches + Answers”

## Why Agentic AI Is Needed

Modern applications require:
- Planning
- Decision making
- Multi-step execution
- Tool usage
- Memory handling

Example:
> “Read emails → extract invoices → update database → notify user”

This requires:
- Multiple steps
- Decision logic
- Tool integration

That is where agents come in.

# What Problem it Solves

## RAG Solves

| Problem | Solution |
| :--- | :--- |
| Hallucination | Uses actual documents |
| Outdated knowledge | Retrieves latest data |
| Large enterprise documents | Semantic search |
| Searching PDFs manually | Intelligent retrieval |

## Agentic AI Solves

| Problem | Solution |
| :--- | :--- |
| Manual workflows | Automation |
| Multi-step reasoning | Planning |
| Tool integration complexity | Agent orchestration |
| Context switching | Memory systems |
| Repetitive engineering tasks | Autonomous execution |

# 3. How It Is Implemented

## A. RAG Architecture

### Flow
```
User Query
     ↓
Embedding Model
     ↓
Vector Search (FAISS)
     ↓
Relevant Chunks Retrieved
     ↓
LLM Generates Final Answer
```

### Step-by-Step Implementation

#### Step 1 — Load Documents
*Example:*
- PDFs
- DOCX
- Database records
- Company knowledge base

#### Step 2 — Chunking
Large documents are split into smaller pieces.
*Example:*
- Chunk 1 → Introduction
- Chunk 2 → Installation
- Chunk 3 → Pricing

#### Step 3 — Generate Embeddings
*Text → Vector representation*

Embeddings capture:
- Meaning
- Semantic similarity

#### Step 4 — Store in FAISS
FAISS stores vectors efficiently for similarity search.

#### Step 5 — Query Retrieval
- User query is converted to embedding.
- Top similar chunks are retrieved.

#### Step 6 — LLM Generation
- Retrieved chunks + user query are sent to LLM.
- LLM generates grounded response.

## B. Agentic AI Architecture

### Core Components

#### 1. Planning
Breaks tasks into smaller steps.
*Example:*
- **Goal:** Create project report
- **Plan:**
  1. Read Jira tickets
  2. Summarize progress
  3. Generate report
  4. Send email

#### 2. Memory
*Types:*
- Short-term memory
- Long-term memory
- Conversation memory

#### 3. Tools
*Agents can use:*
- APIs
- Databases
- Browsers
- Code interpreters
- Email services

#### 4. Execution Engine
Runs tasks step-by-step.

### Typical Agent Flow
```
User Request
    ↓
Planner
    ↓
Task Breakdown
    ↓
Tool Selection
    ↓
Execution
    ↓
Memory Update
    ↓
Final Response
```

# 4. Practical Hands-On Example (Real Application)

## Project 1 — PDF-Based Company Assistant

### Real Use Case
*A company wants:*
- Internal policy chatbot
- HR FAQ assistant
- Technical documentation assistant

### Features
*Users can:*
- Upload PDFs
- Ask questions
- Get contextual answers

### Tech Stack
| Component | Technology |
| :--- | :--- |
| Backend | Python FastAPI |
| Vector DB | FAISS |
| Embeddings | Sentence Transformers |
| LLM | OpenAI / Ollama |
| Frontend | React / Flutter |

### Hands-On Flow

#### Step 1
Upload PDF
*Example:*
- Employee_Handbook.pdf

#### Step 2
Extract text
*Libraries:*
- PyPDF2
- pdfplumber

#### Step 3
Chunk text
*Example:*
- chunk_size = 500
- overlap = 50

#### Step 4
Generate embeddings
*Example:*
- sentence-transformers

#### Step 5
Store in FAISS

#### Step 6
Query chatbot
*Example:*
> "What is the leave policy?"

#### Step 7
Retrieve top chunks

#### Step 8
Generate final response

## Project 2 — Multi-Step Automation Agent

### Real Engineering Example
*Build an AI Dev Assistant:*

#### User Request
> “Generate Spring Boot APIs from requirement document”

### Agent Workflow
```
Requirement PDF
      ↓
Requirement Extraction Agent
      ↓
API Design Agent
      ↓
Code Generation Agent
      ↓
Testing Agent
      ↓
Documentation Agent
```

### Technologies
| Area | Tools |
| :--- | :--- |
| Agent Framework | LangGraph / CrewAI |
| LLM | GPT / Claude |
| Memory | Redis |
| Tools | GitHub API, File System |
| Backend | Python |

# 5. When To Use and When NOT To Use

## Use RAG When

#### ✅ You have:
- PDFs
- Enterprise documents
- Knowledge bases
- Frequently updated information
- Large datasets

#### ✅ Examples:
- HR chatbot
- Legal assistant
- Technical support AI
- Internal enterprise search

## Do NOT Use RAG When

#### ❌ Small static information
*Example:*
> "What is Java?"
- No retrieval needed.

#### ❌ Data changes very rarely
- Simple prompt engineering is enough.

#### ❌ Very low latency systems
RAG adds:
- Retrieval time
- Embedding search overhead

## Use Agentic AI When

#### ✅ Multi-step workflows exist
*Examples:*
- DevOps automation
- AI coding assistants
- Email automation
- Research assistants
- Autonomous workflows

#### ✅ Decision-making is required
*Example:*
> If invoice amount > 1 lakh
> → send approval request
> Else
> → auto approve

## Do NOT Use Agentic AI When

#### ❌ Simple single-step tasks
*Example:*
- Translate text
- Summarize paragraph

#### ❌ Deterministic workflows
- Traditional backend logic is better.

#### ❌ High-risk critical systems
Agents may:
- Hallucinate
- Misuse tools
- Make unexpected decisions

*Examples:*
- Banking transaction approval
- Medical diagnosis
- Critical infrastructure control

# Real-World Applications

## RAG Applications
- ChatGPT with company knowledge
- Internal enterprise search
- AI-powered LMS
- AI legal assistants
- Research paper assistants

## Agentic AI Applications
- AI software engineers
- Autonomous testing systems
- AI research assistants
- Customer support automation
- Multi-agent coding systems
