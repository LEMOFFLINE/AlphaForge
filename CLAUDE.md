# AlphaForge - 投资模拟器

## 项目概述

AlphaForge 是一个基于真实股市数据的虚拟投资模拟平台。用户可以使用虚拟资金进行买卖交易，体验真实市场波动，无需承担任何财务风险。

## 技术栈

### 前端
- React 18 + TypeScript + Vite
- React Router v6 (路由)
- TailwindCSS v4 (样式，主色 #1a3d63)
- Zustand (状态管理)
- Recharts (图表)
- Axios (HTTP 客户端)

### 后端
- FastAPI (Python Web 框架)
- SQLAlchemy ORM
- PostgreSQL (数据库)
- JWT (身份认证)
- Alpha Vantage API (实时股票数据)

## 设计原则

- **Less is More** - 简洁至上的界面设计
- **纯白背景** - 所有页面使用白色底色
- **主色调** - #1a3d63 (深蓝色)
- **响应式** - 适配不同屏幕尺寸

## 项目结构

```
Investment Simulator/
├── frontend/                 # React 前端
│   ├── src/
│   │   ├── components/      # 可复用组件 (AssetChart.tsx)
│   │   ├── lib/             # API 客户端、类型定义
│   │   ├── pages/           # 页面组件
│   │   ├── store/           # Zustand 状态管理
│   │   └── styles/          # 全局样式
│   └── package.json
│
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── api/             # API 路由
│   │   ├── core/            # 配置、数据库连接
│   │   ├── models/          # SQLAlchemy 模型、Pydantic schemas
│   │   ├── services/        # 业务逻辑 (股票缓存、Alpha Vantage)
│   │   └── main.py          # FastAPI 入口
│   └── requirements.txt
│
└── database/                 # 数据库脚本
    └── schema.sql
```

## 核心功能

### 1. 用户系统
- 邮箱注册/登录
- JWT 令牌认证
- 三种初始资金: $100K / $1M / $10M

### 2. 控制台 (`/dashboard`)
- 账户总览（总资产、盈亏、盈亏百分比）
- 实时市场行情
- 持仓列表（实时盈亏）
- 可用资金显示
- 资产曲线图表（30天历史）

### 3. 全球市场 (`/market`)
- 热门股票列表
- 实时报价（5分钟缓存）
- 买入/卖出功能
- 手续费计算: $5 固定 + 0.1%

### 4. 分析页面 (`/analysis`)
- AI 聊天界面（待接入后端）
- 投资建议和趋势分析

## 数据模型

### 核心表
- `users` - 用户信息
- `accounts` - 账户信息
- `positions` - 持仓记录
- `orders` - 订单历史
- `account_values` - 账户价值历史

### 枚举
- `OrderType`: buy, sell
- `OrderStatus`: pending, completed, cancelled

## API 概览

### 认证
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

### 账户
- `GET /api/accounts`
- `POST /api/accounts`

### 交易
- `POST /api/orders` - 创建订单
- `GET /api/orders/{account_id}` - 订单历史

### 股票
- `GET /api/stocks/quote/{symbol}`
- `GET /api/stocks/popular/quotes`
- `GET /api/stocks/search`

### 价值历史
- `GET /api/account-values/{account_id}`

## 关键实现细节

### Alpha Vantage 限流处理
- 免费版限制: 25请求/天
- 解决方案: 服务端缓存，5分钟更新一次
- 缓存服务: `backend/app/services/stock_cache.py`

### 订单处理
- 买入: 检查余额 → 扣款 → 更新持仓
- 卖出: 检查持仓 → 减仓 → 加款
- 手续费: 固定 $5 + 0.1% 比例
- 每笔交易后自动记录账户价值

### 资产曲线
- 交易后自动记录 `account_values`
- 图表使用 Recharts 折线图
- 显示最近30天数据

## 待实现功能

- [ ] 涨跌图标显示
- [ ] 股票搜索功能
- [ ] K线图表
- [ ] AI 分析后端接入

## 开发注意事项

- 所有新页面保持白色背景
- 使用已定义的颜色变量（primary, gain, loss）
- 遵循 Less is More 设计原则
- 新功能需要同时更新前端和后端
