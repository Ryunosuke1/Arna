from typing import Dict, List, Any, Optional
import aiohttp
from bs4 import BeautifulSoup
import json
import logging

class WebTools:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(__name__)
    
    async def _ensure_session(self) -> None:
        """セッションが存在することを確認"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def close(self) -> None:
        """セッションをクローズ"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def search(self, query: str, limit: int = 5) -> List[Dict[str, str]]:
        """
        Web検索を実行する
        
        Args:
            query: 検索クエリ
            limit: 取得する結果の最大数（デフォルト: 5）
        
        Returns:
            List[Dict[str, str]]: 検索結果のリスト。各要素は以下の形式：
            {
                "title": "ページタイトル",
                "url": "ページURL",
                "snippet": "検索結果のスニペット"
            }
        """
        try:
            await self._ensure_session()
            # この実装ではDuckDuckGoのAPIを使用する想定
            # 実際の実装では適切な検索APIに置き換える必要がある
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "no_redirect": 1
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    for result in data.get("Results", [])[:limit]:
                        results.append({
                            "title": result.get("title", ""),
                            "url": result.get("url", ""),
                            "snippet": result.get("snippet", "")
                        })
                    return results
                else:
                    self.logger.error(f"Search request failed with status {response.status}")
                    return []
        
        except Exception as e:
            self.logger.error(f"Error during search: {str(e)}")
            return []
    
    async def scrape(self, url: str) -> Dict[str, Any]:
        """
        指定されたURLのWebページをスクレイプする
        
        Args:
            url: スクレイプするページのURL
        
        Returns:
            Dict[str, Any]: スクレイプした情報。以下の形式：
            {
                "title": "ページタイトル",
                "text": "ページの本文テキスト",
                "metadata": {
                    "description": "メタディスクリプション",
                    "keywords": "メタキーワード"
                }
            }
        """
        try:
            await self._ensure_session()
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # メタデータの抽出
                    metadata = {}
                    for meta in soup.find_all('meta'):
                        if 'name' in meta.attrs and 'content' in meta.attrs:
                            metadata[meta['name']] = meta['content']
                    
                    # テキストの抽出（スクリプトとスタイルを除去）
                    for script in soup(['script', 'style']):
                        script.decompose()
                    
                    return {
                        "title": soup.title.string if soup.title else "",
                        "text": " ".join(soup.stripped_strings),
                        "metadata": metadata
                    }
                else:
                    self.logger.error(f"Scrape request failed with status {response.status}")
                    return {
                        "title": "",
                        "text": "",
                        "metadata": {}
                    }
        
        except Exception as e:
            self.logger.error(f"Error during scraping: {str(e)}")
            return {
                "title": "",
                "text": "",
                "metadata": {},
                "error": str(e)
            }
    
    def __del__(self):
        """デストラクタ: 非同期のクリーンアップを試みる"""
        if self.session and not self.session.closed:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close())
            except Exception:
                pass
