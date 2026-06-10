# AI Short Video Factory · AI 短视频批量生产平台

> 个人开源复刻 MoneyPrinterTurbo 核心流程的短视频批量生产流水线。

## 核心特性

- **端到端自动生成**：输入商品主题 → 文案生成 → 素材匹配 → TTS 配音 → 字幕合成 → 批量成片
- **竖屏适配**：9:16 抖音 / 视频号规格，Hook 3 秒开头结构
- **批量产出**：一次配置批量生成 N 条不同角度的带货视频
- **模板化文案**：卖点/痛点/场景/促销多模板，可选 LLM 生成
- **可插拔 TTS**：默认 edge-tts，无环境时降级为静音占位（保持时间轴正确）
- **ffmpeg 装配**：本机有 ffmpeg 即真实合成，否则输出装配清单

## 快速开始

```bash
# 演练模式（无需任何依赖）
python video_factory.py --topic "冰感内裤" --count 2 --dry-run

# 真实生成（需要 ffmpeg，可选 edge-tts）
python video_factory.py --topic "冰感内裤" --count 3 --assets assets/
```

## 流水线

```
主题 → 文案(Hook+卖点+行动号召) → 素材匹配 → TTS(时长) → SRT字幕 → ffmpeg装配 → outputs/
```

## License

MIT
