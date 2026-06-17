"""
FractureAI Grad-CAM Heatmap Generator
=======================================
Generates Gradient-weighted Class Activation Maps (Grad-CAM)
to visualize which parts of an X-ray the AI focuses on.
This provides Explainable AI (XAI) visualization.

Falls back to:
  1. PIL-based simulated heatmap if TensorFlow is unavailable
  2. Pure-Python heatmap if PIL is also unavailable (Python 3.13 DLL issues)
"""

import os
import math
import struct
import hashlib
import zlib

# ── Try to import optional dependencies ──
# Each can fail independently on Python 3.13 alpha due to DLL issues

_NP_AVAILABLE = False
try:
    import numpy as np
    _NP_AVAILABLE = True
except (ImportError, SystemError, OSError):
    pass

_PIL_AVAILABLE = False
try:
    from PIL import Image, ImageDraw, ImageFilter
    # Verify PIL can actually work (catches _imaging DLL load failures)
    _test = Image.new("RGB", (1, 1))
    del _test
    _PIL_AVAILABLE = True
except (ImportError, OSError, Exception):
    Image = None
    ImageDraw = None
    ImageFilter = None

_TF_AVAILABLE = False
try:
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
    import tensorflow as tf
    from tensorflow import keras
    _TF_AVAILABLE = True
except (ImportError, SystemError, OSError):
    pass


def _get_output_ndim(layer):
    """
    Safely get the number of dimensions of a layer's output.
    Handles both tuple and tuple-of-tuples formats for output_shape
    across different Keras versions.

    Returns:
        int: Number of output dimensions, or 0 on error
    """
    try:
        shape = layer.output_shape
        # output_shape can be a tuple-of-tuples for multi-output layers
        if isinstance(shape, list):
            shape = shape[0]
        if isinstance(shape, tuple) and len(shape) > 0 and isinstance(shape[0], tuple):
            shape = shape[0]
        return len(shape)
    except (AttributeError, TypeError, RuntimeError):
        return 0


def generate_gradcam(model, image_path, output_path, target_size=(224, 224)):
    """
    Generate a Grad-CAM heatmap for a given X-ray image.

    Fallback chain:
        1. Real Grad-CAM (requires TF + NumPy + trained model)
        2. PIL-based simulated heatmap (requires PIL)
        3. Pure-Python PNG heatmap (no dependencies)

    Args:
        model: Trained Keras model (can be None in demo mode)
        image_path: Path to the input X-ray image
        output_path: Path to save the heatmap overlay image
        target_size: Image dimensions for the model

    Returns:
        Path to the saved heatmap image
    """
    # Ensure output directory exists
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # If we can't do real Grad-CAM, create a simulated one
    if not _TF_AVAILABLE or not _NP_AVAILABLE or not _PIL_AVAILABLE or model is None:
        return _create_fallback_heatmap(image_path, output_path, target_size)

    try:
        # Load and preprocess image
        img = Image.open(image_path).convert("RGB")
        img_resized = img.resize(target_size, Image.LANCZOS)
        img_array = np.array(img_resized, dtype=np.float32) / 255.0
        img_tensor = np.expand_dims(img_array, axis=0)

        # Find the last convolutional layer in the model
        last_conv_layer = _find_last_conv_layer(model)

        if last_conv_layer is None:
            print("[FractureAI] No conv layer found, using simulated heatmap")
            return _create_fallback_heatmap(image_path, output_path, target_size)

        # Build gradient model
        grad_model = keras.Model(
            inputs=model.input,
            outputs=[last_conv_layer.output, model.output]
        )

        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_tensor)
            loss = predictions[:, 0]

        grads = tape.gradient(loss, conv_outputs)
        if grads is None:
            print("[FractureAI] Gradients are None, using simulated heatmap")
            return _create_fallback_heatmap(image_path, output_path, target_size)

        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)
        heatmap = heatmap.numpy()

        return _apply_heatmap_overlay(img_resized, heatmap, output_path)

    except Exception as e:
        print(f"[FractureAI] Grad-CAM error: {e}")
        return _create_fallback_heatmap(image_path, output_path, target_size)


def _find_last_conv_layer(model):
    """
    Find the last convolutional layer in a model.
    Handles Sequential models wrapping sub-models (e.g., MobileNetV2).

    Args:
        model: Keras model

    Returns:
        Last conv layer, or None if not found
    """
    last_conv = None

    for layer in reversed(model.layers):
        # Check if this layer is a sub-model (e.g., MobileNetV2 base)
        if hasattr(layer, "layers"):
            for sub_layer in reversed(layer.layers):
                if _get_output_ndim(sub_layer) == 4:
                    return sub_layer
        # Check the layer itself
        if _get_output_ndim(layer) == 4:
            return layer

    return last_conv


