# 3D 模型资产管理系统（Django + Three.js）

一个基于 **Django** 与 **Three.js** 的本地 3D 模型管理系统，支持用户注册登录、模型上传（GLB/GLTF/ZIP）、公开模型库浏览、在线预览（OrbitControls）、下载与删除等能力。

## 功能特性

- **用户体系**
  - 注册 / 登录 / 退出
  - 个人信息页（头像展示）
  - 个人信息编辑（支持头像上传 + 预览）

- **模型管理**
  - 上传：`.glb` / `.gltf` / `.zip`
    - ZIP 支持包含贴图/纹理等资源，服务端安全解压并自动寻找主模型文件
  - 列表：搜索 / 排序 / 分页
  - 详情：模型信息展示
  - 预览：Three.js 在线预览
    - 鼠标左键旋转
    - **按住鼠标中键拖动平移**
    - 鼠标右键缩放
    - 重置视角
    - 全屏预览
  - 下载 / 删除

- **公开模型库（模型管理入口）**
  - 左上角 **“模型管理”** 进入 **公开模型库**：仅展示所有用户的 **公开** 模型
  - 在公开模型库中：仅当模型 **归属为当前用户** 时才显示“删除”按钮

- **管理后台**
  - 管理后台入口为：`/root/`
  - 仅允许用户名为 **root** 且为 `staff` 的管理员登录
  - 登录页不提供后台入口按钮，需要手动访问 `/root/`

## 技术栈

- Python + Django
- SQLite（默认）
- Three.js（GLTFLoader / OrbitControls）

## 目录结构（核心）

- `project/`：Django 项目配置
- `app_assets/`：模型资产应用
- `templates/`：页面模板
- `static/`：站点样式（`site.css`）
- `media/`：上传文件存储目录（运行后自动生成）

## 环境准备

建议使用虚拟环境（venv / conda 均可），确保安装依赖：

```bash
pip install -r requirements.txt
```

## 初始化与运行

1) 迁移数据库：

```bash
python manage.py makemigrations
python manage.py migrate
```

2) 创建管理员（可选）：

如需进入 `/root/` 管理后台，请创建用户名为 `root` 的管理员，并确保为 staff：

```bash
python manage.py createsuperuser
```

3) 启动开发服务器：

```bash
python manage.py runserver
```

然后访问：

- 站点首页/资产列表：`http://127.0.0.1:8000/assets/`
- 公开模型库（左上角“模型管理”）：`http://127.0.0.1:8000/assets/public/`
- 上传：`http://127.0.0.1:8000/upload/`
- 个人信息：`http://127.0.0.1:8000/me/`
- 管理后台：`http://127.0.0.1:8000/root/`

## 上传说明

- 支持上传：
  - `.glb`
  - `.gltf`
  - `.zip`（包含 `.gltf` / `.glb` 主文件及其贴图等资源）

ZIP 上传会进行安全解压（避免路径穿越），并在解压结果中自动寻找主模型文件。

## 常见问题

- **访问 `/admin/` 返回 404**
  - 后台入口为 `/root/`

- **看不到公开模型库的“删除”按钮**
  - 公开模型库中只有模型归属是当前用户时才显示删除

## License

本项目使用 MIT License，详见 `LICENSE`。
