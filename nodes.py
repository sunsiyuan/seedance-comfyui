"""HaryAI models as ComfyUI nodes: Seedance 2.5 video (Volcengine / BytePlus
ModelArk format) and Seedream 5.5 / Nano Banana images (OpenAI images format).

Standard library only. The key is the node's api_key field (saved inside the
workflow file). API reference: https://haryai.com/docs/video.md and
https://haryai.com/docs/image.md
"""
import base64
import io
import json
import os
import time
import urllib.error
import urllib.request
import uuid

import numpy as np
import torch
from PIL import Image

import folder_paths

API = "https://api.haryai.com"
VIDEO_BASE = API + "/api/v3"
# The Unlocked models (dreamina) have fewer content limits than the doubao
# ones, at a higher price (https://haryai.com/en/seedance-api-pricing). The
# labels stay as they were: saved workflows store them.
MODELS = {
    "Seedance 2.5": "doubao-seedance-2-5-260628",
    "Seedance 2.5 Flash": "doubao-seedance-2-5-flash-261115",
    "Seedance 2.5 Unlocked (fewer content limits)": "dreamina-seedance-2-5-260628",
    "Seedance 2.5 Flash Unlocked (fewer content limits)": "dreamina-seedance-2-5-flash-261115",
}
RESOLUTIONS = {name: ["480p", "720p"] if "Flash" in name else ["480p", "720p", "1080p"] for name in MODELS}
# Reference images per request (Volcengine Ark, "创建视频生成任务").
MAX_REFERENCES = {name: 10 if "Flash" in name else 30 for name in MODELS}
RATIOS = ["16:9", "9:16", "1:1", "4:3", "3:4", "21:9"]

IMAGE_MODELS = {
    "Seedream 5.5": "dola-seedream-5-5-261028",
    "Nano Banana 2.1": "gemini-nano-banana-2.1",
    "Nano Banana 2": "gemini-3.1-flash-image",
}
IMAGE_SIZES = {"Seedream 5.5": ["1K", "1.5K", "2K"], "Nano Banana 2.1": ["1K", "2K", "4K"], "Nano Banana 2": ["1K", "2K", "4K"]}
IMAGE_RATIOS = ["1:1", "3:4", "4:3", "9:16", "16:9", "2:3", "3:2", "21:9"]
# Seedream's pixels per size at 1:1; 1.5K stays under the 2.61 MP price step.
SEEDREAM_PIXELS = {"1K": 1024 * 1024, "1.5K": 2_330_000, "2K": 2048 * 2048}

NO_KEY = "Fill in api_key with your HaryAI key from https://haryai.com/en/dashboard"


def _interrupted():
    try:
        import comfy.model_management as mm
        mm.throw_exception_if_processing_interrupted()
    except ImportError:
        pass


def _request(method, url, key, body=None, timeout=60, content_type="application/json"):
    data = body if isinstance(body, (bytes, type(None))) else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {key}", "Content-Type": content_type, "User-Agent": "seedance-comfyui"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except ValueError:
            return e.code, {}


def _jpeg(image):
    """One ComfyUI IMAGE (H, W, C float 0..1) as JPEG bytes."""
    arr = np.clip(image.cpu().numpy() * 255.0, 0, 255).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).convert("RGB").save(buf, format="JPEG", quality=95)
    return buf.getvalue()


def _data_uri(image):
    return "data:image/jpeg;base64," + base64.b64encode(_jpeg(image)).decode()


def _video_output(path):
    try:
        from comfy_api.input_impl import VideoFromFile
        return VideoFromFile(path)
    except ImportError:  # older ComfyUI without a VIDEO type
        return path


