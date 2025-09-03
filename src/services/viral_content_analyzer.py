#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Viral Content Analyzer
Analisador de conteúdo viral com captura de screenshots
"""

import os
import logging
import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json

# Selenium imports
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    from webdriver_manager.chrome import ChromeDriverManager
    HAS_SELENIUM = True
except ImportError:
    #logger.warning("⚠️ Selenium não instalado - screenshots não disponíveis")
    HAS_SELENIUM = False

logger = logging.getLogger(__name__)

# Mock SeleniumChecker if it's not available to avoid errors during initialization
try:
    from .selenium_checker import SeleniumChecker
except ImportError:
    logger.warning("⚠️ selenium_checker não encontrado. Screenshots podem falhar.")
    class SeleniumChecker:
        def is_selenium_ready(self):
            return False # Assume False se o módulo não for encontrado

class ViralContentAnalyzer:
    """Analisador de conteúdo viral com captura automática"""

    def __init__(self):
        """Inicializa o analisador"""
        self.viral_thresholds = {
            'youtube': {
                'min_views': 10000,
                'min_likes': 500,
                'min_comments': 50,
                'engagement_rate': 0.05
            },
            'instagram': {
                'min_likes': 1000,
                'min_comments': 50,
                'engagement_rate': 0.03
            },
            'twitter': {
                'min_retweets': 100,
                'min_likes': 500,
                'min_replies': 20
            },
            'tiktok': {
                'min_views': 50000,
                'min_likes': 2000,
                'min_shares': 100
            }
        }

        self.screenshot_config = {
            'width': 1920,
            'height': 1080,
            'wait_time': 5,
            'scroll_pause': 2
        }

        logger.info("🔥 Viral Content Analyzer inicializado")

    async def analyze_and_capture_viral_content(
        self,
        search_results: Dict[str, Any],
        session_id: str,
        max_captures: int = 15
    ) -> Dict[str, Any]:
        """Analisa e captura conteúdo viral dos resultados de busca"""

        logger.info(f"🔥 Analisando conteúdo viral para sessão: {session_id}")

        analysis_results = {
            'session_id': session_id,
            'analysis_started': datetime.now().isoformat(),
            'viral_content_identified': [],
            'screenshots_captured': [],
            'viral_metrics': {},
            'platform_analysis': {},
            'top_performers': [],
            'engagement_insights': {}
        }

        try:
            # FASE 1: Identificação de Conteúdo Viral
            logger.info("🎯 FASE 1: Identificando conteúdo viral")

            all_content = []

            # Coleta todo o conteúdo
            for platform_results in ['web_results', 'youtube_results', 'social_results']:
                content_list = search_results.get(platform_results, [])
                all_content.extend(content_list)

            # Analisa viralidade
            viral_content = self._identify_viral_content(all_content)
            analysis_results['viral_content_identified'] = viral_content

            # FASE 2: Análise por Plataforma
            logger.info("📊 FASE 2: Análise detalhada por plataforma")
            platform_analysis = self._analyze_by_platform(viral_content)
            analysis_results['platform_analysis'] = platform_analysis

            # FASE 3: Captura de Screenshots
            logger.info("📸 FASE 3: Capturando screenshots do conteúdo viral")

            if HAS_SELENIUM and viral_content:
                try:
                    # Seleciona top performers para screenshot
                    top_content = sorted(
                        viral_content,
                        key=lambda x: x.get('viral_score', 0),
                        reverse=True
                    )[:max_captures]

                    screenshots = await self._capture_viral_screenshots(top_content, session_id)
                    analysis_results['screenshots_captured'] = screenshots
                except Exception as e:
                    logger.warning(f"⚠️ Screenshots não disponíveis: {e}")
                    # Continua sem screenshots - não é crítico
                    analysis_results['screenshots_captured'] = [] # Garante que seja uma lista vazia em caso de erro
            else:
                logger.warning("⚠️ Selenium não disponível ou nenhum conteúdo viral encontrado - screenshots desabilitados")
                analysis_results['screenshots_captured'] = [] # Garante que seja uma lista vazia

            # FASE 4: Métricas e Insights
            logger.info("📈 FASE 4: Calculando métricas virais")

            viral_metrics = self._calculate_viral_metrics(viral_content)
            analysis_results['viral_metrics'] = viral_metrics

            engagement_insights = self._extract_engagement_insights(viral_content)
            analysis_results['engagement_insights'] = engagement_insights

            # Top performers
            analysis_results['top_performers'] = sorted(
                viral_content,
                key=lambda x: x.get('viral_score', 0),
                reverse=True
            )[:10]

            logger.info(f"✅ Análise viral concluída: {len(viral_content)} conteúdos identificados")
            logger.info(f"📸 {len(analysis_results['screenshots_captured'])} screenshots capturados")

            return analysis_results

        except Exception as e:
            logger.error(f"❌ Erro na análise viral: {e}")
            raise

    def _identify_viral_content(self, all_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifica conteúdo viral baseado em métricas"""

        viral_content = []

        for content in all_content:
            platform = content.get('platform', 'web')
            viral_score = self._calculate_viral_score(content, platform)

            if viral_score >= 5.0:  # Threshold viral
                content['viral_score'] = viral_score
                content['viral_category'] = self._categorize_viral_content(content, viral_score)
                viral_content.append(content)

        return viral_content

    def _calculate_viral_score(self, content: Dict[str, Any], platform: str) -> float:
        """Calcula score viral baseado na plataforma"""

        try:
            if platform == 'youtube':
                views = int(content.get('view_count', 0))
                likes = int(content.get('like_count', 0))
                comments = int(content.get('comment_count', 0))

                # Fórmula YouTube: views/1000 + likes/100 + comments/10
                score = (views / 1000) + (likes / 100) + (comments / 10)
                return min(10.0, score / 100)

            elif platform in ['instagram', 'facebook']:
                likes = int(content.get('likes', 0))
                comments = int(content.get('comments', 0))
                shares = int(content.get('shares', 0))

                # Fórmula Instagram/Facebook
                score = (likes / 100) + (comments / 10) + (shares / 5)
                return min(10.0, score / 50)

            elif platform == 'twitter':
                retweets = int(content.get('retweets', 0))
                likes = int(content.get('likes', 0))
                replies = int(content.get('replies', 0))

                # Fórmula Twitter
                score = (retweets / 10) + (likes / 50) + (replies / 5)
                return min(10.0, score / 20)

            elif platform == 'tiktok':
                views = int(content.get('view_count', 0))
                likes = int(content.get('likes', 0))
                shares = int(content.get('shares', 0))

                # Fórmula TikTok
                score = (views / 10000) + (likes / 500) + (shares / 100)
                return min(10.0, score / 50)

            else:
                # Score baseado em relevância para conteúdo web
                relevance = content.get('relevance_score', 0)
                return relevance * 10

        except Exception as e:
            logger.warning(f"⚠️ Erro ao calcular score viral: {e}")
            return 0.0

    def _categorize_viral_content(self, content: Dict[str, Any], viral_score: float) -> str:
        """Categoriza conteúdo viral"""

        if viral_score >= 9.0:
            return 'MEGA_VIRAL'
        elif viral_score >= 7.0:
            return 'VIRAL'
        elif viral_score >= 5.0:
            return 'TRENDING'
        else:
            return 'POPULAR'

    def _analyze_by_platform(self, viral_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa conteúdo viral por plataforma"""

        platform_stats = {}

        for content in viral_content:
            platform = content.get('platform', 'web')

            if platform not in platform_stats:
                platform_stats[platform] = {
                    'total_content': 0,
                    'avg_viral_score': 0,
                    'top_content': [],
                    'engagement_metrics': {},
                    'content_themes': []
                }

            stats = platform_stats[platform]
            stats['total_content'] += 1
            stats['top_content'].append(content)

            # Calcula métricas de engajamento
            if platform == 'youtube':
                stats['engagement_metrics']['total_views'] = stats['engagement_metrics'].get('total_views', 0) + int(content.get('view_count', 0))
                stats['engagement_metrics']['total_likes'] = stats['engagement_metrics'].get('total_likes', 0) + int(content.get('like_count', 0))

            elif platform in ['instagram', 'facebook']:
                stats['engagement_metrics']['total_likes'] = stats['engagement_metrics'].get('total_likes', 0) + int(content.get('likes', 0))
                stats['engagement_metrics']['total_comments'] = stats['engagement_metrics'].get('total_comments', 0) + int(content.get('comments', 0))

        # Calcula médias
        for platform, stats in platform_stats.items():
            if stats['total_content'] > 0:
                total_score = sum(c.get('viral_score', 0) for c in stats['top_content'])
                stats['avg_viral_score'] = total_score / stats['total_content']

                # Ordena top content
                stats['top_content'] = sorted(
                    stats['top_content'],
                    key=lambda x: x.get('viral_score', 0),
                    reverse=True
                )[:5]

        return platform_stats

    async def _capture_viral_screenshots(
        self,
        viral_content: List[Dict[str, Any]],
        session_id: str
    ) -> List[Dict[str, Any]]:
        """Captura screenshots do conteúdo viral"""

        if not HAS_SELENIUM:
            logger.warning("⚠️ Selenium não disponível para screenshots")
            return []

        screenshots = []

        try:
            # Configura Chrome headless para Replit
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--remote-debugging-port=9222")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            # chrome_options.add_argument("--disable-images") # Comentado para permitir carregamento de imagens
            chrome_options.add_argument(f"--window-size={self.screenshot_config['width']},{self.screenshot_config['height']}")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")

            # Usa Chrome do sistema Nix diretamente
            try:
                # Importa o selenium_checker para usar sua lógica aprimorada
                from .selenium_checker import SeleniumChecker # Importa novamente para escopo local

                # Executa verificação completa
                checker = SeleniumChecker()
                check_results = checker.full_check()

                if not check_results['selenium_ready']:
                    logger.warning("⚠️ Selenium não está pronto - screenshots desabilitados")
                    return []

                # Usa o melhor caminho encontrado
                best_chrome_path = check_results.get('best_chrome_path')
                if best_chrome_path:
                    chrome_options.binary_location = best_chrome_path
                    logger.info(f"✅ Chrome configurado: {best_chrome_path}")
                else:
                    logger.warning("⚠️ Chrome não encontrado - screenshots desabilitados")
                    return []

                # Tenta usar ChromeDriverManager primeiro
                try:
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    logger.info("✅ ChromeDriverManager funcionou")
                except Exception as e:
                    logger.warning(f"⚠️ ChromeDriverManager falhou: {e}, tentando usar chromedriver do sistema")
                    # Fallback para chromedriver do sistema (se configurado corretamente)
                    try:
                        driver = webdriver.Chrome(options=chrome_options)
                        logger.info("✅ Chromedriver do sistema funcionou")
                    except WebDriverException as sys_driver_e:
                        logger.error(f"❌ Falha ao iniciar Chrome com chromedriver do sistema: {sys_driver_e}. Certifique-se de que o chromedriver esteja no PATH ou especificado.")
                        return []

            except Exception as e:
                logger.error(f"❌ Falha total na configuração do Chrome: {e}")
                return []

            # Cria diretório para screenshots
            screenshots_dir = Path(f"analyses_data/files/{session_id}")
            screenshots_dir.mkdir(parents=True, exist_ok=True)

            try:
                for i, content in enumerate(viral_content, 1):
                    try:
                        url = content.get('url', '')
                        if not url or not url.startswith(('http://', 'https://')):
                            logger.warning(f"Skipping invalid URL: {url}")
                            continue

                        logger.info(f"📸 Capturando screenshot {i}/{len(viral_content)}: {content.get('title', 'Sem título')}")

                        # Acessa a URL
                        driver.get(url)

                        # Aguarda carregamento
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )

                        # Aguarda renderização completa
                        await asyncio.sleep(self.screenshot_config['wait_time'])

                        # Scroll para carregar conteúdo lazy-loaded
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                        await asyncio.sleep(self.screenshot_config['scroll_pause'])
                        driver.execute_script("window.scrollTo(0, 0);")
                        await asyncio.sleep(1)

                        # Captura informações da página
                        page_title = driver.title or content.get('title', 'Sem título')
                        current_url = driver.current_url

                        # Define nome do arquivo
                        platform = content.get('platform', 'web')
                        viral_score = content.get('viral_score', 0)
                        # Evita caracteres inválidos no nome do arquivo
                        safe_title = "".join(c if c.isalnum() else "_" for c in page_title[:50])
                        filename = f"viral_{platform}_{i:02d}_score{viral_score:.1f}_{safe_title}.png"
                        screenshot_path = screenshots_dir / filename

                        # Captura screenshot
                        driver.save_screenshot(str(screenshot_path))

                        # Verifica se foi criado com sucesso
                        if screenshot_path.exists() and screenshot_path.stat().st_size > 0:
                            screenshot_data = {
                                'filename': filename,
                                'filepath': str(screenshot_path),
                                'relative_path': f"files/{session_id}/{filename}",
                                'url': url,
                                'final_url': current_url,
                                'title': page_title,
                                'platform': platform,
                                'viral_score': viral_score,
                                'viral_category': content.get('viral_category', 'POPULAR'),
                                'content_metrics': {
                                    'views': content.get('view_count', content.get('views', 0)),
                                    'likes': content.get('like_count', content.get('likes', 0)),
                                    'comments': content.get('comment_count', content.get('comments', 0)),
                                    'shares': content.get('shares', 0),
                                    'engagement_rate': content.get('engagement_rate', 0)
                                },
                                'file_size': screenshot_path.stat().st_size,
                                'captured_at': datetime.now().isoformat(),
                                'capture_success': True
                            }

                            screenshots.append(screenshot_data)
                            logger.info(f"✅ Screenshot {i} capturado: {filename}")
                        else:
                            logger.warning(f"⚠️ Falha ao criar arquivo de screenshot {i}: {screenshot_path}")

                    except (TimeoutException, WebDriverException) as e:
                        logger.error(f"❌ Erro de Selenium ao capturar screenshot {i} ({url}): {e}")
                        continue # Tenta o próximo conteúdo
                    except Exception as e:
                        logger.error(f"❌ Erro inesperado ao capturar screenshot {i} ({url}): {e}")
                        continue # Tenta o próximo conteúdo

            finally:
                if 'driver' in locals() and driver:
                    driver.quit()
                    logger.info("✅ Driver do Chrome fechado")

        except Exception as e:
            logger.warning(f"⚠️ Falha geral na captura de screenshots: {e}")
            return [] # Retorna lista vazia em caso de erro grave

        logger.info(f"📸 {len(screenshots)} screenshots capturados com sucesso")
        return screenshots

    def _calculate_viral_metrics(self, viral_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula métricas gerais de viralidade"""

        if not viral_content:
            return {}

        metrics = {
            'total_viral_content': len(viral_content),
            'avg_viral_score': 0,
            'viral_distribution': {
                'MEGA_VIRAL': 0,
                'VIRAL': 0,
                'TRENDING': 0,
                'POPULAR': 0
            },
            'platform_distribution': {},
            'engagement_totals': {
                'total_views': 0,
                'total_likes': 0,
                'total_comments': 0,
                'total_shares': 0
            },
            'top_viral_score': 0,
            'viral_content_percentage': 0 # Este campo não está sendo calculado, mas mantido por consistência
        }

        total_score = 0

        for content in viral_content:
            viral_score = content.get('viral_score', 0)
            total_score += viral_score

            # Atualiza score máximo
            if viral_score > metrics['top_viral_score']:
                metrics['top_viral_score'] = viral_score

            # Distribui por categoria
            category = content.get('viral_category', 'POPULAR')
            metrics['viral_distribution'][category] = metrics['viral_distribution'].get(category, 0) + 1

            # Distribui por plataforma
            platform = content.get('platform', 'web')
            metrics['platform_distribution'][platform] = metrics['platform_distribution'].get(platform, 0) + 1

            # Soma engajamento
            metrics['engagement_totals']['total_views'] += int(content.get('view_count', content.get('views', 0)))
            metrics['engagement_totals']['total_likes'] += int(content.get('like_count', content.get('likes', 0)))
            metrics['engagement_totals']['total_comments'] += int(content.get('comment_count', content.get('comments', 0)))
            metrics['engagement_totals']['total_shares'] += int(content.get('shares', 0))

        # Calcula médias
        if len(viral_content) > 0:
            metrics['avg_viral_score'] = total_score / len(viral_content)
        else:
            metrics['avg_viral_score'] = 0

        return metrics

    def _extract_engagement_insights(self, viral_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extrai insights de engajamento"""

        insights = {
            'best_performing_platforms': [],
            'optimal_content_types': [],
            'engagement_patterns': {},
            'viral_triggers': [],
            'audience_preferences': {}
        }

        # Analisa performance por plataforma
        platform_performance = {}

        for content in viral_content:
            platform = content.get('platform', 'web')
            viral_score = content.get('viral_score', 0)

            if platform not in platform_performance:
                platform_performance[platform] = {
                    'total_score': 0,
                    'content_count': 0,
                    'avg_score': 0
                }

            platform_performance[platform]['total_score'] += viral_score
            platform_performance[platform]['content_count'] += 1

        # Calcula médias e ordena
        for platform, data in platform_performance.items():
            if data['content_count'] > 0:
                data['avg_score'] = data['total_score'] / data['content_count']
            else:
                data['avg_score'] = 0

        insights['best_performing_platforms'] = sorted(
            platform_performance.items(),
            key=lambda x: x[1]['avg_score'],
            reverse=True
        )

        # Identifica padrões de conteúdo
        content_types = {}
        for content in viral_content:
            title = content.get('title', '').lower()

            # Categoriza por tipo de conteúdo
            if any(word in title for word in ['como', 'tutorial', 'passo a passo']):
                content_types['tutorial'] = content_types.get('tutorial', 0) + 1
            elif any(word in title for word in ['dica', 'segredo', 'truque']):
                content_types['dicas'] = content_types.get('dicas', 0) + 1
            elif any(word in title for word in ['caso', 'história', 'experiência']):
                content_types['casos'] = content_types.get('casos', 0) + 1
            elif any(word in title for word in ['análise', 'dados', 'pesquisa']):
                content_types['analise'] = content_types.get('analise', 0) + 1

        insights['optimal_content_types'] = sorted(
            content_types.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return insights

    def generate_viral_content_report(
        self,
        analysis_results: Dict[str, Any],
        session_id: str
    ) -> str:
        """Gera relatório detalhado do conteúdo viral"""

        viral_content = analysis_results.get('viral_content_identified', [])
        screenshots = analysis_results.get('screenshots_captured', [])
        metrics = analysis_results.get('viral_metrics', {})

        report = f"# RELATÓRIO DE CONTEÚDO VIRAL - ARQV30 Enhanced v3.0\n\n**Sessão:** {session_id}  \n**Análise realizada em:** {analysis_results.get('analysis_started', 'N/A')}  \n**Conteúdo viral identificado:** {len(viral_content)}  \n**Screenshots capturados:** {len(screenshots)}\n\n---\n\n## RESUMO EXECUTIVO\n\n### Métricas Gerais:\n- **Total de conteúdo viral:** {metrics.get('total_viral_content', 0)}\n- **Score viral médio:** {metrics.get('avg_viral_score', 0):.2f}/10\n- **Score viral máximo:** {metrics.get('top_viral_score', 0):.2f}/10\n\n### Distribuição por Categoria:\n"

        # Adiciona distribuição viral
        viral_dist = metrics.get('viral_distribution', {})
        for category, count in viral_dist.items():
            report += f"- **{category}:** {count} conteúdos\n"

        report += "\n### Distribuição por Plataforma:\n"
        platform_dist = metrics.get('platform_distribution', {})
        for platform, count in platform_dist.items():
            report += f"- **{platform.title()}:** {count} conteúdos\n"

        report += "\n---\n\n## TOP 10 CONTEÚDOS VIRAIS\n\n"

        # Lista top performers
        top_performers = analysis_results.get('top_performers', [])
        for i, content in enumerate(top_performers[:10], 1):
            report += f"### {i}. {content.get('title', 'Sem título')}\n\n**Plataforma:** {content.get('platform', 'N/A').title()}  \n**Score Viral:** {content.get('viral_score', 0):.2f}/10  \n**Categoria:** {content.get('viral_category', 'N/A')}  \n**URL:** {content.get('url', 'N/A')}  \n"

            # Métricas específicas por plataforma
            if content.get('platform') == 'youtube':
                report += f"**Views:** {content.get('view_count', 0):,}  \n**Likes:** {content.get('like_count', 0):,}  \n**Comentários:** {content.get('comment_count', 0):,}  \n**Canal:** {content.get('channel', 'N/A')}  \n"

            elif content.get('platform') in ['instagram', 'facebook']:
                report += f"**Likes:** {content.get('likes', 0):,}  \n**Comentários:** {content.get('comments', 0):,}  \n**Compartilhamentos:** {content.get('shares', 0):,}  \n"

            elif content.get('platform') == 'twitter':
                report += f"**Retweets:** {content.get('retweets', 0):,}  \n**Likes:** {content.get('likes', 0):,}  \n**Respostas:** {content.get('replies', 0):,}  \n"

            report += "\n"

        # Adiciona screenshots se disponíveis
        if screenshots:
            report += "---\n\n## EVIDÊNCIAS VISUAIS CAPTURADAS\n\n"

            for i, screenshot in enumerate(screenshots, 1):
                report += f"### Screenshot {i}: {screenshot.get('title', 'Sem título')}\n\n**Plataforma:** {screenshot.get('platform', 'N/A').title()}  \n**Score Viral:** {screenshot.get('viral_score', 0):.2f}/10  \n**URL Original:** {screenshot.get('url', 'N/A')}  \n![Screenshot {i}]({screenshot.get('relative_path', '')})  \n\n"

                # Métricas do conteúdo
                metrics = screenshot.get('content_metrics', {})
                if metrics:
                    report += "**Métricas de Engajamento:**  \n"
                    if metrics.get('views'):
                        report += f"- Views: {metrics['views']:,}  \n"
                    if metrics.get('likes'):
                        report += f"- Likes: {metrics['likes']:,}  \n"
                    if metrics.get('comments'):
                        report += f"- Comentários: {metrics['comments']:,}  \n"
                    if metrics.get('shares'):
                        report += f"- Compartilhamentos: {metrics['shares']:,}  \n"

                report += "\n"

        # Insights de engajamento
        engagement_insights = analysis_results.get('engagement_insights', {})
        if engagement_insights:
            report += "---\n\n## INSIGHTS DE ENGAJAMENTO\n\n"

            best_platforms = engagement_insights.get('best_performing_platforms', [])
            if best_platforms:
                report += "### Plataformas com Melhor Performance:\n"
                for platform, data in best_platforms[:3]:
                    report += f"1. **{platform.title()}:** Score médio {data['avg_score']:.2f} ({data['content_count']} conteúdos)\n"

            content_types = engagement_insights.get('optimal_content_types', [])
            if content_types:
                report += "\n### Tipos de Conteúdo Mais Virais:\n"
                for content_type, count in content_types[:5]:
                    report += f"- **{content_type.title()}:** {count} conteúdos virais\n"

        report += f"\n---\n\n*Relatório gerado automaticamente em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*"

        return report

# Instância global
viral_content_analyzer = ViralContentAnalyzer()