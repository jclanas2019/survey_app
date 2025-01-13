# app/services/llm_service.py
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
import asyncio

class LLMService:
    def __init__(self):
        self.llm = OllamaLLM(
            model="llama3.2",
            temperature=0.7
        )
        
        self.interpret_template = """
        Analiza los siguientes resultados de una encuesta de satisfacción:

        Promedios por categoría:
        {category_averages}

        Distribución general de respuestas:
        {response_distribution}

        Por favor, proporciona un análisis detallado que incluya:
        1. Interpretación general de los resultados
        2. Puntos fuertes identificados
        3. Áreas de mejora
        4. Recomendaciones específicas basadas en los datos

        Usa un tono profesional y constructivo. Limita la respuesta a 4-5 párrafos concisos.
        """

        self.interpret_prompt = PromptTemplate(
            input_variables=["category_averages", "response_distribution"],
            template=self.interpret_template
        )

    async def get_interpretation(self, stats: dict) -> str:
        try:
            category_averages_str = "\n".join([
                f"- {category}: {score}/5.0" 
                for category, score in stats['category_averages'].items()
            ])
            
            distribution_str = "\n".join([
                f"- Puntuación {score}: {count} respuestas" 
                for score, count in stats['response_distribution'].items()
            ])
            
            prompt = self.interpret_prompt.format(
                category_averages=category_averages_str,
                response_distribution=distribution_str
            )
            
            interpretation = await asyncio.to_thread(
                lambda: self.llm.predict(prompt)
            )
            
            return interpretation
        except Exception as e:
            return f"No se pudo generar la interpretación automática. Error: {str(e)}"