# Guide de Fine-Tuning - Doctis AI

**Projet:** Doctis AI
**Auteurs:** Adam Beloucif & Amina Medjdoub
**Module:** IA Générative & Data Engineering - EFREI 2025

---

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Prérequis](#prérequis)
3. [Étape 1 : Préparation des données](#étape-1--préparation-des-données)
4. [Étape 2 : Fine-tuning avec QLoRA](#étape-2--fine-tuning-avec-qlora)
5. [Étape 3 : Conversion en GGUF](#étape-3--conversion-en-gguf)
6. [Étape 4 : Déploiement sur Render](#étape-4--déploiement-sur-render)

---

## Vue d'ensemble

Ce guide explique comment fine-tuner un Small Language Model (SLM) comme **Phi-3-mini** ou **TinyLlama** sur un dataset médical, puis le convertir au format **GGUF** pour une exécution CPU-only sur Render.

### Pourquoi le format GGUF ?

- **CPU-only** : Render ne fournit pas de GPU
- **Quantification** : Réduit la taille du modèle (4-8 Go → 2-4 Go)
- **Optimisé** : llama.cpp offre d'excellentes performances sur CPU

---

## Prérequis

- Compte Google Colab (GPU gratuit T4)
- Compte Hugging Face (pour télécharger les modèles)
- ~10 Go d'espace disque (temporaire sur Colab)

---

## Étape 1 : Préparation des données

### Format du dataset

Le dataset doit être au format JSONL avec la structure suivante :

```json
{"instruction": "Quels sont les symptômes de l'appendicite ?", "input": "", "output": "L'appendicite se manifeste par une douleur abdominale intense localisée en bas à droite..."}
{"instruction": "J'ai mal à la tête et je vois des points lumineux", "input": "", "output": "Vos symptômes évoquent une possible migraine avec aura..."}
```

### Datasets médicaux recommandés

- **ChatDoctor** : `lavita/ChatDoctor-HealthCareMagic-100k`
- **MedQuAD** : Questions-réponses médicales
- **Custom** : Créez votre propre dataset à partir de sources fiables

---

## Étape 2 : Fine-tuning avec QLoRA

### Notebook Google Colab

Créez un nouveau notebook Colab et exécutez les cellules suivantes :

```python
# =============================================================================
# Projet: Doctis AI
# Auteurs: Adam Beloucif & Amina Medjdoub
# Description: Fine-tuning d'un SLM pour le diagnostic médical
# =============================================================================

# Cellule 1 : Installation des dépendances
!pip install -q transformers datasets accelerate peft bitsandbytes trl
!pip install -q huggingface_hub

# Connexion à Hugging Face
from huggingface_hub import login
login(token="hf_VOTRE_TOKEN")  # Remplacez par votre token
```

```python
# Cellule 2 : Configuration du modèle
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from datasets import load_dataset

# Configuration
MODEL_NAME = "microsoft/Phi-3-mini-4k-instruct"  # ou "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
OUTPUT_DIR = "./doctis-ai-finetuned"

# Configuration de la quantification 4-bit
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

# Chargement du modèle
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

print(f"✅ Modèle {MODEL_NAME} chargé avec succès")
```

```python
# Cellule 3 : Configuration LoRA
lora_config = LoraConfig(
    r=16,                      # Rang LoRA
    lora_alpha=32,             # Alpha scaling
    target_modules=[           # Modules à fine-tuner
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = prepare_model_for_kbit_training(model)
model = get_peft_model(model, lora_config)

# Affiche le nombre de paramètres entraînables
model.print_trainable_parameters()
```

```python
# Cellule 4 : Chargement du dataset
# Option 1 : Dataset ChatDoctor
dataset = load_dataset("lavita/ChatDoctor-HealthCareMagic-100k", split="train[:5000]")

# Option 2 : Dataset personnalisé
# dataset = load_dataset("json", data_files="votre_dataset.jsonl", split="train")

def format_prompt(example):
    """Formate les exemples pour l'entraînement."""
    instruction = example.get("instruction", example.get("input", ""))
    response = example.get("output", example.get("response", ""))

    return {
        "text": f"""<|system|>
Tu es Doctis AI, un assistant médical bienveillant. Tu analyses les symptômes décrits et fournis des informations médicales claires et rassurantes.<|end|>
<|user|>
{instruction}<|end|>
<|assistant|>
{response}<|end|>"""
    }

dataset = dataset.map(format_prompt)
print(f"✅ Dataset chargé : {len(dataset)} exemples")
```

```python
# Cellule 5 : Configuration de l'entraînement
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    weight_decay=0.01,
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",
    logging_steps=25,
    save_steps=500,
    save_total_limit=2,
    fp16=True,
    optim="paged_adamw_8bit",
    report_to="none"
)

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    tokenizer=tokenizer,
    args=training_args,
    dataset_text_field="text",
    max_seq_length=512
)

print("✅ Trainer configuré, démarrage de l'entraînement...")
```

```python
# Cellule 6 : Lancement du fine-tuning
trainer.train()

# Sauvegarde du modèle
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print(f"✅ Modèle sauvegardé dans {OUTPUT_DIR}")
```

```python
# Cellule 7 : Fusion des poids LoRA (merge)
from peft import AutoPeftModelForCausalLM

# Recharge le modèle avec les adaptateurs LoRA
model = AutoPeftModelForCausalLM.from_pretrained(
    OUTPUT_DIR,
    device_map="auto",
    torch_dtype=torch.float16
)

# Fusionne les poids LoRA dans le modèle de base
merged_model = model.merge_and_unload()

# Sauvegarde du modèle fusionné
MERGED_DIR = "./doctis-ai-merged"
merged_model.save_pretrained(MERGED_DIR, safe_serialization=True)
tokenizer.save_pretrained(MERGED_DIR)

print(f"✅ Modèle fusionné sauvegardé dans {MERGED_DIR}")
```

---

## Étape 3 : Conversion en GGUF

### Installation de llama.cpp

```python
# Cellule 8 : Installation de llama.cpp
!git clone https://github.com/ggerganov/llama.cpp
%cd llama.cpp
!pip install -r requirements.txt
```

### Conversion au format GGUF

```python
# Cellule 9 : Conversion en GGUF
!python convert_hf_to_gguf.py ../doctis-ai-merged \
    --outfile ../doctis-ai.gguf \
    --outtype f16

print("✅ Conversion en GGUF (F16) terminée")
```

### Quantification (réduction de taille)

```python
# Cellule 10 : Quantification Q4_K_M (recommandée pour CPU)
!./llama-quantize ../doctis-ai.gguf ../doctis-ai-Q4_K_M.gguf Q4_K_M

# Autres options de quantification :
# Q8_0  : Meilleure qualité, plus grande taille (~4-5 Go)
# Q4_K_M: Bon équilibre qualité/taille (~2-3 Go) ← RECOMMANDÉ
# Q4_0  : Plus petit, qualité légèrement réduite (~2 Go)

print("✅ Quantification Q4_K_M terminée")
```

### Téléchargement du modèle

```python
# Cellule 11 : Téléchargement
from google.colab import files

# Télécharge le modèle quantifié
files.download("../doctis-ai-Q4_K_M.gguf")

print("✅ Modèle prêt pour le déploiement!")
```

---

## Étape 4 : Déploiement sur Render

### Structure des fichiers sur le serveur

```
backend/
├── models/
│   └── doctis-ai-Q4_K_M.gguf   # Votre modèle quantifié
├── data/
│   └── pathologies.json
├── main.py
└── requirements.txt
```

### Configuration dans main.py

Modifiez la variable `LLM_MODEL_PATH` dans `main.py` :

```python
LLM_MODEL_PATH: str = str(MODELS_DIR / "doctis-ai-Q4_K_M.gguf")
```

### Hébergement du modèle (recommandé)

Comme le fichier GGUF est volumineux (2-4 Go), hébergez-le sur :

1. **Hugging Face Hub** (gratuit, recommandé)
2. **Google Cloud Storage**
3. **AWS S3**

Puis téléchargez-le au démarrage de l'application :

```python
import os
import urllib.request

MODEL_URL = "https://huggingface.co/votre-user/doctis-ai-gguf/resolve/main/doctis-ai-Q4_K_M.gguf"
MODEL_PATH = "./models/doctis-ai-Q4_K_M.gguf"

if not os.path.exists(MODEL_PATH):
    print("⏳ Téléchargement du modèle...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("✅ Modèle téléchargé")
```

---

## Résumé des commandes clés

| Étape | Commande |
|-------|----------|
| Fine-tuning | `trainer.train()` |
| Fusion LoRA | `model.merge_and_unload()` |
| Conversion GGUF | `python convert_hf_to_gguf.py MODEL --outfile model.gguf` |
| Quantification | `./llama-quantize model.gguf model-Q4_K_M.gguf Q4_K_M` |

---

## Ressources

- [llama.cpp GitHub](https://github.com/ggerganov/llama.cpp)
- [PEFT Documentation](https://huggingface.co/docs/peft)
- [QLoRA Paper](https://arxiv.org/abs/2305.14314)
- [Phi-3 Model Card](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct)

---

**Projet réalisé par Adam Beloucif & Amina Medjdoub - EFREI 2025**
