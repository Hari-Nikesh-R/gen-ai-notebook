# Google Colab to Local Ollama Workflow

Google Colab → Train Gemma → Export Model → Download Model → Local Machine → Import into Ollama

*This WILL work.*

### Setup Google Colab

**Open:**
Google Colab

**Step 1 — Enable GPU**
In Colab:
`Runtime` → `Change Runtime Type` → `GPU`

Prefer:
* T4 GPU
* A100 if available

**Step 2 — Verify GPU**
Run:
```bash
!nvidia-smi
```
If GPU appears: you are ready.

###  Install Libraries

**Step 3 — Install Unsloth**
Run:
```bash
!pip install unsloth
!pip install --no-deps transformers accelerate peft trl bitsandbytes
```

**Step 4 — Restart Runtime**
VERY IMPORTANT.
After install:
`Runtime` → `Restart Session`

### Upload Dataset

**Step 5 — Create Dataset**
Create locally:
`dataset.jsonl`

Example:
```json
{"instruction":"Generate question paper","input":"Unit 1: Classes, Objects\nCO1: Understand OOP","output":"Part A:\n1. Define class [CO1]\n\nPart B:\n1. Explain inheritance [CO1]"}
```

**Step 6 — Upload Dataset**
In Colab:
```python
from google.colab import files
uploaded = files.upload()
```
Upload: `dataset.jsonl`

### Why JSONL?

`dataset.jsonl` is used because LLM training frameworks are designed to process **one training example per line**.

That is exactly what **JSONL = JSON Lines** means.

#### Difference Between JSON and JSONL

**Normal JSON**
```json
[
  {
    "instruction": "Generate question paper",
    "input": "Java OOP",
    "output": "Define class"
  },
  {
    "instruction": "Generate question paper",
    "input": "DBMS",
    "output": "Explain normalization"
  }
]
```
This is:
* one BIG JSON array
* entire file loaded together

**JSONL Format**
```jsonl
{"instruction":"Generate question paper","input":"Java OOP","output":"Define class"}
{"instruction":"Generate question paper","input":"DBMS","output":"Explain normalization"}
```

Each line:
* is an independent JSON object
* represents one training sample

#### Why LLM Training Uses JSONL

Because training pipelines process data like:
* Sample 1
* Sample 2
* Sample 3
* ...

one by one.

JSONL is PERFECT for:
* streaming
* batching
* memory efficiency
* parallel processing

### Training

**Step 7 — Load Model**
Run:
```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/gemma-2b",
    max_seq_length = 2048,
    load_in_4bit = True,
)
```
This downloads Gemma directly from Hugging Face. No Ollama involved.

**Step 8 — Add LoRA**
Run:
```python
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = [
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
)
```

**Step 9 — Load Dataset**
Run:
```python
from datasets import load_dataset

dataset = load_dataset(
    "json",
    data_files = "dataset.jsonl",
    split = "train"
)
```

**Step 10 — Format Dataset**
Run:
```python
def formatting_prompts_func(example):
    text = f"""
### Instruction:
{example['instruction']}

### Input:
{example['input']}

### Response:
{example['output']}
"""
    return { "text": text }

dataset = dataset.map(formatting_prompts_func)
```

**Step 11 — Configure Trainer**
Run:
```python
from trl import SFTTrainer
from transformers import TrainingArguments

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = 2048,

    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 60,
        learning_rate = 2e-4,
        logging_steps = 1,
        output_dir = "outputs",
        optim = "adamw_8bit",
        fp16 = True,
    ),
)
```

**Step 12 — Train**
Run:
```python
trainer.train()
```
Now actual fine-tuning starts.

### Save Model

**Step 13 — Save Model**
Run:
```python
model.save_pretrained("question-generator-model")
tokenizer.save_pretrained("question-generator-model")
```

### Download Model

**Step 14 — Zip Model**
Run:
```bash
!zip -r question-generator-model.zip question-generator-model
```

**Step 15 — Download**
Run:
```python
from google.colab import files
files.download("question-generator-model.zip")
```

Now you have:
* trained Hugging Face model

**IMPORTANT UNDERSTANDING**
At this stage:
you DO NOT yet have:
* Ollama model
* GGUF model

You have:
* Hugging Face fine-tuned model

### Convert To GGUF

Now move to your **LOCAL MACHINE**.

**Step 16 — Install llama.cpp**
Clone:
`llama.cpp` Repository
https://github.com/ggml-org/llama.cpp

**Step 17 — Extract Model ZIP**
You should now have:
`question-generator-model/`

**Step 18 — Convert To GGUF**
Inside `llama.cpp`:
<br>
Install dependecies then, 
```bash
pip install unsloth
pip install --no-deps transformers accelerate peft trl bitsandbytes
```
```bash
python convert_hf_to_gguf.py \
    ../question-generator-model \
    --outfile question-generator.gguf \
    --outtype q8_0
```
This creates:
`question-generator.gguf`

### Import Into Ollama

**Step 19 — Create Modelfile**
Create:
`Modelfile`

Content:
```dockerfile
FROM ./question-generator.gguf

PARAMETER temperature 0.7
```

**Step 20 — Create Ollama Model**
Run:
```bash
ollama create question-generator -f Modelfile
```

**Step 21 — Run Your Model**
```bash
ollama run question-generator
```

Test:
```
Generate question paper for Java OOP syllabus with CO mapping
```

---

Colab GPU → Fine-Tuning → Export HF Model → GGUF Conversion → Ollama Import → Production Usage