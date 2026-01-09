"""Base Agent Class for Multi-Agent System

This module provides a base agent class using Google Gemini via Vertex AI.
All specialized agents (Scanner, Analyzer, Creator, etc.) will inherit from this.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

from utils.monitoring import AgentLogger, PerformanceMonitor
from utils.a2a_protocol import a2a_protocol

# Load environment variables
load_dotenv()


class BaseGeminiAgent:
    """Base class for Gemini-powered agents
    
    Provides common functionality for all agents:
    - Vertex AI client initialization
    - Logging and monitoring
    - A2A protocol integration
    - Standard run interface
    """
    
    def __init__(
        self,
        name: str,
        model: str = "gemini-2.5-flash",
        system_instruction: str = None,
        temperature: float = 0.7,
        max_output_tokens: int = 2048
    ):
        """Initialize a Gemini agent
        
        Args:
            name: Agent name (e.g., 'github_scanner', 'code_analyzer')
            model: Gemini model to use (default: gemini-2.5-flash)
            system_instruction: System prompt for the agent
            temperature: Model temperature (0.0-1.0)
            max_output_tokens: Maximum tokens to generate
        """
        self.name = name
        self.model = model
        self.system_instruction = system_instruction
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        
        # Initialize logging and monitoring
        self.logger = AgentLogger(name)
        self.performance = PerformanceMonitor()
        
        # Initialize Vertex AI client
        self.client = self._initialize_client()
        
        self.logger.info(
            f"Agent initialized",
            model=model,
            temperature=temperature
        )
    
    def _initialize_client(self) -> genai.Client:
        """Initialize Vertex AI client"""
        
        try:
            client = genai.Client(
                vertexai=True,
                project=os.getenv("GOOGLE_CLOUD_PROJECT"),
                location=os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
            )
            
            self.logger.info(
                "Vertex AI client initialized",
                project=os.getenv("GOOGLE_CLOUD_PROJECT"),
                region=os.getenv("GOOGLE_CLOUD_REGION")
            )
            
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Vertex AI client: {str(e)}")
            raise
    
    async def run(
        self,
        prompt: str,
        conversation_id: str = None,
        **kwargs
    ) -> str:
        """Run the agent with a prompt
        
        Args:
            prompt: Input prompt for the agent
            conversation_id: Optional conversation ID for A2A tracking
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            str: Agent's response
        """
        
        self.logger.info(
            f"Running agent",
            prompt_length=len(prompt),
            conversation_id=conversation_id
        )
        
        self.performance.start_timer(f"{self.name}_execution")
        
        try:
            # Prepare config
            config = types.GenerateContentConfig(
                temperature=kwargs.get('temperature', self.temperature),
                max_output_tokens=kwargs.get('max_output_tokens', self.max_output_tokens)
            )
            
            # Add system instruction if provided
            if self.system_instruction:
                config.system_instruction = self.system_instruction
            
            # Generate content
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )
            
            duration = self.performance.end_timer(f"{self.name}_execution")
            
            self.logger.info(
                "Agent completed successfully",
                duration=f"{duration:.2f}s",
                response_length=len(response.text)
            )
            
            # Send A2A notification if conversation_id provided
            if conversation_id:
                await a2a_protocol.send_message(
                    sender_id=self.name,
                    sender_type="agent",
                    recipient_id="orchestrator",
                    data={
                        "status": "completed",
                        "duration": duration,
                        "response_length": len(response.text)
                    },
                    conversation_id=conversation_id,
                    message_type="notification"
                )
            
            return response.text
            
        except Exception as e:
            duration = self.performance.end_timer(f"{self.name}_execution")
            self.logger.error(
                f"Agent execution failed: {str(e)}",
                duration=f"{duration:.2f}s" if duration else "N/A"
            )
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent performance statistics"""
        return {
            "name": self.name,
            "model": self.model,
            "performance": self.performance.get_summary(),
            "logs": len(self.logger.get_logs())
        }


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_base_agent():
        """Test the base agent class"""
        
        print("🧪 Testing Base Gemini Agent")
        print("=" * 60)
        
        # Create a test agent
        agent = BaseGeminiAgent(
            name="test_agent",
            model="gemini-2.5-flash",
            system_instruction="You are a helpful coding assistant. Be concise and clear.",
            temperature=0.3
        )
        
        # Test 1: Simple prompt
        print("\n1. Testing simple prompt...")
        response = await agent.run(
            prompt="What is a multi-agent system? Answer in one sentence.",
            conversation_id="test_conv_001"
        )
        print(f"✅ Response: {response}")
        
        # Test 2: Code-related prompt
        print("\n2. Testing code-related prompt...")
        response = await agent.run(
            prompt="Explain what the A2A protocol is for AI agents in 2 sentences.",
            conversation_id="test_conv_001"
        )
        print(f"✅ Response: {response}")
        
        # Test 3: Get statistics
        print("\n3. Getting agent statistics...")
        stats = agent.get_stats()
        print(f"✅ Stats:")
        print(f"   - Agent: {stats['name']}")
        print(f"   - Model: {stats['model']}")
        print(f"   - Operations: {stats['performance']['total_operations']}")
        print(f"   - Total time: {stats['performance']['total_time']:.2f}s")
        print(f"   - Logs: {stats['logs']}")
        
        print("\n" + "=" * 60)
        print("✅ Base Agent test complete!")
        print("🎉 Ready to build specialized agents!")
    
    # Run test
    asyncio.run(test_base_agent())
