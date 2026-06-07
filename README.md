# AlphaForge

一个基于真实股市数据的虚拟投资模拟平台。使用虚拟资金进行买卖交易，体验真实市场波动，无需承担任何财务风险。

## 功能特性

- 📊 **实时市场数据** - 接入 Alpha Vantage API，获取真实股票报价
- 💼 **虚拟交易** - 支持买入/卖出，自动计算手续费
- 📈 **资产追踪** - 实时更新持仓价值，30天资产曲线图表
- 🤖 **AI 分析** - 投资助手界面（即将上线）
- 🎨 **简洁设计** - Less is More 设计理念

## 技术栈

### 前端
- React 18 + TypeScript + Vite
- TailwindCSS v4 (@import 语法)
- React Router v6
- Zustand (状态管理)
- Recharts (图表)
- Axios (HTTP 客户端)

### 后端
- FastAPI (Python 3.10+)
- SQLAlchemy ORM
- PostgreSQL (14+)
- JWT 认证
- Alpha Vantage API (股票数据)

---

## 快速开始

### 前置要求

- [Node.js](https://nodejs.org/) (18+)
- [Python](https://python.org/) (3.10+)
- [PostgreSQL](https://postgresql.org/) (14+)
- Git

### 1. 克隆项目

```bash
git clone <repository-url>
cd "Investment Simulator"
```

### 2. 数据库设置

#### Windows
```bash
# 启动 PostgreSQL 服务
net start postgresql-x64-14

# 创建数据库
psql -U postgres
CREATE DATABASE alphaforge;
\q
```

#### macOS/Linux
```bash
# 启动 PostgreSQL 服务
sudo service postgresql start

# 创建数据库
sudo -u postgres psql
CREATE DATABASE alphaforge;
\q
```

### 3. 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置数据库连接
# 编辑 app/core/config.py，设置你的数据库 URL
# DATABASE_URL = "postgresql://postgres:your-password@localhost/alphaforge"

# 启动后端
uvicorn app.main:app --reload --port 8000
```

### 4. 前端设置

```bash
# 新终端窗口
cd frontend

# 安装依赖
npm install

# 启动前端
npm run dev
```

### 5. 访问应用

打开浏览器访问: http://localhost:5173

---

## 配置说明

### Alpha Vantage API Key

1. 访问 [Alpha Vantage](https://www.alphavantage.co/support/#api-key) 获取免费 API Key
2. 编辑 `backend/app/core/config.py`:
```python
ALPHA_VANTAGE_API_KEY = "your-api-key-here"
```

**注意**: 免费版限制 25 请求/天，项目已实现服务端缓存来优化使用。

### 环境变量（可选）

创建 `backend/.env` 文件:
```
DATABASE_URL=postgresql://postgres:password@localhost/alphaforge
ALPHA_VANTAGE_API_KEY=your-key
SECRET_KEY=your-jwt-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

创建 `frontend/.env` 文件:
```
VITE_API_URL=http://localhost:8000
```

---

## 数据库管理

### 重置数据库

```bash
cd backend
python recreate_tables.py
```

**警告**: 这将删除所有数据！

### 手动执行 SQL

```bash
psql -U postgres -d alphaforge -f ../database/schema.sql
```

---

## 项目结构

```
Investment Simulator/
├── frontend/              # React 前端
│   ├── src/
│   │   ├── components/    # AssetChart 等组件
│   │   ├── lib/          # API 客户端、类型定义
│   │   ├── pages/        # 页面 (Login, Dashboard, Market, Analysis)
│   │   ├── store/        # Zustand store
│   │   └── styles/       # TailwindCSS
│   └── package.json
│
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── api/          # API 路由 (auth, accounts, orders, stocks, account_values)
│   │   ├── core/         # 配置、数据库连接
│   │   ├── models/       # SQLAlchemy 模型、Pydantic schemas
│   │   ├── services/     # 业务逻辑 (股票缓存、Alpha Vantage)
│   │   └── main.py       # FastAPI 入口
│   └── requirements.txt
│
├── database/             # 数据库脚本
│   └── schema.sql
│
├── CLAUDE.md             # 项目开发文档
└── README.md             # 本文件
```

---

## 功能清单

### 已实现
- ✅ 用户注册/登录（JWT 认证）
- ✅ 三种初始资金选择 ($100K / $1M / $10M)
- ✅ 控制台页面（账户总览、持仓、资产曲线）
- ✅ 全球市场页面（实时报价、买入/卖出）
- ✅ 订单系统（手续费计算）
- ✅ 持仓管理（实时盈亏计算）
- ✅ 资产曲线图表（30天历史）
- ✅ 分析页面 UI（AI 聊天界面）

### 待实现
- ⏳ 涨跌图标显示
- ⏳ 股票搜索功能
- ⏳ K线图表
- ⏳ AI 分析后端接入

---

## API 文档

启动后端后访问: http://localhost:8000/docs

### 主要端点

#### 认证
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户

#### 账户
- `GET /api/accounts` - 获取用户所有账户
- `POST /api/accounts` - 创建新账户

#### 交易
- `POST /api/orders` - 创建订单（买入/卖出）
- `GET /api/orders/{account_id}` - 获取订单历史

#### 股票
- `GET /api/stocks/quote/{symbol}` - 获取股票报价
- `GET /api/stocks/popular/quotes` - 获取热门股票报价（缓存）
- `GET /api/stocks/search` - 搜索股票

#### 价值历史
- `GET /api/account-values/{account_id}` - 获取价值历史
- `POST /api/account-values/record/{account_id}` - 记录当前价值

---

## 常见问题

### 后端启动失败
- 检查 PostgreSQL 服务是否运行
- 确认数据库连接字符串正确
- 验证 Python 版本 >= 3.10

### 前端无法连接后端
- 确认后端运行在 http://localhost:8000
- 检查 CORS 配置
- 验证 `VITE_API_URL` 环境变量

### 股票数据不更新
- Alpha Vantage 免费版有 25 请求/天限制
- 数据会缓存 5 分钟，等待缓存过期或重启后端

### 订单创建失败
- 检查账户余额是否充足（买入）
- 检查持仓数量是否足够（卖出）
- 查看后端日志获取详细错误信息

---

## 生产部署

### 使用 Docker（推荐）

```bash
# 构建并启动所有服务
docker-compose up -d
```

### 手动部署

#### 后端
```bash
cd backend
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### 前端
```bash
cd frontend
npm run build
# 使用 nginx 或其他静态文件服务器托管 dist/ 目录
```

---

## 开发指南

### 添加新页面
1. 在 `frontend/src/pages/` 创建页面组件
2. 在 `frontend/src/App.tsx` 添加路由
3. 更新所有页面的导航链接

### 添加新 API
1. 在 `backend/app/api/` 创建路由文件
2. 在 `backend/app/main.py` 注册路由
3. 在 `frontend/src/lib/api.ts` 添加 API 调用
4. 在 `frontend/src/lib/types.ts` 添加类型定义

### 设计原则
- **Less is More** - 简洁至上的界面设计
- **纯白背景** - 所有页面使用白色底色
- **主色调** - #1a3d63 (深蓝色)
- **涨/跌色** - #22c55e (绿) / #ef4444 (红)

---

## 贡献

欢迎提交 Issue 和 Pull Request！

---

## 许可证

MIT License