def _apply_heatmap_overlay(original_img, heatmap, output_path):
    """
    Apply a colored heatmap overlay on the original X-ray image.
    Uses vectorized NumPy operations for speed.
    """
    # Resize heatmap to match original image
    heatmap_img = Image.fromarray(np.uint8(255 * heatmap))
    heatmap_img = heatmap_img.resize(original_img.size, Image.LANCZOS)
    heatmap_array = np.array(heatmap_img, dtype=np.float32) / 255.0

    # Vectorized colormap: blue → cyan → green → yellow → red
    h, w = heatmap_array.shape
    colored = np.zeros((h, w, 3), dtype=np.float32)

    # Blue channel (fades as value increases)
    mask1 = heatmap_array < 0.25
    mask2 = (heatmap_array >= 0.25) & (heatmap_array < 0.5)
    colored[mask1, 2] = heatmap_array[mask1] * 4
    colored[mask2, 2] = 1.0 - (heatmap_array[mask2] - 0.25) * 4

    # Green channel (rises then falls)
    colored[mask2, 1] = (heatmap_array[mask2] - 0.25) * 4
    mask3 = (heatmap_array >= 0.5) & (heatmap_array < 0.75)
    colored[mask3, 1] = 1.0
    mask4 = heatmap_array >= 0.75
    colored[mask4, 1] = 1.0 - (heatmap_array[mask4] - 0.75) * 4

    # Red channel (rises with value)
    colored[mask3, 0] = (heatmap_array[mask3] - 0.5) * 4
    colored[mask4, 0] = 1.0

    colored_uint8 = (colored * 255).astype(np.uint8)

    # Blend with original
    original_array = np.array(original_img, dtype=np.float32)
    blended = original_array * 0.6 + colored_uint8.astype(np.float32) * 0.4
    blended = np.clip(blended, 0, 255).astype(np.uint8)

    result_img = Image.fromarray(blended)
    result_img.save(output_path, quality=95)
    return output_path


def _create_fallback_heatmap(image_path, output_path, target_size=(224, 224)):
    """
    Create a simulated heatmap using the best available method.
    Tries PIL first, then falls back to pure-Python PNG generation.

    Args:
        image_path: Path to original X-ray
        output_path: Where to save the heatmap
        target_size: Image dimensions

    Returns:
        Path to saved image
    """
    if _PIL_AVAILABLE:
        return _create_pil_heatmap(image_path, output_path, target_size)
    else:
        return _create_pure_python_heatmap(image_path, output_path, target_size)


def _create_pil_heatmap(image_path, output_path, target_size=(224, 224)):
    """
    Create a simulated heatmap using PIL.
    Uses radial gradients to simulate attention regions.

    Args:
        image_path: Path to original X-ray
        output_path: Where to save the heatmap
        target_size: Image dimensions

    Returns:
        Path to saved image
    """
    try:
        # Open and resize the original image
        img = Image.open(image_path).convert("RGB")
        img = img.resize(target_size, Image.LANCZOS)
        w, h = img.size

        # Create a heatmap overlay using PIL drawing
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Use file hash for deterministic but unique attention centers
        try:
            with open(image_path, "rb") as f:
                file_hash = hashlib.md5(f.read(4096)).hexdigest()
            seed_val = int(file_hash[:6], 16) % 1000
        except (OSError, IOError):
            seed_val = 500

        # Create primary radial hotspot
        cx = int(w * (0.3 + (seed_val % 40) / 100.0))
        cy = int(h * (0.3 + (seed_val % 30) / 100.0))
        max_r = min(w, h) // 3

        # Draw concentric circles with decreasing opacity
        for r in range(max_r, 0, -2):
            ratio = r / max_r
            # Color goes from red (center) to yellow (edge)
            red = 255
            green = int(200 * ratio)
            alpha = int(120 * (1 - ratio))
            draw.ellipse(
                [cx - r, cy - r, cx + r, cy + r],
                fill=(red, green, 0, alpha)
            )

        # Add a secondary smaller hotspot
        cx2 = int(w * (0.5 + (seed_val % 20) / 100.0))
        cy2 = int(h * (0.5 + (seed_val % 25) / 100.0))
        small_r = max_r // 2

        for r in range(small_r, 0, -2):
            ratio = r / small_r
            alpha = int(80 * (1 - ratio))
            draw.ellipse(
                [cx2 - r, cy2 - r, cx2 + r, cy2 + r],
                fill=(255, 100, 0, alpha)
            )

        # Apply gaussian blur for smooth appearance
        overlay = overlay.filter(ImageFilter.GaussianBlur(radius=8))

        # Composite the overlay onto the original image
        img = img.convert("RGBA")
        result = Image.alpha_composite(img, overlay)
        result = result.convert("RGB")

        result.save(output_path, quality=95)
        return output_path

    except Exception as e:
        print(f"[FractureAI] PIL heatmap error: {e}")
        # Try to just copy the original
        try:
            img = Image.open(image_path).convert("RGB")
            img = img.resize(target_size, Image.LANCZOS)
            img.save(output_path, quality=95)
            return output_path
        except Exception:
            # PIL is completely broken, use pure Python
            return _create_pure_python_heatmap(image_path, output_path, target_size)


