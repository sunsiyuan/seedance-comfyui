# 在 ComfyUI 里用 Seedance 2.5、Seedream 和 Nano Banana（HaryAI）

[English](README.md)

通过 [HaryAI](https://haryai.com/zh/seedance-2-5-comfyui?utm_source=github&utm_medium=readme&utm_campaign=seedance-comfyui) 在 ComfyUI 里调用字节的视频模型 Seedance 2.5，以及图片模型 Seedream 5.5 和 Nano Banana。Seedance 2.5 是 BytePlus 官方价 88 折，Seedream 8 折，Nano Banana 5 折。不用开 BytePlus 或 Google 账号，也不扣 Comfy 的积分，费用从你的 HaryAI 余额扣。

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

在 ComfyUI Manager 里选 **Install via Git URL**，填 `https://github.com/haryai-com/seedance-comfyui`。或者：

```sh
cd ComfyUI/custom_nodes
git clone https://github.com/haryai-com/seedance-comfyui
```

不需要额外安装 Python 包。装好后重启 ComfyUI。

## Key

在 [HaryAI 账户页](https://haryai.com/zh/dashboard?utm_source=github&utm_medium=readme&utm_campaign=seedance-comfyui) 复制 key，填进节点的 `api_key`。key 会存进工作流文件，分享工作流之前记得清空。

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

成片也会存到 `ComfyUI/output/haryai/<任务 id>.mp4`。

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

从 HaryAI 余额扣费。视频按秒：Seedance 2.5 720p 每秒 $0.203，Seedance 2.5 Flash 480p 每秒 $0.059。图片：Seedream 5.5 1K 每张 $0.016，Nano Banana 2.1 1K 每张 $0.0168。失败或审核没过的请求不扣费。全部价格见 [价格页](https://haryai.com/zh/pricing?utm_source=github&utm_medium=readme&utm_campaign=seedance-comfyui)。

## 相关

- [seedance-2.5-api](https://github.com/haryai-com/seedance-2.5-api)：接口本身、curl 示例和常见问题
- [seedance-skill](https://github.com/haryai-com/seedance-skill)：Claude Code 和 Codex 用的 Seedance 2.5 skill
- [n8n-nodes-haryai](https://github.com/haryai-com/n8n-nodes-haryai)：在 n8n 里用（npm 包 `n8n-nodes-haryai`）
- [nano-banana-api](https://github.com/haryai-com/nano-banana-api)：用 OpenAI 图片接口或 Gemini 原生格式调 Nano Banana 2.1 和 2
- 接口文档：[docs/video.md](https://haryai.com/docs/video.md)、[docs/image.md](https://haryai.com/docs/image.md)

MIT 许可。价格截至 2026-11-27。
