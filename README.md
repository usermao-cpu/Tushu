# 📚 图书管理系统 (Library Management System)

基于 Flask 的简单图书管理系统，支持图书的增删改查和搜索功能。

## 技术栈

- **后端**: Python Flask
- **数据库**: SQLite
- **前端**: HTML + CSS (响应式设计)
- **部署**: Docker + Kubernetes
- **CI/CD**: Jenkins Pipeline

## 快速开始

### 本地运行

```bash
pip install -r requirements.txt
python app.py
```

访问 http://localhost:5000

### Docker 运行

```bash
docker build -t library-management .
docker run -d -p 5000:5000 --name library-app library-management
```

### Docker Compose

```bash
docker-compose up -d
```

## 项目结构

```
library-management/
├── app.py                 # Flask 主应用
├── models.py              # 数据库模型
├── requirements.txt       # Python 依赖
├── Dockerfile             # Docker 构建文件
├── docker-compose.yml     # Docker Compose 配置
├── Jenkinsfile            # Jenkins CI/CD Pipeline
├── k8s/                   # Kubernetes 部署清单
│   ├── namespace.yaml     # 命名空间
│   ├── configmap.yaml     # 配置
│   ├── secret.yaml        # 密钥
│   ├── deployment.yaml    # 部署 + PVC
│   ├── service.yaml       # 服务
│   ├── ingress.yaml       # 入口
│   └── hpa.yaml           # 自动扩缩容
├── templates/             # HTML 模板
├── static/                # 静态文件
└── README.md
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/books | 获取所有图书 |
| POST | /api/books | 添加图书 |
| DELETE | /api/books/:id | 删除图书 |
| GET | /health | 健康检查 |

## Kubernetes 部署

```bash
# 1. 创建资源
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# 2. 查看部署状态
kubectl get all -n library-system

# 3. 查看 Pod 日志
kubectl logs -f -n library-system -l app=library-app
```

## CI/CD 流程 (Jenkins)

1. 开发推送代码到 GitHub
2. Jenkins 自动拉取最新代码
3. 运行代码检查和测试
4. 构建 Docker 镜像并推送
5. 自动部署到 K8s 集群

---

> 配置详情见 [Jenkinsfile](Jenkinsfile) 和 [k8s/](k8s/) 目录
