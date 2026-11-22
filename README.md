# Seedance 2.5 in ComfyUI (HaryAI)

[中文](README.zh-CN.md)

A ComfyUI node for Seedance 2.5 and Seedance 2.5 Flash, ByteDance's video models, through [HaryAI](https://haryai.com/en/seedance-2-5-comfyui?utm_source=github&utm_medium=readme&utm_campaign=seedance-comfyui). Seedance 2.5 costs 12% less than BytePlus's official price, needs no BytePlus account and no Comfy credits: it bills your HaryAI balance.

One node, **Seedance 2.5 (HaryAI)** under HaryAI/video:

- text to video
- image to video from a first frame, optionally with a last frame
- up to 4 reference images that keep a character or a product
- generated sound, and spoken lines with lip sync
- outputs a standard VIDEO (connect Save Video) and the task id

## Install

In ComfyUI Manager, search for "Seedance 2.5 (HaryAI)". Or:

```sh
cd ComfyUI/custom_nodes
git clone https://github.com/sunsiyuan/seedance-comfyui
```

No extra Python packages. Restart ComfyUI.

## Key

Get a key on your [HaryAI account page](https://haryai.com/en/dashboard?utm_source=github&utm_medium=readme&utm_campaign=seedance-comfyui) and start ComfyUI with it in the environment:

```sh
export HARYAI_KEY=...
python main.py
```

Or paste it into the node's `api_key` field. A key typed there is saved inside the workflow file, so clear it before you share a workflow.

## Inputs

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
| reference_images | A batch of up to 4 images. Not together with first and last frame |

The clip is also saved to `ComfyUI/output/haryai/<task id>.mp4`.

## Cost

Paid per second of video from your HaryAI balance: Seedance 2.5 at 720p is $0.203 a second, Seedance 2.5 Flash at 480p is $0.059. A failed or moderated task is refunded. All prices: [Seedance API pricing](https://haryai.com/en/seedance-api-pricing?utm_source=github&utm_medium=readme&utm_campaign=seedance-comfyui).

## Related

- [seedance-2.5-api](https://github.com/sunsiyuan/seedance-2.5-api): the API, curl examples, Q&A
- [seedance-skill](https://github.com/sunsiyuan/seedance-skill): Seedance 2.5 as a Claude Code and Codex skill
- [n8n-nodes-haryai](https://github.com/sunsiyuan/n8n-nodes-haryai): the same in n8n (npm `n8n-nodes-haryai`)
- [nano-banana-api](https://github.com/sunsiyuan/nano-banana-api): Nano Banana 2.1 and 2 through the OpenAI images API or Gemini's own format
- API reference: [docs/video.md](https://haryai.com/docs/video.md)

MIT. Prices as of 2026-11-22.
