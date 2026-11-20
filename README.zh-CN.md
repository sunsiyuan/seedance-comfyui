# 在 ComfyUI 里用 Seedance 2.5（HaryAI）

[English](README.md)

一个 ComfyUI 节点，通过 [HaryAI](https://haryai.com/zh/seedance-2-5-comfyui?utm_source=github&utm_medium=readme&utm_campaign=seedance-comfyui) 调用字节的视频模型 Seedance 2.5 和 Seedance 2.5 Flash。价格是 BytePlus 官方价 88 折，不用开 BytePlus 账号，也不扣 Comfy 的积分，费用从你的 HaryAI 余额扣。

节点名叫 **Seedance 2.5 (HaryAI)**，在 HaryAI/video 分类下：

- 文生视频
- 用首帧做图生视频，可以再加一张尾帧
- 最多 4 张参考图，保持同一个角色或同一件商品
- 生成声音，台词配音并对口型
- 输出标准的 VIDEO（接 Save Video 节点）和任务 id

## 安装

在 ComfyUI Manager 里搜 "Seedance 2.5 (HaryAI)"。或者：

```sh
cd ComfyUI/custom_nodes
git clone https://github.com/sunsiyuan/seedance-comfyui
```

不需要额外安装 Python 包。装好后重启 ComfyUI。

## Key

在 [HaryAI 账户页](https://haryai.com/zh/dashboard?utm_source=github&utm_medium=readme&utm_campaign=seedance-comfyui) 复制 key，启动 ComfyUI 前设成环境变量：

```sh
export HARYAI_KEY=...
python main.py
```

也可以直接填进节点的 `api_key`。填在这里的 key 会存进工作流文件，分享工作流之前记得清空。

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

成片也会存到 `ComfyUI/output/haryai/<任务 id>.mp4`。

## 费用

按视频秒数从 HaryAI 余额扣费：Seedance 2.5 720p 每秒 $0.203，Seedance 2.5 Flash 480p 每秒 $0.059。失败或审核没过的任务全额退款。全部价格见 [Seedance API 价格](https://haryai.com/zh/seedance-api-pricing?utm_source=github&utm_medium=readme&utm_campaign=seedance-comfyui)。

## 相关

- [seedance-2.5-api](https://github.com/sunsiyuan/seedance-2.5-api)：接口本身、curl 示例和常见问题
- [seedance-skill](https://github.com/sunsiyuan/seedance-skill)：Claude Code 和 Codex 用的 Seedance 2.5 skill
- 接口文档：[docs/video.md](https://haryai.com/docs/video.md)

MIT 许可。价格截至 2026-11-20。
