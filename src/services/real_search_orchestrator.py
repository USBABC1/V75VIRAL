#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Real Search Orchestrator
Orquestrador de busca REAL massiva com rotação de APIs e captura visual
"""

import os
import logging
import asyncio
import aiohttp
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote_plus
import json

logger = logging.getLogger(__name__)

class RealSearchOrchestrator:
    """Orquestrador de busca REAL massiva - ZERO SIMULAÇÃO"""

    def __init__(self):
        """Inicializa orquestrador com todas as APIs reais"""
        self.api_keys = self._load_all_api_keys()
        self.key_indices = {provider: 0 for provider in self.api_keys.keys()}

        # Provedores em ordem de prioridade
        self.providers = [
            'ALIBABA_WEBSAILOR',  # Adicionado como prioridade máxima
            'FIRECRAWL',
            'JINA', 
            'GOOGLE',
            'EXA',
            'SERPER',
            'YOUTUBE',
            'SUPADATA'
        ]

        # URLs base dos serviços
        self.service_urls = {
            'FIRECRAWL': 'https://api.firecrawl.dev/v0/scrape',
            'JINA': 'https://r.jina.ai/',
            'GOOGLE': 'https://www.googleapis.com/customsearch/v1',
            'EXA': 'https://api.exa.ai/search',
            'SERPER': 'https://google.serper.dev/search',
            'YOUTUBE': 'https://www.googleapis.com/youtube/v3/search',
            'SUPADATA': os.getenv('SUPADATA_API_URL', 'https://server.smithery.ai/@supadata-ai/mcp/mcp')
        }

        self.session_stats = {
            'total_searches': 0,
            'successful_searches': 0,
            'failed_searches': 0,
            'api_rotations': {},
            'content_extracted': 0,
            'screenshots_captured': 0
        }

        logger.info(f"🚀 Real Search Orchestrator inicializado com {sum(len(keys) for keys in self.api_keys.values())} chaves totais")

    def _load_all_api_keys(self) -> Dict[str, List[str]]:
        """Carrega todas as chaves de API do ambiente"""
        api_keys = {}

        for provider in ['FIRECRAWL', 'JINA', 'GOOGLE', 'EXA', 'SERPER', 'YOUTUBE', 'SUPADATA', 'X']:
            keys = []

            # Chave principal
            main_key = os.getenv(f"{provider}_API_KEY")
            if main_key:
                keys.append(main_key)

            # Chaves numeradas
            counter = 1
            while True:
                numbered_key = os.getenv(f"{provider}_API_KEY_{counter}")
                if numbered_key:
                    keys.append(numbered_key)
                    counter += 1
                else:
                    break

            if keys:
                api_keys[provider] = keys
                logger.info(f"✅ {provider}: {len(keys)} chaves carregadas")

        return api_keys

    def get_next_api_key(self, provider: str) -> Optional[str]:
        """Obtém próxima chave de API com rotação automática"""
        if provider not in self.api_keys or not self.api_keys[provider]:
            return None

        keys = self.api_keys[provider]
        current_index = self.key_indices[provider]

        # Obtém chave atual
        key = keys[current_index]

        # Rotaciona para próxima
        self.key_indices[provider] = (current_index + 1) % len(keys)

        # Atualiza estatísticas
        if provider not in self.session_stats['api_rotations']:
            self.session_stats['api_rotations'][provider] = 0
        self.session_stats['api_rotations'][provider] += 1

        logger.debug(f"🔄 {provider}: Usando chave {current_index + 1}/{len(keys)}")
        return key

    async def execute_massive_real_search(
        self, 
        query: str, 
        context: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """Executa busca REAL massiva com todos os provedores"""

        logger.info(f"🚀 INICIANDO BUSCA REAL MASSIVA para: {query}")
        start_time = time.time()

        # Estrutura de resultados
        search_results = {
            'query': query,
            'session_id': session_id,
            'search_started': datetime.now().isoformat(),
            'providers_used': [],
            'web_results': [],
            'social_results': [],
            'youtube_results': [],
            'viral_content': [],
            'screenshots_captured': [],
            'statistics': {
                'total_sources': 0,
                'unique_urls': 0,
                'content_extracted': 0,
                'api_calls_made': 0,
                'search_duration': 0
            }
        }

        try:
            # FASE 1: Busca com Alibaba WebSailor (prioritária)
            logger.info("🔍 FASE 1: Busca com Alibaba WebSailor")
            websailor_results = await self._search_alibaba_websailor(query, context)
            
            if websailor_results.get('success'):
                search_results['web_results'].extend(websailor_results['results'])
                search_results['providers_used'].append('ALIBABA_WEBSAILOR')
                logger.info(f"✅ Alibaba WebSailor retornou {len(websailor_results['results'])} resultados")

            # FASE 2: Busca Web Massiva Simultânea (provedores restantes)
            logger.info("🌐 FASE 2: Busca web massiva simultânea")
            web_tasks = []

            # Firecrawl
            if 'FIRECRAWL' in self.api_keys:
                web_tasks.append(self._search_firecrawl(query))

            # Jina
            if 'JINA' in self.api_keys:
                web_tasks.append(self._search_jina(query))

            # Google
            if 'GOOGLE' in self.api_keys:
                web_tasks.append(self._search_google(query))

            # Exa
            if 'EXA' in self.api_keys:
                web_tasks.append(self._search_exa(query))

            # Serper
            if 'SERPER' in self.api_keys:
                web_tasks.append(self._search_serper(query))

            # Executa todas as buscas web simultaneamente
            if web_tasks:
                web_results = await asyncio.gather(*web_tasks, return_exceptions=True)

                for result in web_results:
                    if isinstance(result, Exception):
                        logger.error(f"❌ Erro na busca web: {result}")
                        continue

                    if result.get('success') and result.get('results'):
                        search_results['web_results'].extend(result['results'])
                        search_results['providers_used'].append(result.get('provider', 'unknown'))

            # FASE 3: Busca em Redes Sociais
            logger.info("📱 FASE 3: Busca massiva em redes sociais")
            social_tasks = []

            # YouTube
            if 'YOUTUBE' in self.api_keys:
                social_tasks.append(self._search_youtube(query))

            # Supadata (Instagram, Facebook, TikTok)
            # if 'SUPADATA' in self.api_keys:
            #     social_tasks.append(self._search_supadata(query))

            # Executa buscas sociais
            if social_tasks:
                social_results = await asyncio.gather(*social_tasks, return_exceptions=True)

                for result in social_results:
                    if isinstance(result, Exception):
                        logger.error(f"❌ Erro na busca social: {result}")
                        continue

                    if result.get('success'):
                        if result.get('platform') == 'youtube':
                            search_results['youtube_results'].extend(result.get('results', []))
                        else:
                            search_results['social_results'].extend(result.get('results', []))

            # FASE 4: Identificação de Conteúdo Viral
            logger.info("🔥 FASE 4: Identificando conteúdo viral")
            viral_content = self._identify_viral_content(
                search_results['youtube_results'] + search_results['social_results']
            )
            search_results['viral_content'] = viral_content

            # FASE 5: Captura de Screenshots
            logger.info("📸 FASE 5: Capturando screenshots do conteúdo viral")
            if viral_content:
                screenshots = await self._capture_viral_screenshots(viral_content, session_id)
                search_results['screenshots_captured'] = screenshots
                self.session_stats['screenshots_captured'] = len(screenshots)

            # Calcula estatísticas finais
            search_duration = time.time() - start_time
            all_results = search_results['web_results'] + search_results['social_results'] + search_results['youtube_results']
            unique_urls = list(set(r.get('url', '') for r in all_results if r.get('url')))

            search_results['statistics'].update({
                'total_sources': len(all_results),
                'unique_urls': len(unique_urls),
                'content_extracted': sum(len(r.get('content', '')) for r in all_results),
                'api_calls_made': sum(self.session_stats['api_rotations'].values()),
                'search_duration': search_duration
            })

            logger.info(f"✅ BUSCA REAL MASSIVA CONCLUÍDA em {search_duration:.2f}s")
            logger.info(f"📊 {len(all_results)} resultados de {len(search_results['providers_used'])} provedores")
            logger.info(f"📸 {len(search_results['screenshots_captured'])} screenshots capturados")

            return search_results

        except Exception as e:
            logger.error(f"❌ ERRO CRÍTICO na busca massiva: {e}")
            raise

    async def _search_alibaba_websailor(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Busca REAL usando Alibaba WebSailor Agent"""
        try:
            # Importa o agente WebSailor
            from services.alibaba_websailor import alibaba_websailor
            
            if not alibaba_websailor or not alibaba_websailor.enabled:
                logger.warning("⚠️ Alibaba WebSailor não está habilitado")
                return {'success': False, 'error': 'Alibaba WebSailor não habilitado'}

            # Executa a pesquisa profunda - CORRIGIDO: chamando o método correto
            research_result = await alibaba_websailor.navigate_and_research_deep(
                query=query,
                context=context,
                max_pages=30,
                depth_levels=2,
                session_id=None # Ou passe session_id se o método aceitar
            )

            if not research_result or not research_result.get('conteudo_consolidado'):
                return {'success': False, 'error': 'Nenhum resultado da pesquisa WebSailor'}

            # Converte resultados do WebSailor para formato padrão
            results = []
            fontes_detalhadas = research_result.get('conteudo_consolidado', {}).get('fontes_detalhadas', [])
            
            for fonte in fontes_detalhadas:
                results.append({
                    'title': fonte.get('title', ''),
                    'url': fonte.get('url', ''),
                    'snippet': '',  # WebSailor não fornece snippet diretamente
                    'source': 'alibaba_websailor',
                    'relevance_score': fonte.get('quality_score', 0.7),
                    'content_length': fonte.get('content_length', 0)
                })

            logger.info(f"✅ Alibaba WebSailor processado com {len(results)} resultados")
            
            return {
                'success': True,
                'provider': 'ALIBABA_WEBSAILOR',
                'results': results,
                'raw_data': research_result
            }

        except ImportError:
            logger.warning("⚠️ Alibaba WebSailor não encontrado")
            return {'success': False, 'error': 'Alibaba WebSailor não disponível'}
        except Exception as e:
            logger.error(f"❌ Erro Alibaba WebSailor: {e}")
            return {'success': False, 'error': str(e)}

    async def _search_firecrawl(self, query: str) -> Dict[str, Any]:
        """Busca REAL usando Firecrawl"""
        try:
            api_key = self.get_next_api_key('FIRECRAWL')
            if not api_key:
                return {'success': False, 'error': 'Firecrawl API key não disponível'}

            # Busca no Google e extrai com Firecrawl
            search_url = f"https://www.google.com/search?q={quote_plus(query)}&hl=pt-BR&gl=BR"

            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }

                payload = {
                    'url': search_url,
                    'formats': ['markdown', 'html'],
                    'onlyMainContent': True,
                    'includeTags': ['p', 'h1', 'h2', 'h3', 'article'],
                    'excludeTags': ['nav', 'footer', 'aside', 'script'],
                    'waitFor': 3000
                }

                async with session.post(
                    self.service_urls['FIRECRAWL'],
                    json=payload,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data.get('data', {}).get('markdown', '')

                        # Extrai resultados do conteúdo
                        results = self._extract_search_results_from_content(content, 'firecrawl')

                        return {
                            'success': True,
                            'provider': 'FIRECRAWL',
                            'results': results,
                            'raw_content': content[:2000]
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Firecrawl erro {response.status}: {error_text}")
                        return {'success': False, 'error': f'HTTP {response.status}'}

        except Exception as e:
            logger.error(f"❌ Erro Firecrawl: {e}")
            return {'success': False, 'error': str(e)}

    async def _search_jina(self, query: str) -> Dict[str, Any]:
        """Busca REAL usando Jina AI"""
        try:
            api_key = self.get_next_api_key('JINA')
            if not api_key:
                return {'success': False, 'error': 'Jina API key não disponível'}

            # Busca múltiplas URLs com Jina
            search_urls = [
                f"https://www.google.com/search?q={quote_plus(query)}&hl=pt-BR",
                f"https://www.bing.com/search?q={quote_plus(query)}&cc=br",
                f"https://search.yahoo.com/search?p={quote_plus(query)}&ei=UTF-8"
            ]

            results = []

            async with aiohttp.ClientSession() as session:
                for search_url in search_urls:
                    try:
                        jina_url = f"{self.service_urls['JINA']}{search_url}"
                        headers = {
                            'Authorization': f'Bearer {api_key}',
                            'Accept': 'text/plain'
                        }

                        async with session.get(
                            jina_url,
                            headers=headers,
                            timeout=30
                        ) as response:
                            if response.status == 200:
                                content = await response.text()
                                extracted_results = self._extract_search_results_from_content(content, 'jina')
                                results.extend(extracted_results)

                    except Exception as e:
                        logger.warning(f"⚠️ Erro em URL Jina {search_url}: {e}")
                        continue

            return {
                'success': True,
                'provider': 'JINA',
                'results': results[:20]  # Limita a 20 resultados
            }

        except Exception as e:
            logger.error(f"❌ Erro Jina: {e}")
            return {'success': False, 'error': str(e)}

    async def _search_google(self, query: str) -> Dict[str, Any]:
        """Busca REAL usando Google Custom Search"""
        try:
            api_key = self.get_next_api_key('GOOGLE')
            cse_id = os.getenv('GOOGLE_CSE_ID')

            if not api_key or not cse_id:
                return {'success': False, 'error': 'Google API não configurada'}

            async with aiohttp.ClientSession() as session:
                params = {
                    'key': api_key,
                    'cx': cse_id,
                    'q': f"{query} Brasil 2024",
                    'num': 10,
                    'lr': 'lang_pt',
                    'gl': 'br',
                    'safe': 'off',
                    'dateRestrict': 'm6'
                }

                async with session.get(
                    self.service_urls['GOOGLE'],
                    params=params,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []

                        for item in data.get('items', []):
                            results.append({
                                'title': item.get('title', ''),
                                'url': item.get('link', ''),
                                'snippet': item.get('snippet', ''),
                                'source': 'google_real',
                                'published_date': item.get('pagemap', {}).get('metatags', [{}])[0].get('article:published_time', ''),
                                'relevance_score': 0.9
                            })

                        return {
                            'success': True,
                            'provider': 'GOOGLE',
                            'results': results
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Google erro {response.status}: {error_text}")
                        return {'success': False, 'error': f'HTTP {response.status}'}

        except Exception as e:
            logger.error(f"❌ Erro Google: {e}")
            return {'success': False, 'error': str(e)}

    async def _search_youtube(self, query: str) -> Dict[str, Any]:
        """Busca REAL no YouTube com foco em conteúdo viral"""
        try:
            api_key = self.get_next_api_key('YOUTUBE')
            if not api_key:
                return {'success': False, 'error': 'YouTube API key não disponível'}

            async with aiohttp.ClientSession() as session:
                params = {
                    'part': "snippet,id",
                    'q': f"{query} Brasil",
                    'key': api_key,
                    'maxResults': 25,
                    'order': 'viewCount',  # Ordena por visualizações
                    'type': 'video',
                    'regionCode': 'BR',
                    'relevanceLanguage': 'pt',
                    'publishedAfter': '2023-01-01T00:00:00Z'
                }

                async with session.get(
                    self.service_urls['YOUTUBE'],
                    params=params,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []

                        for item in data.get('items', []):
                            snippet = item.get('snippet', {})
                            video_id = item.get('id', {}).get('videoId', '')

                            # Busca estatísticas detalhadas
                            stats = await self._get_youtube_video_stats(video_id, api_key, session)

                            results.append({
                                'title': snippet.get('title', ''),
                                'url': f"https://www.youtube.com/watch?v={video_id}",
                                'description': snippet.get('description', ''),
                                'channel': snippet.get('channelTitle', ''),
                                'published_at': snippet.get('publishedAt', ''),
                                'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                                'view_count': stats.get('viewCount', 0),
                                'comment_count': stats.get('commentCount', 0),
                                'platform': 'youtube',
                                'viral_score': self._calculate_viral_score(stats),
                                'relevance_score': 0.85
                            })

                        # Ordena por score viral
                        results.sort(key=lambda x: x['viral_score'], reverse=True)

                        return {
                            'success': True,
                            'provider': 'YOUTUBE',
                            'platform': 'youtube',
                            'results': results
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ YouTube erro {response.status}: {error_text}")
                        return {'success': False, 'error': f'HTTP {response.status}'}

        except Exception as e:
            logger.error(f"❌ Erro YouTube: {e}")
            return {'success': False, 'error': str(e)}

    async def _get_youtube_video_stats(self, video_id: str, api_key: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Obtém estatísticas detalhadas de um vídeo do YouTube"""
        try:
            params = {
                'part': 'statistics',
                'id': video_id,
                'key': api_key
            }

            async with session.get(
                'https://www.googleapis.com/youtube/v3/videos',
                params=params,
                timeout=10
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get('items', [])
                    if items:
                        return items[0].get('statistics', {})

                return {}

        except Exception as e:
            logger.warning(f"⚠️ Erro ao obter stats do vídeo {video_id}: {e}")
            return {}

    async def _search_supadata(self, query: str) -> Dict[str, Any]:
        """Busca REAL usando Supadata MCP"""
        try:
            api_key = self.get_next_api_key('SUPADATA')
            if not api_key:
                return {'success': False, 'error': 'Supadata API key não disponível'}

            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }

                payload = {
                    'method': 'social_search',
                    'params': {
                        'query': query,
                        'platforms': ['instagram', 'facebook', 'tiktok'],
                        'limit': 50,
                        'sort_by': 'engagement',
                        'include_metrics': True
                    }
                }

                async with session.post(
                    self.service_urls['SUPADATA'],
                    json=payload,
                    headers=headers,
                    timeout=45
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []

                        posts = data.get('result', {}).get('posts', [])
                        for post in posts:
                            results.append({
                                'title': post.get('caption', '')[:100],
                                'url': post.get('url', ''),
                                'content': post.get('caption', ''),
                                'platform': post.get('platform', 'social'),
                                'engagement_rate': post.get('engagement_rate', 0),
                                'likes': post.get('likes', 0),
                                'comments': post.get('comments', 0),
                                'shares': post.get('shares', 0),
                                'author': post.get('author', ''),
                                'published_at': post.get('published_at', ''),
                                'viral_score': self._calculate_social_viral_score(post),
                                'relevance_score': 0.8
                            })

                        return {
                            'success': True,
                            'provider': 'SUPADATA',
                            'results': results
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Supadata erro {response.status}: {error_text}")
                        return {'success': False, 'error': f'HTTP {response.status}'}

        except Exception as e:
            logger.error(f"❌ Erro Supadata: {e}")
            return {'success': False, 'error': str(e)}

    async def _search_twitter(self, query: str) -> Dict[str, Any]:
        """Busca REAL no Twitter/X"""
        try:
            api_key = self.get_next_api_key('X')
            if not api_key:
                return {'success': False, 'error': 'X API key não disponível'}

            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }

                params = {
                    'query': f"{query} lang:pt",
                    'max_results': 50,
                    'tweet.fields': 'public_metrics,created_at,author_id',
                    'user.fields': 'username,verified,public_metrics',
                    'expansions': 'author_id'
                }

                async with session.get(
                    'https://api.twitter.com/2/tweets/search/recent',
                    params=params,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []

                        tweets = data.get('data', [])
                        users = {user['id']: user for user in data.get('includes', {}).get('users', [])}

                        for tweet in tweets:
                            author = users.get(tweet.get('author_id', ''), {})
                            metrics = tweet.get('public_metrics', {})

                            results.append({
                                'title': tweet.get('text', '')[:100],
                                'url': f"https://twitter.com/i/status/{tweet.get('id')}",
                                'content': tweet.get('text', ''),
                                'platform': 'twitter',
                                'author': author.get('username', ''),
                                'author_verified': author.get('verified', False),
                                'retweets': metrics.get('retweet_count', 0),
                                'likes': metrics.get('like_count', 0),
                                'replies': metrics.get('reply_count', 0),
                                'quotes': metrics.get('quote_count', 0),
                                'published_at': tweet.get('created_at', ''),
                                'viral_score': self._calculate_twitter_viral_score(metrics),
                                'relevance_score': 0.75
                            })

                        return {
                            'success': True,
                            'provider': 'X',
                            'results': results
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ X/Twitter erro {response.status}: {error_text}")
                        return {'success': False, 'error': f'HTTP {response.status}'}

        except Exception as e:
            logger.error(f"❌ Erro X/Twitter: {e}")
            return {'success': False, 'error': str(e)}

    async def _search_exa(self, query: str) -> Dict[str, Any]:
        """Busca REAL usando Exa Neural Search"""
        try:
            api_key = self.get_next_api_key('EXA')
            if not api_key:
                return {'success': False, 'error': 'Exa API key não disponível'}

            async with aiohttp.ClientSession() as session:
                headers = {
                    'x-api-key': api_key,
                    'Content-Type': 'application/json'
                }

                payload = {
                    'query': f"{query} Brasil mercado tendências",
                    'numResults': 15,
                    'useAutoprompt': True,
                    'type': 'neural',
                    'includeDomains': [
                        'g1.globo.com', 'exame.com', 'valor.globo.com',
                        'estadao.com.br', 'folha.uol.com.br', 'infomoney.com.br'
                    ],
                    'startPublishedDate': '2023-01-01'
                }

                async with session.post(
                    self.service_urls['EXA'],
                    json=payload,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []

                        for item in data.get('results', []):
                            results.append({
                                'title': item.get('title', ''),
                                'url': item.get('url', ''),
                                'snippet': item.get('text', '')[:300],
                                'source': 'exa_neural',
                                'score': item.get('score', 0),
                                'published_date': item.get('publishedDate', ''),
                                'relevance_score': item.get('score', 0.8)
                            })

                        return {
                            'success': True,
                            'provider': 'EXA',
                            'results': results
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Exa erro {response.status}: {error_text}")
                        return {'success': False, 'error': f'HTTP {response.status}'}

        except Exception as e:
            logger.error(f"❌ Erro Exa: {e}")
            return {'success': False, 'error': str(e)}

    async def _search_serper(self, query: str) -> Dict[str, Any]:
        """Busca REAL usando Serper"""
        try:
            api_key = self.get_next_api_key('SERPER')
            if not api_key:
                return {'success': False, 'error': 'Serper API key não disponível'}

            async with aiohttp.ClientSession() as session:
                headers = {
                    'X-API-KEY': api_key,
                    'Content-Type': 'application/json'
                }

                payload = {
                    'q': f"{query} Brasil mercado",
                    'gl': 'br',
                    'hl': 'pt',
                    'num': 15,
                    'autocorrect': True
                }

                async with session.post(
                    self.service_urls['SERPER'],
                    json=payload,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []

                        for item in data.get('organic', []):
                            results.append({
                                'title': item.get('title', ''),
                                'url': item.get('link', ''),
                                'snippet': item.get('snippet', ''),
                                'source': 'serper_real',
                                'position': item.get('position', 0),
                                'relevance_score': 0.85
                            })

                        return {
                            'success': True,
                            'provider': 'SERPER',
                            'results': results
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Serper erro {response.status}: {error_text}")
                        return {'success': False, 'error': f'HTTP {response.status}'}

        except Exception as e:
            logger.error(f"❌ Erro Serper: {e}")
            return {'success': False, 'error': str(e)}

    def _extract_search_results_from_content(self, content: str, provider: str) -> List[Dict[str, Any]]:
        """Extrai resultados de busca do conteúdo extraído"""
        results = []

        if not content:
            return results

        # Divide o conteúdo em seções
        lines = content.split('\n')
        current_result = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detecta títulos (linhas com mais de 20 caracteres e sem URLs)
            if (len(line) > 20 and 
                not line.startswith('http') and 
                not line.startswith('www') and
                '.' not in line[:10]):

                # Salva resultado anterior se existir
                if current_result.get('title'):
                    results.append(current_result)

                # Inicia novo resultado
                current_result = {
                    'title': line,
                    'url': '',
                    'snippet': '',
                    'source': provider,
                    'relevance_score': 0.7
                }

            # Detecta URLs
            elif line.startswith(('http', 'www')):
                if current_result:
                    current_result['url'] = line

            # Detecta descrições (linhas médias)
            elif 50 <= len(line) <= 200 and current_result:
                current_result['snippet'] = line

        # Adiciona último resultado
        if current_result.get('title'):
            results.append(current_result)

        # Filtra resultados válidos
        valid_results = [r for r in results if r.get('title') and len(r.get('title', '')) > 10]

        return valid_results[:15]  # Máximo 15 por provedor

    def _identify_viral_content(self, all_social_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifica conteúdo viral para captura de screenshots"""

        if not all_social_results:
            return []

        # Ordena por score viral
        sorted_content = sorted(
            all_social_results, 
            key=lambda x: x.get('viral_score', 0), 
            reverse=True
        )

        # Seleciona top 10 conteúdos virais
        viral_content = []
        seen_urls = set()

        for content in sorted_content:
            url = content.get('url', '')
            if url and url not in seen_urls and len(viral_content) < 10:
                viral_content.append(content)
                seen_urls.add(url)

        logger.info(f"🔥 {len(viral_content)} conteúdos virais identificados")
        return viral_content

    async def _capture_viral_screenshots(self, viral_content: List[Dict[str, Any]], session_id: str) -> List[Dict[str, Any]]:
        """Captura screenshots do conteúdo viral usando Selenium"""

        screenshots = []

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from webdriver_manager.chrome import ChromeDriverManager

            # Configura Chrome em modo headless
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-gpu")

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

            # Cria diretório para screenshots
            screenshots_dir = f"analyses_data/files/{session_id}"
            os.makedirs(screenshots_dir, exist_ok=True)

            try:
                for i, content in enumerate(viral_content, 1):
                    try:
                        url = content.get('url', '')
                        if not url:
                            continue

                        logger.info(f"📸 Capturando screenshot {i}/10: {content.get('title', 'Sem título')}")

                        # Acessa a URL
                        driver.get(url)

                        # Aguarda carregamento
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )

                        # Aguarda renderização completa
                        time.sleep(3)

                        # Captura screenshot
                        screenshot_path = f"{screenshots_dir}/viral_content_{i:02d}.png"
                        driver.save_screenshot(screenshot_path)

                        # Verifica se foi criado
                        if os.path.exists(screenshot_path) and os.path.getsize(screenshot_path) > 0:
                            screenshots.append({
                                'content_data': content,
                                'screenshot_path': screenshot_path,
                                'filename': f"viral_content_{i:02d}.png",
                                'url': url,
                                'title': content.get('title', ''),
                                'platform': content.get('platform', ''),
                                'viral_score': content.get('viral_score', 0),
                                'captured_at': datetime.now().isoformat()
                            })

                            logger.info(f"✅ Screenshot {i} capturado: {screenshot_path}")
                        else:
                            logger.warning(f"⚠️ Falha ao capturar screenshot {i}")

                    except Exception as e:
                        logger.error(f"❌ Erro ao capturar screenshot {i}: {e}")
                        continue

            finally:
                driver.quit()

        except ImportError:
            logger.error("❌ Selenium não instalado - screenshots não disponíveis")
            return []
        except Exception as e:
            logger.error(f"❌ Erro na captura de screenshots: {e}")
            return []

        return screenshots

    def _calculate_viral_score(self, stats: Dict[str, Any]) -> float:
        """Calcula score viral para YouTube"""
        try:
            views = int(stats.get('viewCount', 0))
            likes = int(stats.get('likeCount', 0))
            comments = int(stats.get('commentCount', 0))

            # Fórmula viral: views + (likes * 10) + (comments * 20)
            viral_score = views + (likes * 10) + (comments * 20)

            # Normaliza para 0-10
            return min(10.0, viral_score / 100000)

        except:
            return 0.0

    def _calculate_social_viral_score(self, post: Dict[str, Any]) -> float:
        """Calcula score viral para redes sociais"""
        try:
            likes = int(post.get('likes', 0))
            comments = int(post.get('comments', 0))
            shares = int(post.get('shares', 0))
            engagement_rate = float(post.get('engagement_rate', 0))

            # Fórmula viral para redes sociais
            viral_score = (likes * 1) + (comments * 5) + (shares * 10) + (engagement_rate * 1000)

            # Normaliza para 0-10
            return min(10.0, viral_score / 10000)

        except:
            return 0.0

    def _calculate_twitter_viral_score(self, metrics: Dict[str, Any]) -> float:
        """Calcula score viral para Twitter"""
        try:
            retweets = int(metrics.get('retweet_count', 0))
            likes = int(metrics.get('like_count', 0))
            replies = int(metrics.get('reply_count', 0))
            quotes = int(metrics.get('quote_count', 0))

            # Fórmula viral para Twitter
            viral_score = (retweets * 10) + (likes * 2) + (replies * 5) + (quotes * 15)

            # Normaliza para 0-10
            return min(10.0, viral_score / 5000)

        except:
            return 0.0

    def get_session_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas da sessão atual"""
        return self.session_stats.copy()

# Instância global
real_search_orchestrator = RealSearchOrchestrator()
