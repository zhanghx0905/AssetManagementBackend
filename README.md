# README

### Structure

* __doc__ 后端API文档，[在线版本](https://www.showdoc.com.cn/AssetManagementBackendDoc)
* __app__ Core settings for Django.
  - users 用户模块
  - asset 资产模块
  - department  部门模块
  - issue 事项模块
* **logs** 生成日志
* **config** local settings
* __pytest.ini__ Configuration for [pytest](https://docs.pytest.org/en/latest/).
* __requirements.txt__ Package manager with `pip`.
* __requirements_dev.txt__ Package manager with `pip`, including extra tools for development.

### 附：本地检查是否能通过测试

```shell
pylint --load-plugins=pylint_django app users asset department issue
python manage.py test
```

### 附：本地检查测试覆盖率

`.coveragerc` 文件：

```
[run]
branch = True
source = app,users,asset,departments
[report]
show_missing = True
```

命令行执行：

```
coverage run manage.py test
coverage report
```