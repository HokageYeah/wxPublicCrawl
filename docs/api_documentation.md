# 微信公众号爬虫API接口文档

本文档详细描述了微信公众号爬虫API的接口定义、参数和返回值，分为两个主要部分：微信官方接口和搜狗微信接口。

## 目录

- [微信公众号爬虫API接口文档](#微信公众号爬虫api接口文档)
  - [目录](#目录)
  - [1. 微信官方接口](#1-微信官方接口)
    - [1.1 搜索微信公众号](#11-搜索微信公众号)
    - [1.2 获取公众号文章列表](#12-获取公众号文章列表)
    - [1.3 获取文章详情](#13-获取文章详情)
    - [1.4 设置Cookie和Token](#14-设置cookie和token)
  - [2. 搜狗微信接口](#2-搜狗微信接口)
    - [2.1 搜索微信公众号信息列表](#21-搜索微信公众号信息列表)
    - [2.2 获取微信公众号详情](#22-获取微信公众号详情)
    - [2.3 测试接口获取微信公众号详情](#23-测试接口获取微信公众号详情)
  - [通用响应格式](#通用响应格式)
  - [错误处理](#错误处理)

## 1. 微信官方接口

### 1.1 搜索微信公众号

通过关键词搜索微信公众号。

**接口路径**：`/api/v1/wx/public/search-wx-public`

**请求方式**：GET

**请求参数**：

| 参数名 | 类型   | 必填 | 描述       | 示例值 |
|--------|--------|------|------------|--------|
| query  | string | 是   | 搜索关键词 | "科技" |
| begin  | int    | 否   | 开始位置   | 0      |
| count  | int    | 否   | 返回数量   | 5      |

**返回结果**：

```json
{
  "platform": "WX_PUBLIC",
  "api": "wx/public/search-wx-public",
  "data": [
    {
      "fakeid": "MzI5MjAxNzY2OQ==",
      "nickname": "科技日报",
      "alias": "kjrb2013",
      "round_head_img": "http://mmbiz.qpic.cn/mmbiz_png/...",
      "service_type": 2
    }
  ],
  "ret": ["SUCCESS::搜索公众号成功"],
  "v": 1
}
```


### 1.2 获取公众号文章列表

根据公众号ID获取该公众号的文章列表。

**接口路径**：`/api/v1/wx/public/get-wx-article-list`

**请求方式**：POST

**请求参数**：

| 参数名 | 类型   | 必填 | 描述       | 示例值 |
|--------|--------|------|------------|--------|
| fakeid | string | 是   | 公众号ID   | "MzI5MjAxNzY2OQ==" |
| begin  | int    | 否   | 开始位置   | 0      |
| count  | int    | 否   | 返回数量   | 5      |

**请求体示例**：

```json
{
  "fakeid": "MzI5MjAxNzY2OQ==",
  "begin": 0,
  "count": 5
}
```


**返回结果**：

```json
{
  "platform": "WX_PUBLIC",
  "api": "wx/public/get-wx-article-list",
  "data": {
    "app_msg_list": [
      {
        "aid": "...",
        "appmsgid": 123456789,
        "cover": "https://mmbiz.qpic.cn/...",
        "digest": "文章摘要",
        "link": "http://mp.weixin.qq.com/s?__biz=...",
        "title": "文章标题",
        "update_time": 1609459200
      }
    ],
    "base_resp": {
      "ret": 0,
      "err_msg": "ok"
    }
  },
  "ret": ["SUCCESS::获取文章列表成功"],
  "v": 1
}
```


### 1.3 获取文章详情

根据文章链接获取文章详细内容。

**接口路径**：`/api/v1/wx/public/get-wx-article-detail-by-link`

**请求方式**：POST

**请求参数**：

| 参数名         | 类型   | 必填 | 描述       | 示例值 |
|----------------|--------|------|------------|--------|
| article_link   | string | 是   | 文章链接   | "http://mp.weixin.qq.com/s?__biz=..." |
| wx_public_id   | string | 是   | 公众号ID   | "MzI5MjAxNzY2OQ==" |
| wx_public_name | string | 是   | 公众号名称 | "科技日报" |

**请求体示例**：

```json
{
  "article_link": "http://mp.weixin.qq.com/s?__biz=...",
  "wx_public_id": "MzI5MjAxNzY2OQ==",
  "wx_public_name": "科技日报"
}
```


**返回结果**：

```json
{
  "platform": "WX_PUBLIC",
  "api": "wx/public/get-wx-article-detail-by-link",
  "data": {
    "title": "文章标题",
    "author": "作者",
    "content": "文章HTML内容",
    "publish_time": "2023-01-01",
    "local_path": "crawlFiles/wx_public/科技日报/文章标题.html"
  },
  "ret": ["SUCCESS::获取文章详情成功"],
  "v": 1
}
```


### 1.4 设置Cookie和Token

设置用于爬取的Cookie和Token。

**接口路径**：`/api/v1/wx/public/set-wx-cookie-token`

**请求方式**：POST

**请求参数**：

| 参数名 | 类型   | 必填 | 描述       | 示例值 |
|--------|--------|------|------------|--------|
| cookie.slave_sid | string | 是 | Cookie中的slave_sid值 | "Q0FBQVlJeHo..." |
| cookie.slave_user | string | 是 | Cookie中的slave_user值 | "MTI3NTg..." |
| token | string | 是 | 访问令牌 | "687410795" |

**请求体示例**：

```json
{
  "cookie": {
    "slave_sid": "Q0FBQVlJeHo...",
    "slave_user": "MTI3NTg..."
  },
  "token": "687410795"
}
```


**返回结果**：

```json
{
  "platform": "WX_PUBLIC",
  "api": "wx/public/set-wx-cookie-token",
  "data": {
    "status": "success",
    "message": "Cookie和Token设置成功"
  },
  "ret": ["SUCCESS::设置Cookie和Token成功"],
  "v": 1
}
```


## 2. 搜狗微信接口

### 2.1 搜索微信公众号信息列表

通过搜狗搜索引擎搜索微信公众号文章。

**接口路径**：`/api/v1/sogou/wx/public/search-wx-public-list`

**请求方式**：GET

**请求参数**：

| 参数名 | 类型   | 必填 | 描述       | 示例值 |
|--------|--------|------|------------|--------|
| query  | string | 是   | 搜索关键词 | "科技" |
| page   | int    | 否   | 页码       | 1      |

**返回结果**：

```json
{
  "platform": "WX_PUBLIC",
  "api": "sogou/wx/public/search-wx-public-list",
  "data": [
    {
      "title": "文章标题",
      "href": "https://weixin.sogou.com/link?url=...",
      "dateTime": "2023-01-01 12:00:00",
      "content": "文章摘要",
      "publisher": "公众号名称"
    }
  ],
  "ret": ["SUCCESS::搜索公众号文章成功"],
  "v": 1
}
```


### 2.2 获取微信公众号详情

获取搜狗微信公众号文章的详细内容。

**接口路径**：`/api/v1/sogou/wx/public/get-wx-public-detail`

**请求方式**：POST

**请求参数**：

| 参数名 | 类型   | 必填 | 描述       | 示例值 |
|--------|--------|------|------------|--------|
| url    | string | 是   | 微信公众号详情链接 | "https://weixin.sogou.com/link?url=..." |
| title  | string | 是   | 公众号名称 | "科技日报" |

**请求体示例**：

```json
{
  "url": "https://weixin.sogou.com/link?url=...",
  "title": "科技日报"
}
```


**返回结果**：

```json
{
  "platform": "WX_PUBLIC",
  "api": "sogou/wx/public/get-wx-public-detail",
  "data": "已保存到本地：crawFile/sogou_wx_public/科技日报.html",
  "ret": ["SUCCESS::获取文章详情成功"],
  "v": 1
}
```


### 2.3 测试接口获取微信公众号详情

测试用接口，用于获取搜狗微信公众号文章的详细内容。

**接口路径**：`/api/v1/sogou/wx/public/get-wx-public-detail-test`

**请求方式**：GET

**请求参数**：无

**返回结果**：

```json
{
  "platform": "WX_PUBLIC",
  "api": "sogou/wx/public/get-wx-public-detail-test",
  "data": "HTML内容或保存成功的消息",
  "ret": ["SUCCESS::测试获取文章详情成功"],
  "v": 1
}
```


## 通用响应格式

所有API接口都遵循以下统一的响应格式：

```json
{
  "platform": "平台标识，如WX_PUBLIC",
  "api": "接口路径",
  "data": "接口返回的数据，可能是对象、数组或字符串",
  "ret": ["状态信息，格式为'STATUS::消息'"],
  "v": "API版本号"
}
```


## 错误处理

当API请求出错时，会返回相应的HTTP状态码和错误信息：

```json
{
  "platform": "平台标识",
  "ret": ["ERROR::错误详情"],
  "data": {
    "request_method": "请求方法"
  },
  "v": 1,
  "api": "接口路径"
}
```


常见错误状态码：
- 400: 请求参数错误
- 401: 未授权
- 404: 资源不存在
- 422: 请求参数验证失败
- 500: 服务器内部错误 