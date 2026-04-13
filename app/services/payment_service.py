import os

class FlowSubscriptionService:
    def __init__(self):
        self.api_key = os.getenv("FLOW_API_KEY", "")
        self.secret_key = os.getenv("FLOW_SECRET_KEY", "")

    def create_subscription_link(self, email):
        """
        Placeholder para integración con Flow.cl
        """
        # Próximamente integración real con Flow
        return None

subscription_service = FlowSubscriptionService()