def _seedream_size(ratio, size):
    """WIDTHxHEIGHT for Seedream at a ratio and size, in multiples of 16."""
    rw, rh = (int(x) for x in ratio.split(":"))
    w = (SEEDREAM_PIXELS[size] * rw / rh) ** 0.5
    r16 = lambda x: max(16, int(x // 16) * 16)
    return f"{r16(w)}x{r16(w * rh / rw)}"


def _multipart(fields, files):
    boundary = uuid.uuid4().hex
    out = io.BytesIO()
    for name, value in fields.items():
        out.write(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    for i, data in enumerate(files):
        out.write(f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="ref-{i}.jpg"\r\n'
                  f"Content-Type: image/jpeg\r\n\r\n".encode())
        out.write(data)
        out.write(b"\r\n")
    out.write(f"--{boundary}--\r\n".encode())
    return out.getvalue(), f"multipart/form-data; boundary={boundary}"


class HaryAISeedance:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "",
                                      "tooltip": "Subject, action, camera, light, style. Spoken lines in quotes (turn on generate_audio)."}),
                "model": (list(MODELS), {"default": "Seedance 2.5"}),
                "resolution": (["480p", "720p", "1080p"], {"default": "720p", "tooltip": "Flash has 480p and 720p only."}),
                "ratio": (RATIOS, {"default": "16:9"}),
                "duration": ("INT", {"default": 5, "min": 4, "max": 30, "step": 1, "tooltip": "Seconds. Billed per second of output."}),
                "generate_audio": ("BOOLEAN", {"default": False}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFF,
                                 "tooltip": "Change it to make a new clip from the same inputs (ComfyUI reuses cached results otherwise). Not sent to the model."}),
            },
            "optional": {
                "first_frame": ("IMAGE", {"tooltip": "Image to video: the clip starts from this frame."}),
                "last_frame": ("IMAGE", {"tooltip": "Used together with first_frame."}),
                "reference_images": ("IMAGE", {"tooltip": "A batch of images that keep a character or product: up to 30 (Flash: 10). Not together with first/last frame."}),
                "api_key": ("STRING", {"default": "", "tooltip": "Your HaryAI key. It is saved in the workflow file: clear it before you share one."}),
            },
        }

    RETURN_TYPES = ("VIDEO", "STRING")
    RETURN_NAMES = ("video", "task_id")
    FUNCTION = "run"
    CATEGORY = "HaryAI/video"
    DESCRIPTION = "Seedance 2.5 and Seedance 2.5 Flash through HaryAI (https://haryai.com). Text to video, first and last frame, reference images, sound."

    def run(self, prompt, model, resolution, ratio, duration, generate_audio, seed,
            first_frame=None, last_frame=None, reference_images=None, api_key=""):
        key = (api_key or "").strip()
        if not key:
            raise ValueError(NO_KEY)
        if not prompt.strip():
            raise ValueError("The prompt is empty.")
        if resolution not in RESOLUTIONS[model]:
            raise ValueError(f"{model} has {', '.join(RESOLUTIONS[model])} only.")
        if reference_images is not None and (first_frame is not None or last_frame is not None):
            raise ValueError("Use either first_frame/last_frame or reference_images, not both.")
        if last_frame is not None and first_frame is None:
            raise ValueError("last_frame needs first_frame.")

        content = [{"type": "text", "text": prompt}]
        if first_frame is not None:
            content.append({"type": "image_url", "image_url": {"url": _data_uri(first_frame[0])}, "role": "first_frame"})
        if last_frame is not None:
            content.append({"type": "image_url", "image_url": {"url": _data_uri(last_frame[0])}, "role": "last_frame"})
        if reference_images is not None:
            if reference_images.shape[0] > MAX_REFERENCES[model]:
                raise ValueError(f"{model} takes at most {MAX_REFERENCES[model]} reference images.")
            for img in reference_images:
                content.append({"type": "image_url", "image_url": {"url": _data_uri(img)}, "role": "reference_image"})

        # Always send duration: without it the longest clip is held from the balance.
        body = {"model": MODELS[model], "content": content, "duration": duration,
                "resolution": resolution, "ratio": ratio, "generate_audio": generate_audio}
        status, out = _request("POST", f"{VIDEO_BASE}/contents/generations/tasks", key, body)
        if status != 200 or "id" not in out:
            raise RuntimeError(f"Submit failed ({status}): {json.dumps(out)}")
        task_id = out["id"]
        print(f"[HaryAI Seedance] task {task_id} submitted")

        # Poll every 10 s. Dropped connections, 429 and 5xx are retried: the task keeps running.
        while True:
            for _ in range(10):
                _interrupted()
                time.sleep(1)
            try:
                status, task = _request("GET", f"{VIDEO_BASE}/contents/generations/tasks/{task_id}", key)
            except (urllib.error.URLError, OSError, TimeoutError):
                continue
            if status == 429 or status >= 500:
                continue
            if status != 200:
                raise RuntimeError(f"Query failed ({status}): {json.dumps(task)}")
            if task.get("status") == "failed":
                # Failed and moderated tasks are refunded in full.
                raise RuntimeError(f"Seedance task failed: {json.dumps(task.get('error'))}. Change the prompt or images and run again.")
            if task.get("status") == "succeeded":
                break

        # The link needs no key, redirects to storage and expires after 24 hours.
        out_dir = os.path.join(folder_paths.get_output_directory(), "haryai")
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f"{task_id}.mp4")
        for attempt in range(5):
            try:
                urllib.request.urlretrieve(task["content"]["video_url"], path)
                break
            except (urllib.error.URLError, OSError):
                if attempt == 4:
                    raise
                time.sleep(5)
        print(f"[HaryAI Seedance] saved {path}")
        return (_video_output(path), task_id)


