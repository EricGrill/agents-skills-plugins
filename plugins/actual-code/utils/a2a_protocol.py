"""A2A Protocol Implementation for Agent Communication

This module implements Google's Agent-to-Agent (A2A) protocol for
enabling interoperability and communication between AI agents.
"""

import uuid
import time
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class A2AMessage:
    """A2A Protocol Message Structure
    
    Implements the standard A2A message format for agent communication.
    """
    
    protocol_version: str = "1.0"
    message_id: str = field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}")
    sender_id: str = ""
    sender_type: str = ""
    recipient_id: str = ""
    message_type: str = "request"  # request, response, broadcast, notification
    timestamp: float = field(default_factory=time.time)
    payload: Dict[str, Any] = field(default_factory=dict)
    conversation_id: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "protocol_version": self.protocol_version,
            "message_id": self.message_id,
            "sender": {
                "agent_id": self.sender_id,
                "agent_type": self.sender_type
            },
            "recipient": {
                "agent_id": self.recipient_id
            },
            "message_type": self.message_type,
            "timestamp": self.timestamp,
            "payload": {
                "data": self.payload.get("data", {}),
                "metadata": {
                    "conversation_id": self.conversation_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'A2AMessage':
        """Create A2AMessage from dictionary"""
        return cls(
            protocol_version=data.get("protocol_version", "1.0"),
            message_id=data.get("message_id", f"msg_{uuid.uuid4().hex[:12]}"),
            sender_id=data.get("sender", {}).get("agent_id", ""),
            sender_type=data.get("sender", {}).get("agent_type", ""),
            recipient_id=data.get("recipient", {}).get("agent_id", ""),
            message_type=data.get("message_type", "request"),
            timestamp=data.get("timestamp", time.time()),
            payload=data.get("payload", {}),
            conversation_id=data.get("payload", {}).get("metadata", {}).get("conversation_id", "")
        )


class A2AProtocol:
    """A2A Protocol Handler
    
    Manages agent-to-agent communication, message routing, and history tracking.
    """
    
    def __init__(self):
        self.message_history: List[A2AMessage] = []
        self.conversation_index: Dict[str, List[A2AMessage]] = {}
    
    async def send_message(
        self,
        sender_id: str,
        sender_type: str,
        recipient_id: str,
        data: Dict[str, Any],
        conversation_id: str,
        message_type: str = "request"
    ) -> A2AMessage:
        """Send an A2A message
        
        Args:
            sender_id: ID of the sending agent
            sender_type: Type of the sending agent (e.g., 'analyzer', 'creator')
            recipient_id: ID of the receiving agent
            data: Message payload data
            conversation_id: ID of the conversation
            message_type: Type of message ('request', 'response', 'broadcast', 'notification')
            
        Returns:
            A2AMessage: The created and logged message
        """
        
        message = A2AMessage(
            sender_id=sender_id,
            sender_type=sender_type,
            recipient_id=recipient_id,
            message_type=message_type,
            payload={"data": data},
            conversation_id=conversation_id
        )
        
        # Log message
        self._log_message(message)
        
        return message
    
    async def broadcast_message(
        self,
        sender_id: str,
        sender_type: str,
        data: Dict[str, Any],
        conversation_id: str
    ) -> A2AMessage:
        """Broadcast message to all agents
        
        Args:
            sender_id: ID of the sending agent
            sender_type: Type of the sending agent
            data: Message payload data
            conversation_id: ID of the conversation
            
        Returns:
            A2AMessage: The created and logged broadcast message
        """
        
        return await self.send_message(
            sender_id=sender_id,
            sender_type=sender_type,
            recipient_id="all_agents",
            data=data,
            conversation_id=conversation_id,
            message_type="broadcast"
        )
    
    async def send_response(
        self,
        sender_id: str,
        sender_type: str,
        recipient_id: str,
        data: Dict[str, Any],
        conversation_id: str,
        original_message_id: str
    ) -> A2AMessage:
        """Send a response to a previous message
        
        Args:
            sender_id: ID of the sending agent
            sender_type: Type of the sending agent
            recipient_id: ID of the receiving agent
            data: Response payload data
            conversation_id: ID of the conversation
            original_message_id: ID of the message being responded to
            
        Returns:
            A2AMessage: The created and logged response message
        """
        
        # Add original message reference to payload
        response_data = {
            **data,
            "in_response_to": original_message_id
        }
        
        return await self.send_message(
            sender_id=sender_id,
            sender_type=sender_type,
            recipient_id=recipient_id,
            data=response_data,
            conversation_id=conversation_id,
            message_type="response"
        )
    
    def _log_message(self, message: A2AMessage) -> None:
        """Log a message to history and index it by conversation"""
        
        self.message_history.append(message)
        
        # Index by conversation ID
        if message.conversation_id not in self.conversation_index:
            self.conversation_index[message.conversation_id] = []
        self.conversation_index[message.conversation_id].append(message)
    
    def get_message_history(
        self, 
        conversation_id: Optional[str] = None,
        sender_id: Optional[str] = None,
        recipient_id: Optional[str] = None
    ) -> List[A2AMessage]:
        """Get message history with optional filtering
        
        Args:
            conversation_id: Filter by conversation ID
            sender_id: Filter by sender ID
            recipient_id: Filter by recipient ID
            
        Returns:
            List[A2AMessage]: Filtered list of messages
        """
        
        # Start with conversation filter if provided (most efficient)
        if conversation_id:
            messages = self.conversation_index.get(conversation_id, [])
        else:
            messages = self.message_history
        
        # Apply additional filters
        if sender_id:
            messages = [msg for msg in messages if msg.sender_id == sender_id]
        
        if recipient_id:
            messages = [msg for msg in messages if msg.recipient_id == recipient_id]
        
        return messages
    
    def get_conversation_stats(self, conversation_id: str) -> Dict[str, Any]:
        """Get statistics for a conversation
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Dict containing conversation statistics
        """
        
        messages = self.get_message_history(conversation_id=conversation_id)
        
        if not messages:
            return {
                "total_messages": 0,
                "message_types": {},
                "agents_involved": [],
                "duration": 0
            }
        
        # Calculate statistics
        message_types = {}
        agents = set()
        
        for msg in messages:
            # Count message types
            message_types[msg.message_type] = message_types.get(msg.message_type, 0) + 1
            
            # Track agents
            agents.add(msg.sender_id)
            if msg.recipient_id != "all_agents":
                agents.add(msg.recipient_id)
        
        # Calculate duration
        start_time = min(msg.timestamp for msg in messages)
        end_time = max(msg.timestamp for msg in messages)
        duration = end_time - start_time
        
        return {
            "total_messages": len(messages),
            "message_types": message_types,
            "agents_involved": list(agents),
            "duration_seconds": duration,
            "start_time": datetime.fromtimestamp(start_time).isoformat(),
            "end_time": datetime.fromtimestamp(end_time).isoformat()
        }
    
    def clear_history(self, conversation_id: Optional[str] = None) -> None:
        """Clear message history
        
        Args:
            conversation_id: If provided, only clear history for this conversation
        """
        
        if conversation_id:
            # Clear specific conversation
            if conversation_id in self.conversation_index:
                # Remove from main history
                self.message_history = [
                    msg for msg in self.message_history 
                    if msg.conversation_id != conversation_id
                ]
                # Remove from index
                del self.conversation_index[conversation_id]
        else:
            # Clear all history
            self.message_history = []
            self.conversation_index = {}


# Global A2A protocol instance for the application
a2a_protocol = A2AProtocol()


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_a2a_protocol():
        """Test the A2A protocol implementation"""
        
        protocol = A2AProtocol()
        conversation_id = "conv_test_001"
        
        print("🧪 Testing A2A Protocol")
        print("=" * 60)
        
        # Test 1: Send a message
        print("\n1. Sending message from scanner to orchestrator...")
        msg1 = await protocol.send_message(
            sender_id="github_scanner",
            sender_type="scanner",
            recipient_id="orchestrator",
            data={"repository": "vercel/next.js", "status": "scanned"},
            conversation_id=conversation_id
        )
        print(f"✅ Message sent: {msg1.message_id}")
        
        # Test 2: Broadcast message
        print("\n2. Broadcasting analysis results to all agents...")
        msg2 = await protocol.broadcast_message(
            sender_id="orchestrator",
            sender_type="coordinator",
            data={"iteration": 1, "results": "analysis_data"},
            conversation_id=conversation_id
        )
        print(f"✅ Broadcast sent: {msg2.message_id}")
        
        # Test 3: Send response
        print("\n3. Sending response from code analyzer...")
        msg3 = await protocol.send_response(
            sender_id="code_analyzer",
            sender_type="analyzer",
            recipient_id="orchestrator",
            data={"architecture": "MVC", "complexity": "medium"},
            conversation_id=conversation_id,
            original_message_id=msg2.message_id
        )
        print(f"✅ Response sent: {msg3.message_id}")
        
        # Test 4: Get message history
        print("\n4. Retrieving message history...")
        history = protocol.get_message_history(conversation_id=conversation_id)
        print(f"✅ Found {len(history)} messages in conversation")
        
        # Test 5: Get conversation stats
        print("\n5. Getting conversation statistics...")
        stats = protocol.get_conversation_stats(conversation_id)
        print(f"✅ Conversation Stats:")
        print(f"   - Total messages: {stats['total_messages']}")
        print(f"   - Message types: {stats['message_types']}")
        print(f"   - Agents involved: {stats['agents_involved']}")
        print(f"   - Duration: {stats['duration_seconds']:.2f}s")
        
        # Test 6: Message serialization
        print("\n6. Testing message serialization...")
        msg_dict = msg1.to_dict()
        print(f"✅ Message serialized to dict: {list(msg_dict.keys())}")
        
        print("\n" + "=" * 60)
        print("✅ All A2A Protocol tests passed!")
        
    # Run tests
    asyncio.run(test_a2a_protocol())
