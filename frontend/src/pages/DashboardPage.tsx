import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { accountApi, positionApi, orderApi, stockApi, accountValueApi } from '../lib/api';
import type { Position, Order, Quote, Account, AccountValue } from '../lib/types';
import AssetChart from '../components/AssetChart';

interface PopularStock {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const { user, logout, currentAccount, setCurrentAccount, setAccounts } = useAuthStore();
  const [positions, setPositions] = useState<Position[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [quoteCache, setQuoteCache] = useState<Record<string, Quote>>({});
  const [popularStocks, setPopularStocks] = useState<PopularStock[]>([]);
  const [valueHistory, setValueHistory] = useState<AccountValue[]>([]);
  const [loading, setLoading] = useState(true);
  const [accountsLoading, setAccountsLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }

    const loadAccounts = async () => {
      try {
        const accounts = await accountApi.getAccounts();
        setAccounts(accounts);

        // 如果没有当前账户，设置第一个账户
        if (!currentAccount && accounts.length > 0) {
          setCurrentAccount(accounts[0]);
        }
      } catch (error) {
        console.error('Failed to load accounts:', error);
      } finally {
        setAccountsLoading(false);
      }
    };

    loadAccounts();
  }, [user, currentAccount, setCurrentAccount, setAccounts, navigate]);

  useEffect(() => {
    // 加载热门股票
    const loadPopularStocks = async () => {
      try {
        // 使用后端的热门股票报价API（已经处理了限流）
        const stocks = await stockApi.getPopularQuotes();
        setPopularStocks(stocks);
      } catch (error) {
        console.error('Failed to load popular stocks:', error);
      }
    };

    loadPopularStocks();
  }, []);

  useEffect(() => {
    if (accountsLoading || !currentAccount) {
      if (!accountsLoading) {
        setLoading(false);
      }
      return;
    }

    const loadData = async () => {
      try {
        const [posData, ordersData, historyData] = await Promise.all([
          positionApi.getPositions(currentAccount.id),
          orderApi.getOrders(currentAccount.id),
          accountValueApi.getHistory(currentAccount.id, 30),
        ]);
        setPositions(posData);
        setOrders(ordersData);
        setValueHistory(historyData);

        // 获取所有持仓的实时报价
        const symbols = [...new Set(posData.map((p) => p.symbol))];
        const quotes: Record<string, Quote> = {};
        await Promise.all(
          symbols.map(async (symbol) => {
            try {
              const quote = await stockApi.getQuote(symbol);
              quotes[symbol] = quote;
            } catch (error) {
              console.error(`Failed to fetch quote for ${symbol}:`, error);
            }
          })
        );
        setQuoteCache(quotes);
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [accountsLoading, currentAccount, navigate]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // 计算总资产和盈亏
  const totalValue = positions.reduce((sum, pos) => {
    const quote = quoteCache[pos.symbol];
    return sum + (quote ? quote.price * pos.shares : 0);
  }, currentAccount?.current_balance || 0);

  const totalCost = positions.reduce((sum, pos) => sum + pos.avg_cost * pos.shares, 0);
  const totalPnL = totalValue - (currentAccount?.initial_balance || 0);
  const totalPnLPercent = ((currentAccount?.initial_balance || 0) > 0
    ? (totalPnL / (currentAccount?.initial_balance || 1)) * 100
    : 0);

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <p className="text-text-muted">加载中...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      {/* 顶部导航 */}
      <nav className="border-b border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <h1 className="text-xl font-medium text-primary">AlphaForge</h1>
          <div className="flex items-center gap-6">
            <button className="text-text font-medium">控制台</button>
            <button onClick={() => navigate('/market')} className="text-text-muted hover:text-text transition-colors">
              全球市场
            </button>
            <button onClick={() => navigate('/analysis')} className="text-text-muted hover:text-text transition-colors">
              分析
            </button>
            <button onClick={handleLogout} className="text-text-muted hover:text-text transition-colors">
              退出
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-3 gap-6 mb-6">
          {/* 账户总览 */}
          <div className="bg-gray-50 rounded-lg p-6">
            <h2 className="text-text-muted text-sm mb-4">账户总览</h2>
            <p className="text-3xl font-medium text-text mb-2">
              ${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </p>
            <p className={`text-sm ${totalPnL >= 0 ? 'text-gain' : 'text-loss'}`}>
              {totalPnL >= 0 ? '+' : ''}${totalPnL.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              {' '}({totalPnLPercent >= 0 ? '+' : ''}{totalPnLPercent.toFixed(2)}%)
            </p>
          </div>

          {/* 市场 */}
          <div className="col-span-2 bg-gray-50 rounded-lg p-6">
            <h2 className="text-text-muted text-sm mb-4">市场</h2>
            <div className="grid grid-cols-5 gap-4">
              {popularStocks.map((stock) => (
                <div key={stock.symbol} className="text-center">
                  <p className="text-sm font-medium text-text">{stock.symbol}</p>
                  <p className="text-lg text-text">${stock.price.toFixed(2)}</p>
                  <p className={`text-sm ${stock.change >= 0 ? 'text-gain' : 'text-loss'}`}>
                    {stock.change >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
                  </p>
                </div>
              ))}
            </div>
            <button
              onClick={() => navigate('/market')}
              className="mt-4 text-sm text-primary hover:underline"
            >
              查看全部市场 →
            </button>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-6">
          {/* 持仓列表 */}
          <div className="col-span-2 bg-gray-50 rounded-lg p-6">
            <h2 className="text-text-muted text-sm mb-4">持仓</h2>
            {positions.length === 0 ? (
              <p className="text-text-muted text-sm">暂无持仓</p>
            ) : (
              <div className="space-y-2">
                {positions.map((pos) => {
                  const quote = quoteCache[pos.symbol];
                  const currentPrice = quote?.price || pos.avg_cost;
                  const pnl = (currentPrice - pos.avg_cost) * pos.shares;
                  const pnlPercent = ((currentPrice - pos.avg_cost) / pos.avg_cost) * 100;

                  return (
                    <div key={pos.id} className="flex items-center justify-between py-3 border-b border-gray-200 last:border-0">
                      <div className="flex items-center gap-4">
                        <span className="font-medium text-text">{pos.symbol}</span>
                        <span className="text-text-muted text-sm">{pos.shares} 股</span>
                      </div>
                      <div className="text-right">
                        <p className="text-text">${currentPrice.toFixed(2)}</p>
                        <p className={`text-sm ${pnl >= 0 ? 'text-gain' : 'text-loss'}`}>
                          {pnl >= 0 ? '+' : ''}{pnlPercent.toFixed(2)}%
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* 可用资金 */}
          <div className="bg-gray-50 rounded-lg p-6">
            <h2 className="text-text-muted text-sm mb-4">可用资金</h2>
            <p className="text-2xl font-medium text-text">
              ${(currentAccount?.current_balance || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </p>
          </div>
        </div>

        {/* 资产曲线图 */}
        <div className="mt-6 bg-gray-50 rounded-lg p-6">
          <h2 className="text-text-muted text-sm mb-4">资产曲线</h2>
          <AssetChart data={valueHistory} />
        </div>
      </main>
    </div>
  );
}
