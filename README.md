# Seedance 2.5, Seedream and Nano Banana in ComfyUI (HaryAI)

[中文](README.zh-CN.md)

ComfyUI nodes for ByteDance's Seedance 2.5 video and for Seedream 5.5 and Nano Banana images, through [HaryAI](https://haryai.com/en/seedance-2-5-comfyui?utm_source=github&utm_medium=readme&utm_campaign=seedance-comfyui). Seedance 2.5 costs 12% less than BytePlus's official price, Seedream 20% less and Nano Banana 50% less. No BytePlus or Google account and no Comfy credits: it bills your HaryAI balance.

**Seedance 2.5 (HaryAI)**, under HaryAI/video:

- text to video
- image to video from a first frame, optionally with a last frame
- reference images that keep a character or a product (up to 30; Flash 10)
- generated sound, and spoken lines with lip sync
- outputs a standard VIDEO (connect Save Video) and the task id

**Seedream / Nano Banana (HaryAI)**, under HaryAI/image:

- Seedream 5.5, Nano Banana 2.1 and Nano Banana 2
- text to image, and reference images or an image to edit (up to 14)
- outputs a standard IMAGE batch

## Install

In ComfyUI Manager choose **Install via Git URL** and paste `https://github.com/haryai-com/seedance-comfyui`. Or:

```sh
cd ComfyUI/custom_nodes
git clone https://github.com/haryai-com/seedance-comfyui
```

No extra Python packages. Restart ComfyUI.

## Key

Copy a key from your [HaryAI account page](https://haryai.com/en/dashboard?utm_source=github&utm_medium=readme&utm_campaign=seedance-comfyui) into the node's `api_key` field. It is saved inside the workflow file, so clear it before you share a workflow.

## Video inputs

| Input | What it does |
|---|---|
| prompt | Subject, action, camera, light, style. Put spoken lines in quotes and turn on generate_audio |
| model | Seedance 2.5, or Seedance 2.5 Flash for cheaper drafts |
| resolution | 480p, 720p, 1080p (Flash: 480p and 720p) |
| ratio | 16:9, 9:16, 1:1, 4:3, 3:4, 21:9 |
| duration | 4 to 30 seconds |
| generate_audio | Sound and speech |
| seed | Change it to make a new clip from the same inputs. ComfyUI reuses a cached result otherwise. Not sent to the model |
| first_frame, last_frame | Image to video |
| reference_images | A batch of up to 30 images (Flash: 10). Not together with first and last frame |

The clip is also saved to `ComfyUI/output/haryai/<task id>.mp4`.

## Image inputs

| Input | What it does |
|---|---|
| prompt | What to draw, or what to change in the images. Refer to them as Image 1, Image 2 |
| model | Seedream 5.5, Nano Banana 2.1, Nano Banana 2 |
| size | Seedream: 1K, 1.5K, 2K. Nano Banana: 1K, 2K, 4K |
| ratio | 1:1, 3:4, 4:3, 9:16, 16:9, 2:3, 3:2, 21:9 |
| count | 1 to 4 images (Seedream; Nano Banana makes one) |
| images | Reference images or the image to edit, a batch of up to 14 |

## Cost

From your HaryAI balance. Video per second: Seedance 2.5 at 720p $0.203, Seedance 2.5 Flash at 480p $0.059. Images: Seedream 5.5 1K $0.016, Nano Banana 2.1 1K $0.0168. A failed or moderated request is not charged. All prices: [pricing](https://haryai.com/en/pricing?utm_source=github&utm_medium=readme&utm_campaign=seedance-comfyui).

## Related

- [seedance-2.5-api](https://github.com/haryai-com/seedance-2.5-api): the API, curl examples, Q&A
- [seedance-skill](https://github.com/haryai-com/seedance-skill): Seedance 2.5 as a Claude Code and Codex skill
- [n8n-nodes-haryai](https://github.com/haryai-com/n8n-nodes-haryai): the same in n8n (npm `n8n-nodes-haryai`)
- [nano-banana-api](https://github.com/haryai-com/nano-banana-api): Nano Banana 2.1 and 2 through the OpenAI images API or Gemini's own format
- API reference: [docs/video.md](https://haryai.com/docs/video.md), [docs/image.md](https://haryai.com/docs/image.md)

MIT. Prices as of 2026-11-27.