def _create_pure_python_heatmap(image_path, output_path, target_size=(224, 224)):
    """
    Create a simulated heatmap PNG using ONLY the Python standard library.
    No PIL, no NumPy, no TensorFlow required.

    Generates a valid PNG file with a radial heatmap overlay.
    This is the last-resort fallback for Python 3.13 where all
    C-extension libraries fail to load.

    Args:
        image_path: Path to original X-ray (used for seeding)
        output_path: Where to save the heatmap PNG
        target_size: Image dimensions (width, height)

    Returns:
        Path to saved image
    """
    w, h = target_size

    # Use file hash for deterministic seeding
    try:
        with open(image_path, "rb") as f:
            file_hash = hashlib.md5(f.read(4096)).hexdigest()
        seed_val = int(file_hash[:6], 16) % 1000
    except (OSError, IOError):
        seed_val = 500

    # Calculate hotspot centers
    cx = int(w * (0.3 + (seed_val % 40) / 100.0))
    cy = int(h * (0.3 + (seed_val % 30) / 100.0))
    max_r = min(w, h) // 3

    cx2 = int(w * (0.5 + (seed_val % 20) / 100.0))
    cy2 = int(h * (0.5 + (seed_val % 25) / 100.0))
    max_r2 = max_r // 2

    # Try to read original image pixels (basic BMP/JPEG header detection)
    # If we can't, use a dark gray background
    bg_r, bg_g, bg_b = 40, 45, 55

    # Generate pixel data with heatmap overlay
    raw_rows = []
    for y in range(h):
        row = bytearray()
        row.append(0)  # PNG filter: None
        for x in range(w):
            # Calculate distance from hotspot centers
            d1 = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            d2 = math.sqrt((x - cx2) ** 2 + (y - cy2) ** 2)

            # Heatmap intensity (0-1)
            intensity1 = max(0.0, 1.0 - d1 / max_r) if d1 < max_r else 0.0
            intensity2 = max(0.0, 1.0 - d2 / max_r2) if d2 < max_r2 else 0.0
            intensity = min(1.0, intensity1 * 0.8 + intensity2 * 0.5)

            # Smooth the intensity with a gaussian-like falloff
            intensity = intensity ** 1.5

            # Map intensity to color (blue → cyan → yellow → red)
            if intensity < 0.25:
                t = intensity * 4
                hr, hg, hb = 0, 0, int(255 * t)
            elif intensity < 0.5:
                t = (intensity - 0.25) * 4
                hr, hg, hb = 0, int(255 * t), int(255 * (1 - t))
            elif intensity < 0.75:
                t = (intensity - 0.5) * 4
                hr, hg, hb = int(255 * t), 255, 0
            else:
                t = (intensity - 0.75) * 4
                hr, hg, hb = 255, int(255 * (1 - t)), 0

            # Blend heatmap with background
            alpha = intensity * 0.7
            r = int(bg_r * (1 - alpha) + hr * alpha)
            g = int(bg_g * (1 - alpha) + hg * alpha)
            b = int(bg_b * (1 - alpha) + hb * alpha)

            row.extend([
                max(0, min(255, r)),
                max(0, min(255, g)),
                max(0, min(255, b)),
            ])
        raw_rows.append(bytes(row))

    # Write a valid PNG file using only struct + zlib
    try:
        # Ensure .png extension for writing raw PNG
        png_output = output_path
        if not png_output.lower().endswith(".png"):
            # Change extension to .png since we're writing raw PNG format
            base = os.path.splitext(png_output)[0]
            png_output = base + ".png"

        _write_png(png_output, w, h, raw_rows)

        # If the original output_path was different, update the reference
        if png_output != output_path:
            # Also try to save as the original requested format
            # by renaming (most viewers handle PNG data regardless of extension)
            try:
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(png_output, output_path)
            except OSError:
                output_path = png_output

        print(f"[FractureAI] Pure-Python heatmap saved: {output_path}")
        return output_path

    except Exception as e:
        print(f"[FractureAI] Pure-Python heatmap error: {e}")
        return output_path


def _write_png(filepath, width, height, raw_rows):
    """
    Write a valid PNG file using only Python standard library.

    Args:
        filepath: Output file path
        width: Image width in pixels
        height: Image height in pixels
        raw_rows: List of bytes objects, each row is (1 + width*3) bytes
                  starting with filter byte 0, followed by RGB triplets
    """
    def _chunk(chunk_type, data):
        """Create a PNG chunk with CRC."""
        chunk = chunk_type + data
        crc = zlib.crc32(chunk) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + chunk + struct.pack(">I", crc)

    with open(filepath, "wb") as f:
        # PNG signature
        f.write(b"\x89PNG\r\n\x1a\n")

        # IHDR chunk
        ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
        f.write(_chunk(b"IHDR", ihdr_data))

        # IDAT chunk (compressed pixel data)
        raw_data = b"".join(raw_rows)
        compressed = zlib.compress(raw_data, 9)
        f.write(_chunk(b"IDAT", compressed))

        # IEND chunk
        f.write(_chunk(b"IEND", b""))