class HaryAIImage:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "",
                                      "tooltip": "What to draw, or for reference images, what to change. Refer to them as Image 1, Image 2."}),
                "model": (list(IMAGE_MODELS), {"default": "Seedream 5.5"}),
                "size": (["1K", "1.5K", "2K", "4K"], {"default": "1K", "tooltip": "Seedream: 1K, 1.5K, 2K. Nano Banana: 1K, 2K, 4K."}),
                "ratio": (IMAGE_RATIOS, {"default": "1:1"}),
                "count": ("INT", {"default": 1, "min": 1, "max": 4, "tooltip": "Seedream only; Nano Banana makes one image."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFF,
                                 "tooltip": "Change it to make new images from the same inputs. Not sent to the model."}),
            },
            "optional": {
                "images": ("IMAGE", {"tooltip": "Reference images or the image to edit (a batch, up to 14). Each is billed for Seedream."}),
                "api_key": ("STRING", {"default": "", "tooltip": "Your HaryAI key. It is saved in the workflow file: clear it before you share one."}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "run"
    CATEGORY = "HaryAI/image"
    DESCRIPTION = "Seedream 5.5, Nano Banana 2.1 and Nano Banana 2 through HaryAI (https://haryai.com). Text to image, reference images and edits."

    def run(self, prompt, model, size, ratio, count, seed, images=None, api_key=""):
        key = (api_key or "").strip()
        if not key:
            raise ValueError(NO_KEY)
        if not prompt.strip():
            raise ValueError("The prompt is empty.")
        if size not in IMAGE_SIZES[model]:
            raise ValueError(f"{model} has {', '.join(IMAGE_SIZES[model])} only.")
        if images is not None and images.shape[0] > 14:
            raise ValueError("At most 14 images.")
        model_id = IMAGE_MODELS[model]

        if model == "Seedream 5.5":
            body = {"model": model_id, "prompt": prompt, "n": count, "size": _seedream_size(ratio, size),
                    "response_format": "b64_json", "watermark": False}
            if images is not None:
                body["image"] = [_data_uri(img) for img in images]
            status, out = _request("POST", f"{API}/v1/images/generations", key, body, timeout=300)
        elif images is not None:
            data, ctype = _multipart({"model": model_id, "prompt": prompt, "aspect_ratio": ratio, "image_size": size},
                                     [_jpeg(img) for img in images])
            status, out = _request("POST", f"{API}/v1/images/edits", key, data, timeout=300, content_type=ctype)
        else:
            body = {"model": model_id, "prompt": prompt, "aspect_ratio": ratio, "image_size": size}
            status, out = _request("POST", f"{API}/v1/images/generations", key, body, timeout=300)

        items = out.get("data") if isinstance(out, dict) else None
        if status != 200 or not items:
            raise RuntimeError(f"Image request failed ({status}): {json.dumps(out)}")
        tensors = []
        for item in items:
            img = Image.open(io.BytesIO(base64.b64decode(item["b64_json"]))).convert("RGB")
            tensors.append(torch.from_numpy(np.asarray(img).astype(np.float32) / 255.0))
        if len({t.shape for t in tensors}) > 1:
            tensors = tensors[:1]  # a batch needs one size
        return (torch.stack(tensors),)


NODE_CLASS_MAPPINGS = {"HaryAISeedance": HaryAISeedance, "HaryAIImage": HaryAIImage}
NODE_DISPLAY_NAME_MAPPINGS = {"HaryAISeedance": "Seedance 2.5 (HaryAI)", "HaryAIImage": "Seedream / Nano Banana (HaryAI)"}
