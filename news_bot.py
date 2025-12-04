# news_bot.py - 修改后的国内可用版本
import os
import requests
import json
from datetime import datetime
import random

class WeChatNewsBot:
    def __init__(self):
        # 从环境变量获取配置
        self.webhook = os.getenv('WECHAT_WEBHOOK')
        self.tianapi_key = os.getenv('TIANAPI_KEY')  # 改为天行数据的key
        
        # 如果没有配置天行数据，使用备用新闻源
        if not self.webhook:
            print("❌ 错误：请先设置WECHAT_WEBHOOK环境变量")
            print("💡 设置方法：")
            print("   1. 在企业微信群里添加机器人")
            print("   2. 复制webhook地址")
            exit(1)
    
    def fetch_news_from_tianapi(self):
        """从天行数据获取新闻"""
        print("📡 从天行数据获取新闻...")
        
        if not self.tianapi_key:
            print("⚠️  未配置TIANAPI_KEY，使用备用新闻")
            return self.get_backup_news()
        
        try:
            # 天行数据新闻头条API
            url = "https://apis.tianapi.com/topnews/index"
            params = {
                'key': self.tianapi_key,
                'num': 10  # 获取10条
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('code') == 200:
                articles = data.get('result', {}).get('list', [])
                print(f"✅ 从天行数据获取到 {len(articles)} 条新闻")
                
                # 转换格式，保持和原代码一致
                formatted_articles = []
                for article in articles[:5]:  # 只取前5条
                    formatted_articles.append({
                        'title': article.get('title', ''),
                        'url': article.get('url', ''),
                        'source': {'name': article.get('source', '天行数据')},
                        'description': article.get('digest', '')
                    })
                return formatted_articles
            else:
                print(f"❌ 天行数据返回错误：{data.get('msg', '未知错误')}")
                return self.get_backup_news()
                
        except Exception as e:
            print(f"❌ 获取新闻失败：{e}")
            return self.get_backup_news()
    
    def fetch_news_from_rss(self):
        """从RSS源获取新闻（备用方案）"""
        print("📡 从RSS源获取新闻...")
        
        rss_sources = [
            "http://www.xinhuanet.com/rss/news.xml",  # 新华社
            "https://rss.cnbeta.com/rss",  # cnBeta
            "http://rss.sina.com.cn/news/market/focus15.xml",  # 新浪财经
        ]
        
        try:
            import feedparser
            # 随机选择一个RSS源
            rss_url = random.choice(rss_sources)
            feed = feedparser.parse(rss_url)
            
            articles = []
            for entry in feed.entries[:5]:  # 取前5条
                articles.append({
                    'title': entry.get('title', '无标题'),
                    'url': entry.get('link', '#'),
                    'source': {'name': feed.feed.get('title', 'RSS源')},
                    'description': entry.get('summary', entry.get('description', ''))[:100]
                })
            
            print(f"✅ 从RSS获取到 {len(articles)} 条新闻")
            return articles
            
        except Exception as e:
            print(f"❌ RSS获取失败：{e}")
            return self.get_backup_news()
    
    def get_backup_news(self):
        """返回内置的备用新闻"""
        print("📡 使用备用新闻...")
        
        backup_news = [
            {
                'title': '科技创新推动高质量发展',
                'url': 'https://example.com/tech1',
                'source': {'name': '科技日报'},
                'description': '近期科技创新成果显著，为经济社会发展注入新动力'
            },
            {
                'title': '数字经济成为增长新引擎',
                'url': 'https://example.com/tech2',
                'source': {'name': '经济观察报'},
                'description': '数字经济发展迅速，正在改变传统产业格局'
            },
            {
                'title': '绿色能源发展迎来新机遇',
                'url': 'https://example.com/tech3',
                'source': {'name': '能源网'},
                'description': '可再生能源技术不断突破，市场前景广阔'
            },
            {
                'title': '人工智能应用加速落地',
                'url': 'https://example.com/tech4',
                'source': {'name': 'AI科技评论'},
                'description': 'AI技术在各行业应用不断深化，创造新价值'
            },
            {
                'title': '智慧城市建设成效显著',
                'url': 'https://example.com/tech5',
                'source': {'name': '城市发展研究'},
                'description': '各地智慧城市建设推进，提升城市治理水平'
            }
        ]
        return backup_news
    
    def fetch_news(self):
        """获取新闻的主函数"""
        # 优先使用天行数据，失败则用RSS，再失败用备用新闻
        if self.tianapi_key:
            news = self.fetch_news_from_tianapi()
            if news and len(news) > 0:
                return news
        
        # 尝试RSS
        try:
            news = self.fetch_news_from_rss()
            if news and len(news) > 0:
                return news
        except:
            pass
        
        # 最后用备用新闻
        return self.get_backup_news()
    
    def format_message(self, articles):
        """格式化Markdown消息"""
        date_str = datetime.now().strftime('%Y年%m月%d日')
        weekday = ['一', '二', '三', '四', '五', '六', '日']
        weekday_str = weekday[datetime.now().weekday()]
        
        # 开始构建消息
        message = f"# 📰 每日新闻简报\n"
        message += f"📅 **{date_str} 星期{weekday_str}**\n\n"
        
        message += "---\n\n"
        
        # 添加每条新闻
        for i, article in enumerate(articles[:5], 1):
            title = article.get('title', '无标题').replace('"', '')
            url = article.get('url', '#')
            source = article.get('source', {}).get('name', '未知来源')
            
            # 处理描述，避免过长
            description = article.get('description', '')
            if description and len(description) > 100:
                description = description[:100] + "..."
            
            message += f"## {i}. {title}\n"
            message += f"**来源**：{source}\n"
            if description:
                message += f"**摘要**：{description}\n"
            message += f"**[🔗 阅读原文]({url})**\n\n"
            message += "---\n\n"
        
        # 添加页脚
        message += "🤖 *此消息由自动新闻机器人推送*\n"
        message += "⏰ *每日早上9点自动更新*"
        
        return message
    
    def send_to_wechat(self, message):
        """发送到企业微信群"""
        print("📤 正在发送到微信群...")
        
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": message
            }
        }
        
        try:
            response = requests.post(
                self.webhook, 
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    print("✅ 消息发送成功！")
                    return True
                else:
                    print(f"❌ 发送失败：{result.get('errmsg')}")
                    return False
            else:
                print(f"❌ HTTP错误：{response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 发送失败：{e}")
            return False
    
    def run(self):
        """运行主程序"""
        print("=" * 50)
        print("📰 开始执行每日新闻推送任务")
        print("=" * 50)
        
        # 获取新闻
        articles = self.fetch_news()
        
        # 格式化消息
        message = self.format_message(articles)
        
        # 发送消息
        success = self.send_to_wechat(message)
        
        # 输出结果
        print("=" * 50)
        if success:
            print("🎉 任务完成！请查看微信群消息")
        else:
            print("😥 任务失败，请检查配置")
        print("=" * 50)

if __name__ == "__main__":
    # 创建机器人实例并运行
    bot = WeChatNewsBot()
    bot.run()
