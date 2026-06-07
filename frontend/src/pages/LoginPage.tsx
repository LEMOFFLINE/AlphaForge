import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../lib/api';
import { useAuthStore } from '../store/authStore';
import heroImage from '../assets/hero.jpg';

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [initialBalance, setInitialBalance] = useState<100000 | 1000000 | 10000000>(100000);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        const response = await authApi.login({ email, password });
        setAuth(response.user, response.access_token);
      } else {
        const response = await authApi.register({ email, password, initial_balance: initialBalance });
        setAuth(response.user, response.access_token);
      }
      navigate('/dashboard');
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || '操作失败，请重试';
      setError(typeof errorMsg === 'string' ? errorMsg : '操作失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen flex bg-white">
      {/* 左侧留白 + 表单 */}
      <div className="w-1/2 flex items-center justify-center p-12">
        <div className="w-full max-w-md">
          <h1 className="text-4xl font-medium mb-2 text-primary">AlphaForge</h1>
          <p className="text-text-muted mb-12">虚拟投资交易平台</p>

          {/* 登录/注册切换 */}
          <div className="flex gap-4 mb-8">
            <button
              onClick={() => setIsLogin(true)}
              className={`pb-2 border-b-2 transition-colors ${
                isLogin ? 'border-primary text-primary' : 'border-transparent text-text-muted'
              }`}
            >
              登录
            </button>
            <button
              onClick={() => setIsLogin(false)}
              className={`pb-2 border-b-2 transition-colors ${
                !isLogin ? 'border-primary text-primary' : 'border-transparent text-text-muted'
              }`}
            >
              注册
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <input
                type="email"
                placeholder="邮箱"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-primary text-text placeholder:text-text-muted"
              />
            </div>
            <div>
              <input
                type="password"
                placeholder="密码"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-primary text-text placeholder:text-text-muted"
              />
            </div>

            {!isLogin && (
              <div>
                <label className="block text-sm text-text-muted mb-2">选择初始本金</label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { value: 100000, label: '$100K' },
                    { value: 1000000, label: '$1M' },
                    { value: 10000000, label: '$10M' },
                  ].map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => setInitialBalance(option.value as any)}
                      className={`py-3 rounded-lg border transition-colors ${
                        initialBalance === option.value
                          ? 'border-primary bg-primary/10 text-primary'
                          : 'border-gray-200 bg-white text-text-muted hover:border-gray-300'
                      }`}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {error && (
              <p className="text-loss text-sm">{error}</p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-primary hover:bg-primaryLight text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '处理中...' : isLogin ? '登录' : '注册'}
            </button>
          </form>
        </div>
      </div>

      {/* 右侧 Hero 图片 */}
      <div className="w-1/2 relative overflow-hidden bg-gray-50">
        <img
          src={heroImage}
          alt="Hero"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent" />
        <div className="absolute bottom-12 left-12 right-12 text-white">
          <h2 className="text-3xl font-medium mb-4">真实市场数据</h2>
          <p className="text-white/80">零风险练习 · 智能分析 · 投资成长</p>
        </div>
      </div>
    </div>
  );
}
