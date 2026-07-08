pipeline {
  agent {
    kubernetes {
      yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: base
    image: kubesphere/builder-base:v4.2.0
    command: ['cat']
    tty: true
    securityContext:
      privileged: true
  - name: jnlp
    image: jenkins/inbound-agent:3309.v27b_9314fd1a_4-1-jdk21
'''
    }
  }

  environment {
    // ------ Git ------
    GIT_URL    = 'https://github.com/usermao-cpu/Tushu.git'
    GIT_BRANCH = 'main'
    GIT_CRED   = 'github-credentials'

    // ------ 阿里云 ACR ------
    REGISTRY_HOST   = 'crpi-yu1tps10hq903zqm.cn-hongkong.personal.cr.aliyuncs.com'
    IMAGE_NAMESPACE = 'pfkj'
    IMAGE_NAME      = 'tushu'
    IMAGE_TAG       = "${BUILD_NUMBER}"
    FULL_IMAGE      = "${REGISTRY_HOST}/${IMAGE_NAMESPACE}/${IMAGE_NAME}:${IMAGE_TAG}"
    LATEST_IMAGE    = "${REGISTRY_HOST}/${IMAGE_NAMESPACE}/${IMAGE_NAME}:latest"
    ACR_CRED        = 'registry-auth'

    // ------ K8s ------
    K8S_NAMESPACE = 'pfkj'
    DEPLOY_NAME   = 'scp0001'
    CONTAINER_NAME = 'scp0001'
    K8S_KUBECONFIG = 'k8s-kubeconfig'
  }

  stages {
    stage('拉取代码') {
      steps {
        git(
          url: "${GIT_URL}",
          branch: "${GIT_BRANCH}",
          credentialsId: "${GIT_CRED}"
        )
        sh '''
          echo "===== 代码拉取完成 ====="
          echo "当前提交版本：$(git rev-parse --short HEAD)"
          echo "当前分支：$(git branch --show-current)"
        '''
      }
    }

    stage('构建镜像') {
      steps {
        container('base') {
          sh """
            echo "===== 配置 vfs 存储驱动 ====="
            mkdir -p /tmp/containers
            cat > /tmp/containers/storage.conf <<'EOF'
[storage]
driver = "vfs"
runroot = "/tmp/containers/run"
graphroot = "/tmp/containers/graph"
EOF
            export CONTAINERS_STORAGE_CONF=/tmp/containers/storage.conf

            echo "===== 替换国内镜像源 ====="
            # 临时替换 sources.list 为阿里云镜像源
            sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list

            echo "===== 开始构建镜像 ====="
            podman build --network=host -t ${FULL_IMAGE} .
            echo "镜像构建完成：${FULL_IMAGE}"
          """
        }
      }
    }

    stage('推送镜像') {
      steps {
        container('base') {
          withCredentials([usernamePassword(
            credentialsId: "${ACR_CRED}",
            usernameVariable: 'REGISTRY_USER',
            passwordVariable: 'REGISTRY_PWD'
          )]) {
            sh """
              echo "===== 配置 vfs 存储驱动 ====="
              mkdir -p /tmp/containers
              cat > /tmp/containers/storage.conf <<'EOF'
[storage]
driver = "vfs"
runroot = "/tmp/containers/run"
graphroot = "/tmp/containers/graph"
EOF
              export CONTAINERS_STORAGE_CONF=/tmp/containers/storage.conf

              echo "===== 登录镜像仓库 ====="
              echo "\${REGISTRY_PWD}" | podman login ${REGISTRY_HOST} -u "\${REGISTRY_USER}" --password-stdin

              echo "===== 推送镜像（版本号 + latest）====="
              podman push ${FULL_IMAGE}
              podman tag ${FULL_IMAGE} ${LATEST_IMAGE}
              podman push ${LATEST_IMAGE}
              podman logout ${REGISTRY_HOST}
              echo "镜像推送完成"
            """
          }
        }
      }
    }

    stage('部署到 K8s') {
      steps {
        withCredentials([kubeconfigFile(
          credentialsId: "${K8S_KUBECONFIG}",
          variable: 'KUBECONFIG'
        )]) {
          sh """
            export KUBECONFIG=\${KUBECONFIG}
            echo "===== 滚动更新 Deployment ====="
            kubectl set image deployment/${DEPLOY_NAME} ${CONTAINER_NAME}=${FULL_IMAGE} -n ${K8S_NAMESPACE}

            echo "===== 等待部署完成 ====="
            kubectl rollout status deployment/${DEPLOY_NAME} -n ${K8S_NAMESPACE} --timeout=300s
            echo "===== 部署成功 ====="
          """
        }
      }
    }
  }

  post {
    success { echo '✅ 流水线全部执行成功' }
    failure { echo '❌ 流水线执行失败，请查看上方日志排查' }
    always  { cleanWs() }
  }
}
