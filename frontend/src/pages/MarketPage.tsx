import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { stockApi, orderApi, accountApi } from '../lib/api';
import type { Account } from '../lib/types';

interface Stock {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
}

interface TradeModalProps {
  stock: Stock | null;
  onClose: () => void;
  onSuccess: () => void;
}

function TradeModal({ stock, onClose, onSuccess }: TradeModalProps) {
  const { currentAccount } = useAuthStore();
  const [type, setType] = useState<'buy' | 'sell'>('buy');
  const [shares, setShares] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!stock) return null;

  const estimatedCost = type === 'buy'
    ? stock.price * (parseInt(shares) || 0) * 1.001 + 5 // 0.1% + $5手续费
    : stock.price * (parseInt(shares) || 0) * 0.999 - 5;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const sharesNum = parseInt(shares);
    if (!sharesNum || sharesNum <= 0) {
      setError('请输入有效的股数');
      setLoading(false);
      return;
    }

    if (!currentAccount) {
      setError('未选择账户');
      setLoading(false);
      return;
    }

    try {
      await orderApi.createOrder({
        account_id: currentAccount.id,
        symbol: stock.symbol,
        type,
        shares: sharesNum,
        price: stock.price,
      });
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || '交易失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-medium">{stock.symbol} - {stock.name}</h3>
          <button onClick={onClose} className="text-text-muted hover:text-text">✕</button>
        </div>

        <div className="mb-4 p-3 bg-gray-50 rounded">
          <p className="text-sm text-text-muted">当前价格</p>
          <p className="text-xl font-medium">${stock.price.toFixed(2)}</p>
          <p className={`text-sm ${stock.change >= 0 ? 'text-gain' : 'text-loss'}`}>
            {stock.change >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setType('buy')}
              className={`flex-1 py-2 rounded-lg transition-colors ${
                type === 'buy' ? 'bg-gain text-white' : 'bg-gray-100 text-text hover:bg-gray-200'
              }`}
            >
              买入
            </button>
            <button
              type="button"
              onClick={() => setType('sell')}
              className={`flex-1 py-2 rounded-lg transition-colors ${
                type === 'sell' ? 'bg-loss text-white' : 'bg-gray-100 text-text hover:bg-gray-200'
              }`}
            >
              卖出
            </button>
          </div>

          <div>
            <label className="block text-sm text-text-muted mb-1">股数</label>
            <input
              type="number"
              value={shares}
              onChange={(e) => setShares(e.target.value)}
              min="1"
              className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:border-primary"
              placeholder="输入股数"
            />
          </div>

          <div className="flex justify-between text-sm">
            <span className="text-text-muted">可用资金</span>
            <span>${currentAccount?.current_balance.toFixed(2) || '0.00'}</span>
          </div>

          <div className="flex justify-between text-sm">
            <span className="text-text-muted">预估金额</span>
            <span>${Math.abs(estimatedCost).toFixed(2)}</span>
          </div>

          {error && <p className="text-loss text-sm">{error}</p>}

          <button
            type="submit"
            disabled={loading || !shares}
            className="w-full py-3 bg-primary hover:bg-primaryLight text-white rounded-lg transition-colors disabled:opacity-50"
          >
            {loading ? '处理中...' : type === 'buy' ? '买入' : '卖出'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default function MarketPage() {
  const navigate = useNavigate();
  const { user, logout, currentAccount, setCurrentAccount, setAccounts } = useAuthStore();
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<string>('');
  const [selectedStock, setSelectedStock] = useState<Stock | null>(null);
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
    loadMarketData();
    const interval = setInterval(loadMarketData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const loadMarketData = async () => {
    try {
      const quotes = await stockApi.getPopularQuotes();
      setStocks(quotes);
      setLastUpdate(new Date().toLocaleTimeString('zh-CN'));
    } catch (error) {
      console.error('Failed to load market data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTradeSuccess = () => {
    // 重新加载账户信息
    if (currentAccount) {
      accountApi.getAccounts().then(setAccounts);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

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
            <button onClick={() => navigate('/dashboard')} className="text-text-muted hover:text-text transition-colors">
              控制台
            </button>
            <button className="text-text font-medium">全球市场</button>
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
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-medium text-text">全球市场</h2>
            <p className="text-text-muted text-sm">
              最后更新: {lastUpdate} · 每5分钟自动刷新
            </p>
          </div>
          <button
            onClick={loadMarketData}
            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            刷新
          </button>
        </div>

        {/* 股票表格 */}
        <div className="bg-gray-50 rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
                  代码
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
                  名称
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-text-muted uppercase tracking-wider">
                  价格
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-text-muted uppercase tracking-wider">
                  涨跌
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-text-muted uppercase tracking-wider">
                  涨跌幅
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-text-muted uppercase tracking-wider">
                  操作
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {stocks.map((stock) => (
                <tr key={stock.symbol} className="hover:bg-gray-100 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="font-medium text-text">{stock.symbol}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-text-muted text-sm">
                    {stock.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right font-medium text-text">
                    ${stock.price.toFixed(2)}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-right ${
                    stock.change >= 0 ? 'text-gain' : 'text-loss'
                  }`}>
                    {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-right ${
                    stock.change_percent >= 0 ? 'text-gain' : 'text-loss'
                  }`}>
                    {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center">
                    <button
                      onClick={() => setSelectedStock(stock)}
                      className="text-primary hover:underline text-sm"
                    >
                      交易
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>

      {selectedStock && (
        <TradeModal
          stock={selectedStock}
          onClose={() => setSelectedStock(null)}
          onSuccess={handleTradeSuccess}
        />
      )}
    </div>
  );
}
