import json
import random
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)


# ============================================================
# 1. CONFIGURATION
# ============================================================

SEED = 42

EMBEDDINGS_PATH = Path(
    "models/lumiguard_distress/embeddings/embeddings.pt"
)

OUTPUT_DIR = Path("models/lumiguard_distress")

MODEL_PATH = OUTPUT_DIR / "best_model.pt"
CLASSES_PATH = OUTPUT_DIR / "classes.json"
INFO_PATH = OUTPUT_DIR / "training_info.json"

INPUT_DIM = 768

BATCH_SIZE = 64
EPOCHS = 40
LEARNING_RATE = 0.001
WEIGHT_DECAY = 0.0001

VALIDATION_SIZE = 0.15
EARLY_STOPPING_PATIENCE = 7

# Probability threshold for predicting distress during evaluation.
# Tune this later using a separate validation set.
DISTRESS_THRESHOLD = 0.50


# ============================================================
# 2. REPRODUCIBILITY
# ============================================================

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("=" * 65)
print("LUMIGUARD - DISTRESS AUDIO CLASSIFIER TRAINING")
print("=" * 65)
print(f"Device: {DEVICE}")
print(f"Embeddings: {EMBEDDINGS_PATH.resolve()}")
print(f"Output directory: {OUTPUT_DIR.resolve()}")


# ============================================================
# 3. LOAD EMBEDDINGS AND LABELS
# ============================================================

if not EMBEDDINGS_PATH.exists():
    raise FileNotFoundError(
        f"\nEmbeddings file not found:\n{EMBEDDINGS_PATH.resolve()}\n"
        "Check the file path and run this script from the audio folder."
    )

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# weights_only=False is used because this file contains a
# dictionary with tensors. Only load a file you trust.
try:
    saved_data = torch.load(
        EMBEDDINGS_PATH,
        map_location="cpu",
        weights_only=False,
    )
except TypeError:
    # Compatibility with older PyTorch versions.
    saved_data = torch.load(
        EMBEDDINGS_PATH,
        map_location="cpu",
    )

if "embeddings" not in saved_data or "labels" not in saved_data:
    raise KeyError(
        "The embeddings file must contain 'embeddings' and 'labels'."
    )

X = torch.as_tensor(
    saved_data["embeddings"],
    dtype=torch.float32,
).contiguous()

y = torch.as_tensor(
    saved_data["labels"],
    dtype=torch.long,
).reshape(-1).contiguous()

print("\n--- Dataset checks ---")
print(f"Embedding shape: {tuple(X.shape)}")
print(f"Label shape: {tuple(y.shape)}")

if X.ndim != 2 or X.shape[1] != INPUT_DIM:
    raise ValueError(
        f"Expected embeddings with shape [N, {INPUT_DIM}], "
        f"but received {tuple(X.shape)}."
    )

if len(X) != len(y):
    raise ValueError(
        f"Number of embeddings ({len(X)}) does not match "
        f"number of labels ({len(y)})."
    )

if len(X) < 10:
    raise ValueError("Not enough samples to train the classifier.")

if not torch.isfinite(X).all():
    raise ValueError(
        "Embeddings contain NaN or infinite values. "
        "Fix these before training."
    )

unique_labels = set(y.unique().tolist())

if unique_labels != {0, 1}:
    raise ValueError(
        f"Expected both labels 0 and 1, but found {unique_labels}."
    )

normal_count = int((y == 0).sum().item())
distress_count = int((y == 1).sum().item())

print(f"Normal samples (0): {normal_count}")
print(f"Distress samples (1): {distress_count}")
print(f"Total samples: {len(y)}")

print("\nLabel meanings:")
print("0 = Normal audio")
print("1 = Distress audio")


# ============================================================
# 4. SPLIT INTO TRAINING AND VALIDATION DATA
# ============================================================

indices = np.arange(len(y))
labels_np = y.numpy()

train_indices, val_indices = train_test_split(
    indices,
    test_size=VALIDATION_SIZE,
    random_state=SEED,
    stratify=labels_np,
)

X_train = X[train_indices]
y_train = y[train_indices]

X_val = X[val_indices]
y_val = y[val_indices]

print("\n--- Data split ---")
print(f"Training samples: {len(X_train)}")
print(f"Validation samples: {len(X_val)}")

print(
    f"Training normal: {int((y_train == 0).sum())}, "
    f"distress: {int((y_train == 1).sum())}"
)
print(
    f"Validation normal: {int((y_val == 0).sum())}, "
    f"distress: {int((y_val == 1).sum())}"
)

train_dataset = TensorDataset(X_train, y_train)
val_dataset = TensorDataset(X_val, y_val)

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    drop_last=False,
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
)


# ============================================================
# 5. DEFINE THE CLASSIFIER
# ============================================================

