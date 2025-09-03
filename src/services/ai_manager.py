
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - AI Manager com Sistema de Ferramentas
Gerenciador inteligente de múltiplas IAs com suporte a ferramentas e fallback automático
"""

import os
import logging
import time
import json
from typing import Dict, List, Optional, Any, Union
import requests
from datetime import datetime, timedelta

# Imports condicionais para os clientes de IA
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from services.groq_client import groq_client
    HAS_GROQ_CLIENT = True
except ImportError:
    HAS_GROQ_CLIENT = False

try:
    from services.search_api_manager import search_api_manager
    HAS_SEARCH_MANAGER = True
except ImportError:
    HAS_SEARCH_MANAGER = False

logger = logging.getLogger(__name__)

class AIManager:
    """Gerenciador de IA com fallback automático e suporte a ferramentas"""

    def __init__(self):
        """Inicializa o gerenciador de IA"""
        self.providers = {}
        self.last_used_provider = None
        self.error_counts = {}
        self.performance_metrics = {}
        self.circuit_breaker = {}
        
        self._initialize_providers()
        logger.info(f"✅ AI Manager inicializado com {len(self.providers)} provedores")

    def _initialize_providers(self):
        """Inicializa todos os provedores de IA disponíveis"""
        
        # Inicializa Gemini
        try:
            if HAS_GEMINI:
                api_key = os.getenv('GEMINI_API_KEY')
                if api_key:
                    genai.configure(api_key=api_key)
                    self.providers['gemini'] = {
                        'client': genai,
                        'available': True,
                        'model': 'gemini-2.0-flash-exp',
                        'priority': 1,
                        'error_count': 0,
                        'consecutive_failures': 0,
                        'max_errors': 5,
                        'last_success': None,
                        'supports_tools': True
                    }
                    logger.info("✅ Gemini 2.0 Flash inicializado.")
                else:
                    logger.info("ℹ️ GEMINI_API_KEY não configurada.")
            else:
                logger.info("ℹ️ Biblioteca 'google-generativeai' não instalada.")
        except Exception as e:
            logger.warning(f"ℹ️ Gemini não disponível: {str(e)}")

        # Inicializa OpenAI
        try:
            if HAS_OPENAI:
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key:
                    openai.api_key = api_key
                    self.providers['openai'] = {
                        'client': openai,
                        'available': True,
                        'model': 'gpt-4-0125-preview',
                        'priority': 2,
                        'error_count': 0,
                        'consecutive_failures': 0,
                        'max_errors': 3,
                        'last_success': None,
                        'supports_tools': True
                    }
                    logger.info("✅ OpenAI GPT-4 inicializado.")
                else:
                    logger.info("ℹ️ OPENAI_API_KEY não configurada.")
            else:
                logger.info("ℹ️ Biblioteca 'openai' não instalada.")
        except Exception as e:
            logger.warning(f"ℹ️ OpenAI não disponível: {str(e)}")

        # Inicializa Groq
        try:
            if HAS_GROQ_CLIENT and groq_client and groq_client.is_enabled():
                self.providers['groq'] = {
                    'client': groq_client,
                    'available': True,
                    'model': 'llama3-70b-8192',
                    'priority': 3,
                    'error_count': 0,
                    'consecutive_failures': 0,
                    'max_errors': 3,
                    'last_success': None,
                    'supports_tools': False
                }
                logger.info("✅ Groq (llama3-70b-8192) inicializado.")
            else:
                logger.info("ℹ️ Groq não disponível ou não configurado.")
        except Exception as e:
            logger.warning(f"ℹ️ Groq não disponível: {str(e)}")

    def _get_available_provider(self, require_tools: bool = False) -> Optional[str]:
        """Seleciona o melhor provedor disponível"""
        available_providers = []
        
        for name, provider in self.providers.items():
            if not provider['available']:
                continue
                
            if require_tools and not provider.get('supports_tools', False):
                continue
                
            if provider['consecutive_failures'] >= provider['max_errors']:
                continue
                
            available_providers.append((name, provider['priority']))
        
        if not available_providers:
            return None
            
        # Ordena por prioridade (menor número = maior prioridade)
        available_providers.sort(key=lambda x: x[1])
        return available_providers[0][0]

    async def google_search_tool(self, query: str) -> Dict[str, Any]:
        """Ferramenta de busca Google para uso pela IA"""
        try:
            if not HAS_SEARCH_MANAGER:
                return {'error': 'Search manager não disponível'}
            
            logger.info(f"🔍 IA solicitou busca: {query}")
            results = await search_api_manager.interleaved_search(query)
            
            # Formata resultados para a IA
            formatted_results = []
            for result in results.get('all_results', []):
                if result.get('success') and result.get('results'):
                    for item in result['results'][:5]:  # Limita a 5 resultados por provedor
                        if isinstance(item, dict):
                            formatted_item = {
                                'title': item.get('title', ''),
                                'url': item.get('url') or item.get('link', ''),
                                'snippet': item.get('snippet') or item.get('content', '')[:200]
                            }
                            if formatted_item['url']:
                                formatted_results.append(formatted_item)
            
            return {
                'query': query,
                'results': formatted_results[:10],  # Máximo 10 resultados
                'total_found': len(formatted_results)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na busca: {e}")
            return {'error': f'Erro na busca: {str(e)}'}

    def _get_google_search_function_definition(self) -> Dict[str, Any]:
        """Definição da função de busca Google para Gemini"""
        return {
            "name": "google_search",
            "description": "Busca informações atualizadas na internet usando múltiplos provedores de busca",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Termo de busca para encontrar informações relevantes"
                    }
                },
                "required": ["query"]
            }
        }

    async def generate_with_tools(self, prompt: str, context: str = "", tools: List[str] = None, max_iterations: int = 5) -> str:
        """
        Gera texto com suporte a ferramentas (function calling)
        
        Args:
            prompt: Prompt principal para a IA
            context: Contexto adicional (dados coletados)
            tools: Lista de ferramentas disponíveis ['google_search']
            max_iterations: Máximo de iterações para evitar loops
        """
        if tools is None:
            tools = ['google_search']
        
        # Verifica se há provedores com suporte a ferramentas
        provider_name = self._get_available_provider(require_tools=True)
        if not provider_name:
            logger.warning("⚠️ Nenhum provedor com suporte a ferramentas disponível, usando geração normal")
            return await self.generate_text(prompt + "\n\n" + context)
        
        provider = self.providers[provider_name]
        logger.info(f"🤖 Usando {provider_name} com ferramentas: {tools}")
        
        # Prepara mensagens
        full_prompt = f"{prompt}\n\nContexto disponível:\n{context}"
        
        # Loop de execução com ferramentas
        iteration = 0
        conversation_history = []
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"🔄 Iteração {iteration}/{max_iterations}")
            
            try:
                if provider_name == 'gemini':
                    result = await self._execute_gemini_with_tools(full_prompt, tools, conversation_history)
                elif provider_name == 'openai':
                    result = await self._execute_openai_with_tools(full_prompt, tools, conversation_history)
                else:
                    # Fallback para geração normal
                    return await self.generate_text(full_prompt)
                
                if result['type'] == 'text':
                    logger.info(f"✅ Resposta final gerada em {iteration} iterações")
                    return result['content']
                elif result['type'] == 'tool_call':
                    # Executa a ferramenta solicitada
                    tool_name = result['tool_name']
                    tool_args = result['tool_args']
                    
                    if tool_name == 'google_search' and 'query' in tool_args:
                        search_result = await self.google_search_tool(tool_args['query'])
                        conversation_history.append({
                            'type': 'tool_call',
                            'tool_name': tool_name,
                            'args': tool_args,
                            'result': search_result
                        })
                        
                        # Atualiza o contexto com os resultados da busca
                        search_context = self._format_search_results(search_result)
                        full_prompt += f"\n\nResultados da busca para '{tool_args['query']}':\n{search_context}"
                    else:
                        logger.warning(f"⚠️ Ferramenta {tool_name} não reconhecida ou argumentos inválidos")
                        break
                
            except Exception as e:
                logger.error(f"❌ Erro na iteração {iteration}: {e}")
                break
        
        logger.warning(f"⚠️ Máximo de iterações atingido ({max_iterations}), retornando resposta parcial")
        return "Análise realizada com ferramentas, mas processo interrompido por limite de iterações."

    async def _execute_gemini_with_tools(self, prompt: str, tools: List[str], history: List[Dict]) -> Dict[str, Any]:
        """Executa Gemini com suporte a ferramentas"""
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            # Prepara function declarations se google_search está nas tools
            function_declarations = []
            if 'google_search' in tools:
                function_declarations.append(self._get_google_search_function_definition())
            
            # Configura ferramentas se disponíveis
            tool_config = None
            if function_declarations:
                tool_config = genai.protos.Tool(function_declarations=function_declarations)
            
            # Inicia chat com ferramentas
            if tool_config:
                chat = model.start_chat(tools=[tool_config])
            else:
                chat = model.start_chat()
            
            # Envia mensagem
            response = chat.send_message(prompt)
            
            # Verifica se há function calls
            if response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        function_call = part.function_call
                        return {
                            'type': 'tool_call',
                            'tool_name': function_call.name,
                            'tool_args': dict(function_call.args)
                        }
            
            # Se não há function calls, retorna o texto
            return {
                'type': 'text',
                'content': response.text
            }
            
        except Exception as e:
            logger.error(f"❌ Erro no Gemini com ferramentas: {e}")
            raise

    async def _execute_openai_with_tools(self, prompt: str, tools: List[str], history: List[Dict]) -> Dict[str, Any]:
        """Executa OpenAI com suporte a ferramentas"""
        try:
            # Prepara tools para OpenAI
            openai_tools = []
            if 'google_search' in tools:
                openai_tools.append({
                    "type": "function",
                    "function": self._get_google_search_function_definition()
                })
            
            messages = [{"role": "user", "content": prompt}]
            
            # Adiciona histórico se existir
            for item in history:
                if item['type'] == 'tool_call':
                    messages.append({
                        "role": "assistant",
                        "tool_calls": [{
                            "id": f"call_{int(time.time())}",
                            "type": "function",
                            "function": {
                                "name": item['tool_name'],
                                "arguments": json.dumps(item['args'])
                            }
                        }]
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": f"call_{int(time.time())}",
                        "content": json.dumps(item['result'])
                    })
            
            # Faz a chamada
            if openai_tools:
                response = openai.ChatCompletion.create(
                    model="gpt-4-0125-preview",
                    messages=messages,
                    tools=openai_tools,
                    tool_choice="auto"
                )
            else:
                response = openai.ChatCompletion.create(
                    model="gpt-4-0125-preview",
                    messages=messages
                )
            
            message = response.choices[0].message
            
            # Verifica tool calls
            if hasattr(message, 'tool_calls') and message.tool_calls:
                tool_call = message.tool_calls[0]
                return {
                    'type': 'tool_call',
                    'tool_name': tool_call.function.name,
                    'tool_args': json.loads(tool_call.function.arguments)
                }
            
            return {
                'type': 'text',
                'content': message.content
            }
            
        except Exception as e:
            logger.error(f"❌ Erro no OpenAI com ferramentas: {e}")
            raise

    def _format_search_results(self, search_result: Dict[str, Any]) -> str:
        """Formata resultados de busca para contexto da IA"""
        if 'error' in search_result:
            return f"Erro na busca: {search_result['error']}"
        
        formatted = f"Busca: {search_result.get('query', '')}\n"
        formatted += f"Total encontrado: {search_result.get('total_found', 0)} resultados\n\n"
        
        for i, result in enumerate(search_result.get('results', []), 1):
            formatted += f"{i}. {result.get('title', 'Sem título')}\n"
            formatted += f"   URL: {result.get('url', '')}\n"
            formatted += f"   Resumo: {result.get('snippet', 'Sem descrição')}\n\n"
        
        return formatted

    async def generate_text(self, prompt: str, max_tokens: int = 8192, temperature: float = 0.7) -> str:
        """Gera texto usando o melhor provedor disponível"""
        provider_name = self._get_available_provider()
        
        if not provider_name:
            raise Exception("Nenhum provedor de IA disponível")
        
        provider = self.providers[provider_name]
        
        try:
            start_time = time.time()
            
            if provider_name == 'gemini':
                result = await self._generate_gemini(prompt, max_tokens, temperature)
            elif provider_name == 'openai':
                result = await self._generate_openai(prompt, max_tokens, temperature)
            elif provider_name == 'groq':
                result = provider['client'].generate(prompt, max_tokens)
            else:
                raise Exception(f"Provedor {provider_name} não implementado")
            
            # Registra sucesso
            provider['last_success'] = datetime.now()
            provider['consecutive_failures'] = 0
            
            processing_time = time.time() - start_time
            logger.info(f"✅ {provider_name} gerou {len(result)} caracteres em {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            # Registra falha
            provider['error_count'] += 1
            provider['consecutive_failures'] += 1
            
            logger.error(f"❌ Erro no {provider_name}: {e}")
            
            # Tenta próximo provedor se houver falhas consecutivas
            if provider['consecutive_failures'] >= provider['max_errors']:
                provider['available'] = False
                logger.warning(f"⚠️ {provider_name} desabilitado temporariamente")
                return await self.generate_text(prompt, max_tokens, temperature)
            
            raise

    async def _generate_gemini(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Gera texto usando Gemini"""
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text

    async def _generate_openai(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Gera texto usando OpenAI"""
        response = openai.ChatCompletion.create(
            model="gpt-4-0125-preview",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content

    def get_status(self) -> Dict[str, Any]:
        """Retorna status dos provedores"""
        status = {
            'total_providers': len(self.providers),
            'available_providers': sum(1 for p in self.providers.values() if p['available']),
            'providers': {}
        }
        
        for name, provider in self.providers.items():
            status['providers'][name] = {
                'available': provider['available'],
                'model': provider['model'],
                'error_count': provider['error_count'],
                'consecutive_failures': provider['consecutive_failures'],
                'last_success': provider['last_success'].isoformat() if provider['last_success'] else None,
                'supports_tools': provider.get('supports_tools', False)
            }
        
        return status

# Instância global
ai_manager = AIManager()
