# README

本地运行之前务必

```bash
pip install -r requirements_dev.txt
```

确保本地环境已安装所有依赖



### Structure

* __doc__ 后端文档，调用相关接口前请仔细阅读！
* __app__ Core settings for Django.
* **users** Django App, 用户管理
* **log** 生成的日志
* __pytest.ini__ Configuration for [pytest](https://docs.pytest.org/en/latest/).
* __requirements.txt__ Package manager with `pip`.
* __requirements_dev.txt__ Package manager with `pip`, including extra tools for development.