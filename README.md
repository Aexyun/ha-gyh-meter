<p align="center">
  <img src="https://raw.githubusercontent.com/aexyun/ha-gyh-meter/main/custom_components/gyh_meter/brand/logo.png" width="100%">
</p>
## 公元汇电费余额查询 (GYH Meter)

Home Assistant 自定义集成，用于实时抓取并展示“公元汇”物业系统（或同类微服务平台）的电表剩余金额与累计用电量。

## 功能特性
* ⚡ **实时余额监控**：支持查询电表剩余费用与累计用量。
* ⚙️ **全 UI 配置**：无需修改 `configuration.yaml`，全程在 UI 界面配置。
* ⏱️ **动态刷新率**：支持在 UI 的“选项”中随时修改数据更新频率，防止被服务器封禁。
* 🛡️ **错误校验**：添加时自动校验参数有效性。

## 安装方法 (通过 HACS)
1. 打开 Home Assistant 的 HACS 界面。
2. 点击右上角的三个点，选择 **自定义存储库 (Custom repositories)**。
3. 在 URL 中输入本 GitHub 仓库地址：`https://github.com/Aexyun/ha-gyh-meter`
4. 类别选择 **集成 (Integration)**，点击添加。
5. 在 HACS 中搜索 `公元汇电费余额查询` 并下载。
6. 重启 Home Assistant。

## 获取配置参数
请在微信环境中访问物业缴费页面进行抓包：
1. 找到 `electricMeterQuery` 接口的 POST 请求。
2. 从 Payload 中获取 `wechatUserId` 和 `electricUserUid` (电表号)。
3. 从请求的 URL 或前置页面的链接中获取 `OpenID`。
