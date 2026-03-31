# 如何使用GitHub Actions自动打包

## 设置步骤

1. **初始化Git仓库（如果还没有）：**
```bash
cd /Users/a1212
git init
git add .
git commit -m "Initial commit: 3MF Gcode Extractor"
```

2. **创建GitHub仓库并推送：**
```bash
# 在GitHub上创建新仓库，然后：
git remote add origin https://github.com/你的用户名/3mf-gcode-extractor.git
git branch -M main
git push -u origin main
```

3. **触发自动打包：**

**方式1：创建版本标签（推荐）**
```bash
git tag v1.0.0
git push origin v1.0.0
```

**方式2：手动触发**
- 访问 GitHub仓库 → Actions → Build Executables → Run workflow

## 打包结果

打包完成后，会自动创建Release，包含：
- `3MF_Gcode_Extractor.exe` - Windows版本
- `3MF_Gcode_Extractor.dmg` - Mac版本

用户可以直接从GitHub Releases页面下载。

## 本地已有的Mac版本

当前目录已有打包好的Mac版本：
`/Users/a1212/dist/3MF_Gcode_Extractor.app`

可以直接使用或分发。
