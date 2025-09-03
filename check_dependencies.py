
#!/usr/bin/env python3
"""
Script para verificar dependências críticas do ARQV30
"""

import subprocess
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_chrome():
    """Verifica se o Chrome está instalado"""
    try:
        result = subprocess.run(['google-chrome', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info(f"✅ Chrome: {result.stdout.strip()}")
            return True
    except Exception as e:
        logger.error(f"❌ Chrome não encontrado: {e}")
    
    # Procura no Nix store
    import glob
    nix_paths = glob.glob("/nix/store/*/bin/google-chrome*")
    if nix_paths:
        logger.info(f"✅ Chrome encontrado no Nix: {nix_paths[0]}")
        return True
    
    return False

def check_chromedriver():
    """Verifica se o ChromeDriver está disponível"""
    try:
        result = subprocess.run(['chromedriver', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info(f"✅ ChromeDriver: {result.stdout.strip()}")
            return True
    except Exception as e:
        logger.error(f"❌ ChromeDriver não encontrado: {e}")
    
    return False

def check_selenium():
    """Verifica se o Selenium está importável"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        logger.info("✅ Selenium importado com sucesso")
        return True
    except ImportError as e:
        logger.error(f"❌ Selenium não importável: {e}")
        return False

def main():
    """Executa todas as verificações"""
    logger.info("🔍 Verificando dependências do ARQV30...")
    
    checks = {
        'Chrome': check_chrome(),
        'ChromeDriver': check_chromedriver(), 
        'Selenium': check_selenium()
    }
    
    all_ok = all(checks.values())
    
    if all_ok:
        logger.info("✅ Todas as dependências estão OK!")
        return 0
    else:
        logger.error("❌ Algumas dependências estão faltando:")
        for name, status in checks.items():
            status_emoji = "✅" if status else "❌"
            logger.error(f"  {status_emoji} {name}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
