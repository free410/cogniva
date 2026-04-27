"""
高级切块策略测试脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from services.advanced_chunker import AdvancedChunker, chunk_text

# 测试文本
test_text = """
## 第一章：深度学习基础

深度学习是机器学习的一个分支，它使用多层神经网络来分析各种因素。

### 1.1 神经网络概述

神经网络是由大量节点（或称为"神经元"）组成的计算系统。这些节点相互连接，可以处理复杂的信息。

第一层是输入层，负责接收原始数据。隐藏层负责特征提取和转换。最后一层是输出层，产生最终预测结果。

### 1.2 反向传播算法

反向传播是训练神经网络的核心算法。它通过计算损失函数关于每个参数的梯度来更新网络权重。

反向传播的基本步骤如下：
1. 前向传播：计算网络输出
2. 计算损失：衡量预测与真实值的差距
3. 反向传播：计算梯度
4. 更新权重：调整参数以减少损失

### 1.3 激活函数

激活函数为神经网络引入非线性。常用的激活函数包括：

- ReLU: max(0, x)，计算简单但效果很好
- Sigmoid: 1/(1+e^(-x))，输出范围[0,1]
- Tanh: (e^x - e^(-x))/(e^x + e^(-x))，输出范围[-1,1]

## 第二章：卷积神经网络

卷积神经网络（CNN）是处理图像数据的利器。

### 2.1 卷积层

卷积层通过滤波器提取局部特征。滤波器在输入上滑动，计算加权和。

卷积操作可以捕获空间层次结构。低层卷积提取边缘和纹理，高层卷积提取更抽象的特征。

### 2.2 池化层

池化层用于减少特征图的空间尺寸。最大池化选择区域内的最大值，平均池化计算平均值。

池化可以提高模型的鲁棒性，减少过拟合风险。

## 第三章：循环神经网络

循环神经网络（RNN）擅长处理序列数据。

### 3.1 基本结构

RNN具有循环连接，可以处理任意长度的序列。隐藏状态存储了之前的信息。

### 3.2 长短期记忆网络（LSTM）

LSTM通过门控机制解决长期依赖问题。遗忘门决定保留多少之前的信息。

输入门控制新信息的流入，输出门决定输出什么。
"""


def test_chunking():
    """测试各种切块策略"""

    print("=" * 60)
    print("高级切块策略测试")
    print("=" * 60)

    # 配置
    chunk_size = 300
    overlap = 50

    # 创建切块器
    chunker = AdvancedChunker(
        chunk_size=chunk_size,
        chunk_overlap=overlap
    )

    strategies = [
        ("recursive", "递归字符切块"),
        ("semantic", "语义切块"),
        ("markdown", "Markdown结构切块"),
        ("sliding_window", "滑动窗口切块"),
        ("hybrid", "混合策略")
    ]

    for strategy, description in strategies:
        print(f"\n{'=' * 60}")
        print(f"策略: {strategy} ({description})")
        print("=" * 60)

        try:
            chunks = chunker.chunk(test_text, strategy=strategy)

            print(f"生成块数: {len(chunks)}")
            print(f"平均块大小: {sum(len(c) for c in chunks) / len(chunks):.0f} 字符")

            print("\n--- 块详情 ---")
            for i, chunk in enumerate(chunks[:5], 1):  # 只显示前5个
                preview = chunk[:100] + "..." if len(chunk) > 100 else chunk
                print(f"\n块 {i} ({len(chunk)} 字符):")
                print(preview.replace('\n', ' '))

            if len(chunks) > 5:
                print(f"\n... 还有 {len(chunks) - 5} 个块")

        except Exception as e:
            print(f"策略 {strategy} 执行失败: {e}")

    # 测试便捷函数
    print(f"\n{'=' * 60}")
    print("便捷函数测试")
    print("=" * 60)

    chunks = chunk_text(test_text, chunk_size=200, overlap=30, strategy="recursive")
    print(f"使用 chunk_text() 函数生成 {len(chunks)} 个块")


def compare_strategies():
    """比较不同策略在同一文本上的表现"""
    print("\n" + "=" * 60)
    print("策略比较总结")
    print("=" * 60)

    short_text = "这是一个测试句子。深度学习是机器学习的分支。它使用神经网络。卷积神经网络用于图像处理。循环神经网络用于序列数据。"

    chunker = AdvancedChunker(chunk_size=150, chunk_overlap=20)

    results = {}
    for strategy in ["recursive", "semantic", "sliding_window"]:
        try:
            chunks = chunker.chunk(short_text, strategy=strategy)
            results[strategy] = {
                "count": len(chunks),
                "avg_size": sum(len(c) for c in chunks) / len(chunks) if chunks else 0
            }
        except Exception as e:
            results[strategy] = {"count": 0, "avg_size": 0, "error": str(e)}

    print("\n策略 | 块数 | 平均大小")
    print("-" * 40)
    for strategy, stats in results.items():
        if "error" in stats:
            print(f"{strategy:15} | 错误: {stats['error']}")
        else:
            print(f"{strategy:15} | {stats['count']:3} | {stats['avg_size']:.0f}")


if __name__ == "__main__":
    test_chunking()
    compare_strategies()
