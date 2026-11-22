#!/usr/bin/env node
// Writes README.md and README.zh-CN.md. The discount and per-second prices are
// read from https://haryai.com/llms.txt, so nothing here is typed twice.

import { writeFile } from "node:fs/promises";

const llms = await (await fetch("https://haryai.com/llms.txt")).text();
const share = Number(llms.match(/at (\d+)% of BytePlus's official price/)[1]);
const sec = (model, res) => llms.split("\n").find((l) => l.includes(`(${model})`)).match(new RegExp(`${res} \\$([\\d.]+)`))[1];
const full720 = sec("dreamina-seedance-2-5-260628", "720p");
const flash480 = sec("dreamina-seedance-2-5-flash-261115", "480p");
const utm = (path) => `https://haryai.com${path}?utm_source=github&utm_medium=readme&utm_campaign=seedance-comfyui`;
const today = new Date().toISOString().slice(0, 10);

const en = `# Seedance 2.5 in ComfyUI (HaryAI)

[中文](README.zh-CN.md)

A ComfyUI node for Seedance 2.5 and Seedance 2.5 Flash, ByteDance's video models, through [HaryAI](${utm("/en/seedance-2-5-comfyui")}). Seedance 2.5 costs ${100 - share}% less than BytePlus's official price, needs no BytePlus account and no Comfy credits: it bills your HaryAI balance.

One node, **Seedance 2.5 (HaryAI)** under HaryAI/video:

- text to video
- image to video from a first frame, optionally with a last frame
- up to 4 reference images that keep a character or a product
- generated sound, and spoken lines with lip sync
- outputs a standard VIDEO (connect Save Video) and the task id

## Install

In ComfyUI Manager, search for "Seedance 2.5 (HaryAI)". Or:

\`\`\`sh
cd ComfyUI/custom_nodes
git clone https://github.com/sunsiyuan/seedance-comfyui
\`\`\`

No extra Python packages. Restart ComfyUI.

## Key

Get a key on your [HaryAI account page](${utm("/en/dashboard")}) and start ComfyUI with it in the environment:

\`\`\`sh
export HARYAI_KEY=...
python main.py
\`\`\`

Or paste it into the node's \`api_key\` field. A key typed there is saved inside the workflow file, so clear it before you share a workflow.

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

The clip is also saved to \`ComfyUI/output/haryai/<task id>.mp4\`.

## Cost

Paid per second of video from your HaryAI balance: Seedance 2.5 at 720p is $${full720} a second, Seedance 2.5 Flash at 480p is $${flash480}. A failed or moderated task is refunded. All prices: [Seedance API pricing](${utm("/en/seedance-api-pricing")}).

## Related

- [seedance-2.5-api](https://github.com/sunsiyuan/seedance-2.5-api): the API, curl examples, Q&A
- [seedance-skill](https://github.com/sunsiyuan/seedance-skill): Seedance 2.5 as a Claude Code and Codex skill
- [n8n-nodes-haryai](https://github.com/sunsiyuan/n8n-nodes-haryai): the same in n8n (npm \`n8n-nodes-haryai\`)
- [nano-banana-api](https://github.com/sunsiyuan/nano-banana-api): Nano Banana 2.1 and 2 through the OpenAI images API or Gemini's own format
- API reference: [docs/video.md](https://haryai.com/docs/video.md)

MIT. Prices as of ${today}.
`;

const zh = `# 在 ComfyUI 里用 Seedance 2.5（HaryAI）

[English](README.md)

一个 ComfyUI 节点，通过 [HaryAI](${utm("/zh/seedance-2-5-comfyui")}) 调用字节的视频模型 Seedance 2.5 和 Seedance 2.5 Flash。价格是 BytePlus 官方价 ${share} 折，不用开 BytePlus 账号，也不扣 Comfy 的积分，费用从你的 HaryAI 余额扣。

节点名叫 **Seedance 2.5 (HaryAI)**，在 HaryAI/video 分类下：

- 文生视频
- 用首帧做图生视频，可以再加一张尾帧
- 最多 4 张参考图，保持同一个角色或同一件商品
- 生成声音，台词配音并对口型
- 输出标准的 VIDEO（接 Save Video 节点）和任务 id

## 安装

在 ComfyUI Manager 里搜 "Seedance 2.5 (HaryAI)"。或者：

\`\`\`sh
cd ComfyUI/custom_nodes
git clone https://github.com/sunsiyuan/seedance-comfyui
\`\`\`

不需要额外安装 Python 包。装好后重启 ComfyUI。

## Key

在 [HaryAI 账户页](${utm("/zh/dashboard")}) 复制 key，启动 ComfyUI 前设成环境变量：

\`\`\`sh
export HARYAI_KEY=...
python main.py
\`\`\`

也可以直接填进节点的 \`api_key\`。填在这里的 key 会存进工作流文件，分享工作流之前记得清空。

## 输入

| 输入 | 作用 |
|---|---|
| prompt | 主体、动作、镜头、光线、风格。台词写在引号里，并打开 generate_audio |
| model | Seedance 2.5，打草稿可以用更便宜的 Seedance 2.5 Flash |
| resolution | 480p、720p、1080p（Flash 只有 480p 和 720p） |
| ratio | 16:9、9:16、1:1、4:3、3:4、21:9 |
| duration | 4 到 30 秒 |
| generate_audio | 生成声音和台词 |
| seed | 输入不变但想重新生成时改一下。不改的话 ComfyUI 会直接用缓存的结果。不会传给模型 |
| first_frame、last_frame | 图生视频 |
| reference_images | 一批最多 4 张图，不能和首尾帧一起用 |

成片也会存到 \`ComfyUI/output/haryai/<任务 id>.mp4\`。

## 费用

按视频秒数从 HaryAI 余额扣费：Seedance 2.5 720p 每秒 $${full720}，Seedance 2.5 Flash 480p 每秒 $${flash480}。失败或审核没过的任务全额退款。全部价格见 [Seedance API 价格](${utm("/zh/seedance-api-pricing")})。

## 相关

- [seedance-2.5-api](https://github.com/sunsiyuan/seedance-2.5-api)：接口本身、curl 示例和常见问题
- [seedance-skill](https://github.com/sunsiyuan/seedance-skill)：Claude Code 和 Codex 用的 Seedance 2.5 skill
- [n8n-nodes-haryai](https://github.com/sunsiyuan/n8n-nodes-haryai)：在 n8n 里用（npm 包 \`n8n-nodes-haryai\`）
- [nano-banana-api](https://github.com/sunsiyuan/nano-banana-api)：用 OpenAI 图片接口或 Gemini 原生格式调 Nano Banana 2.1 和 2
- 接口文档：[docs/video.md](https://haryai.com/docs/video.md)

MIT 许可。价格截至 ${today}。
`;

await writeFile("README.md", en);
await writeFile("README.zh-CN.md", zh);
console.log(`README.md, README.zh-CN.md (share ${share}%, 720p $${full720}/s, flash 480p $${flash480}/s)`);
