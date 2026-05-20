# Training LLMs the Easy Way with Unsloth

When it comes to training a Large Language Model (LLM) on a custom dataset, you no longer need to write complex Python code from scratch. Instead, you can utilize the Unsloth Studio GUI to train your models seamlessly. 

This approach provides a user-friendly alternative to writing training scripts manually or using environments like Google Colab. All you need to learn is how to navigate and use the Unsloth Studio interface.

## 1. Install Unsloth Studio

For **Windows** users, you can install Unsloth Studio using PowerShell. For more information, please refer to the [official Quickstart documentation](https://unsloth.ai/docs/new/studio#quickstart).

Open **Windows PowerShell** and run:

```bash
irm https://unsloth.ai/install.ps1 | iex
```

After installation, start the studio by running the following command:

```bash
unsloth studio -H 0.0.0.0 -p 8888
```

## 2. Typical Workflow

Here is a standard workflow to get you started with Unsloth Studio:

1. **Launch Studio** by following the instructions at [Unsloth Installation](https://unsloth.ai/docs/new/studio/install).
2. **Load a model** from your local files or through a supported integration.
3. **Import training data** from PDFs, CSVs, or JSONL files, or build a dataset from scratch.
4. **Clean, refine, and expand** your dataset using [Data Recipes](https://unsloth.ai/docs/new/studio/data-recipe).
5. **Start training** using recommended presets or by customizing the configuration yourself.
6. **Chat with the trained model** and compare its outputs against the base model.
7. **[Save or export](https://unsloth.ai/docs/new/studio#export-save-models)** the model locally to use with your existing tech stack.

## 3. Video Tutorials

If you prefer visual learning, Unsloth provides official video tutorials demonstrating the process:
- [Unsloth Studio Video Tutorials](https://unsloth.ai/docs/new/studio#video-tutorials)

In this module, I will guide you through training a model and using it within Unsloth Studio. Alternatively, we can achieve similar results using tools like Ollama.
