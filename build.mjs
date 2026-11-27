#!/usr/bin/env node
// Writes README.md and README.zh-CN.md. The discount and per-second prices are
// read from https://haryai.com/llms.txt, so nothing here is typed twice.

import { writeFile } from "node:fs/promises";

const llms = await (await fetch("https://haryai.com/llms.txt")).text();
const share = Number(llms.match(/at (\d+)% of BytePlus's official price/)[1]);
const sec = (model, res) => llms.split("\n").find((l) => l.includes(`(${model})`)).match(new RegExp(`${res} \\$([\\d.]+)`))[1];
const full720 = sec("dreamina-seedance-2-5-260628", "720p");
const flash480 = sec("dreamina-seedance-2-5-flash-261115", "480p");
const img = (model) => {
  const line = llms.split("\n").find((l) => l.includes(`(${model}), `));
  return { off: 100 - Number(line.match(/(\d+)% of the official price/)[1]), k1: line.match(/1K \$([\d.]+)/)[1] };
};
const seedream = img("dola-seedream-5-5-261028");
const nb21 = img("gemini-nano-banana-2.1");
const zhe = (pct) => (pct % 10 === 0 ? pct / 10 : pct); // 80 -> 8, 88 -> 88
const utm = (path) => `https://haryai.com${path}?utm_source=github&utm_medium=readme&utm_campaign=seedance-comfyui`;
const today = new Date().toISOString().slice(0, 10);

const en = `# Seedance 2.5, Seedream and Nano Banana in ComfyUI (HaryAI)

[中文](README.zh-CN.md)

ComfyUI nodes for ByteDance's Seedance 2.5 video and for Seedream 5.5 and Nano Banana images, through [HaryAI](${utm("/en/seedance-2-5-comfyui")}). Seedance 2.5 costs ${100 - share}% less than BytePlus's official price, Seedream ${seedream.off}% less and Nano Banana ${nb21.off}% less. No BytePlus or Google account and no Comfy credits: it bills your HaryAI balance.

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

In ComfyUI Manager choose **Install via Git URL** and paste \`https://github.com/haryai-com/seedance-comfyui\`. Or:

\`\`\`sh
cd ComfyUI/custom_nodes
git clone https://github.com/haryai-com/seedance-comfyui
\`\`\`

No extra Python packages. Restart ComfyUI.

## Key

Copy a key from your [HaryAI account page](${utm("/en/dashboard")}) into the node's \`api_key\` field. It is saved inside the workflow file, so clear it before you share a workflow.

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

The clip is also saved to \`ComfyUI/output/haryai/<task id>.mp4\`.

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

From your HaryAI balance. Video per second: Seedance 2.5 at 720p $${full720}, Seedance 2.5 Flash at 480p $${flash480}. Images: Seedream 5.5 1K $${seedream.k1}, Nano Banana 2.1 1K $${nb21.k1}. A failed or moderated request is not charged. All prices: [pricing](${utm("/en/pricing")}).

## Related

- [seedance-2.5-api](https://github.com/haryai-com/seedance-2.5-api): the API, curl examples, Q&A
- [seedance-skill](https://github.com/haryai-com/seedance-skill): Seedance 2.5 as a Claude Code and Codex skill
- [n8n-nodes-haryai](https://github.com/haryai-com/n8n-nodes-haryai): the same in n8n (npm \`n8n-nodes-haryai\`)
- [nano-banana-api](https://github.com/haryai-com/nano-banana-api): Nano Banana 2.1 and 2 through the OpenAI images API or Gemini's own format
- API reference: [docs/video.md](https://haryai.com/docs/video.md), [docs/image.md](https://haryai.com/docs/image.md)

MIT. Prices as of ${today}.
`;

const zh = `# 在 ComfyUI 里用 Seedance 2.5、Seedream 和 Nano Banana（HaryAI）

[English](README.md)

通过 [HaryAI](${utm("/zh/seedance-2-5-comfyui")}) 在 ComfyUI 里调用字节的视频模型 Seedance 2.5，以及图片模型 Seedream 5.5 和 Nano Banana。Seedance 2.5 是 BytePlus 官方价 ${zhe(share)} 折，Seedream ${zhe(100 - seedream.off)} 折，Nano Banana ${zhe(100 - nb21.off)} 折。不用开 BytePlus 或 Google 账号，也不扣 Comfy 的积分，费用从你的 HaryAI 余额扣。

**Seedance 2.5 (HaryAI)**，在 HaryAI/video 分类下：

- 文生视频
- 用首帧做图生视频，可以再加一张尾帧
- 参考图保持同一个角色或同一件商品（最多 30 张，Flash 10 张）
- 生成声音，台词配音并对口型
- 输出标准的 VIDEO（接 Save Video 节点）和任务 id

**Seedream / Nano Banana (HaryAI)**，在 HaryAI/image 分类下：

- Seedream 5.5、Nano Banana 2.1、Nano Banana 2
- 文生图，也可以放参考图或要修改的图（最多 14 张）
- 输出标准的 IMAGE

## 安装

在 ComfyUI Manager 里选 **Install via Git URL**，填 \`https://github.com/haryai-com/seedance-comfyui\`。或者：

\`\`\`sh
cd ComfyUI/custom_nodes
git clone https://github.com/haryai-com/seedance-comfyui
\`\`\`

不需要额外安装 Python 包。装好后重启 ComfyUI。

## Key

在 [HaryAI 账户页](${utm("/zh/dashboard")}) 复制 key，填进节点的 \`api_key\`。key 会存进工作流文件，分享工作流之前记得清空。

## 视频节点的输入

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
| reference_images | 一批最多 30 张图（Flash 10 张），不能和首尾帧一起用 |

成片也会存到 \`ComfyUI/output/haryai/<任务 id>.mp4\`。

## 图片节点的输入

| 输入 | 作用 |
|---|---|
| prompt | 要画什么，或者要把图改成什么样。引用参考图时写 Image 1、Image 2 |
| model | Seedream 5.5、Nano Banana 2.1、Nano Banana 2 |
| size | Seedream：1K、1.5K、2K。Nano Banana：1K、2K、4K |
| ratio | 1:1、3:4、4:3、9:16、16:9、2:3、3:2、21:9 |
| count | 1 到 4 张（Seedream；Nano Banana 每次一张） |
| images | 参考图或要修改的图，一批最多 14 张 |

## 费用

从 HaryAI 余额扣费。视频按秒：Seedance 2.5 720p 每秒 $${full720}，Seedance 2.5 Flash 480p 每秒 $${flash480}。图片：Seedream 5.5 1K 每张 $${seedream.k1}，Nano Banana 2.1 1K 每张 $${nb21.k1}。失败或审核没过的请求不扣费。全部价格见 [价格页](${utm("/zh/pricing")})。

## 相关

- [seedance-2.5-api](https://github.com/haryai-com/seedance-2.5-api)：接口本身、curl 示例和常见问题
- [seedance-skill](https://github.com/haryai-com/seedance-skill)：Claude Code 和 Codex 用的 Seedance 2.5 skill
- [n8n-nodes-haryai](https://github.com/haryai-com/n8n-nodes-haryai)：在 n8n 里用（npm 包 \`n8n-nodes-haryai\`）
- [nano-banana-api](https://github.com/haryai-com/nano-banana-api)：用 OpenAI 图片接口或 Gemini 原生格式调 Nano Banana 2.1 和 2
- 接口文档：[docs/video.md](https://haryai.com/docs/video.md)、[docs/image.md](https://haryai.com/docs/image.md)

MIT 许可。价格截至 ${today}。
`;

await writeFile("README.md", en);
await writeFile("README.zh-CN.md", zh);
console.log(`README.md, README.zh-CN.md (share ${share}%, 720p $${full720}/s, flash 480p $${flash480}/s, seedream ${seedream.off}% off $${seedream.k1}, nb2.1 ${nb21.off}% off $${nb21.k1})`);
