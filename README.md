# LamoJudge
## Introduction
一個酷酷的開源 Online Judge
![](preview.png)
## Getting Started
- 安裝 Python 依賴套件
    ```
    pip install -r requirements.txt
    ```
- 部署 Docker
    ```
    docker build -t judge-sandbox
    docker run --memory="1g" --memory-swap="2g" judge-sandbox
    ```
- 部屬 MongoDB

## TO-DO
- [ ] 完成 Judging queue