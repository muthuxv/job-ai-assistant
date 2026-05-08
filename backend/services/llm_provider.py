# backend/services/llm_provider.py
from abc import ABC, abstractmethod
from typing import Optional
import json
import os

class BaseLLMProvider(ABC):
    """Interface commune pour tous les LLM providers"""
    
    @abstractmethod
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Génère du texte à partir d'un prompt"""
        pass
    
    def generate_json(self, prompt: str, temperature: float = 0.2) -> dict:
        """Génère et parse du JSON"""
        response = self.generate(prompt, temperature=temperature, max_tokens=3000)
        
        # Nettoie le JSON
        content = response.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        return json.loads(content.strip())


class GeminiProvider(BaseLLMProvider):
    
    def __init__(self, api_key: str):
        from google import generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3.1-flash-lite')
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        response = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens
            }
        )
        return response.text


class ClaudeProvider(BaseLLMProvider):
    
    def __init__(self, api_key: str):
        from anthropic import Anthropic
        self.client = Anthropic(api_key=api_key)
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text


class OpenAIProvider(BaseLLMProvider):
    
    def __init__(self, api_key: str):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content


def get_provider(provider_name: str, api_key: str) -> BaseLLMProvider:
    """
    Factory : retourne le bon provider selon le nom
    """
    providers = {
        "gemini": GeminiProvider,
        "claude": ClaudeProvider,
        "openai": OpenAIProvider,
    }
    
    if provider_name not in providers:
        raise ValueError(f"Provider inconnu : {provider_name}. Choisir parmi : {list(providers.keys())}")
    
    return providers[provider_name](api_key)