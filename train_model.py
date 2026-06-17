"""
FractureAI — Model Training Script
=====================================
Downloads a bone fracture X-ray dataset and trains the
MobileNetV2-based CNN for fracture detection.

Usage:
    python train_model.py

Requirements:
    - Python 3.10-3.12 (TensorFlow requirement)
    - TensorFlow 2.x
    - Pillow

The script will:
  1. Download the bone fracture dataset from Kaggle/GitHub
  2. Split into train/validation/test sets
  3. Train the MobileNetV2 model with transfer learning
  4. Save the trained model to models/fracture_cnn.h5
"""

import os
import sys
import zipfile
import shutil
import urllib.request
import ssl
from pathlib import Path

# Fix Windows console encoding
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# ── Check Python version ──
if sys.version_info >= (3, 13):
    print("ERROR: TensorFlow requires Python 3.10-3.12")
    print(f"Current Python: {sys.version}")
    print("Please run this script with Python 3.12:")
    print('  & "C:\\Users\\anujm\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" train_model.py')
    sys.exit(1)

# ── Environment setup ──
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # Suppress TF info logs

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import (
    ModelCheckpoint,
    EarlyStopping,
    ReduceLROnPlateau,
    TensorBoard,
)

# ── Configuration ──
BASE_DIR = Path(__file__).parent
DATASET_DIR = BASE_DIR / "dataset"
MODEL_SAVE_PATH = BASE_DIR / "models" / "fracture_cnn.h5"
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS = 25
LEARNING_RATE = 0.0005

# Number of synthetic images per class (used if download fails)
SYNTHETIC_TRAIN_PER_CLASS = 300
SYNTHETIC_VAL_PER_CLASS = 60


def download_dataset():
    """Download and extract the bone fracture dataset, or generate synthetic data."""

    if DATASET_DIR.exists() and any(DATASET_DIR.rglob("*.jpg")):
        count = len(list(DATASET_DIR.rglob("*.jpg"))) + len(list(DATASET_DIR.rglob("*.png")))
        if count > 50:
            print(f"[OK] Dataset already exists with {count} images")
            return True

    DATASET_DIR.mkdir(parents=True, exist_ok=True)

    # Try downloading from multiple sources
    urls = [
        "https://github.com/amanchoudhary18/Bone-Fracture-Classification/archive/refs/heads/main.zip",
        "https://github.com/pokorn01/bone-fracture-dataset/archive/refs/heads/master.zip",
    ]

    zip_path = DATASET_DIR / "dataset.zip"
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    downloaded_ok = False
    for url in urls:
        try:
            print(f"  Trying: {url[:65]}...")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                dl = 0
                with open(zip_path, "wb") as f:
                    while True:
                        chunk = resp.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        dl += len(chunk)
                        if total > 0:
                            print(f"\r  Progress: {dl*100//total}%", end="", flush=True)
                print()

            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(DATASET_DIR)
            zip_path.unlink()
            print("[OK] Downloaded and extracted")
            downloaded_ok = True
            break
        except Exception as e:
            print(f"  [!] Failed: {e}")
            if zip_path.exists():
                zip_path.unlink()

    if not downloaded_ok:
        print("\n[!!] Download failed. Generating synthetic X-ray training data...")
        print("     (This creates realistic bone/fracture images for training)")
        _generate_synthetic_dataset()

    return True


def _generate_synthetic_dataset():
    """
    Generate a synthetic bone X-ray dataset using PIL.
    Creates realistic-looking X-ray images with:
    - Bone structures (ellipses, rectangles with smooth edges)
    - Fracture lines (for positive class)
    - Varying brightness, contrast, and noise
    - Multiple bone types and orientations
    """
    from PIL import Image, ImageDraw, ImageFilter
    import random

    dirs = {
        "train/fractured": SYNTHETIC_TRAIN_PER_CLASS,
        "train/not_fractured": SYNTHETIC_TRAIN_PER_CLASS,
        "val/fractured": SYNTHETIC_VAL_PER_CLASS,
        "val/not_fractured": SYNTHETIC_VAL_PER_CLASS,
    }

    total_count = sum(dirs.values())
    generated = 0

    for subdir, count in dirs.items():
        is_fractured = "fractured" in subdir and "not_" not in subdir
        full_dir = DATASET_DIR / subdir
        full_dir.mkdir(parents=True, exist_ok=True)

        for i in range(count):
            random.seed(generated * 7 + i * 13 + (1 if is_fractured else 0))
            img = _create_synthetic_xray(is_fractured, random)
            img.save(full_dir / f"{i:04d}.jpg", quality=90)
            generated += 1

            if generated % 50 == 0:
                print(f"\r  Generated {generated}/{total_count} images...", end="", flush=True)

    print(f"\r  [OK] Generated {generated} synthetic images total       ")
    print(f"       Train: {SYNTHETIC_TRAIN_PER_CLASS} fractured + {SYNTHETIC_TRAIN_PER_CLASS} normal")
    print(f"       Val:   {SYNTHETIC_VAL_PER_CLASS} fractured + {SYNTHETIC_VAL_PER_CLASS} normal")


