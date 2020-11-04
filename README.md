# README

后端API文档正在转移至[在线版本](https://www.showdoc.com.cn/AssetManagementBackendDoc)。

### Structure

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
coverage run -m pytest --junit-xml=xunit-reports/xunit-result.xml
```

### 附：本地检查测试覆盖率

在根目录下创建`.coveragerc` 文件：

```
[run]
source = app,users,asset,department,issue
[report]
show_missing = True
```

命令行执行：

```
coverage run manage.py test
coverage report
```