"""Orchestrator agent for coordinating parallel prompt optimization."""

import asyncio
from typing import Optional

from agents.optimizer import OptimizerAgent
from models.schemas import OptimizeOptions, OptimizeResponse, OptimizedPrompt
from config import SUPPORTED_PROVIDERS


class OrchestratorAgent:
    """
    Main coordinator that manages parallel prompt optimization
    across multiple AI providers.
    
    The orchestrator:
    1. Validates the request
    2. Spawns parallel optimizer tasks for each provider
    3. Aggregates results into a single response
    """
    
    def __init__(self):
        self.optimizer = OptimizerAgent()
    
    async def optimize(
        self,
        prompt: str,
        providers: list[str],
        options: Optional[OptimizeOptions] = None,
    ) -> OptimizeResponse:
        """
        Optimize a prompt for multiple providers in parallel.
        
        Args:
            prompt: The original prompt to optimize
            providers: List of provider names to optimize for
            options: Optimization options
            
        Returns:
            OptimizeResponse with results for all providers
        """
        if options is None:
            options = OptimizeOptions()
        
        # Validate providers
        valid_providers = [p for p in providers if p in SUPPORTED_PROVIDERS]
        
        # Create optimization tasks for parallel execution
        tasks = [
            self._optimize_for_provider(prompt, provider, options)
            for provider in valid_providers
        ]
        
        # Run all optimizations in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Build response map
        optimized = {}
        for provider, result in zip(valid_providers, results):
            if isinstance(result, Exception):
                # Handle any unexpected exceptions
                optimized[provider] = OptimizedPrompt(
                    provider=provider,
                    prompt=prompt,
                    changes=[],
                    success=False,
                    error=str(result),
                )
            else:
                optimized[provider] = result
        
        return OptimizeResponse(
            original=prompt,
            optimized=optimized,
        )
    
    async def _optimize_for_provider(
        self,
        prompt: str,
        provider: str,
        options: OptimizeOptions,
    ) -> OptimizedPrompt:
        """
        Run optimization for a single provider.
        
        This is called in parallel for each provider.
        """
        return await self.optimizer.optimize(
            prompt=prompt,
            provider=provider,
            preserve_structure=options.preserve_structure,
        )


