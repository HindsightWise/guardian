from abc import ABC, abstractmethod

class BaseSocialProvider(ABC):
    """Abstract base class for all Aion social communication providers."""
    
    @abstractmethod
    def ignite(self) -> None:
        """Initializes and starts the provider's connection sequence."""
        pass

    @abstractmethod
    def broadcast(self, message: str) -> None:
        """Sends a broadcast message through the provider's channel.
        
        Args:
            message: The text content to be broadcasted.
        """
        pass
