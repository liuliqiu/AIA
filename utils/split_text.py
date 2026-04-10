import numpy as np
import re
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


def split_sentences(long_text):
    return reg.split(long_text)


def segment_by_similarity(sentences, model_name="all-MiniLM-L6-v2", threshold=None):
    """
    基于句子嵌入和相邻相似度阈值进行文本分段。

    Args:
        sentences (list of str): 分句后的句子列表。
        model_name (str): sentence-transformers 模型名称。
        threshold (float or None): 相似度阈值，若为None则自动计算（取中位数）。

    Returns:
        list of list: 分段后的句子列表。
    """
    # 1. 加载模型并计算嵌入
    model = SentenceTransformer(model_name)
    embeddings = model.encode(sentences, convert_to_tensor=False)  # shape: (n, dim)

    # 2. 计算相邻句子余弦相似度
    sims = []
    for i in range(len(embeddings) - 1):
        sim = cosine_similarity([embeddings[i]], [embeddings[i + 1]])[0][0]
        sims.append(sim)

    # 3. 确定阈值
    if threshold is None:
        # 使用中位数作为默认阈值（可根据数据分布调整）
        threshold = np.median(sims)
        # 也可以使用更保守的策略，如 25% 分位数
        # threshold = np.percentile(sims, 25)

    # 4. 找到分割点
    split_indices = [i for i, s in enumerate(sims) if s < threshold]

    # 5. 构建段落
    paragraphs = []
    start = 0
    for split in split_indices:
        # 从 start 到 split（包含）为一个段落
        paragraphs.append(sentences[start : split + 1])
        start = split + 1
    # 添加最后一个段落
    if start < len(sentences):
        paragraphs.append(sentences[start:])

    return paragraphs


def split_text(long_text, threshold=0.5):
    reg = re.compile("(?<=[。？！.?!])(?![0-9])")
    sentences = reg.split(long_text)
    paragraphs = segment_by_similarity(
        sentences, model_name="./models/all-MiniLM-L6-v2/", threshold=threshold
    )
    return "\n\n".join("".join(para) for para in paragraphs)
