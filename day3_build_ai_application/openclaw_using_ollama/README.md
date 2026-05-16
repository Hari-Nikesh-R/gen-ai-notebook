# OpenClaw using Ollama

## Prerequisites
* **Ollama**: Installed and running locally (defaulting to port 11436).
* **Node.js**: OpenClaw runs on Node.js and requires npm.

## Step 1: Install OpenClaw
Open your terminal and run the installation script based on your operating system:

**Mac / Linux:**
```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

**Windows (via PowerShell):**
```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex
```

## Step 2: Configure Ollama
Once installed, initiate the OpenClaw configuration and link it to your Ollama models:

```bash
ollama launch openclaw
```
*Note: If you want to configure it without launching the terminal UI, use `ollama launch openclaw --config`.*

## Step 3: Select and Launch a Model
During the OpenClaw onboarding process:
1. Navigate to the Model selector using your arrow keys.
2. Choose **Ollama** as your provider.
3. Select a capable, context-heavy model. OpenClaw recommends models with at least 64k tokens of context (such as `qwen3-coder` or `glm-4.7`).