#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - WebSailor Integration REAL
Navegação web REAL sem cache ou simulação - DADOS 100% REAIS
"""

import os
import logging
import time
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import quote_plus, urljoin
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
import random

logger = logging.getLogger(__name__)

class WebSailorAgent:
    """Agente WebSailor para navegação web REAL - SEM CACHE OU SIMULAÇÃO"""
    
    def __init__(self):
        """Inicializa agente WebSailor REAL"""
        self.enabled = os.getenv("WEBSAILOR_ENABLED", "true").lower() == "true"
        self.google_search_key = os.getenv("GOOGLE_SEARCH_KEY")
        self.jina_api_key = os.getenv("JINA_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")
        
        # URLs das APIs
        self.google_search_url = "https://www.googleapis.com/customsearch/v1"
        self.jina_reader_url = "https://r.jina.ai/"
        
        # Headers REAIS para requisições
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        # SEM CACHE - TUDO REAL!
        logger.info(f"WebSailor Agent REAL initialized - Enabled: {self.enabled}")
    
    def is_available(self) -> bool:
        """Verifica se o WebSailor está disponível"""
        return self.enabled
    
    def navigate_and_research(
        self, 
        query: str, 
        context: Dict[str, Any],
        max_pages: int = 15,
        depth: int = 3,
        aggressive_mode: bool = True
    ) -> Dict[str, Any]:
        """Navega e pesquisa informações REAIS com profundidade máxima"""
        
        if not self.is_available():
            logger.warning("WebSailor não está disponível")
            return self._generate_emergency_real_research(query, context)
        
        try:
            logger.info(f"🚀 INICIANDO PESQUISA REAL para: {query}")
            start_time = time.time()
            
            all_page_contents = []
            
            # 1. BUSCA REAL MÚLTIPLA
            search_engines = [
                self._google_search_real,
                self._bing_search_real,
                self._duckduckgo_search_real,
                self._yahoo_search_real
            ]
            
            for search_engine in search_engines:
                try:
                    results = search_engine(query, max_pages)
                    if results:
                        logger.info(f"✅ {search_engine.__name__}: {len(results)} resultados REAIS")
                        
                        # Extrai conteúdo REAL de cada página
                        for result in results[:10]:  # Top 10 por engine
                            content = self._extract_real_page_content(result["url"])
                            if content and len(content) > 100:  # Só conteúdo substancial
                                all_page_contents.append({
                                    "url": result["url"],
                                    "title": result["title"],
                                    "content": content,
                                    "relevance_score": self._calculate_real_relevance(content, query, context),
                                    "source_type": "real_search",
                                    "search_engine": search_engine.__name__
                                })
                                
                                # Delay para não sobrecarregar
                                time.sleep(0.5)
                    
                except Exception as e:
                    logger.warning(f"Erro em {search_engine.__name__}: {str(e)}")
                    continue
            
            # 2. PESQUISA EM PROFUNDIDADE REAL
            if depth > 1 and all_page_contents:
                logger.info(f"🔍 PESQUISA EM PROFUNDIDADE REAL (nível {depth})...")
                top_pages = sorted(all_page_contents, key=lambda x: x["relevance_score"], reverse=True)[:5]
                
                for page in top_pages:
                    internal_links = self._extract_real_internal_links(page["url"], page["content"])
                    for link in internal_links[:3]:  # Top 3 links internos
                        internal_content = self._extract_real_page_content(link)
                        if internal_content and len(internal_content) > 100:
                            all_page_contents.append({
                                "url": link,
                                "title": f"Link interno de {page['title']}",
                                "content": internal_content,
                                "relevance_score": self._calculate_real_relevance(internal_content, query, context) * 0.8,
                                "source_type": "internal_link",
                                "parent_url": page["url"]
                            })
                            time.sleep(0.3)
            
            # 3. PESQUISA DE QUERIES RELACIONADAS REAIS
            if aggressive_mode:
                logger.info("🎯 PESQUISA AGRESSIVA COM QUERIES RELACIONADAS REAIS...")
                related_queries = self._generate_real_related_queries(query, context)
                
                for related_query in related_queries[:3]:
                    try:
                        related_results = self._google_search_real(related_query, 5)
                        for result in related_results:
                            content = self._extract_real_page_content(result["url"])
                            if content and len(content) > 100:
                                all_page_contents.append({
                                    "url": result["url"],
                                    "title": result["title"],
                                    "content": content,
                                    "relevance_score": self._calculate_real_relevance(content, query, context) * 0.7,
                                    "source_type": "related_query",
                                    "original_query": related_query
                                })
                                time.sleep(0.4)
                    except Exception as e:
                        logger.warning(f"Erro em query relacionada '{related_query}': {str(e)}")
                        continue
            
            # 4. FILTRA E ORDENA POR RELEVÂNCIA REAL
            all_page_contents = [p for p in all_page_contents if p["relevance_score"] > 1.0]
            all_page_contents.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            # 5. CONSOLIDA INFORMAÇÕES REAIS
            research_result = self._consolidate_real_research(all_page_contents, query, context)
            
            end_time = time.time()
            logger.info(f"✅ PESQUISA REAL CONCLUÍDA em {end_time - start_time:.2f} segundos")
            logger.info(f"📊 {len(all_page_contents)} páginas REAIS analisadas")
            
            return research_result
            
        except Exception as e:
            logger.error(f"❌ ERRO CRÍTICO na pesquisa real: {str(e)}", exc_info=True)
            return self._generate_emergency_real_research(query, context)
    
    def _google_search_real(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca REAL usando Google Custom Search API"""
        
        if not self.google_search_key or not self.google_cse_id:
            logger.warning("Google Search API não configurada")
            return []
        
        try:
            enhanced_query = self._enhance_search_query_real(query)
            
            params = {
                "key": self.google_search_key,
                "cx": self.google_cse_id,
                "q": enhanced_query,
                "num": min(max_results, 10),
                "lr": "lang_pt",
                "gl": "br",
                "safe": "off",
                "dateRestrict": "m6",  # Últimos 6 meses
                "sort": "date"
            }
            
            response = requests.get(
                self.google_search_url,
                params=params,
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get("items", []):
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "google_real"
                    })
                
                logger.info(f"🔍 Google Search REAL: {len(results)} resultados")
                return results
            else:
                logger.warning(f"Google Search falhou: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Erro no Google Search REAL: {str(e)}")
            return []
    
    def _bing_search_real(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca REAL usando Bing"""
        
        try:
            # Bing search via scraping
            search_url = f"https://www.bing.com/search?q={quote_plus(query)}&cc=br&setlang=pt-br"
            
            response = requests.get(
                search_url,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []
                
                # Extrai resultados do Bing
                result_items = soup.find_all('li', class_='b_algo')
                
                for item in result_items[:max_results]:
                    title_elem = item.find('h2')
                    if title_elem:
                        link_elem = title_elem.find('a')
                        if link_elem:
                            title = title_elem.get_text(strip=True)
                            url = link_elem.get('href', '')
                            
                            snippet_elem = item.find('p')
                            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                            
                            if url and title:
                                results.append({
                                    "title": title,
                                    "url": url,
                                    "snippet": snippet,
                                    "source": "bing_real"
                                })
                
                logger.info(f"🔍 Bing Search REAL: {len(results)} resultados")
                return results
                
        except Exception as e:
            logger.error(f"Erro no Bing Search REAL: {str(e)}")
            return []
    
    def _duckduckgo_search_real(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca REAL usando DuckDuckGo"""
        
        try:
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            
            response = requests.get(
                search_url,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []
                
                result_divs = soup.find_all('div', class_='result')
                
                for div in result_divs[:max_results]:
                    title_elem = div.find('a', class_='result__a')
                    snippet_elem = div.find('a', class_='result__snippet')
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        url = title_elem.get('href', '')
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                        
                        if url and title and url.startswith('http'):
                            results.append({
                                "title": title,
                                "url": url,
                                "snippet": snippet,
                                "source": "duckduckgo_real"
                            })
                
                logger.info(f"🔍 DuckDuckGo Search REAL: {len(results)} resultados")
                return results
                
        except Exception as e:
            logger.error(f"Erro no DuckDuckGo Search REAL: {str(e)}")
            return []
    
    def _yahoo_search_real(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca REAL usando Yahoo"""
        
        try:
            search_url = f"https://br.search.yahoo.com/search?p={quote_plus(query)}"
            
            response = requests.get(
                search_url,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []
                
                result_items = soup.find_all('div', class_='Sr')
                
                for item in result_items[:max_results]:
                    title_elem = item.find('h3')
                    if title_elem:
                        link_elem = title_elem.find('a')
                        if link_elem:
                            title = title_elem.get_text(strip=True)
                            url = link_elem.get('href', '')
                            
                            snippet_elem = item.find('span', class_='fz-ms')
                            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                            
                            if url and title and url.startswith('http'):
                                results.append({
                                    "title": title,
                                    "url": url,
                                    "snippet": snippet,
                                    "source": "yahoo_real"
                                })
                
                logger.info(f"🔍 Yahoo Search REAL: {len(results)} resultados")
                return results
                
        except Exception as e:
            logger.error(f"Erro no Yahoo Search REAL: {str(e)}")
            return []
    
    def _extract_real_page_content(self, url: str) -> Optional[str]:
        """Extrai conteúdo REAL de uma página web"""
        
        if not url or not url.startswith("http"):
            return None
        
        try:
            # Tenta primeiro com Jina Reader se disponível
            if self.jina_api_key:
                content = self._extract_with_jina_real(url)
                if content:
                    return content
            
            # Fallback para extração direta
            return self._extract_direct_real(url)
                
        except Exception as e:
            logger.error(f"Erro ao extrair conteúdo REAL de {url}: {str(e)}")
            return None
    
    def _extract_with_jina_real(self, url: str) -> Optional[str]:
        """Extrai conteúdo REAL usando Jina Reader API"""
        
        try:
            headers = {
                **self.headers,
                "Authorization": f"Bearer {self.jina_api_key}"
            }
            
            jina_url = f"{self.jina_reader_url}{url}"
            
            response = requests.get(
                jina_url,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                content = response.text
                
                if len(content) > 15000:
                    content = content[:15000] + "... [conteúdo truncado para otimização]"
                
                logger.info(f"✅ Jina Reader REAL: {len(content)} caracteres de {url}")
                return content
            else:
                logger.warning(f"Jina Reader falhou para {url}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erro no Jina Reader REAL para {url}: {str(e)}")
            return None
    
    def _extract_direct_real(self, url: str) -> Optional[str]:
        """Extração REAL direta usando requests + BeautifulSoup"""
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=20,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Remove elementos desnecessários
                for element in soup(["script", "style", "nav", "footer", "header", "form", "aside", "iframe", "noscript"]):
                    element.decompose()
                
                # Extrai texto principal
                main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|article'))
                
                if main_content:
                    text = main_content.get_text()
                else:
                    text = soup.get_text()
                
                # Limpa o texto
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = " ".join(chunk for chunk in chunks if chunk and len(chunk) > 3)
                
                if len(text) > 10000:
                    text = text[:10000] + "... [conteúdo truncado para otimização]"
                
                logger.info(f"✅ Extração direta REAL: {len(text)} caracteres de {url}")
                return text
            else:
                logger.warning(f"Falha ao acessar {url}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erro na extração direta REAL para {url}: {str(e)}")
            return None
    
    def _extract_real_internal_links(self, base_url: str, content: str) -> List[str]:
        """Extrai links internos REAIS de uma página"""
        
        links = []
        try:
            # Faz nova requisição para obter HTML completo
            response = requests.get(base_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                base_domain = base_url.split('/')[2]
                
                for a_tag in soup.find_all("a", href=True):
                    href = a_tag["href"]
                    full_url = urljoin(base_url, href)
                    
                    # Filtra apenas links do mesmo domínio
                    if (full_url.startswith('http') and 
                        base_domain in full_url and 
                        "#" not in full_url and 
                        full_url != base_url and
                        not any(ext in full_url.lower() for ext in ['.pdf', '.jpg', '.png', '.gif', '.zip'])):
                        links.append(full_url)
                
                logger.info(f"🔗 {len(links)} links internos REAIS encontrados em {base_url}")
        except Exception as e:
            logger.warning(f"Erro ao extrair links internos REAIS de {base_url}: {str(e)}")
        
        return list(set(links))[:10]  # Remove duplicatas e limita
    
    def _calculate_real_relevance(
        self, 
        content: str, 
        query: str, 
        context: Dict[str, Any]
    ) -> float:
        """Calcula score de relevância REAL do conteúdo"""
        
        if not content or len(content) < 50:
            return 0.0
        
        content_lower = content.lower()
        query_lower = query.lower()
        
        score = 0.0
        
        # Score baseado na query (peso maior)
        query_words = [w for w in query_lower.split() if len(w) > 2]
        for word in query_words:
            occurrences = content_lower.count(word)
            score += occurrences * 2.0  # Peso aumentado
        
        # Score baseado no contexto
        context_terms = []
        
        if context.get("segmento"):
            context_terms.append(str(context["segmento"]).lower())
        
        if context.get("produto"):
            context_terms.append(str(context["produto"]).lower())
        
        if context.get("publico"):
            context_terms.append(str(context["publico"]).lower())
        
        for term in context_terms:
            if term and len(term) > 2:
                occurrences = content_lower.count(term)
                score += occurrences * 1.5
        
        # Bonus para termos de mercado específicos
        market_terms = [
            "mercado", "análise", "tendência", "oportunidade", "estratégia", 
            "marketing", "concorrência", "público", "crescimento", "demanda", 
            "inovação", "tecnologia", "brasil", "brasileiro", "2024", "2025",
            "dados", "estatística", "pesquisa", "relatório", "estudo"
        ]
        
        for term in market_terms:
            occurrences = content_lower.count(term)
            score += occurrences * 0.5
        
        # Bonus por densidade de informação
        word_count = len(content.split())
        if word_count > 500:
            score += 2.0
        
        # Bonus por presença de números/percentuais
        import re
        numbers = re.findall(r'\d+(?:\.\d+)?%?', content)
        score += len(numbers) * 0.3
        
        # Normaliza score baseado no tamanho do conteúdo
        normalized_score = score / (len(content) / 1000 + 1)
        
        return min(normalized_score, 100.0)
    
    def _enhance_search_query_real(self, query: str) -> str:
        """Melhora a query de busca para pesquisa REAL de mercado"""
        
        # Termos que aumentam a precisão da busca
        precision_terms = [
            "dados", "estatísticas", "relatório", "pesquisa", "análise",
            "mercado brasileiro", "Brasil 2024", "tendências", "oportunidades"
        ]
        
        enhanced_query = query
        
        # Adiciona termos de precisão se não estiverem presentes
        query_lower = query.lower()
        for term in precision_terms[:3]:  # Máximo 3 termos adicionais
            if term.lower() not in query_lower:
                enhanced_query += f" {term}"
        
        return enhanced_query.strip()
    
    def _generate_real_related_queries(self, original_query: str, context: Dict[str, Any]) -> List[str]:
        """Gera queries relacionadas REAIS para pesquisa abrangente"""
        
        segmento = context.get("segmento", "")
        produto = context.get("produto", "")
        
        related_queries = []
        
        # Queries baseadas em aspectos específicos REAIS
        if segmento:
            related_queries.extend([
                f"dados mercado {segmento} Brasil 2024 crescimento",
                f"principais empresas {segmento} brasileiras líderes",
                f"tendências futuras {segmento} oportunidades investimento",
                f"análise competitiva {segmento} market share",
                f"regulamentações {segmento} mudanças legais impactos"
            ])
        
        if produto:
            related_queries.extend([
                f"demanda {produto} Brasil estatísticas consumo",
                f"preço médio {produto} mercado brasileiro benchmarks",
                f"inovações {produto} tecnologias emergentes"
            ])
        
        # Queries de inteligência de mercado REAL
        related_queries.extend([
            f"investimentos {original_query} venture capital funding",
            f"startups {original_query} unicórnios brasileiros",
            f"cases sucesso {original_query} empresas brasileiras"
        ])
        
        # Remove duplicatas e queries muito similares
        unique_queries = []
        for query in related_queries:
            if (query.lower() not in original_query.lower() and 
                query not in unique_queries and
                len(query.split()) >= 3):  # Queries substanciais
                unique_queries.append(query)
        
        return unique_queries[:5]  # Top 5 queries relacionadas
    
    def _consolidate_real_research(
        self, 
        page_contents: List[Dict[str, Any]], 
        query: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Consolida informações REAIS da pesquisa"""
        
        if not page_contents:
            return self._generate_emergency_real_research(query, context)
        
        # Ordena por relevância REAL
        page_contents.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Combina conteúdo das páginas mais relevantes
        combined_content = ""
        sources_list = []
        unique_insights = set()
        
        for i, page in enumerate(page_contents[:20]):  # Top 20 páginas
            combined_content += f"\n--- FONTE {i+1}: {page['title']} ({page['url']}) ---\n"
            combined_content += page["content"][:2000]  # Limita por página
            
            sources_list.append({
                "title": page["title"],
                "url": page["url"],
                "relevance_score": round(page["relevance_score"], 2),
                "source_type": page["source_type"],
                "search_engine": page.get("search_engine", "unknown")
            })
            
            # Extrai insights únicos
            insights = self._extract_real_insights(page["content"], query, context)
            unique_insights.update(insights)
            
            if len(combined_content) > 25000:  # Limite total
                combined_content = combined_content[:25000] + "... [conteúdo adicional disponível]"
                break
        
        # Análise de tendências REAL
        trends = self._analyze_real_trends(combined_content, context)
        opportunities = self._identify_real_opportunities(combined_content, context)
        
        result = {
            "query": query,
            "context": context,
            "pages_analyzed": len(page_contents),
            "research_summary": {
                "combined_content": combined_content,
                "key_insights": list(unique_insights)[:15],  # Top 15 insights únicos
                "market_trends": trends,
                "opportunities": opportunities,
                "data_quality_score": self._calculate_data_quality(page_contents)
            },
            "sources": sources_list,
            "metadata": {
                "research_date": datetime.now().isoformat(),
                "agent": "WebSailor_REAL",
                "version": "2.0.0",
                "total_content_length": len(combined_content),
                "unique_sources": len(set(s["url"] for s in sources_list)),
                "search_engines_used": len(set(s.get("search_engine", "unknown") for s in sources_list)),
                "ai_assisted_consolidation": False,
                "real_data_guarantee": True
            }
        }
        
        return result
    
    def _extract_real_insights(self, content: str, query: str, context: Dict[str, Any]) -> List[str]:
        """Extrai insights REAIS do conteúdo"""
        
        insights = []
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 50]
        
        # Padrões para identificar insights valiosos
        insight_patterns = [
            r'crescimento de (\d+(?:\.\d+)?%)',
            r'mercado de R\$ ([\d,\.]+)',
            r'(\d+(?:\.\d+)?%) dos consumidores',
            r'tendência de (\w+)',
            r'oportunidade de (\w+)',
            r'principal desafio é (\w+)',
            r'futuro do (\w+)',
            r'inovação em (\w+)'
        ]
        
        for sentence in sentences[:50]:  # Analisa até 50 sentenças
            sentence_lower = sentence.lower()
            
            # Verifica se contém termos relevantes
            if any(term in sentence_lower for term in [
                'crescimento', 'mercado', 'oportunidade', 'tendência', 
                'futuro', 'inovação', 'desafio', 'consumidor'
            ]):
                # Verifica se contém dados numéricos
                import re
                if re.search(r'\d+', sentence):
                    insights.append(sentence[:200])  # Limita tamanho
        
        return insights[:10]  # Top 10 insights por página
    
    def _analyze_real_trends(self, content: str, context: Dict[str, Any]) -> List[str]:
        """Analisa tendências REAIS do conteúdo"""
        
        trends = []
        content_lower = content.lower()
        
        # Padrões de tendências
        trend_keywords = [
            'inteligência artificial', 'ia', 'machine learning',
            'sustentabilidade', 'esg', 'verde',
            'digital', 'digitalização', 'transformação digital',
            'mobile', 'aplicativo', 'app',
            'e-commerce', 'marketplace', 'vendas online',
            'automação', 'robotização',
            'personalização', 'customização',
            'experiência do cliente', 'cx',
            'dados', 'big data', 'analytics'
        ]
        
        for keyword in trend_keywords:
            if keyword in content_lower:
                # Busca contexto ao redor da palavra-chave
                import re
                pattern = rf'.{{0,100}}{re.escape(keyword)}.{{0,100}}'
                matches = re.findall(pattern, content_lower, re.IGNORECASE)
                
                if matches:
                    trend_context = matches[0].strip()
                    if len(trend_context) > 50:
                        trends.append(f"Tendência identificada: {trend_context[:150]}...")
        
        return trends[:5]  # Top 5 tendências
    
    def _identify_real_opportunities(self, content: str, context: Dict[str, Any]) -> List[str]:
        """Identifica oportunidades REAIS do conteúdo"""
        
        opportunities = []
        content_lower = content.lower()
        
        # Padrões de oportunidades
        opportunity_keywords = [
            'oportunidade', 'potencial', 'crescimento', 'expansão',
            'nicho', 'gap', 'lacuna', 'demanda não atendida',
            'mercado emergente', 'novo mercado', 'segmento inexplorado'
        ]
        
        for keyword in opportunity_keywords:
            if keyword in content_lower:
                import re
                pattern = rf'.{{0,100}}{re.escape(keyword)}.{{0,100}}'
                matches = re.findall(pattern, content_lower, re.IGNORECASE)
                
                if matches:
                    opp_context = matches[0].strip()
                    if len(opp_context) > 50:
                        opportunities.append(f"Oportunidade: {opp_context[:150]}...")
        
        return opportunities[:5]  # Top 5 oportunidades
    
    def _calculate_data_quality(self, page_contents: List[Dict[str, Any]]) -> float:
        """Calcula qualidade dos dados REAIS coletados"""
        
        if not page_contents:
            return 0.0
        
        quality_score = 0.0
        
        # Pontuação por diversidade de fontes
        unique_domains = len(set(p["url"].split('/')[2] for p in page_contents))
        quality_score += min(unique_domains * 10, 50)  # Máximo 50 pontos
        
        # Pontuação por relevância média
        avg_relevance = sum(p["relevance_score"] for p in page_contents) / len(page_contents)
        quality_score += min(avg_relevance * 2, 30)  # Máximo 30 pontos
        
        # Pontuação por quantidade de conteúdo
        total_content = sum(len(p["content"]) for p in page_contents)
        if total_content > 50000:
            quality_score += 20  # 20 pontos por volume substancial
        
        return min(quality_score, 100.0)
    
    def _generate_emergency_real_research(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gera pesquisa de emergência com dados REAIS básicos"""
        
        logger.warning("⚠️ Gerando pesquisa de emergência REAL")
        
        return {
            "query": query,
            "context": context,
            "pages_analyzed": 0,
            "research_summary": {
                "combined_content": f"PESQUISA DE EMERGÊNCIA para: {query}. Sistema em modo de recuperação - dados limitados disponíveis.",
                "key_insights": [
                    f"Pesquisa emergencial para '{query}' - sistema em recuperação",
                    "Recomenda-se nova tentativa com configuração completa das APIs",
                    "Dados limitados disponíveis no momento"
                ],
                "market_trends": [
                    "Sistema em modo de emergência - tendências limitadas"
                ],
                "opportunities": [
                    "Reconfigurar APIs para análise completa"
                ],
                "data_quality_score": 10.0
            },
            "sources": [],
            "metadata": {
                "research_date": datetime.now().isoformat(),
                "agent": "WebSailor_Emergency",
                "version": "2.0.0",
                "note": "Modo de emergência ativado - configure APIs para dados completos",
                "real_data_guarantee": False
            }
        }

# Instância global do serviço REAL
websailor_agent = WebSailorAgent()