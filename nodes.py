"""Seedance 2.5 through HaryAI (Volcengine / BytePlus ModelArk format) as a ComfyUI node.

Standard library only. The key comes from the HARYAI_KEY environment variable,
or from the node's api_key field (that one is saved inside the workflow file).
API reference: https://haryai.com/docs/video.md
"""
import base64
import io
import json
import os
import time
import urllib.error
import urllib.request

import numpy as np
from PIL import Image

import folder_paths

BASE = os.environ.get("HARYAI_BASE_URL", "https://api.haryai.com/api/v3").rstrip("/")
MODELS = {
    "Seedance 2.5": "dreamina-seedance-2-5-260628",
    "Seedance 2.5 Flash": "dreamina-seedance-2-5-flash-261115",
}
RESOLUTIONS = {"Seedance 2.5": ["480p", "720p", "1080p"], "Seedance 2.5 Flash": ["480p", "720p"]}
RATIOS = ["16:9", "9:16", "1:1", "4:3", "3:4", "21:9"]


def _interrupted():
    try:
        import comfy.model_management as mm
        mm.throw_exception_if_processing_interrupted()
    except ImportError:
        pass


def _request(method, url, key, body=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "seedance-comfyui"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except ValueError:
            return e.code, {}


def _data_uri(image):
    """One ComfyUI IMAGE (H, W, C float 0..1) as a JPEG data URI."""
    arr = np.clip(image.cpu().numpy() * 255.0, 0, 255).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).convert("RGB").save(buf, format="JPEG", quality=95)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def _video_output(path):
    try:
        from comfy_api.input_impl import VideoFromFile
        return VideoFromFile(path)
    except ImportError:  # older ComfyUI without a VIDEO type
        return path


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
                "reference_images": ("IMAGE", {"tooltip": "Up to 4 images (a batch) that keep a character or product. Not together with first/last frame."}),
                "api_key": ("STRING", {"default": "", "tooltip": "Leave empty to use the HARYAI_KEY environment variable. A key typed here is saved in the workflow file."}),
            },
        }

    RETURN_TYPES = ("VIDEO", "STRING")
    RETURN_NAMES = ("video", "task_id")
    FUNCTION = "run"
    CATEGORY = "HaryAI/video"
    DESCRIPTION = "Seedance 2.5 and Seedance 2.5 Flash through HaryAI (https://haryai.com). Text to video, first and last frame, reference images, sound."

    def run(self, prompt, model, resolution, ratio, duration, generate_audio, seed,
            first_frame=None, last_frame=None, reference_images=None, api_key=""):
        key = (api_key or "").strip() or os.environ.get("HARYAI_KEY", "")
        if not key:
            raise ValueError("No HaryAI key. Set the HARYAI_KEY environment variable before starting ComfyUI, "
                             "or fill in api_key. Get a key at https://haryai.com")
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
            if reference_images.shape[0] > 4:
                raise ValueError("At most 4 reference images.")
            for img in reference_images:
                content.append({"type": "image_url", "image_url": {"url": _data_uri(img)}, "role": "reference_image"})

        # Always send duration: without it the longest clip is held from the balance.
        body = {"model": MODELS[model], "content": content, "duration": duration,
                "resolution": resolution, "ratio": ratio, "generate_audio": generate_audio}
        status, out = _request("POST", f"{BASE}/contents/generations/tasks", key, body)
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
                status, task = _request("GET", f"{BASE}/contents/generations/tasks/{task_id}", key)
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


NODE_CLASS_MAPPINGS = {"HaryAISeedance": HaryAISeedance}
NODE_DISPLAY_NAME_MAPPINGS = {"HaryAISeedance": "Seedance 2.5 (HaryAI)"}
