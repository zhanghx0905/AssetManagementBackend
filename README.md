# README

企业固定资产管理系统 后端仓库，2020 THU-CST 软件工程优秀大作业.

[前端仓库](https://github.com/xieyt2000/AssetManagementFrontend)

[在线部署](https://asset-management-frontend-goodnight.app.secoder.net/#/login)

### Structure

* __app__ Core settings for Django.
  - user 用户模块
  - asset 资产模块
  - department  部门模块
  - issue 事项模块
* **logs** 生成日志
* **config** local settings
* __pytest.ini__ Configuration for [pytest](https://docs.pytest.org/en/latest/).
* __requirements.txt__ Package manager with `pip`.
* __requirements_dev.txt__ Package manager with `pip`, including extra tools for development.
* **sonar-project.properties** sonarQube 配置
* **.gitlab-ci.yml** gitlab CI 配置
* **Dockerfile** Docker 环境配置

## Development manual

### 本地检查是否能通过测试

```shell
pylint --load-plugins=pylint_django app user asset department issue
coverage run -m pytest --junit-xml=xunit-reports/xunit-result.xml
```

### 本地检查测试覆盖率

在根目录下创建`.coveragerc` 文件：

```
[run]
source = app,user,asset,department,issue
[report]
show_missing = True
```

命令行执行：

```
coverage run manage.py test
coverage report
```