class DistressClassifier(nn.Module):
    def __init__(self, input_dim=768):
        super().__init__()

        self.net = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.BatchNorm1d(256),
            nn.GELU(),
            nn.Dropout(0.30),

            nn.Linear(256, 128),
            nn.GELU(),
            nn.Dropout(0.20),

            nn.Linear(128, 2),
        )

    def forward(self, x):
        return self.net(x)


model = DistressClassifier(INPUT_DIM).to(DEVICE)

print("\n--- Model architecture ---")
print(model)


# ============================================================
# 6. HANDLE CLASS IMBALANCE
# ============================================================

train_normal_count = int((y_train == 0).sum().item())
train_distress_count = int((y_train == 1).sum().item())

if train_normal_count == 0 or train_distress_count == 0:
    raise ValueError(
        "Both classes must be present in the training split."
    )

# Inverse-frequency weights calculated using training data only.
total_train = train_normal_count + train_distress_count

class_weights = torch.tensor(
    [
        total_train / (2.0 * train_normal_count),
        total_train / (2.0 * train_distress_count),
    ],
    dtype=torch.float32,
    device=DEVICE,
)

criterion = nn.CrossEntropyLoss(weight=class_weights)

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=LEARNING_RATE,
    weight_decay=WEIGHT_DECAY,
)

print("\nClass weights:")
print(f"Normal: {class_weights[0].item():.4f}")
print(f"Distress: {class_weights[1].item():.4f}")


# ============================================================
# 7. VALIDATION FUNCTION
# ============================================================

def evaluate_model(model, loader):
    model.eval()

    total_loss = 0.0
    total_samples = 0

    all_labels = []
    all_probabilities = []

    with torch.no_grad():
        for batch_X, batch_y in loader:
            batch_X = batch_X.to(DEVICE)
            batch_y = batch_y.to(DEVICE)

            logits = model(batch_X)
            loss = criterion(logits, batch_y)

            probabilities = torch.softmax(logits, dim=1)[:, 1]

            total_loss += loss.item() * len(batch_y)
            total_samples += len(batch_y)

            all_labels.extend(batch_y.cpu().tolist())
            all_probabilities.extend(probabilities.cpu().tolist())

    average_loss = total_loss / max(total_samples, 1)

    actual = np.asarray(all_labels, dtype=np.int64)
    probabilities = np.asarray(
        all_probabilities,
        dtype=np.float64,
    )

    predicted = (
        probabilities >= DISTRESS_THRESHOLD
    ).astype(np.int64)

    accuracy = accuracy_score(actual, predicted)

    precision = precision_score(
        actual,
        predicted,
        pos_label=1,
        zero_division=0,
    )

    recall = recall_score(
        actual,
        predicted,
        pos_label=1,
        zero_division=0,
    )

    f1 = f1_score(
        actual,
        predicted,
        pos_label=1,
        zero_division=0,
    )

    return {
        "loss": average_loss,
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "actual": actual,
        "predicted": predicted,
        "probabilities": probabilities,
    }


# ============================================================
# 8. TRAINING LOOP WITH EARLY STOPPING
# ============================================================

best_val_loss = float("inf")
best_epoch = 0
epochs_without_improvement = 0

history = []

print("\n" + "=" * 65)
print("STARTING TRAINING")
print("=" * 65)

for epoch in range(1, EPOCHS + 1):

    model.train()

    running_loss = 0.0
    samples_seen = 0

    for batch_X, batch_y in train_loader:
        batch_X = batch_X.to(DEVICE)
        batch_y = batch_y.to(DEVICE)

        optimizer.zero_grad(set_to_none=True)

        logits = model(batch_X)
        loss = criterion(logits, batch_y)

        loss.backward()
        optimizer.step()

        running_loss += loss.item() * len(batch_y)
        samples_seen += len(batch_y)

    train_loss = running_loss / max(samples_seen, 1)

    metrics = evaluate_model(model, val_loader)

    epoch_info = {
        "epoch": epoch,
        "train_loss": float(train_loss),
        "validation_loss": float(metrics["loss"]),
        "validation_accuracy": metrics["accuracy"],
        "validation_precision": metrics["precision"],
        "validation_recall": metrics["recall"],
        "validation_f1": metrics["f1"],
    }

    history.append(epoch_info)

    print(
        f"Epoch [{epoch:02d}/{EPOCHS}] | "
        f"Train Loss: {train_loss:.4f} | "
        f"Val Loss: {metrics['loss']:.4f} | "
        f"Accuracy: {metrics['accuracy']:.4f} | "
        f"Precision: {metrics['precision']:.4f} | "
        f"Recall: {metrics['recall']:.4f} | "
        f"F1: {metrics['f1']:.4f}"
    )

    # Save the model with the lowest validation loss.
    if metrics["loss"] < best_val_loss:
        best_val_loss = metrics["loss"]
        best_epoch = epoch
        epochs_without_improvement = 0

        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "input_dim": INPUT_DIM,
                "classes": {
                    "normal": 0,
                    "distress": 1,
                },
                "architecture": "MLP_768_256_128_2",
                "distress_threshold": DISTRESS_THRESHOLD,
                "best_epoch": best_epoch,
                "best_validation_loss": best_val_loss,
                "seed": SEED,
            },
            MODEL_PATH,
        )

        print(f"  Saved best model: {MODEL_PATH}")

    else:
        epochs_without_improvement += 1

    if epochs_without_improvement >= EARLY_STOPPING_PATIENCE:
        print(
            f"\nEarly stopping: validation loss did not improve "
            f"for {EARLY_STOPPING_PATIENCE} consecutive epochs."
        )
        break


