
#  Importing required libraries

import os
import re
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser

# Defining the ElectronicsNegotiationBot class
class ElectronicsNegotiationBot:
    def __init__(self):
        
        load_dotenv()
       
        # Comprehensive product detection patterns
        self.product_patterns = [
            # Computing Devices
            r'\b(laptop|notebook|desktop|computer|macbook|chromebook|ultrabook)\b',
            
            # Mobile Devices
            r'\b(smartphone|phone|mobile|iphone|android|galaxy|pixel|oneplus)\b',
            
            # Tablets
            r'\b(tablet|ipad|galaxy tab|surface|kindle|tab)\b',
            
            # Audio Devices
            r'\b(headphone|earphone|earbud|airpod|headset|speaker|soundbar|bluetooth speaker)\b',
            
            # Wearable Technology
            r'\b(smartwatch|watch|fitbit|apple watch|samsung watch|garmin|wearable)\b',
            
            # Cameras and Imaging
            r'\b(camera|dslr|mirrorless|action camera|gopro|digital camera|camcorder)\b',
            
            # Gaming Devices
            r'\b(gaming laptop|console|playstation|xbox|nintendo|gaming pc|steam deck)\b',
            
            # Home Entertainment
            r'\b(smart tv|television|tv|oled|qled|led tv|monitor|projector)\b',
            
            # Smart Home Devices
            r'\b(smart home|smart speaker|smart display|smart hub|alexa|google home|echo)\b',
            
            # Photography and Imaging Accessories
            r'\b(drone|gimbal|action cam|stabilizer|lens|tripod)\b',
            
            # Audio Equipment
            r'\b(microphone|mixer|audio interface|synthesizer|keyboard|midi controller)\b',
            
            # Networking Devices
            r'\b(router|modem|wifi extender|network switch|access point)\b',
            
            # Storage and Memory
            r'\b(external drive|ssd|hard drive|usb drive|memory card|flash drive)\b',
            
            # Miscellaneous Electronics
            r'\b(electronic|device|gadget|tech|accessory)\b'
        ]
        
        # Set up Groq Chat with Llama 3.1
        self.chat = ChatGroq(
            temperature=0.7,
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.output_parser = StrOutputParser()
        self.conversation_history = []
        
        # Pricing Strategy
        self.base_price_map = {
            'laptop': 800,
            'smartphone': 600,
            'tablet': 400,
            'headphone': 200,
            'smartwatch': 250,
            'camera': 500,
            'console': 400,
            'tv': 600,
            'default': 500
        }
        
        # Negotiation parameters
        self.urgency_threshold = 3
        self.interaction_count = 0
        self.lowest_offer_seen = float('inf')
        self.current_product = None

#      Detect electronic products with comprehensive pattern matching
    def extract_product_details(self, user_message):
      
        for pattern in self.product_patterns:
            match = re.search(pattern, user_message, re.IGNORECASE)
            if match:
                return match.group(0).lower()
        
        return "electronic device"

#      Dynamically determine base price based on product type
    def determine_base_price(self, product):
      
        normalized_product = ''.join(product.split()).lower()
        
        for key, price in self.base_price_map.items():
            if key in normalized_product:
                return price
        
        return self.base_price_map['default']

#      Strategic offer evaluation with product-specific nuances

    def evaluate_offer(self, user_offer):

        self.interaction_count += 1
        
        # Determine base price for current product
        base_price = self.determine_base_price(self.current_product)
        minimum_acceptable_price = base_price * 0.7
        
        # Track lowest offer
        self.lowest_offer_seen = min(self.lowest_offer_seen, user_offer)
        
        # Extremely low offer rejection
        if user_offer < minimum_acceptable_price * 0.6:
            return {
                "status": "reject",
                "message": f"${user_offer} is far below the value of our {self.current_product}. Our minimum price is ${minimum_acceptable_price:.2f}.",
                "counteroffer": base_price
            }
        
        # Slightly low offer counteroffer
        if user_offer < base_price * 0.8:
            counteroffer = (base_price + user_offer) / 1.5
            
            # Urgency messaging
            urgency_message = (
                f" Limited stock of {self.current_product} available! "
                "Tech evolves quickly, and this model won't be around forever."
            ) if self.interaction_count >= self.urgency_threshold else ""
            
            return {
                "status": "counteroffer",
                "message": f"Interesting offer. Let's meet at ${counteroffer:.2f}.{urgency_message}",
                "counteroffer": counteroffer
            }
        
        # Acceptable offer
        if user_offer >= base_price * 0.9:
            bonus_message = (
                f" Act now and get a free accessory pack for your {self.current_product}!" 
                if self.interaction_count >= self.urgency_threshold else ""
            )
            return {
                "status": "accept",
                "message": f"Excellent! We can finalize at ${user_offer:.2f}.{bonus_message}",
                "counteroffer": user_offer
            }
        
        # Default negotiation
        return {
            "status": "negotiate",
            "message": f"Let's continue our discussion about the {self.current_product}.",
            "counteroffer": base_price
        }

#    Negotiation method to handle user offers and generate responses

    def negotiate(self, user_message):
       
        self.current_product = self.extract_product_details(user_message)
        
        try:
            user_offer = float(''.join(filter(str.isdigit, user_message)) or 
                               self.determine_base_price(self.current_product))
        except ValueError:
            user_offer = self.determine_base_price(self.current_product)
        
        history_text = "\n".join([
            f"User: {turn['user_message']}\nBot: {turn['bot_response']}" 
            for turn in self.conversation_history
        ])
        
        negotiation_prompt = ChatPromptTemplate.from_messages([
            ("system", """
              You are a tough yet witty negotiator selling high-demand fashion items. Your goal is to maximize revenue while ensuring a win-win deal.

            **Base Price Determination:**
            - Based on the product name, estimate a reasonable base price. For example, luxury items like designer handbags might have a base price of $500, while casual items like t-shirts might be $50.
            - Assume high demand for trendy or seasonal items, and adjust the base price upward accordingly.

            **Negotiation Strategies:**
            - **Anchoring:** Start with a price higher than your target to set the negotiation range.
            - **Bracketing:** When countering, aim for a price that splits the difference between the user's offer and your desired price.
            - **Bundling:** Offer additional items or services to make the deal more attractive without lowering the price too much.
            - **Time-based Concessions:** If the user hesitates, gradually lower the price over multiple rounds, but never below your minimum acceptable price.
            - **Emotional Appeals:** Use language that highlights exclusivity, urgency, or the fear of missing out to encourage the user to agree.
            - **Urgency:** Mention limited stock or time-sensitive offers to prompt quicker decisions.
            - **Limited-time Discounts:** Introduce small, time-bound discounts if the user is close to agreeing but needs a nudge.

            **Negotiation Logic:**
            - Track the user's offers and adjust your strategy; if they consistently lowball, become firmer.
            - Set a minimum acceptable price (e.g., 75% of base price) and do not go below it.
            - Recognize when the user is near their maximum and push for closure with a final offer.
            - Handle multiple negotiation rounds by gradually conceding small amounts while maintaining your target.

            **Response Guidelines:**
            - In your first response, provide an initial response of 100-150 words introducing the product, highlighting its uniqueness and current demand, and setting a strong opening price based on the base price determination. Then, address the user's message if applicable.
            - For subsequent responses, respond concisely (small length) based on the user's message and the negotiation strategies.

            **Conversation Style:**
            - Be tough but engaging; use wit and charm to keep the negotiation lively.

            **Conversation History:** {conversation_history}
            """),
            ("human", "{user_message}")
        ])
        
        offer_evaluation = self.evaluate_offer(user_offer)
        
        negotiation_chain = negotiation_prompt | self.chat | self.output_parser
        
        try:
            enhanced_message = f"{user_message} (Offer: ${user_offer:.2f} for {self.current_product})"
            
            negotiation_response = negotiation_chain.invoke({
                "user_message": enhanced_message,
                "conversation_history": history_text,
                "product": self.current_product
            })
            
            final_response = f"{offer_evaluation['message']} {negotiation_response}"
            
            self.conversation_history.append({
                "user_message": user_message, 
                "bot_response": final_response
            })
            
            return final_response
        
        except Exception as e:
            return f"Negotiation error: {e}"


if __name__ == "__main__":
    bot = ElectronicsNegotiationBot()
    print("Advanced Electronics Negotiation Bot Ready!")
    while True:
        user_message = input("You: ").strip()
        if user_message.lower() in ["exit", "quit"]:
            break
        response = bot.negotiate(user_message)
        print("Vendor's Response:", response)