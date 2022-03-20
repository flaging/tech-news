# Feed

## 介绍

本repo是一个RSS的内容更新repo，使用github action实现新消息的更新。

每小时拉取[RSS列表](./list.txt)中的RSS源，并将内容更新在每页上。

历史存档在[这里](./ARCHIVED.md)

### TODO

- [ ] 将RSSHUB迁移到repo上，直接在更新时构建RSSHUB镜像然后本地读取对应端口信息
- [x] 实现最README页直接展示今天新更新的信息
- [x] 重新设计sqlite3数据库中字段信息，包括但不限于文章更新时间、拉取时间，文章标题，文章正文内容等
- [ ] 优化更新和对比效率
- [ ] 做好所有rss源适配

## 今日更新
