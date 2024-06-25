import jieba
import requests
import streamlit as st
from streamlit_echarts import st_echarts
from collections import Counter
from bs4 import BeautifulSoup
import re
import string
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

# 清理和预处理文本函数
def preprocess_text(text):
    text = re.sub(r'\s+', '', text)  # 去除空白字符
    text = re.sub(r'[\n\r]', '', text)  # 去除换行符
    text = re.sub(r'[^\w\s]', '', text)  # 去除标点符号
    text = re.sub(r'\d+', '', text)  # 去除数字
    return text.strip()

# 分词函数
def word_segmentation(text):
    stopwords = set(
        ['的', '了', '在', '是', '我', '你', '他', '她', '它', '们', '这', '那', '之', '与', '和', '或', '虽然', '但是', '然而', '因此', '日', '月', '转发', '收藏', '取消', '类', '年', '请', '微信', '其他'])
    words = jieba.lcut(text)
    return [word for word in words if word not in stopwords]

# 提取正文文本
def extract_main_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.select('.search-result-item')  # 修改选择器以匹配实际页面结构
    if content:
        return ' '.join([c.get_text() for c in content])
    return soup.get_text()

# 生成词云图
def generate_wordcloud(word_counts):
    if word_counts:
        font_path = os.path.join(os.path.dirname(__file__), 'simhei.ttf')
        if not os.path.exists(font_path):
            st.error(f"字体文件未找到：{font_path}")
            return

        try:
            wordcloud = WordCloud(font_path=font_path, width=800, height=400).generate_from_frequencies(word_counts)
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            st.pyplot(plt)
        except Exception as e:
            st.error(f"生成词云图时出现错误: {e}")
    else:
        st.write("没有足够的词语生成词云图。")

# 运行主程序
def main():
    st.set_page_config(
        page_title="文本处理",
        page_icon="📝",
    )

    st.title("欢迎使用 Streamlit 文本处理 📝")

    base_url = st.text_input('请输入基础 URL :')
    num_pages = st.number_input('请输入要爬取的页数:', min_value=1, value=20)

    if base_url:
        all_text = ""

        for page in range(1, num_pages + 1):
            url = f"{base_url}&page={page}"
            try:
                response = requests.get(url)
                response.encoding = 'utf-8'
                html_content = response.text

                st.write(f"获取第 {page} 页内容成功")

                text = extract_main_text(html_content)
                st.text_area(f"第 {page} 页提取的正文文本：", text, height=200)
                all_text += text

            except Exception as e:
                st.error(f"爬取第 {page} 页时出现错误: {e}")

        if all_text:
            st.write("所有页内容合并成功")

            # 预处理文本
            text_preprocessed = preprocess_text(all_text)
            st.text_area("预处理后的文本：", text_preprocessed[:500], height=200)

            words = word_segmentation(text_preprocessed)
            st.write("分词结果：", words[:50])  # 仅展示前50个词

            word_count = Counter(words)
            most_common_words = word_count.most_common(20)

            st.write("词频统计结果：", most_common_words)

            if most_common_words:
                chart_options = {
                    "tooltip": {"trigger": 'item', "formatter": '{b} : {c}'},
                    "xAxis": [{
                        "type": "category",
                        "data": [word for word, count in most_common_words],
                        "axisLabel": {"interval": 0, "rotate": 45}
                    }],
                    "yAxis": [{"type": "value"}],
                    "series": [{
                        "type": "bar",
                        "data": [count for word, count in most_common_words]
                    }]
                }

                st_echarts(chart_options, height='500px')

                # 生成词云图
                st.write("词云图：")
                generate_wordcloud(dict(most_common_words))
            else:
                st.write("没有足够的词语生成可视化图表。")

if __name__ == "__main__":
    main()
