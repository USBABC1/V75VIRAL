#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Configuração do Módulo Viral
Configurações para integração com o app viral
"""

import os

# Configurações do Worker Viral
VIRAL_CONFIG = {
    # URL do worker viral - pode ser local ou em produção
    'worker_url': os.getenv('VIRAL_WORKER_URL', 'http://localhost:8787'),
    
    # Configurações de busca padrão
    'default_max_images': 20,
    'default_min_engagement': 50,
    'default_platforms': ['instagram', 'facebook'],
    
    # Configurações de timeout
    'request_timeout': 30,
    'max_retries': 3,
    
    # Configurações de imagens
    'images_dir': 'analyses_data/viral_images',
    'max_image_size_mb': 10,
    'allowed_extensions': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
    
    # Configurações de fallback
    'enable_fallback': True,
    'fallback_message': 'Módulo viral não disponível - usando dados simulados'
}

# URLs de exemplo para diferentes ambientes
ENVIRONMENT_URLS = {
    'local': 'http://localhost:8787',
    'development': 'https://your-dev-worker.your-subdomain.workers.dev',
    'production': 'https://your-prod-worker.your-subdomain.workers.dev'
}

def get_viral_config():
    """Retorna configuração do viral baseada no ambiente"""
    env = os.getenv('ENVIRONMENT', 'local')
    config = VIRAL_CONFIG.copy()
    
    if env in ENVIRONMENT_URLS:
        config['worker_url'] = ENVIRONMENT_URLS[env]
    
    return config

def is_viral_enabled():
    """Verifica se o módulo viral está habilitado"""
    return os.getenv('ENABLE_VIRAL', 'true').lower() == 'true'

def get_viral_platforms():
    """Retorna plataformas configuradas para busca viral"""
    platforms_str = os.getenv('VIRAL_PLATFORMS', 'instagram,facebook')
    return [p.strip() for p in platforms_str.split(',')]