import os
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain

class NegotiationBot:
    def __init__(self, product: str):
        # Initialize OpenAI API key
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "your-api-key")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4-turbo",
            temperature=0.7,
            max_tokens=250
        )
        
        # Determine base price and negotiation style
        self.base_price = self._determine_base_price(product)
        self.negotiation_style = self._select_negotiation_style(product)
        
        # Create memory for conversation context
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create negotiation prompt template
        self.negotiation_prompt = PromptTemplate(
            input_variables=["product", "base_price", "negotiation_style", "chat_history", "human_input"],
            template="""
Negotiation Scenario:
- Product: {product}
- Base Price: ${base_price}
- Negotiation Style: {negotiation_style}

Conversation History:
{chat_history}

Current User Input: {human_input}

Negotiation Guidelines:
1. Maintain the selected negotiation style
2. Provide strategic and context-aware responses
3. Focus on achieving a mutually beneficial outcome
4. Adjust pricing and approach based on conversation progression

Respond as a skilled negotiator:
"""
        )
        
        # Create LLM Chain
        self.negotiation_chain = LLMChain(
            llm=self.llm,
            prompt=self.negotiation_prompt,
            memory=self.memory,
            verbose=True
        )
    
    def _determine_base_price(self, product: str) -> float:
        """
        Determine base price using LLM
        """
        price_prompt = PromptTemplate(
            input_variables=["product"],
            template="""
Estimate a precise market price for the product based on these criteria:
- Product: {product}
- Consider market value, quality, and typical pricing
- Provide a single numeric price in USD
- Range: $30 - $1000

Estimated Price:
"""
        )
        
        price_chain = LLMChain(llm=self.llm, prompt=price_prompt)
        result = price_chain.run(product)
        
        # Extract numeric price
        import re
        price_match = re.search(r'\$?(\d+(?:\.\d+)?)', result)
        return float(price_match.group(1)) if price_match else 200.0
    
    def _select_negotiation_style(self, product: str) -> str:
        """
        Select negotiation style based on product
        """
        style_prompt = PromptTemplate(
            input_variables=["product"],
            template="""
Recommend the most appropriate negotiation style for: {product}

Styles:
1. Friendly: Warm, relationship-focused
2. Aggressive: High-pressure, urgent
3. Premium: Luxury, high-end positioning
4. Budget: Cost-effective, value-driven
5. Collaborative: Problem-solving, win-win

Recommended Style:
"""
        )
        
        style_chain = LLMChain(llm=self.llm, prompt=style_prompt)
        result = style_chain.run(product)
        
        # Determine style based on result
        styles = ["friendly", "aggressive", "premium", "budget", "collaborative"]
        for style in styles:
            if style in result.lower():
                return style
        
        return "friendly"
    
    def negotiate(self, user_input: str) -> str:
        """
        Process negotiation response
        """
        response = self.negotiation_chain.run({
            "product": self.product,
            "base_price": self.base_price,
            "negotiation_style": self.negotiation_style,
            "human_input": user_input
        })
        
        return response

def main():
    print("🤖 Langchain Negotiation Bot 🤖")
    
    # Get product from user
    product = input("Describe the product you want to negotiate: ").lower()
    
    # Initialize negotiation bot
    bot = NegotiationBot(product)
    
    print(f"\n🏪 Vendor (Selected {bot.negotiation_style.capitalize()} style): Ready to negotiate {product}")
    print("Base Price: ${:.2f}".format(bot.base_price))
    print("Type 'exit' to end the conversation")
    
    # Negotiation loop
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() == 'exit':
                print("🏪 Vendor: Thanks for your interest. Have a great day!")
                break
            
            response = bot.negotiate(user_input)
            print(f"🏪 Vendor: {response}")
        
        except KeyboardInterrupt:
            print("\n\n🏪 Vendor: Negotiation interrupted. Come back when you're ready!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

if __name__ == "__main__":
    main()