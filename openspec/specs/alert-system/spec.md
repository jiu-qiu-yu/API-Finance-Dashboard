## Requirements

### Requirement: Balance threshold configuration
系统 SHALL 允许用户为每个上游站点设置低余额告警阈值（如余额 < $5）。该阈值 SHALL 可在站点设置中配置。

#### Scenario: User sets alert threshold
- **WHEN** 用户配置上游站点的告警阈值为 $5.00
- **THEN** 系统保存阈值并在巡检后用于评估

### Requirement: OS native notification on low balance
每次巡检完成后，系统 SHALL 检查所有上游余额是否低于阈值。若有上游余额等于或低于阈值，系统 SHALL 发送操作系统原生通知（Windows Toast / macOS 通知中心），附带告警声音。通知内容 SHALL 使用中文。

#### Scenario: Low balance triggers notification
- **WHEN** 巡检完成，上游 "ProviderX" 余额 $3.00，阈值 $5.00
- **THEN** 系统发送 OS 通知："额度告急: ProviderX 余额 $3.00，低于阈值 $5.00"
- **AND** 通知附带告警声音

#### Scenario: All balances healthy
- **WHEN** 巡检完成，所有上游余额均高于阈值
- **THEN** 系统不发送任何告警通知

#### Scenario: 多个上游同时告急
- **WHEN** 巡检完成，3 个上游低于阈值
- **THEN** 系统发送一条汇总通知："New API 额度告急：3 个上游余额不足"
- **AND** 通知内容包含各告急上游的名称和余额

### Requirement: Cross-platform notification abstraction
系统 SHALL 提供统一的通知接口，兼容 Windows（Toast 通知）和 macOS（通知中心）。平台差异 SHALL 封装在通用 Notifier 接口后。

#### Scenario: Notification on Windows
- **WHEN** 在 Windows 系统上触发告警
- **THEN** 显示 Windows Toast 通知，包含标题、内容和声音

#### Scenario: Notification on macOS
- **WHEN** 在 macOS 系统上触发告警
- **THEN** 显示 macOS 通知中心通知，包含标题、内容和声音
