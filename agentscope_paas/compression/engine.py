"""
Context Compression Engine for AgentScope-PaaS

This module provides intelligent context compression strategies including
semantic compression, token-based compression, and hybrid approaches.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
import math


class CompressionStrategy(Enum):
    """Compression strategy types"""
    SEMANTIC = "semantic"
    TOKEN_BASED = "token_based"
    HYBRID = "hybrid"


class CompressionQuality(Enum):
    """Compression quality levels"""
    HIGH = "high"      # Less compression, higher quality
    MEDIUM = "medium"  # Balanced compression and quality
    LOW = "low"        # Maximum compression, lower quality


class ContextCompressionError(Exception):
    """Context compression related errors"""
    pass


class ContextCompressionEngine:
    """Intelligent context compression engine"""

    def __init__(self):
        """Initialize compression engine"""
        self.logger = self._get_logger()
        self.compression_stats: Dict[str, Any] = {}
        self.compression_history: List[Dict[str, Any]] = []

    def _get_logger(self):
        """Get logger instance"""
        try:
            from agentscope_paas.utils.logger import get_logger
            return get_logger(__name__)
        except ImportError:
            logging.basicConfig(level=logging.INFO)
            return logging.getLogger(__name__)

    # Synchronous wrapper methods for FastAPI compatibility
    def analyze_context_sync(self, context: List[Dict[str, Any]], compression_config: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous wrapper for analyze_context (now direct call since method is sync)"""
        return self.analyze_context(context, compression_config)

    def compress_context_sync(self, context: List[Dict[str, Any]], compression_config: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous wrapper for compress_context (now direct call since method is sync)"""
        return self.compress_context(context, compression_config)

    def analyze_context(self, context: List[Dict[str, Any]], compression_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze context and provide compression recommendations

        Args:
            context: Conversation context to analyze
            compression_config: Compression configuration

        Returns:
            Analysis results with recommendations
        """
        if not context:
            return {
                "total_messages": 0,
                "estimated_tokens": 0,
                "compression_needed": False,
                "recommendations": []
            }

        try:
            # Calculate current context metrics
            total_messages = len(context)
            estimated_tokens = self._estimate_tokens(context)
            message_ages = self._calculate_message_ages(context)
            importance_scores = self._calculate_importance_scores(context, compression_config)

            # Get trigger conditions
            trigger_conditions = compression_config.get("trigger_conditions", {})
            max_context_length = trigger_conditions.get("max_context_length", 4000)
            token_threshold = trigger_conditions.get("token_threshold", 3000)

            # Determine if compression is needed
            compression_needed = (
                total_messages > max_context_length or
                estimated_tokens > token_threshold
            )

            # Generate recommendations
            recommendations = []
            if compression_needed:
                active_strategy = compression_config.get("active_strategy", "hybrid")
                recommendations.append({
                    "type": "compress",
                    "strategy": active_strategy,
                    "reason": f"Context exceeds threshold: {estimated_tokens} > {token_threshold} tokens",
                    "potential_savings": self._estimate_compression_savings(context, active_strategy)
                })

                # Check for old messages
                old_messages = [msg for msg, age in zip(context, message_ages) if age > 24]  # 24 hours
                if old_messages:
                    recommendations.append({
                        "type": "remove_old",
                        "count": len(old_messages),
                        "reason": f"Found {len(old_messages)} messages older than 24 hours",
                        "potential_savings": sum(self._estimate_message_tokens(msg) for msg in old_messages)
                    })

            return {
                "total_messages": total_messages,
                "estimated_tokens": estimated_tokens,
                "compression_needed": compression_needed,
                "message_ages": message_ages,
                "importance_scores": importance_scores,
                "recommendations": recommendations,
                "analysis_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Context analysis failed: {str(e)}")
            raise ContextCompressionError(f"Analysis failed: {str(e)}")

    def compress_context(self, context: List[Dict[str, Any]], compression_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compress context using configured strategy

        Args:
            context: Conversation context to compress
            compression_config: Compression configuration

        Returns:
            Compression result with compressed context and statistics
        """
        if not context:
            return {
                "original_context": [],
                "compressed_context": [],
                "compression_stats": {
                    "original_messages": 0,
                    "compressed_messages": 0,
                    "original_tokens": 0,
                    "compressed_tokens": 0,
                    "compression_ratio": 0.0,
                    "information_loss": 0.0
                }
            }

        try:
            start_time = datetime.now()
            active_strategy = compression_config.get("active_strategy", "hybrid")
            quality_controls = compression_config.get("quality_controls", {})

            # Analyze context first
            analysis = self.analyze_context(context, compression_config)

            # Apply compression strategy
            if active_strategy == "semantic":
                compressed_context, stats = self._semantic_compression(context, compression_config)
            elif active_strategy == "token_based":
                compressed_context, stats = self._token_based_compression(context, compression_config)
            elif active_strategy == "hybrid":
                compressed_context, stats = self._hybrid_compression(context, compression_config)
            else:
                raise ContextCompressionError(f"Unknown compression strategy: {active_strategy}")

            # Validate quality controls
            validation_result = self._validate_compression_quality(
                context, compressed_context, quality_controls
            )

            compression_time = (datetime.now() - start_time).total_seconds()

            # Store compression stats
            compression_record = {
                "timestamp": datetime.now().isoformat(),
                "strategy": active_strategy,
                "original_messages": len(context),
                "compressed_messages": len(compressed_context),
                "compression_ratio": stats.get("compression_ratio", 0.0),
                "information_loss": validation_result.get("information_loss", 0.0),
                "coherence_score": validation_result.get("coherence_score", 0.0),
                "compression_time": compression_time
            }
            self.compression_history.append(compression_record)

            return {
                "original_context": context,
                "compressed_context": compressed_context,
                "compression_stats": {
                    **stats,
                    "compression_time": compression_time,
                    "validation": validation_result
                },
                "strategy_used": active_strategy
            }

        except Exception as e:
            self.logger.error(f"Context compression failed: {str(e)}")
            raise ContextCompressionError(f"Compression failed: {str(e)}")

    def _semantic_compression(self, context: List[Dict[str, Any]], config: Dict[str, Any]) -> tuple:
        """Apply semantic compression strategy"""
        strategies = config.get("strategies", {}).get("semantic", {})
        similarity_threshold = strategies.get("similarity_threshold", 0.75)
        preserve_entities = strategies.get("preserve_entities", True)
        preserve_keywords = strategies.get("preserve_keywords", [])

        compressed_context = []
        removed_count = 0
        tokens_saved = 0

        # Group similar messages and keep representatives
        message_groups = self._group_similar_messages(context, similarity_threshold)

        for group in message_groups:
            if len(group) > 1:
                # Keep the most recent message from similar group
                representative = max(group, key=lambda msg: self._get_message_timestamp(msg))
                compressed_context.append(representative)
                removed_count += len(group) - 1
                tokens_saved += sum(self._estimate_message_tokens(msg) for msg in group[:-1])
            else:
                compressed_context.extend(group)

        # Apply keyword preservation
        if preserve_keywords:
            compressed_context = self._preserve_keyword_messages(
                compressed_context, preserve_keywords
            )

        # Calculate statistics
        original_tokens = sum(self._estimate_message_tokens(msg) for msg in context)
        compressed_tokens = sum(self._estimate_message_tokens(msg) for msg in compressed_context)

        return compressed_context, {
            "original_messages": len(context),
            "compressed_messages": len(compressed_context),
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "compression_ratio": compressed_tokens / original_tokens if original_tokens > 0 else 1.0,
            "messages_removed": removed_count,
            "tokens_saved": tokens_saved
        }

    def _token_based_compression(self, context: List[Dict[str, Any]], config: Dict[str, Any]) -> tuple:
        """Apply token-based compression strategy"""
        strategies = config.get("strategies", {}).get("token_based", {})
        max_tokens = strategies.get("max_tokens", 2000)
        preserve_structure = strategies.get("preserve_structure", True)
        priority_sections = strategies.get("priority_sections", [])

        compressed_context = []
        current_tokens = 0
        priority_config = config.get("priority_config", {})

        # Sort messages by importance if priority rules exist
        if priority_config.get("enabled"):
            context = self._sort_by_priority(context, priority_config.get("priority_rules", []))

        # Add messages until token limit reached
        for message in context:
            message_tokens = self._estimate_message_tokens(message)

            if current_tokens + message_tokens <= max_tokens:
                compressed_context.append(message)
                current_tokens += message_tokens
            elif preserve_structure and self._is_structural_message(message):
                # Always preserve structural messages
                compressed_context.append(message)
                current_tokens += message_tokens
            else:
                break  # Token limit reached

        # Calculate statistics
        original_tokens = sum(self._estimate_message_tokens(msg) for msg in context)
        compressed_tokens = sum(self._estimate_message_tokens(msg) for msg in compressed_context)

        return compressed_context, {
            "original_messages": len(context),
            "compressed_messages": len(compressed_context),
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "compression_ratio": compressed_tokens / original_tokens if original_tokens > 0 else 1.0,
            "messages_removed": len(context) - len(compressed_context),
            "tokens_saved": original_tokens - compressed_tokens
        }

    def _hybrid_compression(self, context: List[Dict[str, Any]], config: Dict[str, Any]) -> tuple:
        """Apply hybrid compression strategy"""
        strategies = config.get("strategies", {}).get("hybrid", {})
        semantic_weight = strategies.get("semantic_weight", 0.6)
        token_weight = strategies.get("token_weight", 0.4)
        min_context_length = strategies.get("min_context_length", 1000)
        adaptive_threshold = strategies.get("adaptive_threshold", 0.8)

        # First apply semantic compression
        semantic_compressed, semantic_stats = self._semantic_compression(context, config)

        # Then apply token-based compression if needed
        current_tokens = semantic_stats["compressed_tokens"]

        if current_tokens > min_context_length:
            # Calculate token limit based on weights
            target_tokens = int(min_context_length * adaptive_threshold)
            token_config = config.copy()
            token_config["strategies"]["token_based"]["max_tokens"] = target_tokens

            hybrid_compressed, token_stats = self._token_based_compression(
                semantic_compressed, token_config
            )

            # Calculate hybrid statistics
            original_tokens = sum(self._estimate_message_tokens(msg) for msg in context)
            compressed_tokens = sum(self._estimate_message_tokens(msg) for msg in hybrid_compressed)

            return hybrid_compressed, {
                "original_messages": len(context),
                "compressed_messages": len(hybrid_compressed),
                "original_tokens": original_tokens,
                "compressed_tokens": compressed_tokens,
                "compression_ratio": compressed_tokens / original_tokens if original_tokens > 0 else 1.0,
                "messages_removed": len(context) - len(hybrid_compressed),
                "tokens_saved": original_tokens - compressed_tokens,
                "semantic_pass_stats": semantic_stats,
                "token_pass_stats": token_stats
            }
        else:
            return semantic_compressed, semantic_stats

    def _group_similar_messages(self, context: List[Dict[str, Any]], threshold: float) -> List[List[Dict[str, Any]]]:
        """Group similar messages using semantic similarity"""
        # Simplified similarity grouping based on message content
        groups = []
        used_indices = set()

        for i, message in enumerate(context):
            if i in used_indices:
                continue

            current_group = [message]
            used_indices.add(i)

            # Compare with other messages
            for j, other_message in enumerate(context[i+1:], i+1):
                if j in used_indices:
                    continue

                similarity = self._calculate_message_similarity(message, other_message)
                if similarity >= threshold:
                    current_group.append(other_message)
                    used_indices.add(j)

            groups.append(current_group)

        return groups

    def _calculate_message_similarity(self, msg1: Dict[str, Any], msg2: Dict[str, Any]) -> float:
        """Calculate semantic similarity between two messages"""
        # Simple similarity based on content overlap
        content1 = msg1.get("content", "").lower()
        content2 = msg2.get("content", "").lower()

        if not content1 or not content2:
            return 0.0

        # Calculate word overlap
        words1 = set(content1.split())
        words2 = set(content2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    def _preserve_keyword_messages(self, context: List[Dict[str, Any]], keywords: List[str]) -> List[Dict[str, Any]]:
        """Ensure messages containing keywords are preserved"""
        preserved_messages = []
        keyword_messages = []

        for message in context:
            content = message.get("content", "").lower()
            if any(keyword.lower() in content for keyword in keywords):
                keyword_messages.append(message)
            else:
                preserved_messages.append(message)

        # Put keyword messages at the beginning
        return keyword_messages + preserved_messages

    def _sort_by_priority(self, context: List[Dict[str, Any]], priority_rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort messages by priority rules"""
        def calculate_priority(message):
            score = 0
            for rule in priority_rules:
                if self._matches_priority_rule(message, rule):
                    score += rule.get("priority", 0)
            return score

        return sorted(context, key=calculate_priority, reverse=True)

    def _matches_priority_rule(self, message: Dict[str, Any], rule: Dict[str, Any]) -> bool:
        """Check if message matches priority rule"""
        conditions = rule.get("conditions", {})

        # Check content type
        if "content_type" in conditions:
            message_type = message.get("role", "")
            if message_type not in conditions["content_type"]:
                return False

        # Check keywords
        if "contains_keywords" in conditions:
            content = message.get("content", "").lower()
            if not any(keyword.lower() in content for keyword in conditions["contains_keywords"]):
                return False

        # Check user tagged
        if conditions.get("user_tagged", False):
            if not message.get("metadata", {}).get("user_tagged", False):
                return False

        return True

    def _is_structural_message(self, message: Dict[str, Any]) -> bool:
        """Check if message is structural (should be preserved)"""
        role = message.get("role", "")
        return role in ["system", "user"]

    def _estimate_tokens(self, context: List[Dict[str, Any]]) -> int:
        """Estimate total tokens in context"""
        return sum(self._estimate_message_tokens(message) for message in context)

    def _estimate_message_tokens(self, message: Dict[str, Any]) -> int:
        """Estimate tokens in a single message"""
        content = message.get("content", "")
        # Rough estimate: 1 token ≈ 4 characters
        return len(content) // 4

    def _calculate_message_ages(self, context: List[Dict[str, Any]]) -> List[float]:
        """Calculate ages of messages in hours"""
        now = datetime.now()
        ages = []

        for message in context:
            timestamp_str = message.get("timestamp", message.get("created_at", ""))
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    age_hours = (now - timestamp).total_seconds() / 3600
                    ages.append(age_hours)
                except:
                    ages.append(0.0)  # Invalid timestamp
            else:
                ages.append(0.0)  # No timestamp

        return ages

    def _calculate_importance_scores(self, context: List[Dict[str, Any]], config: Dict[str, Any]) -> List[float]:
        """Calculate importance scores for messages"""
        scores = []
        priority_config = config.get("priority_config", {})

        for message in context:
            score = 0.5  # Base score

            # Increase score for user messages
            if message.get("role") == "user":
                score += 0.2

            # Increase score for recent messages
            timestamp_str = message.get("timestamp", message.get("created_at", ""))
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    age_hours = (datetime.now() - timestamp).total_seconds() / 3600
                    score += max(0, 0.3 - (age_hours / 24))  # Decay over time
                except:
                    pass

            # Apply priority rules if configured
            if priority_config.get("enabled"):
                for rule in priority_config.get("priority_rules", []):
                    if self._matches_priority_rule(message, rule):
                        if rule.get("action") == "preserve":
                            score += 0.3

            scores.append(min(1.0, score))  # Cap at 1.0

        return scores

    def _get_message_timestamp(self, message: Dict[str, Any]) -> datetime:
        """Get message timestamp for comparison"""
        timestamp_str = message.get("timestamp", message.get("created_at", ""))
        if timestamp_str:
            try:
                return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except:
                pass
        return datetime.min

    def _estimate_compression_savings(self, context: List[Dict[str, Any]], strategy: str) -> int:
        """Estimate potential token savings from compression"""
        current_tokens = self._estimate_tokens(context)

        if strategy == "semantic":
            # Assume 30-50% reduction
            return int(current_tokens * 0.4)
        elif strategy == "token_based":
            # Assume 40-60% reduction
            return int(current_tokens * 0.5)
        elif strategy == "hybrid":
            # Assume 35-55% reduction
            return int(current_tokens * 0.45)
        else:
            return int(current_tokens * 0.3)

    def _validate_compression_quality(self, original: List[Dict[str, Any]], compressed: List[Dict[str, Any]], quality_controls: Dict[str, Any]) -> Dict[str, Any]:
        """Validate quality of compressed context"""
        min_coherence = quality_controls.get("min_coherence_score", 0.8)
        max_loss = quality_controls.get("max_information_loss", 0.2)
        enable_validation = quality_controls.get("enable_validation", True)

        if not enable_validation:
            return {
                "coherence_score": 1.0,
                "information_loss": 0.0,
                "validation_passed": True
            }

        # Calculate coherence score
        coherence_score = self._calculate_coherence_score(original, compressed)

        # Calculate information loss
        information_loss = self._calculate_information_loss(original, compressed)

        validation_passed = (
            coherence_score >= min_coherence and
            information_loss <= max_loss
        )

        return {
            "coherence_score": coherence_score,
            "information_loss": information_loss,
            "validation_passed": validation_passed,
            "thresholds": {
                "min_coherence": min_coherence,
                "max_information_loss": max_loss
            }
        }

    def _calculate_coherence_score(self, original: List[Dict[str, Any]], compressed: List[Dict[str, Any]]) -> float:
        """Calculate coherence score of compressed context"""
        if not compressed:
            return 0.0

        # Check if conversation flow is maintained
        role_transitions = 0
        expected_transitions = 0

        for i in range(len(compressed) - 1):
            current_role = compressed[i].get("role", "")
            next_role = compressed[i + 1].get("role", "")

            if current_role != next_role:
                role_transitions += 1
            expected_transitions += 1

        # Calculate flow preservation
        if expected_transitions > 0:
            flow_preservation = role_transitions / expected_transitions
        else:
            flow_preservation = 1.0

        # Check if key information is preserved
        original_content = " ".join(msg.get("content", "") for msg in original)
        compressed_content = " ".join(msg.get("content", "") for msg in compressed)

        if len(original_content) > 0:
            content_preservation = len(compressed_content) / len(original_content)
        else:
            content_preservation = 1.0

        # Combined coherence score
        return (flow_preservation * 0.6 + content_preservation * 0.4)

    def _calculate_information_loss(self, original: List[Dict[str, Any]], compressed: List[Dict[str, Any]]) -> float:
        """Calculate information loss from compression"""
        if not original:
            return 0.0

        # Calculate based on message count reduction
        message_loss = 1.0 - (len(compressed) / len(original))

        # Calculate based on content reduction
        original_tokens = self._estimate_tokens(original)
        compressed_tokens = self._estimate_tokens(compressed)

        if original_tokens > 0:
            token_loss = 1.0 - (compressed_tokens / original_tokens)
        else:
            token_loss = 0.0

        # Combined information loss
        return (message_loss * 0.4 + token_loss * 0.6)

    def get_compression_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent compression history"""
        return self.compression_history[-limit:]

    def get_compression_stats(self) -> Dict[str, Any]:
        """Get overall compression statistics"""
        if not self.compression_history:
            return {
                "total_compressions": 0,
                "average_compression_ratio": 0.0,
                "average_quality_score": 0.0
            }

        total_compressions = len(self.compression_history)
        avg_compression_ratio = sum(
            record.get("compression_ratio", 0.0) for record in self.compression_history
        ) / total_compressions

        avg_coherence = sum(
            record.get("coherence_score", 0.0) for record in self.compression_history
        ) / total_compressions

        return {
            "total_compressions": total_compressions,
            "average_compression_ratio": avg_compression_ratio,
            "average_quality_score": avg_coherence,
            "most_used_strategy": self._get_most_used_strategy()
        }

    def _get_most_used_strategy(self) -> str:
        """Get most commonly used compression strategy"""
        strategy_counts = {}
        for record in self.compression_history:
            strategy = record.get("strategy", "unknown")
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

        return max(strategy_counts, key=strategy_counts.get) if strategy_counts else "none"


# Singleton instance for convenient usage
compression_engine = ContextCompressionEngine()