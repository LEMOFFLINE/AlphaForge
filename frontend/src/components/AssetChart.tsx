import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { AccountValue } from '../lib/types';

interface AssetChartProps {
  data: AccountValue[];
}

export default function AssetChart({ data }: AssetChartProps) {
  // 格式化数据用于图表显示
  const chartData = data.map((item) => ({
    date: new Date(item.recorded_at).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }),
    value: item.total_value,
    cash: item.cash_balance,
    positions: item.positions_value,
  }));

  // 格式化Y轴刻度
  const formatYAxis = (value: number) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    }
    if (value >= 1000) {
      return `$${(value / 1000).toFixed(0)}K`;
    }
    return `$${value}`;
  };

  // 格式化Tooltip
  const formatTooltip = (value: number, name: string) => {
    return [`$${value.toLocaleString()}`, name === 'value' ? '总资产' : name === 'cash' ? '现金' : '持仓'];
  };

  if (chartData.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-text-muted/50">
        暂无数据
      </div>
    );
  }

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="date"
            stroke="#6b7280"
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            stroke="#6b7280"
            fontSize={12}
            tickLine={false}
            axisLine={false}
            tickFormatter={formatYAxis}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
            }}
            formatter={formatTooltip}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#1a3d63"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