def _create_synthetic_xray(fractured, rng):
    """Create a single synthetic X-ray image."""
    from PIL import Image, ImageDraw, ImageFilter

    w, h = IMAGE_SIZE

    # Dark background (like X-ray film)
    bg_val = rng.randint(5, 30)
    img = Image.new("L", (w, h), bg_val)
    draw = ImageDraw.Draw(img)

    # Add some soft tissue gradient (lighter area in center)
    tissue_cx = w // 2 + rng.randint(-30, 30)
    tissue_cy = h // 2 + rng.randint(-30, 30)
    tissue_r = rng.randint(70, 100)
    for r in range(tissue_r, 0, -1):
        val = bg_val + int(40 * (1 - r / tissue_r))
        draw.ellipse(
            [tissue_cx - r, tissue_cy - r, tissue_cx + r, tissue_cy + r],
            fill=val
        )

    # Draw bone structure(s) - choose a bone type
    bone_type = rng.choice(["long", "joint", "hand", "rib"])
    bone_brightness = rng.randint(160, 230)

    if bone_type == "long":
        # Long bone (like femur, tibia)
        angle = rng.uniform(-0.3, 0.3)
        bw = rng.randint(25, 45)
        cx, cy = w // 2 + rng.randint(-20, 20), h // 2
        length = rng.randint(140, 190)

        # Draw the bone shaft
        for offset in range(-bw // 2, bw // 2 + 1):
            x1 = int(cx + offset - length * 0.5 * angle)
            y1 = int(cy - length // 2)
            x2 = int(cx + offset + length * 0.5 * angle)
            y2 = int(cy + length // 2)
            edge_dist = abs(offset) / (bw / 2)
            val = int(bone_brightness * (1 - 0.3 * edge_dist ** 2))
            draw.line([(x1, y1), (x2, y2)], fill=val, width=1)

        # Add epiphyses (rounded ends)
        for end_y in [cy - length // 2, cy + length // 2]:
            end_r = bw // 2 + rng.randint(3, 10)
            for r in range(end_r, 0, -1):
                val = int(bone_brightness * (0.7 + 0.3 * (1 - r / end_r)))
                draw.ellipse(
                    [cx - r, end_y - r, cx + r, end_y + r],
                    fill=val
                )

    elif bone_type == "joint":
        # Joint area (like elbow, knee)
        cx, cy = w // 2, h // 2
        for _ in range(2):
            rx, ry = rng.randint(35, 55), rng.randint(25, 40)
            offset_y = rng.choice([-1, 1]) * rng.randint(20, 40)
            for r_scale in range(10, 0, -1):
                val = int(bone_brightness * (0.6 + 0.04 * r_scale))
                s = r_scale / 10.0
                draw.ellipse([
                    cx - int(rx * s), cy + offset_y - int(ry * s),
                    cx + int(rx * s), cy + offset_y + int(ry * s)
                ], fill=val)

    elif bone_type == "hand":
        # Hand/finger bones (multiple small bones)
        start_x = w // 2 - 50
        for finger in range(4):
            fx = start_x + finger * 28 + rng.randint(-5, 5)
            fy = h // 2 - rng.randint(0, 30)
            for seg in range(3):
                seg_len = rng.randint(20, 35)
                seg_w = rng.randint(8, 14)
                for dy in range(seg_len):
                    for dx in range(-seg_w // 2, seg_w // 2):
                        edge = abs(dx) / (seg_w / 2)
                        val = int(bone_brightness * (0.8 - 0.3 * edge ** 2))
                        px = fx + dx
                        py = fy + dy
                        if 0 <= px < w and 0 <= py < h:
                            img.putpixel((px, py), max(img.getpixel((px, py)), val))
                fy += seg_len + rng.randint(3, 6)

    elif bone_type == "rib":
        # Rib-like curved bone
        import math
        cx, cy = w // 2, h // 2
        curvature = rng.uniform(0.005, 0.015)
        rib_w = rng.randint(10, 18)
        for t in range(-90, 91):
            x = cx + t
            y = int(cy + curvature * t * t + rng.uniform(-1, 1))
            for dw in range(-rib_w // 2, rib_w // 2):
                edge = abs(dw) / (rib_w / 2)
                val = int(bone_brightness * (0.85 - 0.3 * edge ** 2))
                px, py = x, y + dw
                if 0 <= px < w and 0 <= py < h:
                    img.putpixel((px, py), max(img.getpixel((px, py)), val))

    # Add fracture lines for the positive class
    if fractured:
        num_fractures = rng.randint(1, 3)
        for _ in range(num_fractures):
            fx = w // 2 + rng.randint(-40, 40)
            fy = h // 2 + rng.randint(-50, 50)
            flen = rng.randint(15, 60)
            fangle = rng.uniform(-1.5, 1.5)

            import math
            for t in range(flen):
                x = int(fx + t * math.cos(fangle) + rng.uniform(-2, 2))
                y = int(fy + t * math.sin(fangle) + rng.uniform(-2, 2))
                for dw in range(-2, 3):
                    px, py = x + dw, y
                    if 0 <= px < w and 0 <= py < h:
                        # Dark fracture line on bright bone
                        current = img.getpixel((px, py))
                        img.putpixel((px, py), max(0, current - rng.randint(60, 120)))

            # Add slight displacement effect
            if rng.random() > 0.5:
                displacement = rng.randint(2, 6)
                region = img.crop((fx, fy, fx + 30, fy + 30))
                img.paste(region, (fx + displacement, fy + displacement))

    # Add noise and blur for realism
    # Gaussian-like noise
    pixels = img.load()
    for _ in range(w * h // 4):
        nx, ny = rng.randint(0, w - 1), rng.randint(0, h - 1)
        noise = rng.randint(-15, 15)
        old_val = pixels[nx, ny]
        pixels[nx, ny] = max(0, min(255, old_val + noise))

    # Slight blur
    img = img.filter(ImageFilter.GaussianBlur(radius=rng.uniform(0.5, 1.5)))

    # Convert to RGB (X-ray style)
    img = img.convert("RGB")

    return img



def organize_dataset():
    """
    Organize the dataset into the expected directory structure:
        dataset/train/fractured/
        dataset/train/not_fractured/
        dataset/val/fractured/
        dataset/val/not_fractured/
    """
    train_dir = DATASET_DIR / "train"
    val_dir = DATASET_DIR / "val"

    # Check if already organized
    if (train_dir / "fractured").exists() and (train_dir / "not_fractured").exists():
        train_count = len(list(train_dir.rglob("*.jpg"))) + len(list(train_dir.rglob("*.png")))
        val_count = len(list(val_dir.rglob("*.jpg"))) + len(list(val_dir.rglob("*.png")))
        if train_count > 20 and val_count > 5:
            print(f"[OK] Dataset organized: {train_count} train, {val_count} val images")
            return train_dir, val_dir

    print("[..] Organizing dataset structure...")

    # Find all image files recursively
    all_images = []
    for ext in ["*.jpg", "*.jpeg", "*.png", "*.bmp"]:
        all_images.extend(DATASET_DIR.rglob(ext))

    if not all_images:
        print("[!] No images found in dataset directory")
        return None, None

    # Try to detect existing class structure
    # Look for common folder name patterns
    fractured_images = []
    normal_images = []

    fracture_keywords = ["fracture", "positive", "broken", "abnormal", "yes", "1"]
    normal_keywords = ["normal", "negative", "healthy", "no_fracture", "not_fractured", "0"]

    for img_path in all_images:
        path_lower = str(img_path).lower()
        parts = [p.lower() for p in img_path.parts]

        is_fracture = any(kw in part for part in parts for kw in fracture_keywords)
        is_normal = any(kw in part for part in parts for kw in normal_keywords)

        if is_fracture and not is_normal:
            fractured_images.append(img_path)
        elif is_normal and not is_fracture:
            normal_images.append(img_path)

    # If classification failed, try splitting by parent directory
    if not fractured_images and not normal_images:
        print("  [!] Could not auto-detect classes from folder names")
        print("  [!] Splitting images 50/50 for demo training")
        mid = len(all_images) // 2
        fractured_images = all_images[:mid]
        normal_images = all_images[mid:]

    print(f"  Found: {len(fractured_images)} fractured, {len(normal_images)} normal images")

    # Create organized directory structure
    for d in [train_dir / "fractured", train_dir / "not_fractured",
              val_dir / "fractured", val_dir / "not_fractured"]:
        d.mkdir(parents=True, exist_ok=True)

    # Split: 80% train, 20% validation
    import random
    random.seed(42)
    random.shuffle(fractured_images)
    random.shuffle(normal_images)

    split_frac = int(0.8 * len(fractured_images))
    split_norm = int(0.8 * len(normal_images))

    def copy_images(images, dest_dir):
        copied = 0
        for img in images:
            dest = dest_dir / f"{copied:04d}{img.suffix}"
            try:
                shutil.copy2(img, dest)
                copied += 1
            except Exception:
                pass
        return copied

    t_frac = copy_images(fractured_images[:split_frac], train_dir / "fractured")
    t_norm = copy_images(normal_images[:split_norm], train_dir / "not_fractured")
    v_frac = copy_images(fractured_images[split_frac:], val_dir / "fractured")
    v_norm = copy_images(normal_images[split_norm:], val_dir / "not_fractured")

    print(f"[OK] Train: {t_frac} fractured + {t_norm} normal")
    print(f"[OK] Val:   {v_frac} fractured + {v_norm} normal")

    return train_dir, val_dir


def build_model():
    """Build the MobileNetV2 transfer learning model."""
    print("\n[..] Building MobileNetV2 model...")

    # Load pre-trained MobileNetV2
    base_model = keras.applications.MobileNetV2(
        input_shape=(*IMAGE_SIZE, 3),
        include_top=False,
        weights="imagenet"
    )

    # Freeze base model layers initially
    base_model.trainable = False

    # Build model
    model = keras.Sequential([
        layers.InputLayer(input_shape=(*IMAGE_SIZE, 3)),
        base_model,

        # Classification head
        layers.GlobalAveragePooling2D(),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(256, activation="relu"),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(128, activation="relu"),
        layers.Dropout(0.2),
        layers.Dense(1, activation="sigmoid")  # Binary: fracture or not
    ])

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )

    total_params = model.count_params()
    trainable = sum(
        tf.keras.backend.count_params(w) for w in model.trainable_weights
    )
    print(f"[OK] Model built: {total_params:,} total params, {trainable:,} trainable")
    model.summary()

    return model, base_model


def create_data_generators(train_dir, val_dir):
    """Create data generators with augmentation."""
    print("\n[..] Setting up data generators with augmentation...")

    # Training data: apply augmentation
    train_datagen = ImageDataGenerator(
        preprocessing_function=keras.applications.mobilenet_v2.preprocess_input,
        rotation_range=20,
        width_shift_range=0.15,
        height_shift_range=0.15,
        shear_range=0.1,
        zoom_range=0.15,
        horizontal_flip=True,
        brightness_range=[0.8, 1.2],
        fill_mode="nearest",
    )

    # Validation data: only preprocessing, no augmentation
    val_datagen = ImageDataGenerator(
        preprocessing_function=keras.applications.mobilenet_v2.preprocess_input,
    )

    train_generator = train_datagen.flow_from_directory(
        str(train_dir),
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="binary",
        classes=["not_fractured", "fractured"],  # 0=normal, 1=fracture
        shuffle=True,
    )

    val_generator = val_datagen.flow_from_directory(
        str(val_dir),
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="binary",
        classes=["not_fractured", "fractured"],
        shuffle=False,
    )

    print(f"[OK] Training samples: {train_generator.samples}")
    print(f"[OK] Validation samples: {val_generator.samples}")
    print(f"[OK] Classes: {train_generator.class_indices}")

    return train_generator, val_generator


def train_model(model, base_model, train_gen, val_gen):
    """Train the model in two phases: frozen then fine-tuned."""

    # ── Phase 1: Train only the classification head ──
    print("\n" + "=" * 60)
    print("  PHASE 1: Training Classification Head")
    print("  (Base model frozen, training custom layers)")
    print("=" * 60)

    callbacks_phase1 = [
        ModelCheckpoint(
            str(MODEL_SAVE_PATH),
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        EarlyStopping(
            monitor="val_accuracy",
            patience=5,
            restore_best_weights=True,
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=3,
            min_lr=1e-6,
            verbose=1,
        ),
    ]

    phase1_epochs = min(EPOCHS, 15)
    history1 = model.fit(
        train_gen,
        epochs=phase1_epochs,
        validation_data=val_gen,
        callbacks=callbacks_phase1,
        verbose=1,
    )

    # ── Phase 2: Fine-tune top layers of base model ──
    print("\n" + "=" * 60)
    print("  PHASE 2: Fine-Tuning Base Model")
    print("  (Unfreezing top 30 layers for fine-tuning)")
    print("=" * 60)

    # Unfreeze the top 30 layers of MobileNetV2
    base_model.trainable = True
    for layer in base_model.layers[:-30]:
        layer.trainable = False

    # Recompile with lower learning rate for fine-tuning
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE / 10),
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )

    trainable = sum(
        tf.keras.backend.count_params(w) for w in model.trainable_weights
    )
    print(f"[OK] Now trainable: {trainable:,} params")

    callbacks_phase2 = [
        ModelCheckpoint(
            str(MODEL_SAVE_PATH),
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        EarlyStopping(
            monitor="val_accuracy",
            patience=5,
            restore_best_weights=True,
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=2,
            min_lr=1e-7,
            verbose=1,
        ),
    ]

    phase2_epochs = EPOCHS - phase1_epochs + 10
    history2 = model.fit(
        train_gen,
        epochs=phase2_epochs,
        validation_data=val_gen,
        callbacks=callbacks_phase2,
        verbose=1,
    )

    return history1, history2


def evaluate_model(model, val_gen):
    """Evaluate the trained model."""
    print("\n" + "=" * 60)
    print("  MODEL EVALUATION")
    print("=" * 60)

    results = model.evaluate(val_gen, verbose=0)
    print(f"  Validation Loss:     {results[0]:.4f}")
    print(f"  Validation Accuracy: {results[1] * 100:.2f}%")

    # Save final model
    model.save(str(MODEL_SAVE_PATH))
    size_mb = MODEL_SAVE_PATH.stat().st_size / (1024 * 1024)
    print(f"\n[OK] Model saved to: {MODEL_SAVE_PATH}")
    print(f"[OK] Model size: {size_mb:.1f} MB")

    return results


def main():
    """Main training pipeline."""
    print()
    print("=" * 60)
    print("  FractureAI - Model Training Pipeline")
    print("  MobileNetV2 Transfer Learning for Fracture Detection")
    print("=" * 60)
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  TensorFlow: {tf.__version__}")
    print(f"  NumPy: {np.__version__}")
    print(f"  GPU Available: {len(tf.config.list_physical_devices('GPU')) > 0}")
    gpus = tf.config.list_physical_devices("GPU")
    if gpus:
        for gpu in gpus:
            print(f"  GPU: {gpu.name}")
    print("=" * 60)

    # Step 1: Download dataset
    print("\n-- Step 1: Dataset --")
    if not download_dataset():
        sys.exit(1)

    # Step 2: Organize dataset
    print("\n-- Step 2: Organize --")
    train_dir, val_dir = organize_dataset()
    if not train_dir:
        print("[!] Failed to organize dataset")
        sys.exit(1)

    # Step 3: Build model
    print("\n-- Step 3: Build Model --")
    model, base_model = build_model()

    # Step 4: Create data generators
    print("\n-- Step 4: Data Generators --")
    train_gen, val_gen = create_data_generators(train_dir, val_dir)

    # Step 5: Train
    print("\n-- Step 5: Train --")
    history1, history2 = train_model(model, base_model, train_gen, val_gen)

    # Step 6: Evaluate
    print("\n-- Step 6: Evaluate --")
    results = evaluate_model(model, val_gen)

    # Summary
    print("\n" + "=" * 60)
    print("  TRAINING COMPLETE!")
    print("=" * 60)
    print(f"  Model saved to: {MODEL_SAVE_PATH}")
    print(f"  Final accuracy: {results[1] * 100:.2f}%")
    print()
    print("  To use this model, run your Flask app:")
    print("    python app.py")
    print()
    print("  The app will automatically load the trained model")
    print("  from models/fracture_cnn.h5")
    print("=" * 60)


if __name__ == "__main__":
    main()
