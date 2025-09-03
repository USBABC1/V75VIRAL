#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Viral Integration Service
Serviço para integrar com o app viral (Cloudflare Worker)
"""

import os
import logging
import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import requests
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ViralIntegrationService:
    """Serviço para integrar com o app viral"""

    def __init__(self):
        """Inicializa o serviço de integração viral"""
        # URL do worker viral - pode ser configurada via variável de ambiente
        self.viral_worker_url = os.getenv('VIRAL_WORKER_URL', 'http://localhost:8787')
        self.timeout = 30
        self.max_retries = 3
        
        # Diretório para salvar imagens
        self.images_dir = Path("analyses_data/viral_images")
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🔥 Viral Integration Service inicializado - URL: {self.viral_worker_url}")

    async def search_viral_content(
        self,
        query: str,
        session_id: str,
        max_images: int = 20,
        min_engagement: int = 50,
        platforms: List[str] = None
    ) -> Dict[str, Any]:
        """Busca conteúdo viral usando o worker"""
        
        if platforms is None:
            platforms = ['instagram', 'facebook']
        
        logger.info(f"🔍 Buscando conteúdo viral para: {query}")
        
        search_payload = {
            "query": query,
            "max_images": max_images,
            "min_engagement": min_engagement,
            "platforms": platforms
        }
        
        # Primeiro tenta verificar se o serviço viral está disponível
        if not await self._check_viral_service_health():
            logger.warning("⚠️ Serviço viral não disponível, tentando método alternativo")
            # Tenta método síncrono como fallback
            return await self._search_viral_sync_fallback(query, session_id, search_payload)
        
        # Tenta múltiplas vezes com diferentes configurações
        for attempt in range(self.max_retries):
            try:
                # Configuração mais robusta para conexões locais
                connector = aiohttp.TCPConnector(
                    limit=10,
                    limit_per_host=5,
                    ttl_dns_cache=300,
                    use_dns_cache=True,
                    keepalive_timeout=30,
                    enable_cleanup_closed=True
                )
                
                timeout = aiohttp.ClientTimeout(
                    total=15,  # Timeout menor
                    connect=5,
                    sock_read=10
                )
                
                async with aiohttp.ClientSession(
                    connector=connector,
                    timeout=timeout
                ) as session:
                    logger.info(f"🔄 Tentativa {attempt + 1}/{self.max_retries} de conexão viral")
                    
                    async with session.post(
                        f"{self.viral_worker_url}/api/search",
                        json=search_payload,
                        headers={
                            'Content-Type': 'application/json',
                            'User-Agent': 'V70V1-ViralIntegration/1.0'
                        }
                    ) as response:
                        
                        if response.status == 200:
                            result = await response.json()
                            logger.info(f"✅ Viral search concluída - {len(result.get('images', []))} imagens encontradas")
                            
                            # Processa e salva imagens localmente
                            processed_result = await self._process_viral_results(result, session_id)
                            return processed_result
                        else:
                            error_text = await response.text()
                            logger.error(f"❌ Erro na busca viral (tentativa {attempt + 1}): {response.status} - {error_text}")
                            
                            if attempt == self.max_retries - 1:
                                return self._create_fallback_result(query, session_id)
                            
                            # Aguarda antes da próxima tentativa
                            await asyncio.sleep(2 ** attempt)
                            continue
                            
            except (asyncio.TimeoutError, aiohttp.ClientError) as e:
                logger.error(f"⏰ Erro de conexão viral (tentativa {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    return self._create_fallback_result(query, session_id)
                await asyncio.sleep(2 ** attempt)
                continue
                
            except Exception as e:
                logger.error(f"❌ Erro inesperado na integração viral (tentativa {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    return self._create_fallback_result(query, session_id)
                await asyncio.sleep(2 ** attempt)
                continue

    async def _check_viral_service_health(self) -> bool:
        """Verifica se o serviço viral está disponível"""
        try:
            # Usa requests síncrono para verificação rápida
            import requests
            response = requests.get(
                f"{self.viral_worker_url}/api/searches",
                timeout=5,
                headers={'User-Agent': 'V70V1-HealthCheck/1.0'}
            )
            
            if response.status_code in [200, 404]:  # 404 é OK, significa que o serviço está rodando
                logger.info("✅ Serviço viral está disponível")
                return True
            else:
                logger.warning(f"⚠️ Serviço viral retornou status {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            logger.warning("⚠️ Não foi possível conectar ao serviço viral")
            return False
        except requests.exceptions.Timeout:
            logger.warning("⚠️ Timeout ao verificar serviço viral")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Erro ao verificar serviço viral: {e}")
            return False

    async def _search_viral_sync_fallback(self, query: str, session_id: str, search_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Método síncrono de fallback para busca viral"""
        try:
            logger.info("🔄 Tentando busca viral com método síncrono")
            
            import requests
            response = requests.post(
                f"{self.viral_worker_url}/api/search",
                json=search_payload,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'V70V1-SyncFallback/1.0'
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Viral search síncrona concluída - {len(result.get('images', []))} imagens encontradas")
                
                # Processa e salva imagens localmente
                processed_result = await self._process_viral_results(result, session_id)
                return processed_result
            else:
                logger.error(f"❌ Erro na busca viral síncrona: {response.status_code} - {response.text}")
                return self._create_fallback_result(query, session_id)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro de conexão na busca viral síncrona: {e}")
            return self._create_fallback_result(query, session_id)
        except Exception as e:
            logger.error(f"❌ Erro inesperado na busca viral síncrona: {e}")
            return self._create_fallback_result(query, session_id)

    async def _process_viral_results(self, viral_result: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Processa resultados do viral e salva imagens localmente"""
        
        processed_images = []
        session_images_dir = self.images_dir / session_id
        session_images_dir.mkdir(parents=True, exist_ok=True)
        
        images = viral_result.get('images', [])
        
        for i, image_data in enumerate(images):
            try:
                # Baixa e salva a imagem localmente
                local_image_path = await self._download_and_save_image(
                    image_data.get('image_url', ''),
                    session_images_dir,
                    f"viral_image_{i+1}_{int(time.time())}"
                )
                
                # Adiciona informações processadas
                processed_image = {
                    'id': f"viral_{session_id}_{i+1}",
                    'title': image_data.get('title', 'Conteúdo Viral'),
                    'description': image_data.get('description', ''),
                    'platform': image_data.get('platform', 'unknown'),
                    'engagement_score': image_data.get('engagement_score', 0),
                    'views_estimate': image_data.get('views_estimate', 0),
                    'likes_estimate': image_data.get('likes_estimate', 0),
                    'comments_estimate': image_data.get('comments_estimate', 0),
                    'shares_estimate': image_data.get('shares_estimate', 0),
                    'author': image_data.get('author', 'Desconhecido'),
                    'author_followers': image_data.get('author_followers', 0),
                    'post_date': image_data.get('post_date', datetime.now().isoformat()),
                    'hashtags': image_data.get('hashtags', []),
                    'original_url': image_data.get('post_url', ''),
                    'image_url': image_data.get('image_url', ''),
                    'local_image_path': str(local_image_path) if local_image_path else None,
                    'collected_at': datetime.now().isoformat()
                }
                
                processed_images.append(processed_image)
                
            except Exception as e:
                logger.error(f"❌ Erro ao processar imagem viral {i+1}: {e}")
                continue
        
        # Calcula métricas agregadas
        total_engagement = sum(img.get('engagement_score', 0) for img in processed_images)
        total_views = sum(img.get('views_estimate', 0) for img in processed_images)
        total_likes = sum(img.get('likes_estimate', 0) for img in processed_images)
        
        platforms_found = list(set(img.get('platform', 'unknown') for img in processed_images))
        
        return {
            'session_id': session_id,
            'search_completed_at': datetime.now().isoformat(),
            'total_images_found': len(processed_images),
            'total_images_saved': len([img for img in processed_images if img.get('local_image_path')]),
            'platforms_searched': platforms_found,
            'viral_images': processed_images,
            'aggregated_metrics': {
                'total_engagement_score': total_engagement,
                'average_engagement': total_engagement / len(processed_images) if processed_images else 0,
                'total_estimated_views': total_views,
                'total_estimated_likes': total_likes,
                'top_performing_platform': max(platforms_found, key=lambda p: len([img for img in processed_images if img.get('platform') == p])) if platforms_found else 'none'
            },
            'original_viral_result': viral_result
        }

    async def _download_and_save_image(self, image_url: str, save_dir: Path, filename_base: str) -> Optional[Path]:
        """Baixa e salva uma imagem localmente"""
        
        if not image_url:
            return None
            
        try:
            # Determina extensão da imagem
            parsed_url = urlparse(image_url)
            path_parts = parsed_url.path.split('.')
            extension = path_parts[-1].lower() if len(path_parts) > 1 and path_parts[-1].lower() in ['jpg', 'jpeg', 'png', 'gif', 'webp'] else 'jpg'
            
            filename = f"{filename_base}.{extension}"
            file_path = save_dir / filename
            
            # Baixa a imagem
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Salva o arquivo
                        with open(file_path, 'wb') as f:
                            f.write(content)
                        
                        logger.info(f"✅ Imagem salva: {file_path}")
                        return file_path
                    else:
                        logger.warning(f"⚠️ Falha ao baixar imagem: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Erro ao baixar imagem {image_url}: {e}")
            return None

    def _create_fallback_result(self, query: str, session_id: str) -> Dict[str, Any]:
        """Cria resultado de fallback quando a integração viral falha"""
        
        logger.warning("⚠️ Usando resultado de fallback para viral")
        
        return {
            'session_id': session_id,
            'search_completed_at': datetime.now().isoformat(),
            'total_images_found': 0,
            'total_images_saved': 0,
            'platforms_searched': [],
            'viral_images': [],
            'aggregated_metrics': {
                'total_engagement_score': 0,
                'average_engagement': 0,
                'total_estimated_views': 0,
                'total_estimated_likes': 0,
                'top_performing_platform': 'none'
            },
            'error': 'Falha na integração com o serviço viral',
            'fallback_used': True,
            'original_query': query
        }

    def get_viral_search_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Obtém histórico de buscas virais (se o worker estiver disponível)"""
        
        try:
            response = requests.get(
                f"{self.viral_worker_url}/api/searches",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()[:limit]
            else:
                logger.warning(f"⚠️ Falha ao obter histórico viral: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter histórico viral: {e}")
            return []

    def get_viral_search_by_id(self, search_id: str) -> Optional[Dict[str, Any]]:
        """Obtém resultado de busca viral específica por ID"""
        
        try:
            response = requests.get(
                f"{self.viral_worker_url}/api/search/{search_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"⚠️ Busca viral {search_id} não encontrada: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter busca viral {search_id}: {e}")
            return None

# Instância global do serviço
viral_integration_service = ViralIntegrationService()