# ============================================================
# 9. LOAD THE BEST MODEL AND EVALUATE IT
# ============================================================

print("\n" + "=" * 65)
print("FINAL VALIDATION RESULTS")
print("=" * 65)

checkpoint = torch.load(
    MODEL_PATH,
    map_location=DEVICE,
    weights_only=False,
)

model.load_state_dict(checkpoint["model_state_dict"])

final_metrics = evaluate_model(model, val_loader)

actual = final_metrics["actual"]
predicted = final_metrics["predicted"]

print(f"Best epoch: {checkpoint['best_epoch']}")
print(f"Best validation loss: {checkpoint['best_validation_loss']:.4f}")
print(f"Accuracy:  {final_metrics['accuracy']:.4f}")
print(f"Precision: {final_metrics['precision']:.4f}")
print(f"Recall:    {final_metrics['recall']:.4f}")
print(f"F1-score:  {final_metrics['f1']:.4f}")

print("\nClassification report:")
print(
    classification_report(
        actual,
        predicted,
        labels=[0, 1],
        target_names=["Normal", "Distress"],
        zero_division=0,
    )
)

# Rows are actual labels; columns are predicted labels.
#                 Predicted Normal   Predicted Distress
# Actual Normal         TN                  FP
# Actual Distress       FN                  TP

cm = confusion_matrix(actual, predicted, labels=[0, 1])

tn, fp, fn, tp = cm.ravel()

print("Confusion matrix:")
print(cm)
print()
print(f"True Negatives  (normal correctly identified): {tn}")
print(f"False Positives (normal flagged as distress):  {fp}")
print(f"False Negatives (distress missed):             {fn}")
print(f"True Positives  (distress correctly detected): {tp}")


# ============================================================
# 10. SAVE CLASS NAMES AND TRAINING INFORMATION
# ============================================================

with open(CLASSES_PATH, "w", encoding="utf-8") as file:
    json.dump(
        {
            "0": "normal",
            "1": "distress",
        },
        file,
        indent=4,
    )

training_info = {
    "project": "LumiGuard",
    "task": "Binary audio classification",
    "embedding_model": "VoiceCLAP feature embeddings",
    "input_dimension": INPUT_DIM,
    "classes": {
        "0": "normal",
        "1": "distress",
    },
    "dataset": {
        "total_samples": int(len(y)),
        "normal_samples": normal_count,
        "distress_samples": distress_count,
        "training_samples": int(len(X_train)),
        "validation_samples": int(len(X_val)),
    },
    "configuration": {
        "seed": SEED,
        "batch_size": BATCH_SIZE,
        "maximum_epochs": EPOCHS,
        "learning_rate": LEARNING_RATE,
        "weight_decay": WEIGHT_DECAY,
        "validation_size": VALIDATION_SIZE,
        "early_stopping_patience": EARLY_STOPPING_PATIENCE,
        "distress_threshold": DISTRESS_THRESHOLD,
    },
    "best_epoch": int(checkpoint["best_epoch"]),
    "best_validation_loss": float(checkpoint["best_validation_loss"]),
    "validation_metrics": {
        "accuracy": final_metrics["accuracy"],
        "precision": final_metrics["precision"],
        "recall": final_metrics["recall"],
        "f1_score": final_metrics["f1"],
    },
    "confusion_matrix": {
        "true_negative": int(tn),
        "false_positive": int(fp),
        "false_negative": int(fn),
        "true_positive": int(tp),
    },
    "history": history,
    "notes": [
        "Validation metrics are preliminary.",
        "The validation split is random and may contain related recordings "
        "from the same source as training recordings.",
        "Use a separate untouched test set for final evaluation.",
        "A distress prediction indicates possible distress, not a confirmed crime.",
    ],
}

with open(INFO_PATH, "w", encoding="utf-8") as file:
    json.dump(training_info, file, indent=4)

print("\n" + "=" * 65)
print("TRAINING COMPLETED")
print("=" * 65)

print(f"Best model:      {MODEL_PATH.resolve()}")
print(f"Class names:     {CLASSES_PATH.resolve()}")
print(f"Training report: {INFO_PATH.resolve()}")

print(
    "\nImportant: this is a preliminary validation result, "
    "not proof of real-world crime detection accuracy."
)
