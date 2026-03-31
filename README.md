# 3MF Gcode批量提取工具

从.3mf文件中批量提取gcode文件的GUI工具。

## 安装

```bash
pip install tkinterdnd2
```

## 使用方法

1. 运行程序：
```bash
python 3mf_extractor.py
```

2. 拖拽.3mf文件到窗口
3. 选择输出目录（可选，默认当前目录）
4. 点击"开始提取"

## 功能特性

- ✓ 拖拽支持（文件或文件夹）
- ✓ 批量处理
- ✓ 自动处理文件名冲突（model → model_1 → model_2...）
- ✓ 错误处理（跳过损坏文件，继续处理）
- ✓ 实时进度显示

## 输出结构

```
输出目录/
├── model1/
│   ├── plate_1.gcode
│   └── plate_2.gcode
├── model2/
│   └── plate_1.gcode
└── model3_1/  (冲突自动重命名)
    └── plate_1.gcode
```

## 打包为独立程序（可选）

```bash
pip install pyinstaller
pyinstaller --onefile --windowed 3mf_extractor.py
```

生成的exe/app在 `dist/` 目录中。
