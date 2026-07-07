/*
 * Jenkins Pipeline
 * 功能: 自动拉取代码 -> 构建镜像 -> 推送到镜像仓库 -> 部署到 K8s
 *
 * 前置条件:
 *   1. Jenkins 安装以下插件:
 *      - Pipeline
 *      - Git
 *      - Docker Pipeline
 *      - Kubernetes CLI
 *      - Credentials Binding
 *
 *   2. Jenkins 配置凭据:
 *      - github-credentials: GitHub 访问凭据 (Username with password 或 SSH)
 *      - docker-registry-credentials: Docker 镜像仓库凭据 (Username with password)
 *      - kubeconfig: K8s 集群 kubeconfig 文件 (Secret file)
 *
 *   3. Jenkins 全局工具配置:
 *      - Docker
 *      - kubectl
 */

pipeline {
    agent any

    environment {
        // ===== 请修改以下变量 =====
        // GitHub 仓库地址
        GIT_REPO      = 'https://github.com/usermao-cpu/demo01.git'
        GIT_BRANCH    = 'main'

        // Docker 镜像配置
        DOCKER_REGISTRY = 'docker.io'                    // 镜像仓库地址
        DOCKER_IMAGE    = 'usermao-cpu/library-management' // 镜像名称
        IMAGE_TAG       = "${BUILD_NUMBER}"

        // K8s 配置
        K8S_NAMESPACE   = 'library-system'
        K8S_DEPLOYMENT  = 'library-app'

        // 完整镜像标签
        FULL_IMAGE = "${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${IMAGE_TAG}"
    }

    stages {
        stage('① 拉取代码') {
            steps {
                echo "=== 拉取代码: ${GIT_REPO} (${GIT_BRANCH}) ==="
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: "${GIT_BRANCH}"]],
                    userRemoteConfigs: [[
                        url: "${GIT_REPO}",
                        credentialsId: 'github-credentials'
                    ]]
                ])
            }
        }

        stage('② 代码审查 & 测试') {
            parallel {
                stage('代码检查') {
                    steps {
                        echo "=== 运行代码检查 ==="
                        sh '''
                            # Python 语法检查
                            python3 -m py_compile app.py
                            python3 -m py_compile models.py
                            echo "✓ Python 语法检查通过"
                        '''
                    }
                }
                stage('单元测试') {
                    steps {
                        echo "=== 运行单元测试 ==="
                        sh '''
                            pip install -r requirements.txt -q
                            python3 -c "
                            from app import app
                            with app.test_client() as c:
                                resp = c.get('/health')
                                assert resp.status_code == 200
                                print('✓ 健康检查测试通过')
                                resp = c.get('/')
                                assert resp.status_code == 200
                                print('✓ 首页加载测试通过')
                            "
                        '''
                    }
                }
            }
        }

        stage('③ 构建 Docker 镜像') {
            steps {
                echo "=== 构建镜像: ${FULL_IMAGE} ==="
                script {
                    docker.build("${DOCKER_IMAGE}:${IMAGE_TAG}")
                }
            }
        }

        stage('④ 推送镜像到仓库') {
            steps {
                echo "=== 推送镜像: ${FULL_IMAGE} ==="
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-registry-credentials') {
                        docker.image("${DOCKER_IMAGE}:${IMAGE_TAG}").push()
                        docker.image("${DOCKER_IMAGE}:${IMAGE_TAG}").push('latest')
                    }
                }
            }
        }

        stage('⑤ 部署到 K8s 集群') {
            steps {
                echo "=== 部署到 K8s 集群 ==="
                script {
                    // 使用 kubeconfig 文件连接到 K8s
                    withKubeConfig([credentialsId: 'kubeconfig']) {
                        sh '''
                            # 创建 namespace (如果不存在)
                            kubectl create namespace ${K8S_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

                            # 更新 deployment 镜像
                            kubectl set image deployment/${K8S_DEPLOYMENT} \
                                -n ${K8S_NAMESPACE} \
                                library-app=${FULL_IMAGE} \
                                --record

                            # 检查 rollout 状态
                            kubectl rollout status deployment/${K8S_DEPLOYMENT} \
                                -n ${K8S_NAMESPACE} \
                                --timeout=5m
                        '''
                    }
                }
            }
        }
    }

    post {
        success {
            echo "=== 部署成功! ==="
            script {
                withKubeConfig([credentialsId: 'kubeconfig']) {
                    sh '''
                        echo "服务状态:"
                        kubectl get all -n ${K8S_NAMESPACE}
                        echo ""
                        echo "当前镜像版本: ${FULL_IMAGE}"
                    '''
                }
            }
        }

        failure {
            echo "=== 部署失败! ==="
            // 可以添加通知: Slack / 邮件等
        }

        always {
            echo "=== Pipeline 执行完毕 ==="
        }
    }
}
